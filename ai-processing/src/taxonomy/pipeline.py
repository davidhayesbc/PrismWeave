from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

from src.core.config import Config

from .articles import ArticleBuildOptions, load_articles_from_chroma
from .artifacts import default_artifacts_dir, write_json
from .chroma_clusters import ClusterStoreConfig, ClusterVectorStore
from .clustering import ClusteringOptions, cluster_articles


@dataclass(frozen=True)
class ClusterPipelineOptions:
    max_articles: Optional[int] = None
    algorithm: str = "kmeans"
    k: Optional[int] = None


def run_clustering_pipeline(
    config: Config,
    *,
    options: ClusterPipelineOptions,
    artifacts_dir: Optional[Path] = None,
) -> Dict[str, object]:
    documents_root = Path(config.mcp.paths.documents_root)
    artifacts_dir = artifacts_dir or default_artifacts_dir(documents_root)

    articles = load_articles_from_chroma(config, options=ArticleBuildOptions(max_articles=options.max_articles))
    clusters = cluster_articles(articles, options=ClusteringOptions(algorithm=options.algorithm, k=options.k))

    # Persist centroids in ChromaDB clusters collection
    vector_store = ClusterVectorStore(
        ClusterStoreConfig(
            persist_path=Path(config.chroma_db_path),
        )
    )
    vector_store.upsert_clusters(clusters)

    # Emit machine-readable artifacts
    write_json(
        artifacts_dir / "articles.json",
        [a.model_dump() for a in articles],
    )
    write_json(
        artifacts_dir / "clusters.json",
        [c.model_dump() for c in clusters],
    )

    return {
        "articles": len(articles),
        "clusters": len(clusters),
        "artifacts_dir": str(artifacts_dir),
        "clusters_collection": "clusters",
    }
