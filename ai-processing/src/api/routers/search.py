"""Search router — semantic search over the document collection."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from src.api.deps import get_embedding_store

logger = logging.getLogger("prismweave.api.search")

router = APIRouter(prefix="/search", tags=["search"])


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------


class SearchRequest(BaseModel):
    """Semantic search query."""

    query: str = Field(..., min_length=1, description="Search query text")
    max_results: int = Field(10, ge=1, le=100, description="Maximum results to return")
    threshold: float = Field(0.0, ge=0.0, le=1.0, description="Minimum similarity threshold")
    filter_type: Optional[str] = Field(None, description="Filter by file extension (e.g. 'md', 'pdf')")


class SearchResultItem(BaseModel):
    """A single search result."""

    id: str = Field(..., description="Chunk ID")
    source_file: str = Field(..., description="Source file path")
    file_name: str = Field(..., description="Source file name")
    chunk_index: Optional[int] = Field(None, description="Chunk index within source file")
    total_chunks: Optional[int] = Field(None, description="Total chunks for the source file")
    score: Optional[float] = Field(None, description="Similarity score (0-1, higher is better)")
    tags: Optional[str] = Field(None, description="Comma-separated tags")
    content_preview: str = Field(..., description="Truncated content")


class SearchResponse(BaseModel):
    """Response for a semantic search."""

    query: str
    total_results: int
    results: List[SearchResultItem]


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post(
    "",
    response_model=SearchResponse,
    summary="Semantic Search",
    description="Search documents using semantic similarity via Ollama embeddings and ChromaDB",
    responses={
        200: {"description": "Search results returned successfully"},
        500: {"description": "Search backend unavailable"},
    },
)
async def search_documents(request: SearchRequest) -> SearchResponse:
    """
    Perform a semantic similarity search across all stored document chunks.

    The query is embedded using Ollama and compared against stored embeddings
    in ChromaDB. Results are ranked by cosine similarity.
    """
    try:
        store = get_embedding_store()
        results = store.search_similar(request.query, k=request.max_results)
    except Exception as exc:
        logger.error("Search failed: %s", exc)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Search failed: {exc}")

    items: List[SearchResultItem] = []
    for doc in results:
        meta = getattr(doc, "meta", {}) or {}
        score_val = getattr(doc, "score", None)

        # Apply threshold filter
        if request.threshold > 0.0 and score_val is not None:
            try:
                if float(score_val) < request.threshold:
                    continue
            except (TypeError, ValueError):
                pass

        # Apply file-type filter
        source_file = meta.get("source_file", "Unknown")
        if request.filter_type:
            suffix = f".{request.filter_type.lstrip('.')}"
            if Path(source_file).suffix != suffix:
                continue

        content = getattr(doc, "content", "") or ""
        items.append(
            SearchResultItem(
                id=getattr(doc, "id", "") or meta.get("chunk_id", ""),
                source_file=source_file,
                file_name=Path(source_file).name if source_file != "Unknown" else "Unknown",
                chunk_index=meta.get("chunk_index"),
                total_chunks=meta.get("total_chunks"),
                score=float(score_val) if score_val is not None else None,
                tags=meta.get("tags"),
                content_preview=content[:500],
            )
        )

    return SearchResponse(query=request.query, total_results=len(items), results=items)


@router.get(
    "",
    response_model=SearchResponse,
    summary="Semantic Search (GET)",
    description="GET variant of semantic search for simple queries",
)
async def search_documents_get(
    q: str = Query(..., min_length=1, description="Search query"),
    max_results: int = Query(10, ge=1, le=100),
    threshold: float = Query(0.0, ge=0.0, le=1.0),
    filter_type: Optional[str] = Query(None),
) -> SearchResponse:
    """GET convenience wrapper around the POST search endpoint."""
    return await search_documents(
        SearchRequest(query=q, max_results=max_results, threshold=threshold, filter_type=filter_type)
    )
