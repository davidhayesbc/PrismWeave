from __future__ import annotations

import math
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass
class ArticleLayoutPoint:
    article_id: str
    x: float
    y: float


def compute_nearest_neighbors(layout_coords: Dict[str, Tuple[float, float]], k: int = 5) -> Dict[str, List[str]]:
    """Compute k-nearest neighbors for each article based on 2D layout coordinates.

    Args:
        layout_coords: Mapping of article_id to (x, y) coordinates
        k: Number of nearest neighbors to compute

    Returns:
        Mapping of article_id to list of neighbor article_ids
    """
    if not layout_coords or k <= 0:
        return {}

    neighbors: Dict[str, List[str]] = {}
    article_ids = list(layout_coords.keys())

    for article_id in article_ids:
        x1, y1 = layout_coords[article_id]

        # Calculate distances to all other articles
        distances: List[Tuple[str, float]] = []
        for other_id in article_ids:
            if other_id == article_id:
                continue
            x2, y2 = layout_coords[other_id]
            dx = x1 - x2
            dy = y1 - y2
            distance = math.sqrt(dx * dx + dy * dy)
            distances.append((other_id, distance))

        # Sort by distance and take k nearest
        distances.sort(key=lambda x: x[1])
        nearest = [neighbor_id for neighbor_id, _ in distances[:k]]
        neighbors[article_id] = nearest

    return neighbors


def _fallback_grid_layout(article_ids: Iterable[str]) -> Dict[str, Tuple[float, float]]:
    """Deterministic fallback layout when advanced projection is unavailable.

    Places points on a simple grid; this keeps the rest of the system
    functional even if UMAP or embeddings are unavailable during tests.
    """

    coords: Dict[str, Tuple[float, float]] = {}
    ids: List[str] = list(article_ids)
    if not ids:
        return coords

    cols = max(1, int(math.sqrt(len(ids))))
    spacing = 1.0
    for idx, article_id in enumerate(sorted(ids)):
        row = idx // cols
        col = idx % cols
        coords[article_id] = (col * spacing, row * spacing)
    return coords


def compute_fallback_layout(article_ids: Iterable[str]) -> Dict[str, Tuple[float, float]]:
    """Compute a deterministic 2D layout without requiring embeddings.

    This keeps visualization functional even when documents have not yet
    been embedded (e.g. fresh repo / cold-start). The layout is stable for
    a given set of IDs.
    """

    return _fallback_grid_layout(article_ids)


def compute_layout_from_embeddings(embeddings: Dict[str, List[float]]) -> Dict[str, Tuple[float, float]]:
    """Project high-dimensional embeddings into 2D coordinates.

    This function is structured to allow plugging in a more advanced
    projector (e.g. UMAP) later. For now it falls back to a simple grid
    layout when the number of points is small or no optional dependency
    is available.
    """

    if not embeddings:
        return {}

    # Lazy import so UMAP remains an optional dependency.
    try:  # pragma: no cover - exercised only when umap-learn is installed
        import umap  # type: ignore[import]

        ids = list(embeddings.keys())
        vectors = [embeddings[i] for i in ids]
        reducer = umap.UMAP(n_components=2, random_state=42)
        coords_array = reducer.fit_transform(vectors)
        return {doc_id: (float(x), float(y)) for doc_id, (x, y) in zip(ids, coords_array)}
    except ImportError:
        # UMAP not available, use grid fallback
        return _fallback_grid_layout(embeddings.keys())
    except (ValueError, RuntimeError) as e:
        # UMAP computation failed, use grid fallback
        import logging

        logging.getLogger(__name__).warning(f"UMAP layout failed, using grid fallback: {e}")
        return _fallback_grid_layout(embeddings.keys())


__all__ = [
    "ArticleLayoutPoint",
    "compute_fallback_layout",
    "compute_layout_from_embeddings",
    "compute_nearest_neighbors",
]
