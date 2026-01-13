from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from src.core.config import Config

from .artifacts import default_artifacts_dir, read_json, write_json
from .llm_taxonomy import LlmProposalOptions, propose_taxonomy_for_cluster
from .models import Article, Cluster


@dataclass(frozen=True)
class ProposalRunOptions:
    sample_size: int = 10


def run_cluster_proposals(
    config: Config,
    *,
    artifacts_dir: Optional[Path] = None,
    options: ProposalRunOptions = ProposalRunOptions(),
) -> Dict[str, object]:
    documents_root = Path(config.mcp.paths.documents_root)
    artifacts_dir = artifacts_dir or default_artifacts_dir(documents_root)

    articles_payload = read_json(artifacts_dir / "articles.json")
    clusters_payload = read_json(artifacts_dir / "clusters.json")

    articles_by_id: Dict[str, Article] = {a["id"]: Article(**a) for a in articles_payload}
    clusters: List[Cluster] = [Cluster(**c) for c in clusters_payload]

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

    write_json(artifacts_dir / "cluster_proposals.json", proposals)

    return {"clusters": len(clusters), "proposals": len(proposals), "artifacts_dir": str(artifacts_dir)}
