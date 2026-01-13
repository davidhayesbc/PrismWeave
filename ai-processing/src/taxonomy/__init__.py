"""Taxonomy, clustering, and tagging pipeline for PrismWeave.

This module builds a stable taxonomy (categories + tags) from existing article
embeddings stored in ChromaDB, then assigns tags to new and existing articles.

Design goals:
- Deterministic outputs for repeatable taxonomy evolution
- Stable identifiers derived from normalized names
- Machine-readable artifacts (JSON + SQLite)
"""

from .models import Article, ArticleTagAssignment, Cluster, Tag, TaxonomyCategory

__all__ = [
    "Article",
    "Cluster",
    "TaxonomyCategory",
    "Tag",
    "ArticleTagAssignment",
]
