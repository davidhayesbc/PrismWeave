from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from .models import Tag, TaxonomyCategory

_SLUG_RE = re.compile(r"[^a-z0-9]+")


def normalize_name(value: str) -> str:
    """Normalize a human-readable label into a stable slug.

    Rules (deterministic):
    - lowercase
    - trim
    - replace spaces/punctuation with hyphens
    - collapse repeats
    - strip leading/trailing hyphens
    """

    text = value.strip().lower()
    text = _SLUG_RE.sub("-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")


# Deterministic synonym mapping for common corpus terms.
# NOTE: Keep this list small and explicit to avoid churn.
_CANONICAL_SYNONYMS: Dict[str, str] = {
    "llm": "large-language-models",
    "large-language-model": "large-language-models",
    "large-language-models": "large-language-models",
    "foundation-model": "foundation-models",
    "foundation-models": "foundation-models",
    "k8s": "kubernetes",
    "kubernetes": "kubernetes",
    "ci-cd": "ci-cd",
    "cicd": "ci-cd",
}


def canonicalize_normalized_name(normalized: str) -> str:
    return _CANONICAL_SYNONYMS.get(normalized, normalized)


def make_category_id(name: str, parent_id: Optional[str] = None) -> str:
    slug = canonicalize_normalized_name(normalize_name(name))
    if parent_id:
        return f"cat:{parent_id.removeprefix('cat:')}/{slug}"
    return f"cat:{slug}"


def make_tag_id(normalized_name: str) -> str:
    canonical = canonicalize_normalized_name(normalized_name)
    return f"tag:{canonical}"


@dataclass(frozen=True)
class ProposedTaxonomy:
    category_name: str
    category_description: str
    subcategory_name: Optional[str]
    subcategory_description: Optional[str]
    tags: List[Tuple[str, str]]  # (name, description)


def dedupe_tags(raw_tags: Iterable[Tuple[str, str]], *, category_id: Optional[str] = None) -> List[Tag]:
    """Normalize + dedupe tags deterministically."""

    by_norm: Dict[str, Tuple[str, str]] = {}

    for name, description in raw_tags:
        normalized = canonicalize_normalized_name(normalize_name(name))
        if not normalized:
            continue
        if normalized not in by_norm:
            by_norm[normalized] = (name.strip(), (description or "").strip())

    result: List[Tag] = []
    for normalized in sorted(by_norm.keys()):
        name, description = by_norm[normalized]
        result.append(
            Tag(
                id=make_tag_id(normalized),
                name=name,
                normalized_name=normalized,
                description=description or name,
                category_id=category_id,
            )
        )
    return result


def build_category_hierarchy(
    proposals: Iterable[ProposedTaxonomy],
) -> Tuple[List[TaxonomyCategory], Dict[str, str]]:
    """Build a clean hierarchy from raw proposals.

    Returns:
      - categories: list of TaxonomyCategory
      - top_level_by_slug: mapping normalized_slug -> category_id

    Deterministic policy:
      - Top-level categories are merged by canonical normalized name.
      - Subcategories are stored under their parent category id.
    """

    top_levels: Dict[str, TaxonomyCategory] = {}

    # Pass 1: create/merge top-level categories
    for proposal in proposals:
        top_slug = canonicalize_normalized_name(normalize_name(proposal.category_name))
        if not top_slug:
            continue
        cat_id = make_category_id(proposal.category_name)
        if top_slug not in top_levels:
            top_levels[top_slug] = TaxonomyCategory(
                id=cat_id,
                name=proposal.category_name.strip(),
                description=(proposal.category_description or proposal.category_name).strip(),
                parent_id=None,
                level=0,
            )

    # Pass 2: subcategories
    subcats: Dict[str, TaxonomyCategory] = {}
    for proposal in proposals:
        if not proposal.subcategory_name:
            continue
        top_slug = canonicalize_normalized_name(normalize_name(proposal.category_name))
        parent = top_levels.get(top_slug)
        if not parent:
            continue
        sub_slug = canonicalize_normalized_name(normalize_name(proposal.subcategory_name))
        if not sub_slug:
            continue
        sub_id = make_category_id(proposal.subcategory_name, parent_id=parent.id)
        key = f"{parent.id}:{sub_slug}"
        if key in subcats:
            continue
        subcats[key] = TaxonomyCategory(
            id=sub_id,
            name=proposal.subcategory_name.strip(),
            description=(proposal.subcategory_description or proposal.subcategory_name).strip(),
            parent_id=parent.id,
            level=1,
        )

    categories = [top_levels[k] for k in sorted(top_levels.keys())] + [subcats[k] for k in sorted(subcats.keys())]
    return categories, {k: v.id for k, v in top_levels.items()}
