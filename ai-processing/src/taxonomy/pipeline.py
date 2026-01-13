from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

from src.core.config import Config

from .articles import ArticleBuildOptions, load_articles_from_chroma
from .chroma_clusters import ClusterStoreConfig, ClusterVectorStore
from .clustering import ClusteringOptions, cluster_articles
from .store import TaxonomyStore, TaxonomyStoreConfig, default_taxonomy_sqlite_path


@dataclass(frozen=True)
class ClusterPipelineOptions:
    max_articles: Optional[int] = None
    algorithm: str = "kmeans"
    k: Optional[int] = None


def run_clustering_pipeline(
    config: Config,
    *,
    options: ClusterPipelineOptions,
    sqlite_path: Optional[Path] = None,
) -> Dict[str, object]:
    documents_root = Path(config.mcp.paths.documents_root)

    articles = load_articles_from_chroma(config, options=ArticleBuildOptions(max_articles=options.max_articles))
    clusters = cluster_articles(articles, options=ClusteringOptions(algorithm=options.algorithm, k=options.k))

    # Persist centroids in ChromaDB clusters collection
    vector_store = ClusterVectorStore(
        ClusterStoreConfig(
            persist_path=Path(config.chroma_db_path),
        )
    )
    vector_store.upsert_clusters(clusters)

    # Persist pipeline artifacts into SQLite (source of truth).
    sqlite_path = sqlite_path or default_taxonomy_sqlite_path(documents_root)
    store = TaxonomyStore(TaxonomyStoreConfig(sqlite_path=sqlite_path))
    store.initialize()
    store.upsert_articles(articles)
    store.upsert_clusters(clusters)

    return {
        "articles": len(articles),
        "clusters": len(clusters),
        "sqlite": str(sqlite_path),
        "clusters_collection": "clusters",
    }
