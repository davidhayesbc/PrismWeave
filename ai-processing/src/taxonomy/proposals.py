from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from src.core.config import Config

from .llm_taxonomy import LlmProposalOptions, propose_taxonomy_for_cluster
from .models import Article
from .store import TaxonomyStore, TaxonomyStoreConfig, default_taxonomy_sqlite_path


@dataclass(frozen=True)
class ProposalRunOptions:
    sample_size: int = 10


def run_cluster_proposals(
    config: Config,
    *,
    options: ProposalRunOptions = ProposalRunOptions(),
    sqlite_path: Optional[Path] = None,
) -> Dict[str, object]:
    documents_root = Path(config.mcp.paths.documents_root)

    sqlite_path = sqlite_path or default_taxonomy_sqlite_path(documents_root)
    store = TaxonomyStore(TaxonomyStoreConfig(sqlite_path=sqlite_path))
    store.initialize()

    articles = store.list_articles()
    clusters = store.list_clusters()

    if not articles or not clusters:
        raise RuntimeError(
            "Missing required SQLite snapshots for proposals. "
            "Run taxonomy clustering to populate articles/clusters in taxonomy.sqlite. "
            f"sqlite={sqlite_path}"
        )

    articles_by_id: Dict[str, Article] = {a.id: a for a in articles}

    proposals: List[dict] = []
    for cluster in clusters:
        proposal = propose_taxonomy_for_cluster(
            config,
            cluster=cluster,
            articles_by_id=articles_by_id,
            options=LlmProposalOptions(sample_size=options.sample_size),
        )

        proposals.append(
            {
                "cluster_id": cluster.id,
                "category": {"name": proposal.category_name, "description": proposal.category_description},
                "subcategory": (
                    {
                        "name": proposal.subcategory_name,
                        "description": proposal.subcategory_description or proposal.subcategory_name,
                    }
                    if proposal.subcategory_name
                    else None
                ),
                "tags": [{"name": name, "description": desc} for name, desc in proposal.tags],
            }
        )

    store.upsert_cluster_proposals(proposals)

    return {
        "clusters": len(clusters),
        "proposals": len(proposals),
        "sqlite": str(sqlite_path),
    }
