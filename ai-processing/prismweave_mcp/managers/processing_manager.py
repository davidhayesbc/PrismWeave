"""
Processing Manager for PrismWeave MCP Server

Handles AI-powered document processing including:
- Embedding generation
- Tag generation
- Auto-processing workflows
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from src.core.config import Config
from src.core.document_processor import DocumentProcessor
from src.core.embedding_store import EmbeddingStore

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
            raise RuntimeError(f"Processing manager initialization failed: {e}")

    async def generate_embeddings(self, document_path: Path, force_regenerate: bool = False) -> Dict:
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

    async def generate_tags(self, document_path: Path, max_tags: int = 10) -> Dict:
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
        try:
            logger.info(f"Generating tags for: {document_path}")

            # This would use Ollama to generate tags
            # For now, returning a placeholder implementation
            # TODO: Implement actual tag generation with Ollama

            tags = await self._extract_tags_from_document(document_path, max_tags)

            return {
                "success": True,
                "tags": tags,
                "document_id": str(document_path),
                "message": f"Generated {len(tags)} tags",
            }

        except Exception as e:
            logger.error(f"Failed to generate tags for {document_path}: {e}")
            return {"success": False, "tags": [], "document_id": str(document_path), "message": f"Error: {str(e)}"}

    async def _extract_tags_from_document(self, document_path: Path, max_tags: int) -> List[str]:
        """
        Extract tags from document (placeholder implementation)

        TODO: Implement with Ollama LLM
        """
        # Read document
        content = document_path.read_text(encoding="utf-8")

        # Simple keyword extraction (placeholder)
        # In a real implementation, this would use Ollama
        common_words = ["the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with"]
        words = content.lower().split()
        word_freq = {}

        for word in words:
            cleaned = word.strip(".,!?;:()")
            if len(cleaned) > 3 and cleaned not in common_words:
                word_freq[cleaned] = word_freq.get(cleaned, 0) + 1

        # Get top N words as tags
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        tags = [word for word, _ in sorted_words[:max_tags]]

        return tags

    async def auto_process_document(
        self,
        document_path: Path,
        generate_embeddings: bool = True,
        generate_tags: bool = True,
        update_metadata: bool = True,
    ) -> Dict:
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
                # TODO: Update document frontmatter with generated tags
                # This would be implemented by the Document Manager
                pass

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

    async def get_processing_status(self, document_path: Path) -> Dict:
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

    async def remove_embeddings(self, document_path: Path) -> Dict:
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
