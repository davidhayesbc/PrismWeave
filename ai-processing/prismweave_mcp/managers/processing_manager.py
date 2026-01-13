"""
Processing Manager for PrismWeave MCP Server

Handles AI-powered document processing including:
- Embedding generation
- Tag generation
- Auto-processing workflows
"""

import asyncio
import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

import requests

from src.core.config import Config
from src.core.document_processor import DocumentProcessor
from src.core.embedding_store import EmbeddingStore

from prismweave_mcp.utils.document_utils import generate_frontmatter, parse_frontmatter

logger = logging.getLogger(__name__)


class ProcessingManager:
    """
    Manager for AI processing operations

    Integrates with existing DocumentProcessor and EmbeddingStore
    to provide AI-powered analysis and embedding generation.
    """

    def __init__(
        self,
        config: Config,
        document_processor: Optional[DocumentProcessor] = None,
        embedding_store: Optional[EmbeddingStore] = None,
    ):
        """
        Initialize Processing Manager

        Args:
            config: Configuration object
            document_processor: Optional DocumentProcessor instance
            embedding_store: Optional EmbeddingStore instance
        """
        self.config = config
        self.document_processor = document_processor or DocumentProcessor(config)
        self.embedding_store = embedding_store or EmbeddingStore(config)

    async def initialize(self) -> None:
        """
        Initialize processing components

        Raises:
            RuntimeError: If initialization fails
        """
        try:
            # EmbeddingStore doesn't require async initialization
            # It initializes synchronously in __init__
            # Verify it's working by checking document count
            count = self.embedding_store.get_document_count()
            logger.info(f"Processing manager initialized successfully - {count} documents in store")
        except Exception as e:
            logger.error(f"Failed to initialize processing manager: {e}")
            raise RuntimeError(f"Processing manager initialization failed: {e}") from e

    async def generate_embeddings(self, document_path: Path, force_regenerate: bool = False) -> dict:
        """
        Generate embeddings for a document

        Args:
            document_path: Path to document file
            force_regenerate: Force regeneration even if embeddings exist

        Returns:
            Dictionary with embedding generation results:
            {
                "success": bool,
                "chunks_processed": int,
                "document_id": str,
                "message": str
            }
        """
        try:
            logger.info(f"Generating embeddings for: {document_path}")

            # Check if embeddings already exist
            existing_chunk_count = self.embedding_store.get_file_document_count(document_path)
            if existing_chunk_count and existing_chunk_count > 0:
                logger.info(f"Embeddings already exist for {document_path}")
                if not force_regenerate:
                    return {
                        "success": True,
                        "chunks_processed": existing_chunk_count,
                        "document_id": str(document_path),
                        "message": "Embeddings already exist (use force_regenerate=True to recreate)",
                    }

                # Remove existing chunks before regeneration
                self.embedding_store.remove_file_documents(document_path)

            # Load and chunk document
            chunks = self.document_processor.process_document(document_path)

            if not chunks:
                logger.warning(f"No chunks generated for {document_path}")
                return {
                    "success": False,
                    "chunks_processed": 0,
                    "document_id": str(document_path),
                    "message": "Failed to generate chunks from document",
                }

            # Add to embedding store (this generates embeddings automatically)
            self.embedding_store.add_document(document_path, chunks)

            logger.info(f"Successfully generated {len(chunks)} embeddings for {document_path}")

            return {
                "success": True,
                "chunks_processed": len(chunks),
                "document_id": str(document_path),
                "message": f"Generated embeddings for {len(chunks)} chunks",
            }

        except Exception as e:
            logger.error(f"Failed to generate embeddings for {document_path}: {e}")
            return {
                "success": False,
                "chunks_processed": 0,
                "document_id": str(document_path),
                "message": f"Error: {str(e)}",
            }

    async def generate_tags(self, document_path: Path, max_tags: int = 10) -> dict:
        """
        Generate tags for a document using AI

        Args:
            document_path: Path to document file
            max_tags: Maximum number of tags to generate

        Returns:
            Dictionary with tag generation results:
            {
                "success": bool,
                "tags": List[str],
                "document_id": str,
                "message": str
            }
        """
        return await self.generate_tags_with_options(
            document_path=document_path,
            max_tags=max_tags,
            force_regenerate=False,
        )

    async def generate_tags_with_options(
        self,
        document_path: Path,
        max_tags: int = 10,
        force_regenerate: bool = False,
    ) -> dict:
        """Generate semantic tags for a document.

        Behavior:
        - If the document already has tags and force_regenerate=False, returns existing tags.
        - Otherwise tries Ollama LLM tagging; falls back to deterministic keyword extraction.
        """
        try:
            logger.info(f"Generating tags for: {document_path}")

            if not document_path.exists():
                raise FileNotFoundError(f"File not found: {document_path}")

            file_text = document_path.read_text(encoding="utf-8")
            existing_metadata, clean_content = parse_frontmatter(file_text)

            existing_tags = existing_metadata.get("tags")
            normalized_existing = self._normalize_tags(existing_tags)
            if normalized_existing and not force_regenerate:
                return {
                    "success": True,
                    "tags": normalized_existing[:max_tags],
                    "confidence": 1.0,
                    "document_id": str(document_path),
                    "message": "Tags already exist (use force_regenerate=True to regenerate)",
                }

            title = str(existing_metadata.get("title") or document_path.stem)
            source_keywords = existing_metadata.get("source_keywords") or existing_metadata.get("sourceKeywords")
            source_keywords_list = self._normalize_tags(source_keywords)

            # 1) Try Ollama-based semantic tagging
            tags, confidence = await self._generate_tags_via_ollama(
                title=title,
                content=clean_content,
                source_keywords=source_keywords_list,
                max_tags=max_tags,
            )

            # 2) Fallback to deterministic extraction if Ollama unavailable / failed
            if not tags:
                tags = self._extract_tags_fallback(clean_content, source_keywords_list, max_tags)
                confidence = 0.35 if tags else 0.0

            return {
                "success": True,
                "tags": tags,
                "confidence": confidence,
                "document_id": str(document_path),
                "message": f"Generated {len(tags)} tags",
            }

        except Exception as e:
            logger.error(f"Failed to generate tags for {document_path}: {e}")
            return {
                "success": False,
                "tags": [],
                "confidence": 0.0,
                "document_id": str(document_path),
                "message": f"Error: {str(e)}",
            }

    async def _generate_tags_via_ollama(
        self,
        title: str,
        content: str,
        source_keywords: list[str],
        max_tags: int,
    ) -> tuple[list[str], float]:
        """Best-effort semantic tag generation using Ollama.

        Returns (tags, confidence). On failure returns ([], 0.0).
        """
        prompt = self._build_tagging_prompt(title=title, content=content, source_keywords=source_keywords, max_tags=max_tags)
        payload = {
            "model": self.config.tagging_model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.1},
        }

        url = self.config.ollama_host.rstrip("/") + "/api/generate"

        def _do_request() -> dict:
            resp = requests.post(url, json=payload, timeout=self.config.ollama_timeout)
            resp.raise_for_status()
            return resp.json()

        try:
            data = await asyncio.to_thread(_do_request)
            raw = str(data.get("response") or "").strip()
            tags = self._parse_tag_list(raw)
            tags = self._normalize_tags(tags)[:max_tags]
            if not tags:
                return [], 0.0
            return tags, 0.8
        except Exception as exc:
            logger.info(f"Ollama tag generation unavailable/failed; falling back. Reason: {exc}")
            return [], 0.0

    @staticmethod
    def _build_tagging_prompt(title: str, content: str, source_keywords: list[str], max_tags: int) -> str:
        # Keep prompts short to reduce latency.
        excerpt = content.strip()
        if len(excerpt) > 4000:
            excerpt = excerpt[:4000]

        source_hint = ", ".join(source_keywords[:20]) if source_keywords else ""

        return (
            "You are a document tagging assistant.\n"
            "Task: produce a small set of consistent, semantic tags for the document.\n"
            "Rules:\n"
            f"- Return ONLY a JSON array of 1 to {max_tags} strings.\n"
            "- Tags must be lowercase kebab-case (e.g. \"machine-learning\").\n"
            "- Prefer broad topics over site-specific labels.\n"
            "- Avoid duplicates, avoid personal names, avoid dates.\n"
            "\n"
            f"Title: {title}\n"
            + (f"Source keywords (raw hints): {source_hint}\n" if source_hint else "")
            + "Content:\n"
            + excerpt
        )

    @staticmethod
    def _parse_tag_list(text: str) -> list[str]:
        """Parse a JSON array of strings from model output (best-effort)."""
        text = text.strip()
        if not text:
            return []

        # First, try direct JSON.
        try:
            parsed = json.loads(text)
            if isinstance(parsed, list):
                return [str(x) for x in parsed]
        except Exception:
            pass

        # Fallback: extract the first JSON array in the response.
        match = re.search(r"\[[\s\S]*?\]", text)
        if not match:
            return []
        try:
            parsed = json.loads(match.group(0))
            if isinstance(parsed, list):
                return [str(x) for x in parsed]
        except Exception:
            return []
        return []

    @staticmethod
    def _normalize_tags(value: object) -> list[str]:
        """Normalize tags to lowercase kebab-case and dedupe while preserving order."""
        if value is None:
            return []

        if isinstance(value, str):
            # Support comma-separated or YAML-ish strings.
            raw_items = re.split(r"[,;|]", value)
        elif isinstance(value, list):
            raw_items = [str(v) for v in value]
        else:
            raw_items = [str(value)]

        seen: set[str] = set()
        out: list[str] = []
        for item in raw_items:
            t = item.strip().lower()
            if not t:
                continue
            # Convert spaces/underscores to hyphens
            t = re.sub(r"[\s_]+", "-", t)
            # Remove invalid chars
            t = re.sub(r"[^a-z0-9-]", "", t)
            # Collapse hyphens
            t = re.sub(r"-+", "-", t).strip("-")
            if len(t) < 2 or len(t) > 40:
                continue
            if t in seen:
                continue
            seen.add(t)
            out.append(t)
        return out

    @staticmethod
    def _extract_tags_fallback(content: str, source_keywords: list[str], max_tags: int) -> list[str]:
        """Deterministic fallback tag extraction: use source keywords first, then frequent terms."""
        tags: list[str] = []
        tags.extend(source_keywords)

        # Light-weight frequency-based fallback
        stop = {
            "this",
            "that",
            "with",
            "from",
            "your",
            "have",
            "will",
            "what",
            "when",
            "where",
            "which",
            "their",
            "about",
            "there",
            "into",
            "also",
            "because",
            "https",
            "http",
        }
        words = re.findall(r"[a-zA-Z][a-zA-Z0-9_-]{2,}", content.lower())
        freq: dict[str, int] = {}
        for w in words:
            w = re.sub(r"[^a-z0-9-]", "", w)
            w = re.sub(r"-+", "-", w).strip("-")
            if len(w) < 3:
                continue
            if w in stop:
                continue
            freq[w] = freq.get(w, 0) + 1

        for w, _ in sorted(freq.items(), key=lambda kv: kv[1], reverse=True):
            tags.append(w)
            if len(tags) >= max_tags * 3:
                break

        # Normalize + clamp
        return ProcessingManager._normalize_tags(tags)[:max_tags]

    @staticmethod
    def _update_document_tags_frontmatter(document_path: Path, tags: object) -> None:
        """Update (or create) frontmatter tags for a markdown document."""
        normalized_tags = ProcessingManager._normalize_tags(tags)
        if not normalized_tags:
            return

        file_text = document_path.read_text(encoding="utf-8")
        metadata, clean_content = parse_frontmatter(file_text)

        # Preserve existing metadata; only update tags and timestamp fields.
        metadata = dict(metadata)
        metadata["tags"] = normalized_tags
        metadata["tagged_at"] = datetime.now().isoformat()

        frontmatter_text = generate_frontmatter(metadata)
        document_path.write_text(f"{frontmatter_text}\n{clean_content}", encoding="utf-8")

    async def auto_process_document(
        self,
        document_path: Path,
        generate_embeddings: bool = True,
        generate_tags: bool = True,
        update_metadata: bool = True,
    ) -> dict:
        """
        Automatically process a document with multiple AI operations

        Args:
            document_path: Path to document file
            generate_embeddings: Whether to generate embeddings
            generate_tags: Whether to generate tags
            update_metadata: Whether to update document metadata

        Returns:
            Dictionary with processing results:
            {
                "success": bool,
                "embeddings_result": Dict,
                "tags_result": Dict,
                "document_id": str,
                "message": str
            }
        """
        try:
            logger.info(f"Auto-processing document: {document_path}")

            results = {
                "success": True,
                "document_id": str(document_path),
                "embeddings_result": None,
                "tags_result": None,
                "message": "Auto-processing complete",
            }

            # Generate embeddings
            if generate_embeddings:
                embeddings_result = await self.generate_embeddings(document_path)
                results["embeddings_result"] = embeddings_result
                if not embeddings_result["success"]:
                    results["success"] = False
                    results["message"] = "Failed to generate embeddings"

            # Generate tags
            if generate_tags:
                tags_result = await self.generate_tags(document_path)
                results["tags_result"] = tags_result
                if not tags_result["success"]:
                    results["success"] = False
                    if results["message"] == "Auto-processing complete":
                        results["message"] = "Failed to generate tags"

            # Update metadata (if requested)
            if update_metadata and results["tags_result"] and results["tags_result"]["success"]:
                self._update_document_tags_frontmatter(
                    document_path=document_path,
                    tags=results["tags_result"].get("tags", []),
                )

            return results

        except Exception as e:
            logger.error(f"Auto-processing failed for {document_path}: {e}")
            return {
                "success": False,
                "document_id": str(document_path),
                "embeddings_result": None,
                "tags_result": None,
                "message": f"Error: {str(e)}",
            }

    async def get_processing_status(self, document_path: Path) -> dict:
        """
        Get processing status for a document

        Args:
            document_path: Path to document file

        Returns:
            Dictionary with processing status:
            {
                "document_id": str,
                "has_embeddings": bool,
                "embedding_count": int,
                "last_processed": Optional[str]
            }
        """
        try:
            chunk_count = self.embedding_store.get_file_document_count(document_path)

            return {
                "document_id": str(document_path),
                "has_embeddings": chunk_count > 0,
                "embedding_count": chunk_count,
                "last_processed": datetime.now().isoformat() if chunk_count > 0 else None,
            }

        except Exception as e:
            logger.error(f"Failed to get processing status for {document_path}: {e}")
            return {
                "document_id": str(document_path),
                "has_embeddings": False,
                "embedding_count": 0,
                "last_processed": None,
                "error": str(e),
            }

    async def remove_embeddings(self, document_path: Path) -> dict:
        """
        Remove embeddings for a document

        Args:
            document_path: Path to document file

        Returns:
            Dictionary with removal results:
            {
                "success": bool,
                "document_id": str,
                "chunks_removed": int,
                "message": str
            }
        """
        try:
            logger.info(f"Removing embeddings for: {document_path}")

            # Get current chunks count
            chunk_count = self.embedding_store.get_file_document_count(document_path)

            # Delete from embedding store
            removed = self.embedding_store.remove_file_documents(document_path)

            if removed:
                logger.info(f"Removed {chunk_count} embeddings for {document_path}")
            else:
                logger.info(f"No embeddings found to remove for {document_path}")

            return {
                "success": removed,
                "document_id": str(document_path),
                "chunks_removed": chunk_count,
                "message": f"Removed {chunk_count} embedding chunks" if removed else "No embedding chunks found",
            }

        except Exception as e:
            logger.error(f"Failed to remove embeddings for {document_path}: {e}")
            return {
                "success": False,
                "document_id": str(document_path),
                "chunks_removed": 0,
                "message": f"Error: {str(e)}",
            }
