#!/usr/bin/env python3
"""PrismWeave Document Processing CLI."""

from __future__ import annotations

import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, List, Optional

import click

from src.core.config import Config as _ConfigAlias
from src.cli_support import (
    CliError,
    CliState,
    SUPPORTED_EXTENSIONS,
    create_state,
    ensure_ollama_available,
    resolve_repository,
)
from src.core.document_processor import DocumentProcessor
from src.core.embedding_store import EmbeddingStore
from src.core.git_tracker import GitTracker

# Backwards compatibility for tests that patch cli.Config
Config = _ConfigAlias


def _document_metadata(document: Any) -> dict:
    metadata = getattr(document, "metadata", None)
    if isinstance(metadata, dict):
        return metadata
    metadata = getattr(document, "meta", None)
    return metadata if isinstance(metadata, dict) else {}


def _document_content(document: Any) -> str:
    content = getattr(document, "page_content", None)
    if isinstance(content, str):
        return content
    content = getattr(document, "content", "")
    return content if isinstance(content, str) else ""


def _clear_embeddings(state: CliState, store: EmbeddingStore) -> None:
    state.write("🗑️  Clearing existing embeddings...")
    store.clear_collection()

    if state.git_tracker:
        state.git_tracker.reset_processing_state()
        state.write("🔄 Reset processing state")

    state.write("✅ Embeddings cleared")
    state.write()


def _should_skip(file_path: Path, state: CliState, *, force: bool) -> bool:
    if force or not state.git_tracker:
        return False
    processed = state.git_tracker.is_file_processed(file_path)
    if processed:
        state.write_verbose(f"⏭️  Skipping {file_path.name} (already processed and unchanged)")
    return processed


def _process_single_file(
    file_path: Path,
    state: CliState,
    processor: DocumentProcessor,
    store: EmbeddingStore,
    *,
    force: bool = False,
) -> bool:
    if _should_skip(file_path, state, force=force):
        return True

    if state.verbose:
        state.write(f"🔮 Processing: {file_path}")
        state.write(f"🤖 Using model: {state.config.embedding_model}")
        state.write(f"💾 Storage: {state.config.chroma_db_path}")
        state.write()

    try:
        existing_count = store.get_file_document_count(file_path)
        if existing_count > 0:
            state.write_verbose(
                f"🔄 Found {existing_count} existing chunks, removing for update..."
            )
            store.remove_file_documents(file_path)

        state.write_verbose("📄 Loading and processing document...")
        chunks = processor.process_document(file_path)

        if not chunks:
            state.write(f"❌ No chunks generated for {file_path}")
            return False

        state.write_verbose(f"✅ Generated {len(chunks)} chunks")
        state.write_verbose("🔗 Generating and storing embeddings...")
        store.add_document(file_path, chunks)

        if state.verbose:
            state.write_verbose("🔍 Verifying embeddings storage...")
            verification = store.verify_embeddings()
            state.write_verbose(f"✅ Verification result: {verification}")
            state.write_verbose("\n📊 Sample chunk metadata:")
            for index, chunk in enumerate(chunks[:2], start=1):
                metadata = _document_metadata(chunk)
                state.write_verbose(f"  Chunk {index}:")
                state.write_verbose(f"    Content preview: {chunk.content[:100]}...")
                state.write_verbose(f"    Metadata keys: {list(metadata.keys())}")
                if "tags" in metadata:
                    state.write_verbose(f"    Tags: {metadata['tags']}")
                state.write_verbose("")
        else:
            state.write(f"✅ Processed {file_path.name} ({len(chunks)} chunks)")

        return True

    except Exception as exc:  # pragma: no cover - relies on environment interaction
        state.write(f"❌ Error processing {file_path.name}: {exc}")
        if state.verbose:
            import traceback

            traceback.print_exc()
        return False


def _collect_directory_files(
    directory: Path,
    state: CliState,
    *,
    incremental: bool,
    force: bool,
) -> List[Path]:
    if incremental and not state.git_tracker:
        raise CliError("Incremental processing requires a git repository")

    if incremental and state.git_tracker:
        files = list(
            state.git_tracker.get_unprocessed_files(
                file_extensions=set(SUPPORTED_EXTENSIONS)
            )
        )
        state.write_verbose(f"📂 Incremental mode: Found {len(files)} unprocessed files")
        return files

    discovered: List[Path] = []
    for extension in SUPPORTED_EXTENSIONS:
        discovered.extend(directory.rglob(f"*{extension}"))

    mode_text = "force" if force else "full"
    state.write_verbose(f"📂 Processing in {mode_text} mode: Found {len(discovered)} files")
    return discovered


def _summarize_processing(
    state: CliState,
    *,
    success_count: int,
    error_count: int,
    elapsed: float,
) -> None:
    if state.rich:
        table = state.rich.Table(title="Processing Summary")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        table.add_row("✅ Successful", str(success_count))
        if error_count:
            table.add_row("❌ Failed", str(error_count))
        table.add_row("⏱️  Time Elapsed", f"{elapsed:.1f}s")
        if success_count:
            table.add_row("📈 Avg Time/File", f"{elapsed / success_count:.2f}s")
        state.write()
        state.rich.console.print(table)
        return

    state.write("\n📊 Processing Summary:")
    state.write(f"   ✅ Successfully processed: {success_count} files")
    if error_count:
        state.write(f"   ❌ Failed to process: {error_count} files")
    state.write(f"   ⏱️  Time elapsed: {elapsed:.1f}s")
    if success_count:
        state.write(f"   📈 Average time per file: {elapsed / success_count:.2f}s")


def _process_directory(
    directory: Path,
    state: CliState,
    processor: DocumentProcessor,
    store: EmbeddingStore,
    *,
    incremental: bool,
    force: bool,
) -> bool:
    files = _collect_directory_files(directory, state, incremental=incremental, force=force)

    if not files:
        if incremental:
            state.write("✅ No new or changed files to process")
            return True
        state.write(f"❌ No supported files found in {directory}")
        state.write(f"   Supported extensions: {', '.join(SUPPORTED_EXTENSIONS)}")
        return False

    success_count = 0
    error_count = 0
    start = time.time()

    use_progress = state.rich is not None and len(files) > 5
    if use_progress:
        resources = state.rich
        assert resources is not None
        progress = resources.Progress(
            resources.SpinnerColumn(),
            resources.TextColumn("[progress.description]{task.description}"),
            resources.BarColumn(),
            resources.TaskProgressColumn(),
            resources.TimeRemainingColumn(),
            console=resources.console,
        )
        with progress as bar:
            task = bar.add_task("[cyan]Processing documents...", total=len(files))
            for file_path in files:
                bar.update(task, description=f"[cyan]Processing: {file_path.name}")
                try:
                    if _process_single_file(
                        file_path,
                        state,
                        processor,
                        store,
                        force=force,
                    ):
                        success_count += 1
                    else:
                        error_count += 1
                except KeyboardInterrupt:  # pragma: no cover - user interaction
                    state.write("\n⏹️  Processing interrupted by user")
                    break
                finally:
                    bar.update(task, advance=1)
    else:
        for index, file_path in enumerate(files, start=1):
            state.write(f"[{index}/{len(files)}] Processing: {file_path.name}")
            try:
                if _process_single_file(
                    file_path,
                    state,
                    processor,
                    store,
                    force=force,
                ):
                    success_count += 1
                else:
                    error_count += 1
            except KeyboardInterrupt:  # pragma: no cover - user interaction
                state.write("\n⏹️  Processing interrupted by user")
                break

    elapsed = time.time() - start
    _summarize_processing(
        state,
        success_count=success_count,
        error_count=error_count,
        elapsed=elapsed,
    )

    if success_count and state.git_tracker:
        try:
            state.git_tracker.update_last_processed_commit()
            state.write_verbose("   🔄 Updated processing state")
        except Exception as exc:  # pragma: no cover - external git state
            state.write(f"   ⚠️  Warning: Failed to update processing state: {exc}")

    return success_count > 0


def _auto_detect_repository() -> Optional[Path]:
    current = Path.cwd()
    if (current / ".git").exists():
        return current

    for candidate in (
        current / "PrismWeaveDocs",
        current.parent / "PrismWeaveDocs",
        current / "documents",
        current / "docs",
    ):
        if (candidate / ".git").exists():
            return candidate
    return None


def _initialize_git_tracker(
    repo_root: Optional[Path],
    *,
    verbose: bool,
    strict: bool,
) -> Optional[GitTracker]:
    if not repo_root:
        return None

    try:
        tracker = GitTracker(repo_root)
    except Exception as exc:  # pragma: no cover - depends on git setup
        if strict:
            raise CliError(f"Failed to initialize git tracking: {exc}") from exc
        print(f"⚠️  Warning: Git tracking not available: {exc}")
        return None

    if verbose:
        print("🔁 Pulling latest changes from remote...")
    try:
        tracker.pull_latest()
        if verbose:
            print("   ✅ Repository up to date")
    except Exception as exc:  # pragma: no cover - depends on git setup
        print(f"⚠️  Warning: Failed to pull latest changes: {exc}")

    return tracker


def _print_git_summary(state: CliState, repo_root: Path) -> None:
    if not state.verbose or not state.git_tracker:
        return
    summary = state.git_tracker.get_processing_summary()
    state.write_verbose(f"🔄 Git repository: {repo_root}")
    state.write_verbose(
        f"📊 Processing state: {summary['processed_files']} processed, {summary['unprocessed_files']} unprocessed"
    )
    state.write_verbose("")


def _handle_cli_error(exc: CliError) -> None:
    print(f"❌ {exc}")
    sys.exit(1)


@click.group()
def cli() -> None:
    """PrismWeave Document Processing CLI."""


@cli.command()
@click.argument("path", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, path_type=Path),
    help="Configuration file path (default: config.yaml)",
)
@click.option("--verbose", "-v", is_flag=True, help="Show detailed output and metadata")
@click.option("--verify", is_flag=True, help="Verify embeddings storage after processing")
@click.option("--clear", is_flag=True, help="Clear existing embeddings before processing")
@click.option(
    "--incremental",
    "-i",
    is_flag=True,
    help="Only process new or changed files (requires git repository)",
)
@click.option("--force", "-f", is_flag=True, help="Force reprocessing of all files")
@click.option(
    "--repo-path",
    type=click.Path(exists=True, path_type=Path),
    help="Path to git repository (default: auto-detect from path)",
)
def process(
    path: Path,
    config: Optional[Path],
    verbose: bool,
    verify: bool,
    clear: bool,
    incremental: bool,
    force: bool,
    repo_path: Optional[Path],
) -> None:
    """Process documents and generate embeddings using Haystack and Ollama."""

    print("🔮 PrismWeave Document Processor")
    print("=" * 40)

    try:
        if incremental and force:
            raise CliError("Cannot use --incremental and --force together")
        if incremental and clear:
            raise CliError("Cannot use --incremental and --clear together")

        repo_root = resolve_repository(path, repo_path)
        if incremental and not repo_root:
            raise CliError("Incremental processing requires a git repository")

        git_tracker = _initialize_git_tracker(
            repo_root,
            verbose=verbose,
            strict=incremental or repo_path is not None,
        )
        state = create_state(config, verbose, git_tracker)
        if repo_root:
            _print_git_summary(state, repo_root)

        state.write("🔍 Checking Ollama availability...")
        ensure_ollama_available(state.config)
        state.write_verbose("✅ Ollama is running\n")

        processor = DocumentProcessor(state.config, state.git_tracker)
        store = EmbeddingStore(state.config, state.git_tracker)

        if clear:
            _clear_embeddings(state, store)

        if path.is_file():
            state.write(f"📄 Processing single file: {path}")
            if incremental:
                state.write("   (Note: Incremental mode applies to directory processing)")
            state.write()
            success = _process_single_file(
                path,
                state,
                processor,
                store,
                force=force,
            )
        elif path.is_dir():
            mode_desc = "incremental" if incremental else ("force" if force else "standard")
            state.write(f"📂 Processing directory: {path} (mode: {mode_desc})\n")
            success = _process_directory(
                path,
                state,
                processor,
                store,
                incremental=incremental,
                force=force,
            )
        else:
            raise CliError(f"Path is neither a file nor a directory: {path}")

        if not success:
            raise CliError("Processing failed")

        if verify:
            state.write("\n🔍 Verifying embeddings storage...")
            verification = store.verify_embeddings()
            state.write(f"✅ Verification result: {verification}")

        if state.git_tracker:
            try:
                state.git_tracker.commit_processing_state()
                state.write_verbose("📝 Committed processing state")
            except Exception as exc:  # pragma: no cover - external git state
                state.write(f"⚠️  Warning: Failed to commit processing state: {exc}")

        state.write("\n✅ Processing completed successfully!")

    except CliError as exc:
        _handle_cli_error(exc)
    except KeyboardInterrupt:  # pragma: no cover - user interaction
        print("\n⏹️  Processing interrupted by user")
        sys.exit(0)


@cli.command()
@click.argument("repo_path", type=click.Path(exists=True, path_type=Path), required=False)
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, path_type=Path),
    help="Configuration file path (default: config.yaml)",
)
@click.option("--force", is_flag=True, help="Force reprocessing of all files")
@click.option("--verbose", "-v", is_flag=True, help="Show detailed processing information")
def sync(repo_path: Optional[Path], config: Optional[Path], force: bool, verbose: bool) -> None:
    """Sync documents from a git repository, processing only new or changed files."""

    print("🔮 PrismWeave Document Sync")
    print("=" * 40)

    try:
        detected_repo = repo_path or _auto_detect_repository()
        if not detected_repo:
            raise CliError(
                "No git repository found. Specify a repository path or run from within a repository."
            )

        repo_root = resolve_repository(detected_repo, repo_path)
        git_tracker = _initialize_git_tracker(
            repo_root,
            verbose=verbose,
            strict=not force,
        )
        state = create_state(config, verbose, git_tracker)
        state.write(f"📂 Repository: {repo_root}")

        state.write("🔍 Checking Ollama availability...")
        ensure_ollama_available(state.config)
        state.write_verbose("✅ Ollama is running")

        if repo_root:
            _print_git_summary(state, repo_root)

        processor = DocumentProcessor(state.config, state.git_tracker)
        store = EmbeddingStore(state.config, state.git_tracker)

        mode = "force" if force else "incremental"
        state.write(f"🔄 Starting sync (mode: {mode})\n")

        success = _process_directory(
            repo_root,
            state,
            processor,
            store,
            incremental=not force,
            force=force,
        )
        if not success:
            raise CliError("Sync failed")

        if state.git_tracker:
            try:
                state.git_tracker.commit_processing_state()
                state.write_verbose("📝 Committed processing state")
            except Exception as exc:  # pragma: no cover - external git state
                state.write(f"⚠️  Warning: Failed to commit processing state: {exc}")

        state.write("\n✅ Sync completed successfully!")

    except CliError as exc:
        _handle_cli_error(exc)
    except KeyboardInterrupt:  # pragma: no cover
        print("\n⏹️  Sync interrupted by user")
        sys.exit(0)


@cli.command("list")
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, path_type=Path),
    help="Configuration file path (default: config.yaml)",
)
@click.option(
    "--max",
    "-m",
    "max_documents",
    type=int,
    default=50,
    help="Maximum number of files to show (default: 50)",
)
@click.option("--verbose", "-v", is_flag=True, help="Show detailed document information")
@click.option("--source-files", "-s", is_flag=True, help="Show unique source files only")
def list_docs(
    config: Optional[Path],
    max_documents: int,
    verbose: bool,
    source_files: bool,
) -> None:
    """List documents stored in the ChromaDB collection."""

    print("🔮 PrismWeave Document List")
    print("=" * 40)

    try:
        state = create_state(config, verbose)
        store = EmbeddingStore(state.config)

        if source_files:
            state.write("📂 Unique source files in collection:")
            files = store.get_unique_source_files()
            if not files:
                state.write("   No source files found in collection")
                return

            files_to_show = files[:max_documents] if max_documents else files
            for index, file_path in enumerate(files_to_show, start=1):
                state.write(f"   {index:3d}. {Path(file_path).name}")
                state.write_verbose(f"        📁 Full path: {file_path}")

            state.write(
                f"\n📊 Showing {len(files_to_show)} of {len(files)} unique source files"
            )
            return

        state.write(
            f"📄 {'Document chunks' if verbose else 'Source files'} in collection (max: {max_documents}):\n"
        )

        documents = store.list_documents(max_documents)
        if not documents:
            state.write("   No documents found in collection")
            verification = store.verify_embeddings()
            state.write(f"\n🔍 Collection info: {verification}")
            return

        if not verbose:
            all_documents = store.list_documents(None)
            if not all_documents:
                state.write("   No documents found in collection")
                verification = store.verify_embeddings()
                state.write(f"\n🔍 Collection info: {verification}")
                return

            source_groups = {}
            for doc in all_documents:
                source_file = doc["metadata"].get("source_file", "Unknown")
                source_groups.setdefault(source_file, []).append(doc)

            files_to_show = list(source_groups.items())[:max_documents]
            for index, (source_file, docs) in enumerate(files_to_show, start=1):
                file_name = Path(source_file).name if source_file != "Unknown" else "Unknown"
                state.write(f"   {index:3d}. {file_name}")
                state.write(f"        📄 Chunks: {len(docs)}")
                if docs and "tags" in docs[0]["metadata"]:
                    state.write(f"        🏷️  Tags: {docs[0]['metadata']['tags']}")
                total_chars = sum(doc["content_length"] for doc in docs)
                state.write(f"        📏 Total content: {total_chars:,} characters\n")

            files_shown = len(files_to_show)
            total_files = len(source_groups)
            total_chunks = sum(len(docs) for docs in source_groups.values())
            state.write(f"📊 Summary: {files_shown} files shown")
            state.write(
                f"   (Total in collection: {total_files} files, {total_chunks:,} chunks)"
            )
            return

        for index, doc in enumerate(documents, start=1):
            metadata = doc["metadata"]
            source_file = metadata.get("source_file", "Unknown")
            file_name = Path(source_file).name if source_file != "Unknown" else "Unknown"
            state.write(f"   {index:3d}. Chunk ID: {doc['id']}")
            state.write(f"        📁 File: {file_name}")
            if "chunk_index" in metadata:
                chunk_info = f"{metadata['chunk_index'] + 1}/{metadata.get('total_chunks', '?')}"
                state.write(f"        🔢 Chunk: {chunk_info}")
            state.write(f"        📄 Length: {doc['content_length']} characters")
            if "tags" in metadata:
                state.write(f"        🏷️  Tags: {metadata['tags']}")
            state.write(f"        📝 Preview: {doc['content_preview']}\n")

        state.write(f"📊 Showing {len(documents)} chunks")
        total_count = store.get_document_count()
        if len(documents) < total_count:
            state.write(f"   (Total in collection: {total_count:,} chunks)")

    except CliError as exc:
        _handle_cli_error(exc)


@cli.command()
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, path_type=Path),
    help="Configuration file path (default: config.yaml)",
)
def count(config: Optional[Path]) -> None:
    """Show the total count of documents in the ChromaDB collection."""

    print("🔮 PrismWeave Document Count")
    print("=" * 40)

    try:
        state = create_state(config, verbose=False)
        store = EmbeddingStore(state.config)

        total_documents = store.get_document_count()
        unique_sources = len(store.get_unique_source_files())

        state.write("📊 Collection Statistics:")
        state.write(f"   📄 Total document chunks: {total_documents:,}")
        state.write(f"   📁 Unique source files: {unique_sources:,}")
        if total_documents and unique_sources:
            avg_chunks = total_documents / unique_sources
            state.write(f"   📈 Average chunks per file: {avg_chunks:.1f}")

        verification = store.verify_embeddings()
        state.write(f"   🗄️  Collection name: {verification.get('collection_name', 'Unknown')}")
        state.write(f"   💾 Storage path: {verification.get('persist_directory', 'Unknown')}")

    except CliError as exc:
        _handle_cli_error(exc)


@cli.command()
@click.argument("query")
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, path_type=Path),
    help="Configuration file path (default: config.yaml)",
)
@click.option(
    "--max",
    "-m",
    "max_results",
    type=int,
    default=10,
    help="Maximum number of results to return (default: 10)",
)
@click.option(
    "--threshold",
    "-t",
    type=float,
    default=0.0,
    help="Minimum similarity threshold (0.0-1.0, default: 0.0)",
)
@click.option("--verbose", "-v", is_flag=True, help="Show detailed search results")
@click.option("--filter-type", type=str, help="Filter results by file type (e.g., md, txt, pdf)")
def search(
    query: str,
    config: Optional[Path],
    max_results: int,
    threshold: float,
    verbose: bool,
    filter_type: Optional[str],
) -> None:
    """Search documents using semantic similarity."""

    try:
        state = create_state(config, verbose)
        store = EmbeddingStore(state.config)

        heading = "🔍 PrismWeave Semantic Search"
        if state.rich:
            state.rich.console.print(state.rich.Panel(heading, style="bold cyan"))
        else:
            state.write(heading)
            state.write("=" * 40)

        if state.rich:
            with state.rich.console.status(f"[bold green]Searching for: {query}..."):
                results = store.search_similar(query, k=max_results)
        else:
            state.write(f"\n🔎 Searching for: {query}")
            results = store.search_similar(query, k=max_results)

        if threshold > 0.0:
            filtered = []
            for doc in results:
                metadata = _document_metadata(doc)
                if metadata.get("score", 0.0) >= threshold:
                    filtered.append(doc)
            results = filtered

        if filter_type:
            suffix = f".{filter_type.lstrip('.')}"
            filtered = []
            for doc in results:
                metadata = _document_metadata(doc)
                if Path(metadata.get("source_file", "")).suffix == suffix:
                    filtered.append(doc)
            results = filtered

        if not results:
            state.write("\n❌ No results found")
            return

        state.write(f"\n✅ Found {len(results)} results\n")

        for index, doc in enumerate(results, start=1):
            metadata = _document_metadata(doc)
            source_file = metadata.get("source_file", "Unknown")
            file_name = Path(source_file).name if source_file != "Unknown" else "Unknown"
            chunk_info = ""
            if "chunk_index" in metadata and "total_chunks" in metadata:
                chunk_info = f"{metadata['chunk_index'] + 1}/{metadata['total_chunks']}"

            content = _document_content(doc)
            preview_length = 500 if verbose else 200
            preview = content[:preview_length]
            if len(content) > preview_length:
                preview += "..."

            tags = metadata.get("tags")
            score = metadata.get("score")
            lines: List[str] = [f"📁 File: {file_name}"]
            if chunk_info:
                lines.append(f"🔢 Chunk: {chunk_info}")
            if tags:
                lines.append(f"🏷️  Tags: {tags}")
            if score is not None:
                try:
                    lines.append(f"📈 Score: {float(score):.3f}")
                except (TypeError, ValueError):
                    lines.append(f"📈 Score: {score}")
            lines.append("\n📝 Content:\n" + preview)

            if state.rich:
                title = f"Result {index}: {file_name}"
                state.rich.console.print(
                    state.rich.Panel("\n".join(lines), title=title, border_style="green")
                )
            else:
                state.write(f"{index}. {file_name}")
                for line in lines:
                    state.write(f"   {line}")
                state.write()

    except CliError as exc:
        _handle_cli_error(exc)


@cli.command()
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, path_type=Path),
    help="Configuration file path (default: config.yaml)",
)
@click.option("--detailed", "-d", is_flag=True, help="Show detailed analytics")
def stats(config: Optional[Path], detailed: bool) -> None:
    """Show collection statistics and analytics."""

    try:
        state = create_state(config, verbose=detailed)
        store = EmbeddingStore(state.config)

        heading = "📊 PrismWeave Collection Statistics"
        if state.rich:
            state.rich.console.print(state.rich.Panel(heading, style="bold cyan"))
        else:
            state.write(heading)
            state.write("=" * 40)

        total_chunks = store.get_document_count()
        source_files = store.get_unique_source_files()
        total_files = len(source_files)

        if total_chunks == 0:
            state.write("\n❌ No documents in collection")
            return

        avg_chunks = total_chunks / total_files if total_files else 0
        state.write()

        if state.rich:
            overview = state.rich.Table(title="Collection Overview", show_header=True)
            overview.add_column("Metric", style="cyan")
            overview.add_column("Value", style="green")
            overview.add_row("📄 Total Chunks", f"{total_chunks:,}")
            overview.add_row("📁 Source Files", f"{total_files:,}")
            overview.add_row("📈 Avg Chunks/File", f"{avg_chunks:.1f}")
            if detailed:
                documents = store.list_documents(None)
                total_content_length = sum(doc["content_length"] for doc in documents)
                if total_content_length:
                    overview.add_row("📏 Total Content", f"{total_content_length:,} chars")
                    overview.add_row(
                        "📊 Avg Chunk Size",
                        f"{total_content_length / total_chunks:.0f} chars",
                    )
            state.rich.console.print(overview)
        else:
            state.write("📊 Collection Overview:")
            state.write(f"   📄 Total chunks: {total_chunks:,}")
            state.write(f"   📁 Source files: {total_files:,}")
            state.write(f"   📈 Average chunks per file: {avg_chunks:.1f}")

        if detailed:
            documents = store.list_documents(None)
            file_types = {}
            tag_frequency = {}
            total_content = 0
            for doc in documents:
                metadata = doc["metadata"]
                source_file = metadata.get("source_file", "")
                if source_file:
                    ext = Path(source_file).suffix or "no extension"
                    file_types[ext] = file_types.get(ext, 0) + 1
                total_content += doc["content_length"]
                tags = metadata.get("tags", "")
                for tag in (item.strip() for item in tags.split(",")):
                    if tag:
                        tag_frequency[tag] = tag_frequency.get(tag, 0) + 1

            if state.rich and file_types:
                table = state.rich.Table(title="File Type Distribution", show_header=True)
                table.add_column("Extension", style="cyan")
                table.add_column("Count", style="green")
                table.add_column("Percentage", style="yellow")
                for ext, count in sorted(file_types.items(), key=lambda item: item[1], reverse=True):
                    table.add_row(ext, str(count), f"{(count / total_chunks) * 100:.1f}%")
                state.rich.console.print(table)
            elif file_types:
                state.write("\n📑 File Type Distribution:")
                for ext, count in sorted(file_types.items(), key=lambda item: item[1], reverse=True):
                    state.write(f"   {ext}: {count} ({(count / total_chunks) * 100:.1f}%)")

            if state.rich and tag_frequency:
                tag_table = state.rich.Table(title="Top 10 Tags", show_header=True)
                tag_table.add_column("Tag", style="cyan")
                tag_table.add_column("Frequency", style="green")
                for tag, freq in sorted(tag_frequency.items(), key=lambda item: item[1], reverse=True)[
                    :10
                ]:
                    tag_table.add_row(tag, str(freq))
                state.rich.console.print(tag_table)
            elif tag_frequency:
                state.write("\n🏷️  Top 10 Tags:")
                for tag, freq in sorted(tag_frequency.items(), key=lambda item: item[1], reverse=True)[
                    :10
                ]:
                    state.write(f"   {tag}: {freq}")

            if total_content:
                state.write(f"\n📏 Total content: {total_content:,} characters")
                state.write(f"📊 Average chunk size: {total_content / total_chunks:.0f} characters")

        verification = store.verify_embeddings()
        state.write(
            f"\nCollection: {verification.get('collection_name', 'Unknown')}"
        )
        state.write(f"Storage: {verification.get('persist_directory', 'Unknown')}")

    except CliError as exc:
        _handle_cli_error(exc)


@cli.command()
@click.argument("output_file", type=click.Path(path_type=Path))
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, path_type=Path),
    help="Configuration file path (default: config.yaml)",
)
@click.option(
    "--format",
    "-f",
    type=click.Choice(["json", "csv"]),
    default="json",
    help="Export format (default: json)",
)
@click.option("--filter-type", type=str, help="Filter by file type (e.g., md, txt, pdf)")
@click.option("--include-content", is_flag=True, help="Include full content in export (JSON only)")
@click.option("--max", "-m", "max_docs", type=int, help="Maximum number of documents to export")
def export(
    output_file: Path,
    config: Optional[Path],
    format: str,
    filter_type: Optional[str],
    include_content: bool,
    max_docs: Optional[int],
) -> None:
    """Export documents and metadata to JSON or CSV."""

    print("💾 PrismWeave Document Export")
    print("=" * 40)

    try:
        state = create_state(config, verbose=False)
        store = EmbeddingStore(state.config)

        state.write("\n📥 Retrieving documents...")
        documents = store.list_documents(max_docs)
        if not documents:
            state.write("❌ No documents to export")
            return

        if filter_type:
            suffix = f".{filter_type.lstrip('.')}"
            documents = [
                doc
                for doc in documents
                if Path(doc["metadata"].get("source_file", "")).suffix == suffix
            ]
            if not documents:
                state.write(f"❌ No documents found with file type: {filter_type}")
                return
            state.write(f"🔍 Filtered to {len(documents)} documents with type: {filter_type}")

        export_data = {
            "export_date": datetime.now().isoformat(),
            "total_documents": len(documents),
            "collection_name": state.config.collection_name,
            "documents": [],
        }

        for doc in documents:
            metadata = doc["metadata"]
            payload = {
                "id": doc["id"],
                "source_file": metadata.get("source_file", "Unknown"),
                "chunk_index": metadata.get("chunk_index"),
                "total_chunks": metadata.get("total_chunks"),
                "tags": metadata.get("tags", ""),
                "content_length": doc["content_length"],
            }

            if include_content and format == "json":
                try:
                    full_docs = store.document_store.get_documents(ids=[doc["id"]])
                    if full_docs:
                        payload["content"] = full_docs[0].content
                    else:
                        payload["content_preview"] = doc["content_preview"]
                except Exception as exc:  # pragma: no cover - external dependency
                    state.write(f"⚠️  Warning: Failed to fetch full content: {exc}")
                    payload["content_preview"] = doc["content_preview"]
            else:
                payload["content_preview"] = doc["content_preview"]

            export_data["documents"].append(payload)

        if format == "json":
            state.write(f"\n💾 Exporting to JSON: {output_file}")
            with output_file.open("w", encoding="utf-8") as handle:
                json.dump(export_data, handle, indent=2, ensure_ascii=False)
        else:
            state.write(f"\n💾 Exporting to CSV: {output_file}")
            import csv

            with output_file.open("w", newline="", encoding="utf-8") as handle:
                fieldnames = [
                    "id",
                    "source_file",
                    "chunk_index",
                    "total_chunks",
                    "tags",
                    "content_length",
                    "content_preview",
                ]
                writer = csv.DictWriter(handle, fieldnames=fieldnames)
                writer.writeheader()
                for payload in export_data["documents"]:
                    writer.writerow(
                        {
                            "id": payload["id"],
                            "source_file": payload.get("source_file", ""),
                            "chunk_index": payload.get("chunk_index", ""),
                            "total_chunks": payload.get("total_chunks", ""),
                            "tags": payload.get("tags", ""),
                            "content_length": payload.get("content_length", 0),
                            "content_preview": payload.get(
                                "content_preview",
                                payload.get("content", ""),
                            ),
                        }
                    )

        state.write(f"✅ Exported {len(documents)} documents to {output_file}")
        state.write(f"   File size: {output_file.stat().st_size / 1024:.1f} KB")

    except CliError as exc:
        _handle_cli_error(exc)


def main() -> None:
    """Entry point for the CLI when executed directly."""

    cli()


if __name__ == "__main__":
    main()
