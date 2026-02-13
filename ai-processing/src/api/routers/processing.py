"""Processing router — document processing and embedding generation."""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from src.api.deps import get_config, get_document_processor, get_embedding_store
from src.cli_support import SUPPORTED_EXTENSIONS

logger = logging.getLogger("prismweave.api.processing")

router = APIRouter(prefix="/processing", tags=["processing"])


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class ProcessFileRequest(BaseModel):
    """Request to process a single file."""

    path: str = Field(..., description="Absolute or documents-root-relative path to the file")
    force: bool = Field(False, description="Force reprocessing even if already processed")
    verify: bool = Field(False, description="Verify embeddings after processing")


class ProcessDirectoryRequest(BaseModel):
    """Request to process all supported files in a directory."""

    path: Optional[str] = Field(
        None,
        description="Directory path (defaults to documents_root from config)",
    )
    force: bool = Field(False, description="Force reprocessing of all files")
    incremental: bool = Field(False, description="Only process new or changed files")


class ProcessFileResult(BaseModel):
    file_name: str
    chunks: int
    status: str  # "success" | "skipped" | "error"
    error: Optional[str] = None


class ProcessingResponse(BaseModel):
    """Response for processing operations."""

    status: str
    message: str
    files_processed: int = 0
    files_skipped: int = 0
    files_errored: int = 0
    elapsed_seconds: Optional[float] = None
    results: List[ProcessFileResult] = []
    verification: Optional[dict] = None


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post(
    "/file",
    response_model=ProcessingResponse,
    summary="Process Single File",
    description="Process a single document file, generating embeddings and storing in ChromaDB",
    responses={
        200: {"description": "File processed successfully"},
        404: {"description": "File not found"},
        500: {"description": "Processing error"},
    },
)
async def process_file(request: ProcessFileRequest) -> ProcessingResponse:
    """Process a single file: extract content, chunk, embed, and store."""
    cfg = get_config()
    processor = get_document_processor()
    store = get_embedding_store()

    # Resolve path (support relative paths from documents root)
    file_path = Path(request.path)
    if not file_path.is_absolute():
        docs_root = Path(cfg.mcp.paths.documents_root).expanduser().resolve()
        file_path = docs_root / file_path

    file_path = file_path.resolve()

    if not file_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"File not found: {file_path}")

    if not file_path.is_file():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Path is not a file: {file_path}")

    if file_path.suffix not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {file_path.suffix}. Supported: {', '.join(SUPPORTED_EXTENSIONS)}",
        )

    start = time.time()
    try:
        # Remove existing chunks if present
        existing = store.get_file_document_count(file_path)
        if existing > 0 and not request.force:
            return ProcessingResponse(
                status="skipped",
                message=f"File already processed ({existing} chunks). Use force=true to reprocess.",
                files_skipped=1,
                results=[ProcessFileResult(file_name=file_path.name, chunks=existing, status="skipped")],
            )

        if existing > 0:
            store.remove_file_documents(file_path)

        chunks = processor.process_document(file_path)
        if not chunks:
            return ProcessingResponse(
                status="error",
                message=f"No chunks generated for {file_path.name}",
                files_errored=1,
                results=[
                    ProcessFileResult(file_name=file_path.name, chunks=0, status="error", error="No chunks generated")
                ],
            )

        store.add_document(file_path, chunks)
        elapsed = time.time() - start

        verification = None
        if request.verify:
            verification = store.verify_embeddings()

        return ProcessingResponse(
            status="success",
            message=f"Processed {file_path.name}: {len(chunks)} chunks",
            files_processed=1,
            elapsed_seconds=round(elapsed, 2),
            results=[ProcessFileResult(file_name=file_path.name, chunks=len(chunks), status="success")],
            verification=verification,
        )

    except Exception as exc:
        logger.error("Processing failed for %s: %s", file_path, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Processing failed for {file_path.name}: {exc}",
        )


@router.post(
    "/directory",
    response_model=ProcessingResponse,
    summary="Process Directory",
    description="Process all supported documents in a directory",
    responses={
        200: {"description": "Directory processed successfully"},
        404: {"description": "Directory not found"},
        500: {"description": "Processing error"},
    },
)
async def process_directory(request: ProcessDirectoryRequest) -> ProcessingResponse:
    """Process all supported files in a directory."""
    cfg = get_config()
    processor = get_document_processor()
    store = get_embedding_store()

    if request.path:
        dir_path = Path(request.path).expanduser().resolve()
    else:
        dir_path = Path(cfg.mcp.paths.documents_root).expanduser().resolve()

    if not dir_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Directory not found: {dir_path}")
    if not dir_path.is_dir():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Path is not a directory: {dir_path}")

    # Collect files
    files: List[Path] = []
    for ext in SUPPORTED_EXTENSIONS:
        files.extend(dir_path.rglob(f"*{ext}"))

    if not files:
        return ProcessingResponse(
            status="success",
            message=f"No supported files found in {dir_path}",
        )

    start = time.time()
    results: List[ProcessFileResult] = []
    processed = 0
    skipped = 0
    errored = 0

    for file_path in files:
        try:
            existing = store.get_file_document_count(file_path)
            if existing > 0 and not request.force and not request.incremental:
                results.append(ProcessFileResult(file_name=file_path.name, chunks=existing, status="skipped"))
                skipped += 1
                continue

            if existing > 0:
                store.remove_file_documents(file_path)

            chunks = processor.process_document(file_path)
            if not chunks:
                results.append(
                    ProcessFileResult(file_name=file_path.name, chunks=0, status="error", error="No chunks generated")
                )
                errored += 1
                continue

            store.add_document(file_path, chunks)
            results.append(ProcessFileResult(file_name=file_path.name, chunks=len(chunks), status="success"))
            processed += 1

        except Exception as exc:
            logger.error("Error processing %s: %s", file_path.name, exc)
            results.append(ProcessFileResult(file_name=file_path.name, chunks=0, status="error", error=str(exc)))
            errored += 1

    elapsed = time.time() - start
    return ProcessingResponse(
        status="success" if processed > 0 else ("error" if errored > 0 else "success"),
        message=f"Processed {processed} files, skipped {skipped}, errored {errored} in {elapsed:.1f}s",
        files_processed=processed,
        files_skipped=skipped,
        files_errored=errored,
        elapsed_seconds=round(elapsed, 2),
        results=results,
    )
