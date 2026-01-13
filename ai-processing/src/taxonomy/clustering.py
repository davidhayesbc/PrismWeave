from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional

from .ids import stable_cluster_id
from .models import Article, Cluster
from .similarity import cosine_similarity, mean_vector


@dataclass(frozen=True)
class ClusteringOptions:
    algorithm: str = "kmeans"  # "hdbscan" (if available) or "kmeans"
    k: Optional[int] = None
    max_iterations: int = 30


def _choose_k(n: int) -> int:
    if n <= 0:
        return 0
    return max(2, int(round(math.sqrt(n / 2.0))))


def _cosine_distance(a: List[float], b: List[float]) -> float:
    return 1.0 - cosine_similarity(a, b)


def _init_centroids_greedy(vectors: List[List[float]], k: int) -> List[List[float]]:
    """Deterministic centroid initialization.

    Policy:
      - start at vector[0]
      - repeatedly pick the point farthest from its nearest centroid
    """

    if not vectors or k <= 0:
        return []

    centroids = [vectors[0]]

    while len(centroids) < min(k, len(vectors)):
        best_idx = 0
        best_dist = -1.0
        for idx, vec in enumerate(vectors):
            nearest = min(_cosine_distance(vec, c) for c in centroids)
            if nearest > best_dist:
                best_dist = nearest
                best_idx = idx
        centroids.append(vectors[best_idx])

    return [c[:] for c in centroids]


def _assign(vectors: List[List[float]], centroids: List[List[float]]) -> List[int]:
    labels: List[int] = []
    for vec in vectors:
        best_i = 0
        best_d = float("inf")
        for i, c in enumerate(centroids):
            d = _cosine_distance(vec, c)
            if d < best_d:
                best_d = d
                best_i = i
        labels.append(best_i)
    return labels


def _recompute_centroids(vectors: List[List[float]], labels: List[int], k: int) -> List[List[float]]:
    buckets: List[List[List[float]]] = [[] for _ in range(k)]
    for vec, label in zip(vectors, labels):
        if 0 <= label < k:
            buckets[label].append(vec)

    new_centroids: List[List[float]] = []
    for bucket in buckets:
        if not bucket:
            # Keep an empty centroid placeholder; caller may reinitialize.
            new_centroids.append([])
        else:
            new_centroids.append(mean_vector(bucket))
    return new_centroids


def kmeans_cluster(articles: List[Article], *, options: ClusteringOptions) -> List[Cluster]:
    if not articles:
        return []

    vectors = [a.embedding for a in articles]
    article_ids = [a.id for a in articles]
    embedding_by_id: Dict[str, List[float]] = {a.id: a.embedding for a in articles}

    k = options.k or _choose_k(len(articles))
    k = min(k, len(articles))
    if k <= 1:
        return []

    centroids = _init_centroids_greedy(vectors, k)
    labels: List[int] = [-1] * len(vectors)

    for _ in range(max(1, int(options.max_iterations))):
        new_labels = _assign(vectors, centroids)
        if new_labels == labels:
            break
        labels = new_labels

        new_centroids = _recompute_centroids(vectors, labels, k)

        # Reinitialize any empty centroid deterministically (pick farthest point).
        for i, c in enumerate(new_centroids):
            if c:
                continue
            best_idx = 0
            best_dist = -1.0
            for idx, vec in enumerate(vectors):
                nearest = min(_cosine_distance(vec, cc) for cc in new_centroids if cc)
                if nearest > best_dist:
                    best_dist = nearest
                    best_idx = idx
            new_centroids[i] = vectors[best_idx]

        centroids = new_centroids

    # Build clusters
    clusters_by_label: Dict[int, List[str]] = {}
    for article_id, label in zip(article_ids, labels):
        clusters_by_label.setdefault(label, []).append(article_id)

    clusters: List[Cluster] = []
    for label in sorted(clusters_by_label.keys()):
        members = sorted(clusters_by_label[label])
        member_vectors = [embedding_by_id[article_id] for article_id in members if article_id in embedding_by_id]
        centroid = mean_vector(member_vectors)

        cluster_id = stable_cluster_id(members, algorithm=options.algorithm)
        clusters.append(
            Cluster(
                id=cluster_id,
                article_ids=members,
                centroid_embedding=centroid,
                metadata={"algorithm": options.algorithm, "k": k, "label": label, "size": len(members)},
            )
        )

    return clusters


def cluster_articles(articles: List[Article], *, options: ClusteringOptions) -> List[Cluster]:
    """Cluster articles.

    Preferred: HDBSCAN (when available + numeric deps installed)
    Fallback: deterministic cosine K-means (pure python)
    """

    algo = (options.algorithm or "kmeans").lower()
    if algo == "hdbscan":
        # Optional path: only when deps are present.
        try:
            import hdbscan  # type: ignore
            import numpy as np  # type: ignore

            vectors = np.array([a.embedding for a in articles], dtype=float)
            clusterer = hdbscan.HDBSCAN(
                min_cluster_size=10,
                min_samples=5,
                metric="euclidean",
            )
            labels = clusterer.fit_predict(vectors)

            clusters_by_label: Dict[int, List[str]] = {}
            for article, label in zip(articles, labels):
                if int(label) == -1:
                    continue
                clusters_by_label.setdefault(int(label), []).append(article.id)

            clusters: List[Cluster] = []
            for label in sorted(clusters_by_label.keys()):
                members = sorted(clusters_by_label[label])
                member_vectors = [a.embedding for a in articles if a.id in set(members)]
                centroid = mean_vector(member_vectors)
                cluster_id = stable_cluster_id(members, algorithm="hdbscan")
                clusters.append(
                    Cluster(
                        id=cluster_id,
                        article_ids=members,
                        centroid_embedding=centroid,
                        metadata={"algorithm": "hdbscan", "label": label, "size": len(members)},
                    )
                )
            return clusters
        except Exception:
            # Fall back to k-means if anything isn't available.
            pass

    return kmeans_cluster(articles, options=ClusteringOptions(**{**options.__dict__, "algorithm": "kmeans"}))
