from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Article(BaseModel):
    """Logical article unit for taxonomy.

    Note: PrismWeave stores embeddings at chunk-level in ChromaDB. The taxonomy
    pipeline constructs article-level embeddings by averaging chunk embeddings
    for a given source file.
    """

    id: str
    title: str
    url: Optional[str] = None
    content: str
    summary: Optional[str] = None
    embedding: List[float]


class Cluster(BaseModel):
    id: str
    article_ids: List[str]
    centroid_embedding: List[float]
    category_id: Optional[str] = None
    subcategory_id: Optional[str] = None

    metadata: Dict[str, Any] = Field(default_factory=dict)


class TaxonomyCategory(BaseModel):
    id: str
    name: str
    description: str
    parent_id: Optional[str] = None
    level: int = 0


class Tag(BaseModel):
    id: str
    name: str
    normalized_name: str
    description: str
    category_id: Optional[str] = None


class ArticleTagAssignment(BaseModel):
    article_id: str
    tag_id: str
    confidence: float
