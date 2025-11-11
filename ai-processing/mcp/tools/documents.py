"""
Document Creation and Modification MCP Tools

MCP tool implementations for creating and updating documents.
"""

from typing import Any, Dict

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

    async def create_document(self, request: CreateDocumentRequest) -> Dict[str, Any]:
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
                    error_type="CreationError", message=result.get("error", "Failed to create document")
                )
                return error.model_dump()

            document_id = result["document_id"]
            file_path = result["file_path"]

            # Optional: Generate embeddings and tags
            processing_result = None
            if request.auto_process:
                try:
                    processing_manager = await self._ensure_processing_manager()

                    # Generate embeddings
                    embedding_result = await processing_manager.generate_embeddings(
                        document_id=document_id, force_regenerate=False
                    )

                    # Generate tags
                    tag_result = await processing_manager.generate_tags(document_id=document_id)

                    processing_result = {
                        "embeddings_generated": embedding_result.get("success", False),
                        "tags_generated": tag_result.get("success", False),
                        "generated_tags": tag_result.get("tags", []),
                    }
                except Exception as proc_error:
                    # Log but don't fail the entire operation
                    processing_result = {"error": str(proc_error)}

            # Optional: Commit to git
            commit_result = None
            if request.auto_commit:
                try:
                    git_manager = await self._ensure_git_manager()

                    commit_msg = request.commit_message or f"Create document: {request.title}"
                    commit_response = git_manager.commit_changes(
                        message=commit_msg, files=[file_path], push=request.auto_push or False
                    )

                    commit_result = {
                        "committed": commit_response.get("success", False),
                        "commit_sha": commit_response.get("commit_sha"),
                        "pushed": commit_response.get("pushed", False),
                    }
                except Exception as git_error:
                    # Log but don't fail the entire operation
                    commit_result = {"error": str(git_error)}

            # Build response
            response = CreateDocumentResponse(
                success=True,
                document_id=document_id,
                file_path=file_path,
                message=result.get("message", "Document created successfully"),
                processing_result=processing_result,
                commit_result=commit_result,
            )

            return response.model_dump()

        except Exception as e:
            error = ErrorResponse(
                error_type="CreationError",
                message=f"Failed to create document: {str(e)}",
                details={"title": request.title},
            )
            return error.model_dump()

    async def update_document(self, request: UpdateDocumentRequest) -> Dict[str, Any]:
        """
        Update an existing document with optional embedding regeneration

        Args:
            request: Document update request

        Returns:
            UpdateDocumentResponse dict or ErrorResponse dict
        """
        try:
            # Prepare updates dict
            updates = {}
            if request.title is not None:
                updates["title"] = request.title
            if request.content is not None:
                updates["content"] = request.content
            if request.tags is not None:
                updates["tags"] = request.tags
            if request.category is not None:
                updates["category"] = request.category
            if request.metadata is not None:
                updates["metadata"] = request.metadata

            # Update the document
            result = self.document_manager.update_document(
                document_id=request.document_id, document_path=request.path, updates=updates
            )

            if not result["success"]:
                error = ErrorResponse(
                    error_type="UpdateError",
                    message=result.get("error", "Failed to update document"),
                    details={"document_id": request.document_id, "path": request.path},
                )
                return error.model_dump()

            # Optional: Regenerate embeddings if content changed
            embedding_result = None
            if request.regenerate_embeddings and request.content is not None:
                try:
                    processing_manager = await self._ensure_processing_manager()

                    embedding_response = await processing_manager.generate_embeddings(
                        document_id=request.document_id,
                        document_path=request.path,
                        force_regenerate=True,
                    )

                    embedding_result = {
                        "regenerated": embedding_response.get("success", False),
                        "embedding_count": embedding_response.get("embedding_count", 0),
                    }
                except Exception as embed_error:
                    # Log but don't fail the entire operation
                    embedding_result = {"error": str(embed_error)}

            # Build response
            response = UpdateDocumentResponse(
                success=True,
                document_id=result.get("document_id"),
                file_path=result.get("file_path"),
                message=result.get("message", "Document updated successfully"),
                updates_applied=list(updates.keys()),
                embedding_result=embedding_result,
            )

            return response.model_dump()

        except Exception as e:
            error = ErrorResponse(
                error_type="UpdateError",
                message=f"Failed to update document: {str(e)}",
                details={"document_id": request.document_id, "path": request.path},
            )
            return error.model_dump()
