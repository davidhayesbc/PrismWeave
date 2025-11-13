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

            # Perform search using SearchManager
            # SearchManager.search_documents returns tuple: (results, total)
            search_results_list, total_found = self.search_manager.search_documents(
                query=request.query,
                max_results=request.max_results,
                similarity_threshold=request.similarity_threshold,
                filters=None,  # No advanced filtering for now
            )

            # search_results_list is already a list of SearchResult objects with correct schema
            # Convert to response format (schema: query, results, total_results)
            response = SearchDocumentsResponse(
                query=request.query,
                results=search_results_list,
                total_results=total_found,
            )

            return response.model_dump()

        except Exception as e:
            error = ErrorResponse(
                error=f"Search failed: {str(e)}", error_code="SEARCH_FAILED", details={"query": request.query}
            )
            return error.model_dump()

    async def get_document(self, request: GetDocumentRequest) -> dict[str, Any]:
        """
        Get a single document by ID or path

        Args:
            request: Get document request

        Returns:
            GetDocumentResponse dict or ErrorResponse dict
        """
        try:
            # Get document using DocumentManager
            document = self.document_manager.get_document_by_id(request.document_id)

            if not document:
                error = ErrorResponse(
                    error="Document not found",
                    error_code="DOCUMENT_NOT_FOUND",
                    details={"document_id": request.document_id},
                )
                return error.model_dump()

            # Convert to response format
            from prismweave_mcp.schemas.responses import Document, DocumentMetadata

            # Create DocumentMetadata from dict
            doc_metadata = DocumentMetadata(
                title=document.get("title", ""),
                tags=document.get("tags", []),
                category=document.get("category"),
                created_at=document.get("created_at"),
                modified_at=document.get("updated_at"),
                word_count=document.get("metadata", {}).get("word_count"),
                reading_time=document.get("metadata", {}).get("reading_time"),
                source_url=document.get("metadata", {}).get("source_url"),
                author=document.get("metadata", {}).get("author"),
            )

            # Create Document
            doc = Document(
                id=document["id"],
                path=document.get("file_path", ""),
                content=document.get("content", ""),
                metadata=doc_metadata,
                has_embeddings=document.get("has_embeddings", False),
            )

            # GetDocumentResponse schema only has: document
            response = GetDocumentResponse(document=doc)

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
                # Get document ID from additional metadata
                doc_id = doc_metadata.additional.get("id", "") if doc_metadata.additional else ""
                if not doc_id:
                    # Fallback: generate ID from title
                    from prismweave_mcp.utils.document_utils import generate_document_id

                    doc_id = generate_document_id()

                # Create Document object (with empty content for listing - just metadata)
                doc = Document(
                    id=doc_id,
                    path="",  # Path not available in metadata
                    content="",  # Don't load full content for listing
                    metadata=doc_metadata,
                    has_embeddings=False,  # Would need to check embedding store
                )
                doc_list.append(doc)

            # Convert to response format (use total_count from manager)
            response = ListDocumentsResponse(
                documents=doc_list,
                total_count=total_count,
                category=request.category,
            )

            return response.model_dump()

        except Exception as e:
            error = ErrorResponse(
                error=f"Failed to list documents: {str(e)}",
                error_code="DOCUMENT_LIST_FAILED",
                details={"filters": request.model_dump()},
            )
            return error.model_dump()

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
                return error.model_dump()

            # Return metadata directly (no specific schema for this)
            return {"metadata": metadata, "success": True}

        except Exception as e:
            error = ErrorResponse(
                error=f"Failed to get metadata: {str(e)}",
                error_code="METADATA_RETRIEVAL_FAILED",
                details={"document_id": request.document_id},
            )
            return error.model_dump()
