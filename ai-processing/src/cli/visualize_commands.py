from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

import click

from src.cli_support import CliError, create_state
from src.core.embedding_store import EmbeddingStore
from src.core.layout import compute_layout_from_embeddings, compute_nearest_neighbors
from src.core.metadata_index import (
    INDEX_RELATIVE_PATH,
    build_metadata_index,
    load_existing_index,
    save_index,
)


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

    # (1) Rebuild metadata index from documents
    index = build_metadata_index(docs_root, target_index)
    state.write(f"✅ Indexed {len(index)} articles")

    # (2) Ensure article-level embeddings exist in Chroma and compute layout
    try:
        store = EmbeddingStore(state.config, state.git_tracker)
    except Exception as exc:  # pragma: no cover - environment specific
        state.write(f"⚠️  Skipping embedding/layout step (failed to init store): {exc}")
        return

    # Collect an article-level embedding by averaging chunk embeddings per source file.
    article_embeddings: Dict[str, List[float]] = {}
    for article in index.values():
        try:
            vector = store.get_article_embedding(Path(article.path))
            if vector is not None:
                article_embeddings[article.id] = list(vector)
        except Exception:
            continue

    if not article_embeddings:
        state.write("ℹ️  No embeddings found for articles; layout step skipped")
        return

    layout_coords = compute_layout_from_embeddings(article_embeddings)

    # (3) Compute k-nearest neighbors based on layout coordinates
    neighbors_map = compute_nearest_neighbors(layout_coords, k=5)

    # (4) Persist x,y and neighbors back into metadata index
    for article_id, (x, y) in layout_coords.items():
        article = index.get(article_id)
        if not article:
            continue
        # Attach coordinates to a lightweight view of metadata via dynamic attributes
        # API layer can choose how to expose these.
        article.x = float(x)
        article.y = float(y)
        article.neighbors = neighbors_map.get(article_id, [])

    save_index(index, target_index)
    state.write(f"🗺️  Updated layout for {len(layout_coords)} articles")
    state.write(f"🔗 Computed neighbors for {len(neighbors_map)} articles")


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
