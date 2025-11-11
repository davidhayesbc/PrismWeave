"""
AI Processing MCP Tools

MCP tool implementations for AI-powered document processing.
"""

from typing import Any, Dict

from mcp.managers.processing_manager import ProcessingManager
from mcp.schemas.requests import GenerateEmbeddingsRequest, GenerateTagsRequest
from mcp.schemas.responses import ErrorResponse, GenerateEmbeddingsResponse, GenerateTagsResponse
from src.core.config import Config


class ProcessingTools:
    """MCP tools for AI processing operations"""

    def __init__(self, config: Config):
        """
        Initialize processing tools

        Args:
            config: Configuration object
        """
        self.config = config
        self.processing_manager: ProcessingManager | None = None
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize the processing manager (requires async setup)"""
        if not self._initialized:
            self.processing_manager = ProcessingManager(config=self.config)
            await self.processing_manager.initialize()
            self._initialized = True

    async def generate_embeddings(self, request: GenerateEmbeddingsRequest) -> Dict[str, Any]:
        """
        Generate embeddings for a document

        Args:
            request: Embedding generation request

        Returns:
            GenerateEmbeddingsResponse dict or ErrorResponse dict
        """
        try:
            if not self._initialized or not self.processing_manager:
                await self.initialize()

            # Get document path from request
            from pathlib import Path

            document_path = Path(request.path) if request.path else Path(request.document_id)

            # Generate embeddings using ProcessingManager
            result = await self.processing_manager.generate_embeddings(
                document_path=document_path,
                force_regenerate=request.force_regenerate,
            )

            # Convert to response format
            response = GenerateEmbeddingsResponse(
                success=result["success"],
                document_id=result["document_id"],
                path=str(document_path),
                embeddings_count=result.get("chunks_processed", 0),
                chunks_processed=result.get("chunks_processed", 0),
                error=result.get("message") if not result["success"] else None,
            )

            return response.model_dump()

        except Exception as e:
            error = ErrorResponse(
                error=f"Failed to generate embeddings: {str(e)}",
                error_code="EMBEDDING_GENERATION_FAILED",
                details={"document_id": request.document_id, "path": request.path},
            )
            return error.model_dump()

    async def generate_tags(self, request: GenerateTagsRequest) -> Dict[str, Any]:
        """
        Generate tags for a document using AI

        Args:
            request: Tag generation request

        Returns:
            GenerateTagsResponse dict or ErrorResponse dict
        """
        try:
            if not self._initialized or not self.processing_manager:
                await self.initialize()

            # Get document path from request
            from pathlib import Path

            document_path = Path(request.path) if request.path else Path(request.document_id)

            # Generate tags using ProcessingManager
            result = await self.processing_manager.generate_tags(
                document_path=document_path,
                max_tags=request.max_tags,
            )

            # Convert to response format
            response = GenerateTagsResponse(
                success=result["success"],
                document_id=result["document_id"],
                path=str(document_path),
                tags=result.get("tags", []),
                merged=request.merge_with_existing,
                error=result.get("message") if not result["success"] else None,
            )

            return response.model_dump()

        except Exception as e:
            error = ErrorResponse(
                error=f"Failed to generate tags: {str(e)}",
                error_code="TAG_GENERATION_FAILED",
                details={"document_id": request.document_id, "path": request.path},
            )
            return error.model_dump()
