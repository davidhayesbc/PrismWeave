"""
Search and Retrieval MCP Tools

MCP tool implementations for searching and retrieving documents.
"""

from typing import Any

from prismweave_mcp.managers.document_manager import DocumentManager
from prismweave_mcp.managers.search_manager import SearchManager
from prismweave_mcp.schemas.requests import GetDocumentRequest, ListDocumentsRequest, SearchDocumentsRequest
from prismweave_mcp.schemas.responses import (
    ErrorResponse,
    GetDocumentResponse,
    ListDocumentsResponse,
    SearchDocumentsResponse,
)
from src.core.config import Config


class SearchTools:
    """MCP tools for search and document retrieval operations"""

    def __init__(self, config: Config):
        """
        Initialize search tools

        Args:
            config: Configuration object
        """
        self.config = config
        self.document_manager = DocumentManager(config)
        self.search_manager: SearchManager | None = None
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize the search manager (requires async setup for ChromaDB)"""
        if not self._initialized:
            self.search_manager = SearchManager(config=self.config)
            await self.search_manager.initialize()
            # Update document manager with embedding store for efficient lookups
            if self.search_manager.embedding_store:
                self.document_manager.embedding_store = self.search_manager.embedding_store
            self._initialized = True

    async def search_documents(self, request: SearchDocumentsRequest) -> dict[str, Any]:
        """
        Search documents using semantic search

        Args:
            request: Search request with query and filters

        Returns:
            SearchDocumentsResponse dict or ErrorResponse dict
        """
        try:
            if not self._initialized or not self.search_manager:
                await self.initialize()

            # Build filters dictionary from request parameters
            filters = {}
            if request.tags:
                filters["tags"] = request.tags
            if request.category:
                filters["category"] = request.category
            if request.generated_only:
                filters["generated"] = True

            # Perform search using SearchManager
            # SearchManager.search_documents returns tuple: (results, total)
            search_results_list, total_found = self.search_manager.search_documents(
                query=request.query,
                max_results=request.max_results,
                similarity_threshold=request.similarity_threshold,
                filters=filters if filters else None,
            )

            # search_results_list is already a list of SearchResult objects with correct schema
            # Convert to response format (schema: query, results, total_results)
            response = SearchDocumentsResponse(
                query=request.query,
                results=search_results_list,
                total_results=total_found,
            )

            return response.model_dump(mode="json")

        except (ValueError, RuntimeError, KeyError) as e:
            error = ErrorResponse(
                error=f"Search failed: {str(e)}", error_code="SEARCH_FAILED", details={"query": request.query}
            )
            return error.model_dump(mode="json")
        except Exception as e:
            error = ErrorResponse(
                error=f"Unexpected search error: {str(e)}", error_code="SEARCH_ERROR", details={"query": request.query}
            )
            return error.model_dump(mode="json")

    async def get_document(self, request: GetDocumentRequest) -> dict[str, Any]:
        """
        Retrieve a specific document by ID or path

        Args:
            request: Document retrieval request

        Returns:
            GetDocumentResponse dict or ErrorResponse dict
        """
        try:
            if not self._initialized:
                await self.initialize()

            # Get document by ID (most efficient)
            if request.document_id:
                document = self.document_manager.get_document_by_id(request.document_id)
                if not document:
                    error = ErrorResponse(
                        error="Document not found",
                        error_code="DOCUMENT_NOT_FOUND",
                        details={"document_id": request.document_id},
                    )
                    return error.model_dump()

            # Get by path if provided instead of ID
            elif request.path:
                try:
                    document = self.document_manager.get_document_by_path(request.path)
                    if not document:
                        error = ErrorResponse(
                            error="Document not found",
                            error_code="DOCUMENT_NOT_FOUND",
                            details={"path": request.path},
                        )
                        return error.model_dump()
                except ValueError:
                    error = ErrorResponse(
                        error="Document not found",
                        error_code="DOCUMENT_NOT_FOUND",
                        details={"path": request.path},
                    )
                    return error.model_dump()
            else:
                error = ErrorResponse(
                    error="Either document_id or path must be provided",
                    error_code="INVALID_REQUEST",
                    details={},
                )
                return error.model_dump()

            # Respect include_content flag
            if not request.include_content:
                document = document.model_copy(update={"content": ""})

            response = GetDocumentResponse(document=document)
            return response.model_dump()

        except Exception as e:
            error = ErrorResponse(
                error=f"Failed to get document: {str(e)}",
                error_code="DOCUMENT_RETRIEVAL_FAILED",
                details={"document_id": request.document_id},
            )
            return error.model_dump()

    async def list_documents(self, request: ListDocumentsRequest) -> dict[str, Any]:
        """
        List documents with optional filtering and sorting

        Args:
            request: List documents request

        Returns:
            ListDocumentsResponse dict or ErrorResponse dict
        """
        try:
            # List documents using DocumentManager (returns tuple: documents, total_count)
            # Calculate limit to fetch enough for offset pagination
            fetch_limit = request.limit + request.offset if request.limit else None

            documents, total_count = self.document_manager.list_documents(
                tags=request.tags,
                category=request.category,
                generated_only=False,
                sort_by="modified_at",  # Default sort
                sort_order="desc",
                limit=fetch_limit,
            )

            # Apply pagination offset
            if request.offset > 0:
                documents = documents[request.offset :]

            # Trim to limit
            if request.limit:
                documents = documents[: request.limit]

            # Convert DocumentMetadata objects to Document objects (without full content for efficiency)
            from prismweave_mcp.schemas.responses import Document

            doc_list = []
            for doc_metadata in documents:
                doc_id = ""
                doc_path = ""

                if doc_metadata.additional:
                    doc_id = doc_metadata.additional.get("id", "")
                    doc_path = doc_metadata.additional.get("path", "")

                if not doc_id:
                    from prismweave_mcp.utils.document_utils import generate_document_id

                    doc_id = generate_document_id()

                doc = Document(
                    id=doc_id,
                    path=doc_path,
                    content="",
                    metadata=doc_metadata,
                    has_embeddings=False,
                )
                doc_list.append(doc)

            # Convert to response format (use total_count from manager)
            response = ListDocumentsResponse(
                documents=doc_list,
                total_count=total_count,
                category=request.category,
            )

            return response.model_dump(mode="json")

        except Exception as e:
            error = ErrorResponse(
                error=f"Failed to list documents: {str(e)}",
                error_code="DOCUMENT_LIST_FAILED",
                details={"filters": request.model_dump()},
            )
            return error.model_dump(mode="json")

    async def get_document_metadata(self, request: GetDocumentRequest) -> dict[str, Any]:
        """
        Get document metadata only (no content)

        Args:
            request: Get document request

        Returns:
            Dict with metadata or ErrorResponse dict
        """
        try:
            # Get metadata using DocumentManager (schema only has document_id, no path)
            metadata = self.document_manager.get_document_metadata(document_id=request.document_id)

            if not metadata:
                error = ErrorResponse(
                    error="Document not found",
                    error_code="DOCUMENT_NOT_FOUND",
                    details={"document_id": request.document_id},
                )
                return error.model_dump(mode="json")

            # Return metadata directly - convert to dict properly
            # metadata is a DocumentMetadata Pydantic model, convert using model_dump(mode='json')
            metadata_dict = metadata.model_dump(mode="json") if hasattr(metadata, "model_dump") else metadata
            return {"metadata": metadata_dict, "success": True}

        except Exception as e:
            error = ErrorResponse(
                error=f"Failed to get metadata: {str(e)}",
                error_code="METADATA_RETRIEVAL_FAILED",
                details={"document_id": request.document_id},
            )
            return error.model_dump(mode="json")
