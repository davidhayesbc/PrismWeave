from __future__ import annotations

from src.core.layout import compute_layout_from_embeddings


def test_compute_layout_from_embeddings_returns_coords_for_each_id() -> None:
    embeddings = {
        "a": [0.1, 0.2, 0.3],
        "b": [0.4, 0.5, 0.6],
        "c": [0.7, 0.8, 0.9],
    }

    coords = compute_layout_from_embeddings(embeddings)

    assert set(coords.keys()) == set(embeddings.keys())
    for x, y in coords.values():
        assert isinstance(x, float)
        assert isinstance(y, float)


def test_compute_layout_from_embeddings_handles_empty_input() -> None:
    coords = compute_layout_from_embeddings({})
    assert coords == {}
