"""Rebuild router — embedding rebuild and full rebuild-everything endpoint."""

from __future__ import annotations

import logging
import shutil
import time
from pathlib import Path
from typing import Dict, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from src.api.deps import check_ollama_available, get_config
from src.cli_support import SUPPORTED_EXTENSIONS

logger = logging.getLogger("prismweave.api.rebuild")

router = APIRouter(prefix="/rebuild", tags=["rebuild"])


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------


class RebuildEmbeddingsRequest(BaseModel):
    force: bool = Field(True, description="Force reprocessing of all files")
    verify: bool = Field(True, description="Verify embeddings after rebuild")


class RebuildEverythingRequest(BaseModel):
    """Parameters for the full rebuild-everything pipeline."""

    algorithm: str = Field("kmeans", pattern="^(kmeans|hdbscan)$")
    k: Optional[int] = Field(None, ge=2)
    max_articles: Optional[int] = Field(None, ge=1)
    sample_size: int = Field(10, ge=1, le=100)
    top_n: int = Field(8, ge=1, le=50)
    min_confidence: float = Field(0.15, ge=0.0, le=1.0)
    tags_only: bool = Field(False, description="Only rebuild tag embeddings + assignment (skip clustering)")


class RebuildResponse(BaseModel):
    status: str
    message: str
    elapsed_seconds: Optional[float] = None
    phases: Dict = Field(default_factory=dict, description="Results for each phase of the rebuild")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post(
    "/embeddings",
    response_model=RebuildResponse,
    summary="Rebuild Embeddings",
    description="Wipe and rebuild the ChromaDB embedding store from documents on disk",
    responses={
        200: {"description": "Embeddings rebuilt successfully"},
        503: {"description": "Ollama not available"},
        500: {"description": "Rebuild failed"},
    },
)
async def rebuild_embeddings(request: RebuildEmbeddingsRequest) -> RebuildResponse:
    """Rebuild the ChromaDB embedding store from scratch."""
    ollama_status = check_ollama_available()
    if not ollama_status["available"]:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Ollama not available: {ollama_status.get('error', 'unknown')}",
        )

    cfg = get_config()
    docs_root = Path(cfg.mcp.paths.documents_root).expanduser().resolve()
    chroma_path = Path(cfg.chroma_db_path).expanduser().resolve()

    if not docs_root.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Documents root not found: {docs_root}")

    start = time.time()
    phases: Dict = {}

    try:
        from src.core.document_processor import DocumentProcessor
        from src.core.embedding_store import EmbeddingStore
        from src.core.git_tracker import GitTracker

        # Wipe existing ChromaDB
        if chroma_path.exists():
            shutil.rmtree(chroma_path)
            phases["wipe"] = "ChromaDB directory removed"
        chroma_path.mkdir(parents=True, exist_ok=True)

        # Also wipe processing state
        processing_state = docs_root / ".prismweave" / "processing_state.sqlite"
        if processing_state.exists():
            processing_state.unlink()
            phases["processing_state"] = "processing_state.sqlite removed"

        git_tracker = None
        if (docs_root / ".git").exists():
            try:
                git_tracker = GitTracker(docs_root, cfg)
            except Exception:
                pass

        processor = DocumentProcessor(cfg, git_tracker)
        store = EmbeddingStore(cfg, git_tracker)

        # Collect and process all files
        files = []
        for ext in SUPPORTED_EXTENSIONS:
            files.extend(docs_root.rglob(f"*{ext}"))

        processed = 0
        for file_path in files:
            try:
                chunks = processor.process_document(file_path)
                if chunks:
                    store.add_document(file_path, chunks)
                    processed += 1
            except Exception as exc:
                logger.warning("Failed to process %s: %s", file_path.name, exc)

        phases["processing"] = {"files_found": len(files), "files_processed": processed}

        verification = None
        if request.verify:
            verification = store.verify_embeddings()
            phases["verification"] = verification

        elapsed = time.time() - start
        return RebuildResponse(
            status="success",
            message=f"Rebuilt embeddings: {processed} files processed in {elapsed:.1f}s",
            elapsed_seconds=round(elapsed, 2),
            phases=phases,
        )

    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Embeddings rebuild failed: %s", exc)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Rebuild failed: {exc}")


@router.post(
    "/everything",
    response_model=RebuildResponse,
    summary="Rebuild Everything",
    description="Full rebuild: embeddings → clustering → proposals → taxonomy → tag assignment",
    responses={
        200: {"description": "Full rebuild completed"},
        503: {"description": "Ollama not available"},
        500: {"description": "Rebuild failed"},
    },
)
async def rebuild_everything(request: RebuildEverythingRequest) -> RebuildResponse:
    """Run the full rebuild-everything pipeline (equivalent to CLI rebuild-everything)."""
    ollama_status = check_ollama_available()
    if not ollama_status["available"]:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Ollama not available: {ollama_status.get('error', 'unknown')}",
        )

    cfg = get_config()
    docs_root = Path(cfg.mcp.paths.documents_root).expanduser().resolve()
    chroma_path = Path(cfg.chroma_db_path).expanduser().resolve()

    if not docs_root.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Documents root not found: {docs_root}")

    start = time.time()
    phases: Dict = {}

    try:
        from src.core.document_processor import DocumentProcessor
        from src.core.embedding_store import EmbeddingStore
        from src.core.git_tracker import GitTracker
        from src.taxonomy.assignments import AssignmentOptions, run_article_tag_assignment
        from src.taxonomy.pipeline import ClusterPipelineOptions, run_clustering_pipeline
        from src.taxonomy.proposals import ProposalRunOptions, run_cluster_proposals
        from src.taxonomy.store import default_taxonomy_sqlite_path
        from src.taxonomy.tag_embeddings import TagEmbeddingOptions, embed_and_store_tags
        from src.taxonomy.taxonomy_builder import run_taxonomy_normalize_and_store

        taxonomy_sqlite = default_taxonomy_sqlite_path(docs_root)
        taxonomy_artifacts_dir = docs_root / ".prismweave" / "taxonomy" / "artifacts"

        if request.tags_only:
            # Tags-only mode: re-embed tags + re-assign
            phase_start = time.time()

            embed_result = embed_and_store_tags(cfg, options=TagEmbeddingOptions(use_description=True))
            phases["embed_tags"] = embed_result

            assign_result = run_article_tag_assignment(
                cfg, options=AssignmentOptions(top_n=request.top_n, min_confidence=request.min_confidence)
            )
            phases["assign"] = assign_result

            elapsed = time.time() - start
            return RebuildResponse(
                status="success",
                message=f"Tag rebuild completed: {assign_result.get('assignments', 0)} assignments in {elapsed:.1f}s",
                elapsed_seconds=round(elapsed, 2),
                phases=phases,
            )

        # Phase 1: Wipe + rebuild embeddings
        phase_start = time.time()

        if chroma_path.exists():
            shutil.rmtree(chroma_path)
        chroma_path.mkdir(parents=True, exist_ok=True)

        processing_state = docs_root / ".prismweave" / "processing_state.sqlite"
        if processing_state.exists():
            processing_state.unlink()

        git_tracker = None
        if (docs_root / ".git").exists():
            try:
                git_tracker = GitTracker(docs_root, cfg)
            except Exception:
                pass

        processor = DocumentProcessor(cfg, git_tracker)
        store = EmbeddingStore(cfg, git_tracker)

        files = []
        for ext in SUPPORTED_EXTENSIONS:
            files.extend(docs_root.rglob(f"*{ext}"))

        processed = 0
        for f in files:
            try:
                chunks = processor.process_document(f)
                if chunks:
                    store.add_document(f, chunks)
                    processed += 1
            except Exception as exc:
                logger.warning("Failed to process %s: %s", f.name, exc)

        phases["embeddings"] = {"files": processed, "elapsed": round(time.time() - phase_start, 2)}

        # Phase 2: Wipe taxonomy
        phase_start = time.time()
        if taxonomy_sqlite.exists():
            taxonomy_sqlite.unlink()
        if taxonomy_artifacts_dir.exists():
            shutil.rmtree(taxonomy_artifacts_dir)
        phases["taxonomy_wipe"] = {"elapsed": round(time.time() - phase_start, 2)}

        # Phase 3: Clustering
        phase_start = time.time()
        cluster_result = run_clustering_pipeline(
            cfg,
            options=ClusterPipelineOptions(
                max_articles=request.max_articles,
                algorithm=request.algorithm,
                k=request.k,
            ),
        )
        phases["clustering"] = {**cluster_result, "elapsed": round(time.time() - phase_start, 2)}

        # Phase 4: LLM proposals
        phase_start = time.time()
        proposals_result = run_cluster_proposals(cfg, options=ProposalRunOptions(sample_size=request.sample_size))
        phases["proposals"] = {**proposals_result, "elapsed": round(time.time() - phase_start, 2)}

        # Phase 5: Normalize + embed tags
        phase_start = time.time()
        normalize_result = run_taxonomy_normalize_and_store(cfg)
        embed_result = embed_and_store_tags(cfg, options=TagEmbeddingOptions(use_description=True))
        phases["normalize_embed"] = {
            "categories": normalize_result.get("categories"),
            "tags": normalize_result.get("tags"),
            "embedded_tags": embed_result.get("tags"),
            "elapsed": round(time.time() - phase_start, 2),
        }

        # Phase 6: Assign tags
        phase_start = time.time()
        assign_result = run_article_tag_assignment(
            cfg, options=AssignmentOptions(top_n=request.top_n, min_confidence=request.min_confidence)
        )
        phases["assign"] = {**assign_result, "elapsed": round(time.time() - phase_start, 2)}

        elapsed = time.time() - start
        return RebuildResponse(
            status="success",
            message=f"Full rebuild completed in {elapsed:.1f}s",
            elapsed_seconds=round(elapsed, 2),
            phases=phases,
        )

    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Full rebuild failed: %s", exc)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Rebuild failed: {exc}")
