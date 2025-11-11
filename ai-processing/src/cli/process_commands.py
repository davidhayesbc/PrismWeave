"""Process and sync commands for PrismWeave CLI."""

from __future__ import annotations

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
