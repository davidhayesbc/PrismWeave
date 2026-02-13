"""Documents router — collection listing, count, stats, and export."""

from __future__ import annotations

import csv
import io
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from src.api.deps import get_config, get_embedding_store

logger = logging.getLogger("prismweave.api.documents")

router = APIRouter(prefix="/documents", tags=["documents"])


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------


class DocumentChunk(BaseModel):
    """A single document chunk from the embedding store."""

    id: str
    source_file: str
    file_name: str
    chunk_index: Optional[int] = None
    total_chunks: Optional[int] = None
    tags: Optional[str] = None
    content_length: int
    content_preview: str


class DocumentListResponse(BaseModel):
    """Paginated list of document chunks."""

    total_chunks: int
    total_source_files: int
    chunks: List[DocumentChunk]


class DocumentCountResponse(BaseModel):
    """Collection count summary."""

    total_chunks: int
    unique_source_files: int
    average_chunks_per_file: Optional[float] = None


class FileTypeDistribution(BaseModel):
    extension: str
    count: int
    percentage: float


class TagFrequency(BaseModel):
    tag: str
    frequency: int


class DocumentStatsResponse(BaseModel):
    """Collection statistics and analytics."""

    total_chunks: int
    unique_source_files: int
    average_chunks_per_file: Optional[float] = None
    total_content_length: Optional[int] = None
    average_chunk_size: Optional[float] = None
    collection_name: str
    storage_path: str
    file_type_distribution: List[FileTypeDistribution] = []
    top_tags: List[TagFrequency] = []


class ExportRequest(BaseModel):
    """Export configuration."""

    format: str = Field("json", pattern="^(json|csv)$", description="Export format: json or csv")
    filter_type: Optional[str] = Field(None, description="Filter by file extension")
    include_content: bool = Field(False, description="Include full content in JSON export")
    max_docs: Optional[int] = Field(None, ge=1, description="Maximum documents to export")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get(
    "",
    response_model=DocumentListResponse,
    summary="List Documents",
    description="List document chunks stored in ChromaDB",
)
async def list_documents(
    max_results: int = Query(50, ge=1, le=1000, description="Maximum chunks to return"),
) -> DocumentListResponse:
    """List document chunks with metadata."""
    try:
        store = get_embedding_store()
        documents = store.list_documents(max_results)
        source_files = store.get_unique_source_files()

        chunks = []
        for doc in documents:
            meta = doc["metadata"]
            source_file = meta.get("source_file", "Unknown")
            chunks.append(
                DocumentChunk(
                    id=doc["id"],
                    source_file=source_file,
                    file_name=Path(source_file).name if source_file != "Unknown" else "Unknown",
                    chunk_index=meta.get("chunk_index"),
                    total_chunks=meta.get("total_chunks"),
                    tags=meta.get("tags"),
                    content_length=doc["content_length"],
                    content_preview=doc["content_preview"],
                )
            )

        return DocumentListResponse(
            total_chunks=store.get_document_count(),
            total_source_files=len(source_files),
            chunks=chunks,
        )
    except Exception as exc:
        logger.error("Failed to list documents: %s", exc)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


@router.get(
    "/count",
    response_model=DocumentCountResponse,
    summary="Document Count",
    description="Get total document chunk and source file counts",
)
async def document_count() -> DocumentCountResponse:
    """Return total chunks and unique source file counts."""
    try:
        store = get_embedding_store()
        total_chunks = store.get_document_count()
        source_files = store.get_unique_source_files()
        unique = len(source_files)
        avg = total_chunks / unique if unique else None
        return DocumentCountResponse(
            total_chunks=total_chunks,
            unique_source_files=unique,
            average_chunks_per_file=avg,
        )
    except Exception as exc:
        logger.error("Failed to get document count: %s", exc)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


@router.get(
    "/stats",
    response_model=DocumentStatsResponse,
    summary="Collection Statistics",
    description="Get detailed collection statistics and analytics",
)
async def document_stats() -> DocumentStatsResponse:
    """Return detailed collection statistics including file type distribution and top tags."""
    try:
        store = get_embedding_store()
        cfg = get_config()
        total_chunks = store.get_document_count()
        source_files = store.get_unique_source_files()
        unique = len(source_files)
        avg_chunks = total_chunks / unique if unique else None

        verification = store.verify_embeddings()

        # Compute detailed stats
        documents = store.list_documents(None)
        total_content = 0
        file_types: Dict[str, int] = {}
        tag_frequency: Dict[str, int] = {}

        for doc in documents:
            meta = doc["metadata"]
            total_content += doc["content_length"]

            source_file = meta.get("source_file", "")
            if source_file:
                ext = Path(source_file).suffix or "no extension"
                file_types[ext] = file_types.get(ext, 0) + 1

            tags_str = meta.get("tags", "")
            for tag in (t.strip() for t in tags_str.split(",") if t.strip()):
                tag_frequency[tag] = tag_frequency.get(tag, 0) + 1

        file_type_dist = sorted(
            [
                FileTypeDistribution(
                    extension=ext,
                    count=cnt,
                    percentage=round(cnt / total_chunks * 100, 1) if total_chunks else 0,
                )
                for ext, cnt in file_types.items()
            ],
            key=lambda x: x.count,
            reverse=True,
        )

        top_tags = sorted(
            [TagFrequency(tag=t, frequency=f) for t, f in tag_frequency.items()],
            key=lambda x: x.frequency,
            reverse=True,
        )[:10]

        return DocumentStatsResponse(
            total_chunks=total_chunks,
            unique_source_files=unique,
            average_chunks_per_file=avg_chunks,
            total_content_length=total_content if total_content else None,
            average_chunk_size=round(total_content / total_chunks) if total_chunks else None,
            collection_name=verification.get("collection_name", cfg.collection_name),
            storage_path=verification.get("persist_directory", cfg.chroma_db_path),
            file_type_distribution=file_type_dist,
            top_tags=top_tags,
        )
    except Exception as exc:
        logger.error("Failed to get stats: %s", exc)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


@router.post(
    "/export",
    summary="Export Documents",
    description="Export document metadata and content as JSON or CSV download",
    responses={
        200: {
            "description": "File download",
            "content": {
                "application/json": {},
                "text/csv": {},
            },
        },
    },
)
async def export_documents(request: ExportRequest) -> StreamingResponse:
    """Export documents as a downloadable JSON or CSV file."""
    try:
        store = get_embedding_store()
        cfg = get_config()
        documents = store.list_documents(request.max_docs)

        if not documents:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No documents to export")

        # Apply file-type filter
        if request.filter_type:
            suffix = f".{request.filter_type.lstrip('.')}"
            documents = [d for d in documents if Path(d["metadata"].get("source_file", "")).suffix == suffix]
            if not documents:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No documents with file type '{request.filter_type}'",
                )

        if request.format == "json":
            import json

            export_data: Dict[str, Any] = {
                "export_date": datetime.now().isoformat(),
                "total_documents": len(documents),
                "collection_name": cfg.collection_name,
                "documents": [],
            }
            for doc in documents:
                meta = doc["metadata"]
                payload: Dict[str, Any] = {
                    "id": doc["id"],
                    "source_file": meta.get("source_file", "Unknown"),
                    "chunk_index": meta.get("chunk_index"),
                    "total_chunks": meta.get("total_chunks"),
                    "tags": meta.get("tags", ""),
                    "content_length": doc["content_length"],
                    "content_preview": doc["content_preview"],
                }
                export_data["documents"].append(payload)

            content = json.dumps(export_data, indent=2, ensure_ascii=False)
            return StreamingResponse(
                iter([content]),
                media_type="application/json",
                headers={"Content-Disposition": "attachment; filename=prismweave-export.json"},
            )

        # CSV
        output = io.StringIO()
        fieldnames = ["id", "source_file", "chunk_index", "total_chunks", "tags", "content_length", "content_preview"]
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        for doc in documents:
            meta = doc["metadata"]
            writer.writerow(
                {
                    "id": doc["id"],
                    "source_file": meta.get("source_file", ""),
                    "chunk_index": meta.get("chunk_index", ""),
                    "total_chunks": meta.get("total_chunks", ""),
                    "tags": meta.get("tags", ""),
                    "content_length": doc["content_length"],
                    "content_preview": doc["content_preview"],
                }
            )

        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=prismweave-export.csv"},
        )

    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Export failed: %s", exc)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))
