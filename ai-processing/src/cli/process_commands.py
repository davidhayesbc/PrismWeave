"""Process and sync commands for PrismWeave CLI."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path
from typing import Optional

import click

from src.cli_support import CliError, create_state, ensure_ollama_available, resolve_repository
from src.core.document_processor import DocumentProcessor
from src.core.embedding_store import EmbeddingStore

from .git_utils import auto_detect_repository, initialize_git_tracker, print_git_summary
from .processing_utils import clear_embeddings, process_directory, process_single_file


def handle_cli_error(exc: CliError) -> None:
    """Handle CLI errors by printing and exiting."""
    print(f"❌ {exc}")
    sys.exit(1)


@click.command()
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
    *,
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

        git_tracker = initialize_git_tracker(
            repo_root,
            verbose=verbose,
            strict=incremental or repo_path is not None,
        )
        state = create_state(config, verbose, git_tracker)
        if repo_root:
            print_git_summary(state, repo_root)

        state.write("🔍 Checking Ollama availability...")
        ensure_ollama_available(state.config)
        state.write_verbose("✅ Ollama is running\n")

        processor = DocumentProcessor(state.config, state.git_tracker)
        store = EmbeddingStore(state.config, state.git_tracker)

        if clear:
            clear_embeddings(state, store)

        if path.is_file():
            state.write(f"📄 Processing single file: {path}")
            if incremental:
                state.write("   (Note: Incremental mode applies to directory processing)")
            state.write()
            success = process_single_file(
                path,
                state,
                processor,
                store,
                force=force,
            )
        elif path.is_dir():
            mode_desc = "incremental" if incremental else ("force" if force else "standard")
            state.write(f"📂 Processing directory: {path} (mode: {mode_desc})\n")
            success = process_directory(
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
            except (OSError, RuntimeError) as exc:
                state.write(f"⚠️  Warning: Failed to commit processing state: {exc}")

        state.write("\n✅ Processing completed successfully!")

    except CliError as exc:
        handle_cli_error(exc)
    except KeyboardInterrupt:
        print("\n⏹️  Processing interrupted by user")
        sys.exit(0)


@click.command()
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
        detected_repo = repo_path or auto_detect_repository()
        if not detected_repo:
            raise CliError("No git repository found. Specify a repository path or run from within a repository.")

        repo_root = resolve_repository(detected_repo, repo_path)
        if not repo_root:
            # Fail early with a clear error so subsequent calls receive a proper Path
            raise CliError(f"Failed to resolve repository path: {detected_repo}")

        git_tracker = initialize_git_tracker(
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
            print_git_summary(state, repo_root)

        processor = DocumentProcessor(state.config, state.git_tracker)
        store = EmbeddingStore(state.config, state.git_tracker)

        mode = "force" if force else "incremental"
        state.write(f"🔄 Starting sync (mode: {mode})\n")

        success = process_directory(
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
            except (OSError, RuntimeError) as exc:  # pragma: no cover - external git state
                state.write(f"⚠️  Warning: Failed to commit processing state: {exc}")

        state.write("\n✅ Sync completed successfully!")

    except CliError as exc:
        handle_cli_error(exc)
    except KeyboardInterrupt:  # pragma: no cover
        print("\n⏹️  Sync interrupted by user")
        sys.exit(0)


@click.command(name="rebuild-db")
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, path_type=Path),
    help="Configuration file path (default: config.yaml)",
)
@click.option("--verbose", "-v", is_flag=True, help="Show detailed rebuild output")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompts")
def rebuild_db(config: Optional[Path], verbose: bool, yes: bool) -> None:
    """Clean and rebuild the ChromaDB embedding store for all documents."""

    print("🔮 PrismWeave ChromaDB Rebuild")
    print("=" * 40)

    state = None

    try:
        state = create_state(config, verbose)

        docs_root = Path(state.config.mcp.paths.documents_root).expanduser().resolve()
        chroma_path = Path(state.config.chroma_db_path).expanduser().resolve()
        processing_state_file = docs_root / ".prismweave" / "processing_state.sqlite"
        processing_state_file.parent.mkdir(parents=True, exist_ok=True)

        if not docs_root.exists():
            raise CliError(f"Documents root not found: {docs_root}")

        state.write(f"📁 Documents root: {docs_root}")
        state.write(f"🧠 ChromaDB path: {chroma_path}")
        state.write(f"🗂️  Processing state: {processing_state_file}\n")

        if not yes:
            confirm = click.confirm(
                "This will DELETE the ChromaDB database and processing_state.sqlite. Continue?",
                default=False,
            )
            if not confirm:
                state.write("❎ Rebuild cancelled.")
                return

        if chroma_path.exists():
            shutil.rmtree(chroma_path)
            state.write("🧹 Removed existing ChromaDB directory")
        else:
            state.write("ℹ️ ChromaDB directory already clean")

        chroma_path.mkdir(parents=True, exist_ok=True)

        if processing_state_file.exists():
            processing_state_file.unlink()
            state.write("🗑️  Deleted processing_state.sqlite")
        else:
            state.write("ℹ️ processing_state.sqlite not found (already clean)")

        repo_root = docs_root if (docs_root / ".git").exists() else None
        git_tracker = initialize_git_tracker(
            repo_root,
            verbose=verbose,
            strict=False,
        )
        state.git_tracker = git_tracker

        if repo_root and git_tracker:
            print_git_summary(state, repo_root)
        elif repo_root and not git_tracker:
            state.write("⚠️  Proceeding without git tracking (initialization failed)")

        state.write("\n🔍 Checking Ollama availability...")
        ensure_ollama_available(state.config)
        state.write_verbose("✅ Ollama is running\n")

        processor = DocumentProcessor(state.config, state.git_tracker)
        store = EmbeddingStore(state.config, state.git_tracker)

        state.write("⚙️  Rebuilding embeddings for all supported documents...\n")
        success = process_directory(
            docs_root,
            state,
            processor,
            store,
            incremental=False,
            force=True,
        )

        if not success:
            raise CliError("Rebuild failed: no documents were processed")

        state.write("\n🔍 Verifying rebuilt collection...")
        verification = store.verify_embeddings()

        if verification.get("status") != "success":
            raise CliError(f"Verification failed: {verification.get('error', 'unknown error')}")

        doc_count = verification.get("document_count", 0)
        collection = verification.get("collection_name", state.config.collection_name)
        state.write(f"✅ Rebuild complete: {doc_count} chunks stored in '{collection}'")

        search_state = verification.get("search_functional")
        if search_state is not None:
            label = "functional" if search_state else "unavailable"
            state.write(f"🔎 Search status: {label}")

    except CliError as exc:
        handle_cli_error(exc)
    except KeyboardInterrupt:  # pragma: no cover - user initiated cancel
        print("\n⏹️  Rebuild interrupted by user")
        sys.exit(0)
