from __future__ import annotations

from pathlib import Path
from typing import Optional

import click

from src.cli_support import CliError, create_state
from src.core.metadata_index import INDEX_RELATIVE_PATH, build_metadata_index, load_existing_index


@click.group()
def visualize() -> None:
    """Visualization-related utilities (metadata index, layout, etc.)."""


@visualize.command(name="build-index")
@click.option(
    "--documents-root",
    "documents_root",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    help="Root directory containing markdown documents (default: config.mcp.paths.documents_root)",
)
@click.option(
    "--index-path",
    type=click.Path(path_type=Path),
    help="Override path for the generated index file (JSON)",
)
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, path_type=Path),
    help="Configuration file path (default: config.yaml)",
)
@click.option("--verbose", "-v", is_flag=True, help="Show detailed output")
def build_index(
    documents_root: Optional[Path],
    index_path: Optional[Path],
    config: Optional[Path],
    verbose: bool,
) -> None:
    """Rebuild the article metadata index from markdown documents."""

    state = create_state(config, verbose)

    docs_root = documents_root or Path(state.config.mcp.paths.documents_root).expanduser().resolve()
    if not docs_root.exists():
        raise CliError(f"Documents root not found: {docs_root}")

    target_index = index_path or (docs_root / INDEX_RELATIVE_PATH)
    state.write(f"📁 Documents root: {docs_root}")
    state.write(f"🗂️  Index path: {target_index}")

    index = build_metadata_index(docs_root, target_index)
    state.write(f"✅ Indexed {len(index)} articles")


@visualize.command(name="print-index")
@click.option(
    "--documents-root",
    "documents_root",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    help="Root directory containing markdown documents (default: config.mcp.paths.documents_root)",
)
@click.option(
    "--index-path",
    type=click.Path(path_type=Path),
    help="Override path for the index file (JSON)",
)
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, path_type=Path),
    help="Configuration file path (default: config.yaml)",
)
@click.option("--verbose", "-v", is_flag=True, help="Show detailed output")
def print_index(
    documents_root: Optional[Path],
    index_path: Optional[Path],
    config: Optional[Path],
    verbose: bool,
) -> None:
    """Print a human-readable summary of the metadata index."""

    state = create_state(config, verbose)

    docs_root = documents_root or Path(state.config.mcp.paths.documents_root).expanduser().resolve()
    target_index = index_path or (docs_root / INDEX_RELATIVE_PATH)

    index = load_existing_index(target_index)
    if not index:
        state.write("(no index entries found)")
        return

    state.write(f"Found {len(index)} articles in index:")
    for article in index.values():
        state.write(f"- {article.id} :: {article.title} [{', '.join(article.tags)}]")


__all__ = ["visualize"]
