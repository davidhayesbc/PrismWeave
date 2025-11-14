"""
AI Processing MCP Tools

MCP tool implementations for AI-powered document processing.
"""

from typing import Any

from prismweave_mcp.managers.document_manager import DocumentManager
from prismweave_mcp.managers.processing_manager import ProcessingManager
from prismweave_mcp.schemas.requests import GenerateEmbeddingsRequest, GenerateTagsRequest
from prismweave_mcp.schemas.responses import ErrorResponse, GenerateEmbeddingsResponse, GenerateTagsResponse
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
        self.document_manager = DocumentManager(config)
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize the processing manager (requires async setup)"""
        if not self._initialized:
            self.processing_manager = ProcessingManager(config=self.config)
            await self.processing_manager.initialize()
            self._initialized = True

    async def generate_embeddings(self, request: GenerateEmbeddingsRequest) -> dict[str, Any]:
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

            document = self.document_manager.get_document_by_id(request.document_id)
            if not document:
                error = ErrorResponse(
                    error="Document not found",
                    error_code="DOCUMENT_NOT_FOUND",
                    details={"document_id": request.document_id},
                )
                return error.model_dump()

            document_path = (self.document_manager.docs_root / document.path).resolve()

            if not document_path.exists():
                error = ErrorResponse(
                    error="Document path not found",
                    error_code="DOCUMENT_PATH_NOT_FOUND",
                    details={"document_id": request.document_id, "path": str(document_path)},
                )
                return error.model_dump()

            result = await self.processing_manager.generate_embeddings(
                document_path=document_path,
                force_regenerate=request.force_regenerate,
            )

            if not result.get("success", False):
                error = ErrorResponse(
                    error=result.get("message", "Failed to generate embeddings"),
                    error_code="EMBEDDING_GENERATION_FAILED",
                    details={"document_id": request.document_id},
                )
                return error.model_dump()

            response = GenerateEmbeddingsResponse(
                document_id=request.document_id,
                embedding_count=result.get("chunks_processed", 0),
                model=request.model,
            )

            return response.model_dump()

        except Exception as e:
            error = ErrorResponse(
                error=f"Failed to generate embeddings: {str(e)}",
                error_code="EMBEDDING_GENERATION_FAILED",
                details={"document_id": request.document_id},
            )
            return error.model_dump()

    async def generate_tags(self, request: GenerateTagsRequest) -> dict[str, Any]:
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

            document = self.document_manager.get_document_by_id(request.document_id)
            if not document:
                error = ErrorResponse(
                    error="Document not found",
                    error_code="DOCUMENT_NOT_FOUND",
                    details={"document_id": request.document_id},
                )
                return error.model_dump()

            document_path = (self.document_manager.docs_root / document.path).resolve()

            if not document_path.exists():
                error = ErrorResponse(
                    error="Document path not found",
                    error_code="DOCUMENT_PATH_NOT_FOUND",
                    details={"document_id": request.document_id, "path": str(document_path)},
                )
                return error.model_dump()

            result = await self.processing_manager.generate_tags(
                document_path=document_path,
                max_tags=request.max_tags,
            )

            # Check if processing succeeded
            if not result["success"]:
                error = ErrorResponse(
                    error=result.get("message", "Tag generation failed"),
                    error_code="TAG_GENERATION_FAILED",
                    details={"document_id": request.document_id},
                )
                return error.model_dump()

            # Convert to response format (schema only has: document_id, tags, confidence)
            response = GenerateTagsResponse(
                document_id=request.document_id,
                tags=result.get("tags", []),
                confidence=result.get("confidence", 0.0),
            )

            return response.model_dump()

        except Exception as e:
            error = ErrorResponse(
                error=f"Failed to generate tags: {str(e)}",
                error_code="TAG_GENERATION_FAILED",
                details={"document_id": request.document_id},
            )
            return error.model_dump()
