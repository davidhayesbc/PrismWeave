"""Taxonomy router — clustering, proposals, normalization, and tag assignment."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from src.api.deps import check_ollama_available, get_config

logger = logging.getLogger("prismweave.api.taxonomy")

router = APIRouter(prefix="/taxonomy", tags=["taxonomy"])


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------


class ClusterRequest(BaseModel):
    algorithm: str = Field("kmeans", pattern="^(kmeans|hdbscan)$", description="Clustering algorithm")
    k: Optional[int] = Field(None, ge=2, description="K for KMeans (default: sqrt(n/2))")
    max_articles: Optional[int] = Field(None, ge=1, description="Limit articles for clustering")


class ProposeRequest(BaseModel):
    sample_size: int = Field(10, ge=1, le=100, description="Representative samples per cluster")


class AssignRequest(BaseModel):
    top_n: int = Field(8, ge=1, le=50, description="Max tags per article")
    min_confidence: float = Field(0.15, ge=0.0, le=1.0, description="Minimum confidence for tag assignment")


class TagNewRequest(BaseModel):
    path: str = Field(..., description="Path to the article file to tag")
    top_n: int = Field(8, ge=1, le=50, description="Max tags")
    min_confidence: float = Field(0.15, ge=0.0, le=1.0)
    max_cluster_distance: float = Field(1.5, ge=0.0)
    llm_refine: bool = Field(False, description="Use LLM to refine tags")


class EmbedTagsRequest(BaseModel):
    use_description: bool = Field(True, description="Embed tag descriptions (vs. names only)")


class TaxonomyOperationResponse(BaseModel):
    status: str
    message: str
    details: Dict = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post(
    "/cluster",
    response_model=TaxonomyOperationResponse,
    summary="Build Clusters",
    description="Build clusters from existing article embeddings and store centroid vectors",
)
async def cluster(request: ClusterRequest) -> TaxonomyOperationResponse:
    """Build clusters from article embeddings in ChromaDB."""
    try:
        from src.taxonomy.pipeline import ClusterPipelineOptions, run_clustering_pipeline

        cfg = get_config()
        result = run_clustering_pipeline(
            cfg,
            options=ClusterPipelineOptions(
                max_articles=request.max_articles,
                algorithm=request.algorithm,
                k=request.k,
            ),
        )
        return TaxonomyOperationResponse(
            status="success",
            message=f"Clustered {result['articles']} articles into {result['clusters']} clusters",
            details=result,
        )
    except Exception as exc:
        logger.error("Clustering failed: %s", exc)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Clustering failed: {exc}")


@router.post(
    "/propose",
    response_model=TaxonomyOperationResponse,
    summary="Generate Proposals",
    description="Use local LLM to propose category/subcategory/tags for each cluster",
)
async def propose(request: ProposeRequest) -> TaxonomyOperationResponse:
    """Generate LLM-based taxonomy proposals for each cluster."""
    ollama_status = check_ollama_available()
    if not ollama_status["available"]:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Ollama not available: {ollama_status.get('error', 'unknown')}",
        )

    try:
        from src.taxonomy.proposals import ProposalRunOptions, run_cluster_proposals

        cfg = get_config()
        result = run_cluster_proposals(cfg, options=ProposalRunOptions(sample_size=request.sample_size))
        return TaxonomyOperationResponse(
            status="success",
            message=f"Generated {result['proposals']} proposals",
            details=result,
        )
    except Exception as exc:
        logger.error("Proposal generation failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Proposal generation failed: {exc}"
        )


@router.post(
    "/normalize",
    response_model=TaxonomyOperationResponse,
    summary="Normalize Taxonomy",
    description="Normalize/dedupe cluster proposals into a stable taxonomy and persist to SQLite",
)
async def normalize() -> TaxonomyOperationResponse:
    """Normalize cluster proposals into a stable taxonomy."""
    try:
        from src.taxonomy.taxonomy_builder import run_taxonomy_normalize_and_store

        cfg = get_config()
        result = run_taxonomy_normalize_and_store(cfg)
        return TaxonomyOperationResponse(
            status="success",
            message=f"Stored taxonomy: {result['categories']} categories, {result['tags']} tags",
            details=result,
        )
    except Exception as exc:
        logger.error("Taxonomy normalization failed: %s", exc)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Normalization failed: {exc}")


@router.post(
    "/embed-tags",
    response_model=TaxonomyOperationResponse,
    summary="Embed Tags",
    description="Embed tag descriptions and store them in ChromaDB for fast tag assignment",
)
async def embed_tags(request: EmbedTagsRequest) -> TaxonomyOperationResponse:
    """Embed tag descriptions and store them in ChromaDB."""
    ollama_status = check_ollama_available()
    if not ollama_status["available"]:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Ollama not available: {ollama_status.get('error', 'unknown')}",
        )

    try:
        from src.taxonomy.tag_embeddings import TagEmbeddingOptions, embed_and_store_tags

        cfg = get_config()
        result = embed_and_store_tags(cfg, options=TagEmbeddingOptions(use_description=request.use_description))
        return TaxonomyOperationResponse(
            status="success",
            message=f"Embedded {result['tags']} tags",
            details=result,
        )
    except Exception as exc:
        logger.error("Tag embedding failed: %s", exc)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Tag embedding failed: {exc}")


@router.post(
    "/assign",
    response_model=TaxonomyOperationResponse,
    summary="Assign Tags",
    description="Assign tags to articles using proposal + embedding-based refinement",
)
async def assign(request: AssignRequest) -> TaxonomyOperationResponse:
    """Assign tags to articles and persist to SQLite."""
    try:
        from src.taxonomy.assignments import AssignmentOptions, run_article_tag_assignment

        cfg = get_config()
        opts = AssignmentOptions(top_n=request.top_n, min_confidence=request.min_confidence)
        result = run_article_tag_assignment(cfg, options=opts)
        return TaxonomyOperationResponse(
            status="success",
            message=f"Wrote {result['assignments']} tag assignments for {result['articles']} articles",
            details=result,
        )
    except Exception as exc:
        logger.error("Tag assignment failed: %s", exc)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Tag assignment failed: {exc}")


@router.post(
    "/tag-new",
    response_model=TaxonomyOperationResponse,
    summary="Tag New Article",
    description="Tag a new article file using existing cluster centroids and global tags",
)
async def tag_new(request: TagNewRequest) -> TaxonomyOperationResponse:
    """Tag a new article using existing cluster centroids and global tags."""
    ollama_status = check_ollama_available()
    if not ollama_status["available"]:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Ollama not available: {ollama_status.get('error', 'unknown')}",
        )

    file_path = Path(request.path).expanduser().resolve()
    if not file_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"File not found: {file_path}")

    try:
        from src.taxonomy.new_article import NewArticleTaggingOptions, tag_new_article

        cfg = get_config()
        result = tag_new_article(
            cfg,
            article_path=file_path,
            options=NewArticleTaggingOptions(
                top_n=request.top_n,
                min_confidence=request.min_confidence,
                max_cluster_distance=request.max_cluster_distance,
                llm_refine=request.llm_refine,
            ),
        )
        tags_value = result.get("tags")
        tags_list: List = tags_value if isinstance(tags_value, list) else []
        return TaxonomyOperationResponse(
            status="success",
            message=f"Tagged {result.get('article_id', file_path.name)}: {len(tags_list)} tags",
            details=result,
        )
    except Exception as exc:
        logger.error("Tag-new failed: %s", exc)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Tag-new failed: {exc}")
