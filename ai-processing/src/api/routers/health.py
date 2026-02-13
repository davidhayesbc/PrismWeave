"""Health router — service health, Ollama status, and environment info."""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from src.api.deps import check_ollama_available, get_config

logger = logging.getLogger("prismweave.api.health")

router = APIRouter(tags=["health"])


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------


class OllamaStatus(BaseModel):
    available: bool
    host: str
    models: List[str] = []
    error: Optional[str] = None


class ServiceHealth(BaseModel):
    status: str = Field(..., description="healthy | degraded | unhealthy")
    service: str = "prismweave-api"
    version: str = "0.1.0"
    documents_root: Optional[str] = None
    documents_root_exists: bool = False
    chroma_db_path: Optional[str] = None
    chroma_db_exists: bool = False
    ollama: OllamaStatus
    environment: Dict[str, Optional[str]] = Field(default_factory=dict, description="Relevant environment variables")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get(
    "/health/detailed",
    response_model=ServiceHealth,
    summary="Detailed Health Check",
    description="Comprehensive health check including Ollama, ChromaDB, and documents root status",
)
async def detailed_health() -> ServiceHealth:
    """Return comprehensive health information."""
    cfg = get_config()

    docs_root = Path(cfg.mcp.paths.documents_root).expanduser().resolve()
    chroma_path = Path(cfg.chroma_db_path).expanduser().resolve()

    ollama_info = check_ollama_available()
    ollama_status = OllamaStatus(
        available=ollama_info["available"],
        host=ollama_info["host"],
        models=ollama_info.get("models", []),
        error=ollama_info.get("error"),
    )

    docs_exists = docs_root.exists()
    chroma_exists = chroma_path.exists()
    status = "healthy"
    if not docs_exists:
        status = "degraded"
    if not ollama_info["available"]:
        status = "degraded"

    return ServiceHealth(
        status=status,
        documents_root=str(docs_root),
        documents_root_exists=docs_exists,
        chroma_db_path=str(chroma_path),
        chroma_db_exists=chroma_exists,
        ollama=ollama_status,
        environment={
            "DOCUMENTS_PATH": os.environ.get("DOCUMENTS_PATH"),
            "ARTICLE_INDEX_PATH": os.environ.get("ARTICLE_INDEX_PATH"),
            "API_PORT": os.environ.get("API_PORT"),
            "OTEL_EXPORTER_OTLP_ENDPOINT": os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT"),
        },
    )


@router.get(
    "/health/ollama",
    response_model=OllamaStatus,
    summary="Ollama Health Check",
    description="Check Ollama connectivity and list available models",
)
async def ollama_health() -> OllamaStatus:
    """Dedicated Ollama health check endpoint."""
    info = check_ollama_available()
    return OllamaStatus(
        available=info["available"],
        host=info["host"],
        models=info.get("models", []),
        error=info.get("error"),
    )
