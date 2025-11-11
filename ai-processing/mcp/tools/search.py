"""
Search and Retrieval MCP Tools

MCP tool implementations for searching and retrieving documents.
"""

from typing import Any

from mcp.managers.document_manager import DocumentManager
from mcp.managers.search_manager import SearchManager
from mcp.schemas.requests import GetDocumentRequest, ListDocumentsRequest, SearchDocumentsRequest
from mcp.schemas.responses import (
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

            # Extract filters from generic filters dict
            filters = request.filters or {}
            tag_filter = filters.get("tags")
            date_filter = filters.get("date_range")
            generated_only = filters.get("generated_only", False)
            category_filter = filters.get("category")

            # Perform search using SearchManager
            results = await self.search_manager.search_documents(
                query=request.query,
                max_results=request.max_results,
                similarity_threshold=request.similarity_threshold,
                tag_filter=tag_filter,
                date_filter=date_filter,
                generated_only=generated_only,
                category_filter=category_filter,
            )

            # Convert results to SearchResult objects
            from mcp.schemas.responses import SearchResult

            search_results = []
            for result in results["results"]:
                search_result = SearchResult(
                    document_id=result.get("document_id", ""),
                    path=result.get("path", ""),
                    title=result.get("title", ""),
                    similarity_score=result.get("score", result.get("similarity_score", 0.0)),
                    snippet=result.get("snippet", ""),
                    metadata=result.get("metadata"),
                    content=result.get("content"),
                )
                search_results.append(search_result)

            # Convert to response format
            response = SearchDocumentsResponse(
                success=True,
                results=search_results,
                total_found=results["total_results"],
                query=request.query,
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
            if request.document_id:
                document = self.document_manager.get_document_by_id(request.document_id)
            elif request.path:
                document = self.document_manager.get_document_by_path(request.path)
            else:
                raise ValueError("Either document_id or path must be provided")

            if not document:
                error = ErrorResponse(
                    error="Document not found",
                    error_code="DOCUMENT_NOT_FOUND",
                    details={"document_id": request.document_id, "path": request.path},
                )
                return error.model_dump()

            # Convert to response format
            from mcp.schemas.responses import Document, DocumentMetadata

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

            response = GetDocumentResponse(success=True, document=doc)

            return response.model_dump()

        except Exception as e:
            error = ErrorResponse(
                error=f"Failed to get document: {str(e)}",
                error_code="DOCUMENT_RETRIEVAL_FAILED",
                details={"document_id": request.document_id, "path": request.path},
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
            # List documents using DocumentManager
            # Note: DocumentManager has different parameters, so we pass what's compatible
            documents = self.document_manager.list_documents(
                tag_filter=None,  # Schema uses directory/pattern, not tag_filter
                category_filter=None,
                generated_only=False,
                sort_by=request.sort_by,
                sort_order=request.sort_order,
                limit=request.limit,
            )

            # Filter by directory/pattern if provided (client-side filtering)
            if request.directory:
                documents = [doc for doc in documents if request.directory in doc.get("file_path", "")]
            if request.pattern:
                import fnmatch

                documents = [
                    doc for doc in documents if fnmatch.fnmatch(doc.get("file_path", ""), f"*{request.pattern}*")
                ]

            # Apply pagination offset
            if request.offset > 0:
                documents = documents[request.offset :]

            # Convert to DocumentSummary objects
            from mcp.schemas.responses import DocumentSummary

            doc_summaries = []
            for doc in documents:
                doc_summary = DocumentSummary(
                    id=doc.get("id", ""),
                    path=doc.get("file_path", ""),
                    title=doc.get("title", ""),
                    size_bytes=doc.get("size_bytes", 0),
                    modified_at=doc.get("modified_at"),
                    tags=doc.get("tags", []),
                    category=doc.get("category"),
                )
                doc_summaries.append(doc_summary)

            # Convert to response format
            response = ListDocumentsResponse(
                success=True,
                documents=doc_summaries,
                total_count=len(doc_summaries),
                offset=request.offset,
                limit=request.limit,
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
            # Get metadata using DocumentManager
            if request.document_id:
                metadata = self.document_manager.get_document_metadata(document_id=request.document_id)
            elif request.path:
                metadata = self.document_manager.get_document_metadata(document_path=request.path)
            else:
                raise ValueError("Either document_id or path must be provided")

            if not metadata:
                error = ErrorResponse(
                    error="Document not found",
                    error_code="DOCUMENT_NOT_FOUND",
                    details={"document_id": request.document_id, "path": request.path},
                )
                return error.model_dump()

            # Return metadata directly (no specific schema for this)
            return {"metadata": metadata, "success": True}

        except Exception as e:
            error = ErrorResponse(
                error=f"Failed to get metadata: {str(e)}",
                error_code="METADATA_RETRIEVAL_FAILED",
                details={"document_id": request.document_id, "path": request.path},
            )
            return error.model_dump()
