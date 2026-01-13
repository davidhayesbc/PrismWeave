from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from src.core.config import Config

from .chroma_clusters import ClusterStoreConfig, ClusterVectorStore
from .models import ArticleTagAssignment, Tag
from .normalize import canonicalize_normalized_name, normalize_name
from .store import TaxonomyStore, TaxonomyStoreConfig, default_taxonomy_sqlite_path


@dataclass(frozen=True)
class AssignmentOptions:
    top_n: int = 8
    min_confidence: float = 0.15
    proposal_confidence: float = 0.75


def _distance_to_confidence(distance: float) -> float:
    # Chroma distances are non-negative. Map smaller distance -> higher confidence.
    return 1.0 / (1.0 + max(distance, 0.0))


def run_article_tag_assignment(
    config: Config,
    *,
    sqlite_path: Optional[Path] = None,
    options: AssignmentOptions = AssignmentOptions(),
) -> Dict[str, object]:
    documents_root = Path(config.mcp.paths.documents_root)

    sqlite_path = sqlite_path or default_taxonomy_sqlite_path(documents_root)
    store = TaxonomyStore(TaxonomyStoreConfig(sqlite_path=sqlite_path))
    store.initialize()

    articles = store.list_articles()
    clusters = store.list_clusters()
    proposals_payload = store.list_cluster_proposals()

    if not articles:
        raise RuntimeError(f"No articles found in taxonomy.sqlite. Run taxonomy clustering first. sqlite={sqlite_path}")

    if not clusters:
        raise RuntimeError(f"No clusters found in taxonomy.sqlite. Run taxonomy clustering first. sqlite={sqlite_path}")

    if not proposals_payload:
        raise RuntimeError(
            f"No cluster proposals found in taxonomy.sqlite. Run taxonomy propose first. sqlite={sqlite_path}"
        )

    tags_list = store.list_tags()
    if not tags_list:
        raise RuntimeError(f"No tags found in taxonomy.sqlite. Run taxonomy normalize first. sqlite={sqlite_path}")

    tags: Dict[str, Tag] = {t.id: t for t in tags_list}
    tag_id_by_normalized = {t.normalized_name: t.id for t in tags.values()}

    # cluster_id -> list of normalized tag names from the LLM proposal
    proposal_tags: Dict[str, List[str]] = {}
    for item in proposals_payload:
        cluster_id = str(item.get("cluster_id", ""))
        tags_payload = item.get("tags") or []
        normalized: List[str] = []
        for t in tags_payload:
            if not isinstance(t, dict):
                continue
            name = str(t.get("name", "")).strip()
            if not name:
                continue
            normalized.append(canonicalize_normalized_name(normalize_name(name)))
        proposal_tags[cluster_id] = sorted(set(n for n in normalized if n))

    article_to_cluster: Dict[str, str] = {}
    for cluster in clusters:
        for article_id in cluster.article_ids:
            article_to_cluster[article_id] = cluster.id

    vector_store = ClusterVectorStore(ClusterStoreConfig(persist_path=Path(config.chroma_db_path)))

    assignments: List[ArticleTagAssignment] = []

    for article in articles:
        cluster_id = article_to_cluster.get(article.id)

        # Start with proposal tags for its cluster.
        initial_norms = proposal_tags.get(cluster_id or "", []) if cluster_id else []
        by_tag_id: Dict[str, float] = {}
        for norm in initial_norms:
            tag_id = tag_id_by_normalized.get(norm)
            if tag_id:
                by_tag_id[tag_id] = max(by_tag_id.get(tag_id, 0.0), options.proposal_confidence)

        # Embedding-based refinement.
        try:
            results = vector_store.query_tag_embeddings(article.embedding, n_results=max(1, int(options.top_n)))
            ids = (results.get("ids") or [[]])[0]
            distances = (results.get("distances") or [[]])[0]
            for tag_id, dist in zip(ids, distances):
                conf = _distance_to_confidence(float(dist))
                if conf >= options.min_confidence:
                    by_tag_id[str(tag_id)] = max(by_tag_id.get(str(tag_id), 0.0), conf)
        except (KeyError, ValueError, TypeError, RuntimeError):
            # Tag embedding collection might not exist yet, or results may be missing.
            pass

        # Materialize
        for tag_id, confidence in sorted(by_tag_id.items(), key=lambda kv: (-kv[1], kv[0]))[
            : max(0, int(options.top_n))
        ]:
            assignments.append(ArticleTagAssignment(article_id=article.id, tag_id=tag_id, confidence=float(confidence)))

    store.upsert_article_tag_assignments(assignments)

    return {
        "articles": len(articles),
        "assignments": len(assignments),
        "sqlite": str(sqlite_path),
    }
