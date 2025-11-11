"""Utilities for processing documents and directories."""

from __future__ import annotations

import time
import traceback
from pathlib import Path
from typing import List

from src.cli_support import CliError, CliState, SUPPORTED_EXTENSIONS
from src.core.document_processor import DocumentProcessor
from src.core.embedding_store import EmbeddingStore
from .document_utils import get_document_metadata


def should_skip_file(file_path: Path, state: CliState, *, force: bool) -> bool:
    """Check if file should be skipped during processing."""
    if force or not state.git_tracker:
        return False
    processed = state.git_tracker.is_file_processed(file_path)
    if processed:
        state.write_verbose(f"⏭️  Skipping {file_path.name} (already processed and unchanged)")
    return processed


def process_single_file(
    file_path: Path,
    state: CliState,
    processor: DocumentProcessor,
    store: EmbeddingStore,
    *,
    force: bool = False,
) -> bool:
    """Process a single document file."""
    if should_skip_file(file_path, state, force=force):
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
                metadata = get_document_metadata(chunk)
                state.write_verbose(f"  Chunk {index}:")
                state.write_verbose(f"    Content preview: {chunk.content[:100]}...")
                state.write_verbose(f"    Metadata keys: {list(metadata.keys())}")
                if "tags" in metadata:
                    state.write_verbose(f"    Tags: {metadata['tags']}")
                state.write_verbose("")
        else:
            state.write(f"✅ Processed {file_path.name} ({len(chunks)} chunks)")

        return True

    except (OSError, ValueError, RuntimeError) as exc:  # pragma: no cover - relies on environment interaction
        state.write(f"❌ Error processing {file_path.name}: {exc}")
        if state.verbose:
            traceback.print_exc()
        return False


def collect_directory_files(
    directory: Path,
    state: CliState,
    *,
    incremental: bool,
    force: bool,
) -> List[Path]:
    """Collect files to process from a directory."""
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


def summarize_processing(
    state: CliState,
    *,
    success_count: int,
    error_count: int,
    elapsed: float,
) -> None:
    """Display processing summary."""
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


def process_directory(
    directory: Path,
    state: CliState,
    processor: DocumentProcessor,
    store: EmbeddingStore,
    *,
    incremental: bool,
    force: bool,
) -> bool:
    """Process all supported files in a directory."""
    files = collect_directory_files(directory, state, incremental=incremental, force=force)

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
        with progress as progress_bar:
            task = progress_bar.add_task("[cyan]Processing documents...", total=len(files))
            for file_path in files:
                progress_bar.update(task, description=f"[cyan]Processing: {file_path.name}")
                try:
                    if process_single_file(
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
                    progress_bar.update(task, advance=1)
    else:
        for index, file_path in enumerate(files, start=1):
            state.write(f"[{index}/{len(files)}] Processing: {file_path.name}")
            try:
                if process_single_file(
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
    summarize_processing(
        state,
        success_count=success_count,
        error_count=error_count,
        elapsed=elapsed,
    )

    if success_count and state.git_tracker:
        try:
            state.git_tracker.update_last_processed_commit()
            state.write_verbose("   🔄 Updated processing state")
        except (OSError, RuntimeError) as exc:  # pragma: no cover - external git state
            state.write(f"   ⚠️  Warning: Failed to update processing state: {exc}")

    return success_count > 0


def clear_embeddings(state: CliState, store: EmbeddingStore) -> None:
    """Clear all embeddings from the store."""
    state.write("🗑️  Clearing existing embeddings...")
    store.clear_collection()

    if state.git_tracker:
        state.git_tracker.reset_processing_state()
        state.write("🔄 Reset processing state")

    state.write("✅ Embeddings cleared")
    state.write()
