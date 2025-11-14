"""
Document Creation and Modification MCP Tools

MCP tool implementations for creating and updating documents.
"""

from typing import Any

from prismweave_mcp.managers.document_manager import DocumentManager
from prismweave_mcp.managers.git_manager import GitManager
from prismweave_mcp.managers.processing_manager import ProcessingManager
from prismweave_mcp.schemas.requests import CreateDocumentRequest, UpdateDocumentRequest
from prismweave_mcp.schemas.responses import CreateDocumentResponse, ErrorResponse, UpdateDocumentResponse
from src.core.config import Config


class DocumentTools:
    """MCP tools for document creation and modification operations"""

    def __init__(self, config: Config):
        """
        Initialize document tools

        Args:
            config: Configuration object
        """
        self.config = config
        self.document_manager = DocumentManager(config)
        self.processing_manager: ProcessingManager | None = None
        self.git_manager: GitManager | None = None
        self._processing_initialized = False
        self._git_initialized = False

    async def _ensure_processing_manager(self) -> ProcessingManager:
        """Lazy initialization of processing manager"""
        if not self._processing_initialized or not self.processing_manager:
            self.processing_manager = ProcessingManager(config=self.config)
            await self.processing_manager.initialize()
            self._processing_initialized = True
        return self.processing_manager

    async def _ensure_git_manager(self) -> GitManager:
        """Lazy initialization of git manager"""
        if not self._git_initialized or not self.git_manager:
            self.git_manager = GitManager(config=self.config)
            self._git_initialized = True
        return self.git_manager

    async def create_document(self, request: CreateDocumentRequest) -> dict[str, Any]:
        """
        Create a new document

        Args:
            request: Document creation request

        Returns:
            CreateDocumentResponse dict or ErrorResponse dict
        """
        try:
            # Create the document (use additional_metadata from schema, not metadata)
            document, file_path = self.document_manager.create_document(
                title=request.title,
                content=request.content,
                tags=request.tags or [],
                category=request.category,
                metadata=request.additional_metadata or {},
            )

            response = CreateDocumentResponse(
                document_id=document.id,
                path=str(file_path),
            )

            return response.model_dump()

        except Exception as e:
            error = ErrorResponse(
                error=f"Failed to create document: {str(e)}",
                error_code="DOCUMENT_CREATION_EXCEPTION",
                details={"title": request.title},
            )
            return error.model_dump()

    async def update_document(self, request: UpdateDocumentRequest) -> dict[str, Any]:
        """
        Update an existing document

        Args:
            request: Document update request

        Returns:
            UpdateDocumentResponse dict or ErrorResponse dict
        """
        try:
            # Prepare updates dict and track fields (use additional_metadata from schema)
            updates = {}
            updated_fields = []

            if request.title is not None:
                updates["title"] = request.title
                updated_fields.append("title")
            if request.content is not None:
                updates["content"] = request.content
                updated_fields.append("content")
            if request.tags is not None:
                updates["tags"] = request.tags
                updated_fields.append("tags")
            if request.additional_metadata is not None:
                updates["metadata"] = request.additional_metadata
                updated_fields.append("metadata")

            metadata_updates = updates.get("metadata", {}).copy() if "metadata" in updates else {}
            if request.category is not None:
                metadata_updates["category"] = request.category
                if "category" not in updated_fields:
                    updated_fields.append("category")
                if "metadata" not in updated_fields:
                    updated_fields.append("metadata")
            metadata_param = metadata_updates or None

            self.document_manager.update_document(
                document_id=request.document_id,
                content=updates.get("content"),
                title=updates.get("title"),
                tags=updates.get("tags"),
                metadata=metadata_param,
            )

            response = UpdateDocumentResponse(
                document_id=request.document_id,
                updated_fields=updated_fields,
            )

            return response.model_dump()

        except Exception as e:
            error = ErrorResponse(
                error=f"Failed to update document: {str(e)}",
                error_code="DOCUMENT_UPDATE_EXCEPTION",
                details={"document_id": request.document_id},
            )
            return error.model_dump()
