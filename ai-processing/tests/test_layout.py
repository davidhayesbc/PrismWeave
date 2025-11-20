from __future__ import annotations

from src.core.layout import compute_layout_from_embeddings, compute_nearest_neighbors


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


def test_compute_nearest_neighbors_returns_k_neighbors_for_each_article() -> None:
    layout_coords = {
        "a": (0.0, 0.0),
        "b": (1.0, 0.0),
        "c": (0.0, 1.0),
        "d": (10.0, 10.0),
    }

    neighbors = compute_nearest_neighbors(layout_coords, k=2)

    assert set(neighbors.keys()) == set(layout_coords.keys())
    for neighbor_list in neighbors.values():
        assert len(neighbor_list) == 2
        assert all(isinstance(n, str) for n in neighbor_list)


def test_compute_nearest_neighbors_orders_by_distance() -> None:
    layout_coords = {
        "a": (0.0, 0.0),
        "b": (1.0, 0.0),  # Distance 1 from a
        "c": (2.0, 0.0),  # Distance 2 from a
        "d": (3.0, 0.0),  # Distance 3 from a
    }

    neighbors = compute_nearest_neighbors(layout_coords, k=3)

    # For article 'a', nearest neighbors should be b, c, d in that order
    assert neighbors["a"] == ["b", "c", "d"]


def test_compute_nearest_neighbors_handles_k_larger_than_available() -> None:
    layout_coords = {
        "a": (0.0, 0.0),
        "b": (1.0, 0.0),
    }

    neighbors = compute_nearest_neighbors(layout_coords, k=10)

    # Each article has only 1 other article available
    assert len(neighbors["a"]) == 1
    assert len(neighbors["b"]) == 1


def test_compute_nearest_neighbors_handles_empty_input() -> None:
    neighbors = compute_nearest_neighbors({}, k=5)
    assert neighbors == {}


def test_compute_nearest_neighbors_handles_zero_k() -> None:
    layout_coords = {
        "a": (0.0, 0.0),
        "b": (1.0, 0.0),
    }

    neighbors = compute_nearest_neighbors(layout_coords, k=0)
    assert neighbors == {}
