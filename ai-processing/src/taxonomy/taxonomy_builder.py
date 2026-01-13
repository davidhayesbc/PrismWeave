from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from src.core.config import Config

from .artifacts import default_artifacts_dir, read_json, write_json
from .models import Tag, TaxonomyCategory
from .normalize import (
    ProposedTaxonomy,
    build_category_hierarchy,
    canonicalize_normalized_name,
    dedupe_tags,
    normalize_name,
)
from .store import TaxonomyStore, TaxonomyStoreConfig, default_taxonomy_sqlite_path


@dataclass(frozen=True)
class TaxonomyBuildResult:
    categories: List[TaxonomyCategory]
    tags: List[Tag]
    cluster_category_map: Dict[str, Tuple[Optional[str], Optional[str]]]


def build_taxonomy_from_proposals(proposals_payload: List[dict]) -> TaxonomyBuildResult:
    proposals: List[ProposedTaxonomy] = []
    proposal_by_cluster: Dict[str, ProposedTaxonomy] = {}

    for item in proposals_payload:
        cluster_id = str(item.get("cluster_id", ""))
        category = item.get("category") or {}
        subcategory = item.get("subcategory")
        tags = item.get("tags") or []

        category_name = str(category.get("name", "")).strip()
        category_desc = str(category.get("description", "")).strip() or category_name

        sub_name: Optional[str] = None
        sub_desc: Optional[str] = None
        if isinstance(subcategory, dict):
            sub_name = str(subcategory.get("name", "")).strip() or None
            sub_desc = str(subcategory.get("description", "")).strip() or sub_name

        tag_pairs: List[tuple[str, str]] = []
        for t in tags:
            if not isinstance(t, dict):
                continue
            name = str(t.get("name", "")).strip()
            desc = str(t.get("description", "")).strip()
            if name:
                tag_pairs.append((name, desc))

        if not category_name:
            continue

        proposal = ProposedTaxonomy(
            category_name=category_name,
            category_description=category_desc,
            subcategory_name=sub_name,
            subcategory_description=sub_desc,
            tags=tag_pairs,
        )
        proposals.append(proposal)
        if cluster_id:
            proposal_by_cluster[cluster_id] = proposal

    categories, top_level_by_slug = build_category_hierarchy(proposals)

    # Build global tag set (dedupe by normalized_name across all clusters)
    global_by_norm: Dict[str, Tag] = {}

    for proposal in proposals:
        top_slug = canonicalize_normalized_name(normalize_name(proposal.category_name))
        category_id = top_level_by_slug.get(top_slug)
        for tag in dedupe_tags(proposal.tags, category_id=category_id):
            # Keep first (deterministic due to sorted) but allow later to fill missing description.
            existing = global_by_norm.get(tag.normalized_name)
            if (
                existing is None
                or existing.description == existing.name
                and tag.description
                and tag.description != tag.name
            ):
                global_by_norm[tag.normalized_name] = tag

    tags = [global_by_norm[norm] for norm in sorted(global_by_norm.keys())]

    # Build cluster → (category_id, subcategory_id)
    cluster_map: Dict[str, Tuple[Optional[str], Optional[str]]] = {}
    category_by_id = {c.id: c for c in categories}

    for cluster_id, proposal in proposal_by_cluster.items():
        top_slug = canonicalize_normalized_name(normalize_name(proposal.category_name))
        category_id = top_level_by_slug.get(top_slug)
        subcategory_id: Optional[str] = None

        if proposal.subcategory_name and category_id:
            sub_slug = canonicalize_normalized_name(normalize_name(proposal.subcategory_name))
            candidate_id = f"cat:{category_id.removeprefix('cat:')}/{sub_slug}"
            if candidate_id in category_by_id:
                subcategory_id = candidate_id

        cluster_map[cluster_id] = (category_id, subcategory_id)

    return TaxonomyBuildResult(categories=categories, tags=tags, cluster_category_map=cluster_map)


def run_taxonomy_normalize_and_store(
    config: Config,
    *,
    artifacts_dir: Optional[Path] = None,
    sqlite_path: Optional[Path] = None,
) -> Dict[str, object]:
    documents_root = Path(config.mcp.paths.documents_root)
    artifacts_dir = artifacts_dir or default_artifacts_dir(documents_root)

    proposals_payload = read_json(artifacts_dir / "cluster_proposals.json")
    result = build_taxonomy_from_proposals(proposals_payload)

    sqlite_path = sqlite_path or default_taxonomy_sqlite_path(documents_root)
    store = TaxonomyStore(TaxonomyStoreConfig(sqlite_path=sqlite_path))
    store.initialize()
    store.upsert_categories(result.categories)
    store.upsert_tags(result.tags)

    for cluster_id, (category_id, subcategory_id) in sorted(result.cluster_category_map.items()):
        store.map_cluster_to_category(cluster_id, category_id, subcategory_id)

    write_json(
        artifacts_dir / "taxonomy.json",
        {
            "categories": [c.model_dump() for c in result.categories],
            "tags": [t.model_dump() for t in result.tags],
            "cluster_category_map": {
                cluster_id: {"category_id": cat, "subcategory_id": sub}
                for cluster_id, (cat, sub) in sorted(result.cluster_category_map.items())
            },
        },
    )

    return {
        "categories": len(result.categories),
        "tags": len(result.tags),
        "sqlite": str(sqlite_path),
        "artifacts_dir": str(artifacts_dir),
    }
