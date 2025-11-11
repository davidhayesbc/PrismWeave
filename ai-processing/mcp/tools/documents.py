"""
Document Creation and Modification MCP Tools

MCP tool implementations for creating and updating documents.
"""

from typing import Any

from mcp.managers.document_manager import DocumentManager
from mcp.managers.git_manager import GitManager
from mcp.managers.processing_manager import ProcessingManager
from mcp.schemas.requests import CreateDocumentRequest, UpdateDocumentRequest
from mcp.schemas.responses import CreateDocumentResponse, ErrorResponse, UpdateDocumentResponse
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
        Create a new document with optional auto-processing and git commit

        Args:
            request: Document creation request

        Returns:
            CreateDocumentResponse dict or ErrorResponse dict
        """
        try:
            # Create the document
            result = self.document_manager.create_document(
                title=request.title,
                content=request.content,
                metadata=request.metadata or {},
                tags=request.tags or [],
                category=request.category,
            )

            if not result["success"]:
                error = ErrorResponse(
                    error=result.get("error", "Failed to create document"), error_code="DOCUMENT_CREATION_FAILED"
                )
                return error.model_dump()

            document_id = result["document_id"]
            file_path = result["file_path"]

            # Track processing results
            embeddings_generated = False
            tags_generated = False

            # Optional: Generate embeddings and tags
            if request.auto_process:
                try:
                    processing_manager = await self._ensure_processing_manager()

                    # Generate embeddings
                    embedding_result = await processing_manager.generate_embeddings(
                        document_id=document_id, force_regenerate=False
                    )
                    embeddings_generated = embedding_result.get("success", False)

                    # Generate tags
                    tag_result = await processing_manager.generate_tags(document_id=document_id)
                    tags_generated = tag_result.get("success", False)

                except Exception:
                    # Log but don't fail the entire operation
                    pass

            # Track commit results
            committed = False

            # Optional: Commit to git
            if request.auto_commit:
                try:
                    git_manager = await self._ensure_git_manager()

                    commit_msg = f"Create document: {request.title}"
                    commit_response = git_manager.commit_changes(message=commit_msg, files=[file_path], push=False)

                    committed = commit_response.get("success", False)

                except Exception:
                    # Log but don't fail the entire operation
                    pass

            # Build response using proper schema
            response = CreateDocumentResponse(
                success=True,
                document_id=document_id,
                path=file_path,
                embeddings_generated=embeddings_generated,
                tags_generated=tags_generated,
                committed=committed,
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
        Update an existing document with optional embedding regeneration

        Args:
            request: Document update request

        Returns:
            UpdateDocumentResponse dict or ErrorResponse dict
        """
        try:
            # Prepare updates dict and track fields
            updates = {}
            fields_updated = []

            if request.title is not None:
                updates["title"] = request.title
                fields_updated.append("title")
            if request.content is not None:
                updates["content"] = request.content
                fields_updated.append("content")
            if request.tags is not None:
                updates["tags"] = request.tags
                fields_updated.append("tags")
            if request.metadata is not None:
                updates["metadata"] = request.metadata
                fields_updated.append("metadata")

            # Update the document
            result = self.document_manager.update_document(
                document_id=request.document_id, document_path=request.path, updates=updates
            )

            if not result["success"]:
                error = ErrorResponse(
                    error=result.get("error", "Failed to update document"),
                    error_code="DOCUMENT_UPDATE_FAILED",
                    details={"document_id": request.document_id, "path": request.path},
                )
                return error.model_dump()

            # Track embeddings regeneration
            embeddings_regenerated = False

            # Optional: Regenerate embeddings if content changed
            if request.regenerate_embeddings and request.content is not None:
                try:
                    processing_manager = await self._ensure_processing_manager()

                    embedding_response = await processing_manager.generate_embeddings(
                        document_id=request.document_id,
                        document_path=request.path,
                        force_regenerate=True,
                    )

                    embeddings_regenerated = embedding_response.get("success", False)
                except Exception:
                    # Log but don't fail the entire operation
                    pass

            # Track commit results
            committed = False

            # Optional: Commit to git
            if request.auto_commit:
                try:
                    git_manager = await self._ensure_git_manager()

                    commit_msg = f"Update document: {request.document_id}"
                    file_path = result.get("file_path", request.path)
                    commit_response = git_manager.commit_changes(message=commit_msg, files=[file_path], push=False)

                    committed = commit_response.get("success", False)

                except Exception:
                    # Log but don't fail the entire operation
                    pass

            # Build response using proper schema
            response = UpdateDocumentResponse(
                success=True,
                document_id=result.get("document_id"),
                path=result.get("file_path"),
                fields_updated=fields_updated,
                embeddings_regenerated=embeddings_regenerated,
                committed=committed,
            )

            return response.model_dump()

        except Exception as e:
            error = ErrorResponse(
                error=f"Failed to update document: {str(e)}",
                error_code="DOCUMENT_UPDATE_EXCEPTION",
                details={"document_id": request.document_id, "path": request.path},
            )
            return error.model_dump()
