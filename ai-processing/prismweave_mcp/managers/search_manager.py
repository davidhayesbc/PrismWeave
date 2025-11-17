"""
Search Manager for MCP Server

Handles semantic search operations using ChromaDB and the existing EmbeddingStore.
Provides filtering, ranking, and snippet generation for search results.
"""

import contextlib
from datetime import datetime
from pathlib import Path
from typing import Optional

from haystack import Document as HaystackDocument

from prismweave_mcp.schemas.responses import DocumentMetadata, SearchResult
from prismweave_mcp.utils.path_utils import get_document_category, get_documents_root, is_generated_document
from src.core.config import Config
from src.core.embedding_store import EmbeddingStore


class SearchManager:
    """Manage semantic search operations"""

    def __init__(self, config: Config, embedding_store: Optional[EmbeddingStore] = None):
        """
        Initialize Search Manager

        Args:
            config: Application configuration
            embedding_store: Optional pre-initialized EmbeddingStore (creates new if not provided)
        """
        self.config = config
        self.docs_root = get_documents_root(config.mcp.paths.documents_root)

        # Use provided embedding store or create new one
        if embedding_store is not None:
            self.embedding_store = embedding_store
        else:
            self.embedding_store = EmbeddingStore(config)

    async def initialize(self) -> None:
        """
        Initialize search manager (async for future compatibility)

        Currently no async initialization needed, but keeping for consistency
        """
        # Verify embedding store is working
        status = self.embedding_store.verify_embeddings()
        if status["status"] != "success":
            raise RuntimeError(f"Embedding store verification failed: {status.get('error')}")

    def search_documents(
        self,
        query: str,
        max_results: Optional[int] = None,
        similarity_threshold: Optional[float] = None,
        filters: Optional[dict] = None,
    ) -> tuple[list[SearchResult], int]:
        """
        Search documents semantically with filtering

        Args:
            query: Search query text
            max_results: Maximum results to return (default: from config)
            similarity_threshold: Minimum similarity score (default: from config)
            filters: Optional filters dictionary with keys:
                - tags: List of tags (documents must have all)
                - category: Category name
                - generated: True/False to filter by generated status
                - date_from: Minimum date (ISO format)
                - date_to: Maximum date (ISO format)

        Returns:
            Tuple of (list of SearchResult objects, total matches before limit)
        """
        # Use config defaults if not provided
        if max_results is None:
            max_results = self.config.mcp.search.max_results

        if similarity_threshold is None:
            similarity_threshold = self.config.mcp.search.similarity_threshold

        # Perform semantic search
        results_with_scores = self.embedding_store.search_similar_with_scores(query, k=max_results * 2)

        # Filter and process results
        search_results = []
        seen_documents = set()  # Track unique documents

        for haystack_doc, score in results_with_scores:
            # Check similarity threshold
            if score < similarity_threshold:
                continue

            # Get source file path
            source_file = haystack_doc.meta.get("source_file") or haystack_doc.meta.get("file_path")
            if not source_file:
                continue

            source_path = Path(source_file)

            # Skip if we've already seen this document
            if source_path in seen_documents:
                continue

            # Apply filters
            if filters and not self._apply_filters(source_path, haystack_doc, filters):
                continue

            # Build search result
            try:
                search_result = self._build_search_result(source_path, haystack_doc, score, query)
                search_results.append(search_result)
                seen_documents.add(source_path)
            except Exception:
                # Skip documents that can't be processed
                continue

            # Check if we have enough results
            if len(search_results) >= max_results:
                break

        total_matches = len(search_results)

        return search_results, total_matches

    def _apply_filters(self, source_path: Path, haystack_doc: HaystackDocument, filters: dict) -> bool:
        """
        Apply filters to a search result

        Args:
            source_path: Path to source document
            haystack_doc: Haystack document with metadata
            filters: Filters dictionary

        Returns:
            True if document passes all filters, False otherwise
        """
        # Filter by tags
        if "tags" in filters and filters["tags"]:
            doc_tags = haystack_doc.meta.get("tags", "")
            if isinstance(doc_tags, str):
                doc_tags = [t.strip() for t in doc_tags.split(",")]
            elif not isinstance(doc_tags, list):
                doc_tags = []

            required_tags = filters["tags"]
            if not all(tag in doc_tags for tag in required_tags):
                return False

        # Filter by category
        if "category" in filters and filters["category"]:
            doc_category = get_document_category(source_path, self.docs_root)
            if doc_category != filters["category"]:
                return False

        # Filter by generated status
        if "generated" in filters:
            is_gen = is_generated_document(source_path, self.docs_root)
            if is_gen != filters["generated"]:
                return False

        # Filter by date range
        if "date_from" in filters or "date_to" in filters:
            # Try to get date from metadata
            created_date_str = haystack_doc.meta.get("created_date")
            if created_date_str:
                try:
                    doc_date = datetime.fromisoformat(created_date_str)

                    if "date_from" in filters:
                        from_date = datetime.fromisoformat(filters["date_from"])
                        if doc_date < from_date:
                            return False

                    if "date_to" in filters:
                        to_date = datetime.fromisoformat(filters["date_to"])
                        if doc_date > to_date:
                            return False

                except (ValueError, TypeError):
                    # If date parsing fails, skip date filtering for this doc
                    pass

        return True

    def _build_search_result(
        self, source_path: Path, haystack_doc: HaystackDocument, score: float, query: str
    ) -> SearchResult:
        """
        Build a SearchResult object from Haystack document

        Args:
            source_path: Path to source document
            haystack_doc: Haystack document chunk
            score: Similarity score
            query: Original search query

        Returns:
            SearchResult object
        """
        # Get document metadata
        metadata = haystack_doc.meta

        # Get relative path
        try:
            relative_path = source_path.relative_to(self.docs_root)
        except ValueError:
            relative_path = source_path

        # Parse title
        title = metadata.get("title", source_path.stem)

        # Generate snippet from content
        snippet = self._generate_snippet(haystack_doc.content, query)

        # Build DocumentMetadata if we have enough info
        doc_metadata = None
        try:
            # Get or parse tags
            tags = metadata.get("tags", [])
            if isinstance(tags, str):
                tags = [t.strip() for t in tags.split(",") if t.strip()]

            # Get category
            category = get_document_category(source_path, self.docs_root)

            # Parse dates if available
            created_at = None
            if "created_date" in metadata:
                with contextlib.suppress(ValueError, TypeError):
                    created_at = datetime.fromisoformat(metadata["created_date"])
                    pass
            modified_at = None
            if "modified_date" in metadata:
                with contextlib.suppress(ValueError, TypeError):
                    modified_at = datetime.fromisoformat(metadata["modified_date"])
                    pass

            doc_metadata = DocumentMetadata(
                title=title,
                tags=tags,
                category=category,
                created_at=created_at,
                modified_at=modified_at,
                word_count=metadata.get("word_count"),
                reading_time=metadata.get("reading_time"),
                source_url=metadata.get("source_url"),
                author=metadata.get("author"),
            )
        except Exception:
            # If metadata construction fails, continue without it
            pass

        return SearchResult(
            document_id=metadata.get("id") or metadata.get("document_id", f"chunk_{haystack_doc.id}"),
            path=str(relative_path),
            score=score,
            excerpt=snippet,
            title=title,
            metadata=doc_metadata,
        )

    def _generate_snippet(self, content: Optional[str], query: str, max_length: int = 200) -> str:
        """
        Generate a snippet from content centered around query terms

        Args:
            content: Full content text (may be None)
            query: Search query
            max_length: Maximum snippet length

        Returns:
            Snippet string with context around query terms
        """
        if not content:
            return ""

        # Clean content
        content = content.strip()

        # If content is short enough, return it all
        if len(content) <= max_length:
            return content

        # Try to find query terms in content
        query_lower = query.lower()
        content_lower = content.lower()

        # Find best position (where query appears)
        query_pos = content_lower.find(query_lower)

        if query_pos == -1:
            # Query not found exactly, take from beginning
            snippet = content[:max_length]
        else:
            # Center snippet around query
            start = max(0, query_pos - max_length // 2)
            end = min(len(content), start + max_length)

            # Adjust start if we're at the end
            if end - start < max_length:
                start = max(0, end - max_length)

            snippet = content[start:end]

            # Add ellipsis if needed
            if start > 0:
                snippet = "..." + snippet
            if end < len(content):
                snippet = snippet + "..."

        return snippet.strip()

    def get_search_stats(self) -> dict:
        """
        Get statistics about the search index

        Returns:
            Dictionary with search statistics
        """
        status = self.embedding_store.verify_embeddings()

        return {
            "total_chunks": status.get("document_count", 0),
            "unique_documents": len(self.embedding_store.get_unique_source_files()),
            "collection_name": status.get("collection_name"),
            "search_functional": status.get("search_functional"),
            "persist_directory": status.get("persist_directory"),
        }
