"""Shared dependencies for API routers.

Provides lazy-initialized singletons for config, embedding store, and document
processor so that each router can import what it needs without circular imports
or duplicated initialization logic.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from src.core.config import Config, load_config
from src.core.document_processor import DocumentProcessor
from src.core.embedding_store import EmbeddingStore
from src.core.git_tracker import GitTracker

logger = logging.getLogger("prismweave.api.deps")

# Lazy singletons — populated on first access via ``get_*`` helpers.
_config: Optional[Config] = None
_store: Optional[EmbeddingStore] = None
_processor: Optional[DocumentProcessor] = None


def get_config() -> Config:
    """Return the shared Config, loading from config.yaml if needed."""
    global _config
    if _config is None:
        _config = load_config()
    return _config


def get_embedding_store() -> EmbeddingStore:
    """Return a shared EmbeddingStore singleton."""
    global _store
    if _store is None:
        cfg = get_config()
        docs_root = Path(cfg.mcp.paths.documents_root).expanduser().resolve()
        git_tracker: Optional[GitTracker] = None
        if (docs_root / ".git").exists():
            try:
                git_tracker = GitTracker(docs_root, cfg)
            except Exception:
                logger.warning("Failed to initialize GitTracker; proceeding without git tracking")
        _store = EmbeddingStore(cfg, git_tracker)
    return _store


def get_document_processor() -> DocumentProcessor:
    """Return a shared DocumentProcessor singleton."""
    global _processor
    if _processor is None:
        cfg = get_config()
        docs_root = Path(cfg.mcp.paths.documents_root).expanduser().resolve()
        git_tracker: Optional[GitTracker] = None
        if (docs_root / ".git").exists():
            try:
                git_tracker = GitTracker(docs_root, cfg)
            except Exception:
                logger.warning("Failed to initialize GitTracker; proceeding without git tracking")
        _processor = DocumentProcessor(cfg, git_tracker)
    return _processor


def check_ollama_available() -> dict:
    """Check Ollama connectivity and return a status dict."""
    cfg = get_config()
    try:
        import requests

        response = requests.get(f"{cfg.ollama_host}/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            models = [m.get("name", "") for m in data.get("models", [])]
            return {"available": True, "host": cfg.ollama_host, "models": models}
        return {"available": False, "host": cfg.ollama_host, "error": f"HTTP {response.status_code}"}
    except Exception as exc:
        return {"available": False, "host": cfg.ollama_host, "error": str(exc)}
