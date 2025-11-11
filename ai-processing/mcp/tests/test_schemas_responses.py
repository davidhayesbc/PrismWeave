"""
Tests for MCP response schemas
"""

from datetime import datetime

import pytest

from mcp.schemas.responses import (
    CommitToGitResponse,
    CreateDocumentResponse,
    Document,
    DocumentMetadata,
    DocumentSummary,
    ErrorResponse,
    GenerateEmbeddingsResponse,
    GenerateTagsResponse,
    GetDocumentResponse,
    ListDocumentsResponse,
    SearchDocumentsResponse,
    SearchResult,
    UpdateDocumentResponse,
)


class TestDocumentMetadata:
    """Tests for DocumentMetadata schema"""

    def test_valid_metadata(self) -> None:
        """Test creating valid metadata"""
        metadata = DocumentMetadata(title="Test Article", tags=["ai", "ml"], category="tech", word_count=1500)

        assert metadata.title == "Test Article"
        assert metadata.tags == ["ai", "ml"]
        assert metadata.category == "tech"
        assert metadata.word_count == 1500

    def test_default_values(self) -> None:
        """Test default values"""
        metadata = DocumentMetadata(title="Test")

        assert metadata.tags == []
        assert metadata.category is None
        assert metadata.created_at is None
        assert metadata.modified_at is None


class TestDocument:
    """Tests for Document schema"""

    def test_valid_document(self) -> None:
        """Test creating a valid document"""
        metadata = DocumentMetadata(title="Test", tags=["test"])
        doc = Document(
            id="doc_123",
            path="generated/test.md",
            content="# Test\n\nContent",
            metadata=metadata,
            has_embeddings=True,
        )

        assert doc.id == "doc_123"
        assert doc.path == "generated/test.md"
        assert doc.content == "# Test\n\nContent"
        assert doc.metadata.title == "Test"
        assert doc.has_embeddings is True


class TestSearchResult:
    """Tests for SearchResult schema"""

    def test_valid_search_result(self) -> None:
        """Test creating a valid search result"""
        result = SearchResult(
            document_id="doc_123",
            path="documents/test.md",
            title="Test Article",
            similarity_score=0.85,
            snippet="This is a test snippet...",
        )

        assert result.document_id == "doc_123"
        assert result.similarity_score == 0.85
        assert result.snippet == "This is a test snippet..."


class TestSearchDocumentsResponse:
    """Tests for SearchDocumentsResponse schema"""

    def test_successful_response(self) -> None:
        """Test creating a successful search response"""
        result = SearchResult(
            document_id="doc_123",
            path="documents/test.md",
            title="Test",
            similarity_score=0.85,
            snippet="Test snippet",
        )

        response = SearchDocumentsResponse(success=True, results=[result], total_found=1, query="test query")

        assert response.success is True
        assert len(response.results) == 1
        assert response.total_found == 1
        assert response.query == "test query"
        assert response.error is None

    def test_error_response(self) -> None:
        """Test creating an error response"""
        response = SearchDocumentsResponse(success=False, results=[], total_found=0, query="test", error="Search failed")

        assert response.success is False
        assert len(response.results) == 0
        assert response.error == "Search failed"


class TestGetDocumentResponse:
    """Tests for GetDocumentResponse schema"""

    def test_successful_response(self) -> None:
        """Test creating a successful get document response"""
        metadata = DocumentMetadata(title="Test")
        doc = Document(id="doc_123", path="test.md", content="Content", metadata=metadata)

        response = GetDocumentResponse(success=True, document=doc)

        assert response.success is True
        assert response.document is not None
        assert response.document.id == "doc_123"
        assert response.error is None


class TestListDocumentsResponse:
    """Tests for ListDocumentsResponse schema"""

    def test_successful_response(self) -> None:
        """Test creating a successful list response"""
        doc_summary = DocumentSummary(
            id="doc_123", path="test.md", title="Test", size_bytes=1024, tags=["test"], category="tech"
        )

        response = ListDocumentsResponse(
            success=True, documents=[doc_summary], total_count=1, offset=0, limit=100
        )

        assert response.success is True
        assert len(response.documents) == 1
        assert response.total_count == 1
        assert response.offset == 0
        assert response.limit == 100


class TestCreateDocumentResponse:
    """Tests for CreateDocumentResponse schema"""

    def test_successful_response(self) -> None:
        """Test creating a successful create response"""
        response = CreateDocumentResponse(
            success=True,
            document_id="doc_123",
            path="generated/test.md",
            embeddings_generated=True,
            tags_generated=True,
            committed=False,
        )

        assert response.success is True
        assert response.document_id == "doc_123"
        assert response.path == "generated/test.md"
        assert response.embeddings_generated is True
        assert response.tags_generated is True
        assert response.committed is False


class TestUpdateDocumentResponse:
    """Tests for UpdateDocumentResponse schema"""

    def test_successful_response(self) -> None:
        """Test creating a successful update response"""
        response = UpdateDocumentResponse(
            success=True,
            document_id="doc_123",
            path="test.md",
            fields_updated=["content", "tags"],
            embeddings_regenerated=True,
            committed=False,
        )

        assert response.success is True
        assert response.fields_updated == ["content", "tags"]
        assert response.embeddings_regenerated is True


class TestGenerateEmbeddingsResponse:
    """Tests for GenerateEmbeddingsResponse schema"""

    def test_successful_response(self) -> None:
        """Test creating a successful embeddings response"""
        response = GenerateEmbeddingsResponse(
            success=True,
            document_id="doc_123",
            path="test.md",
            embeddings_count=15,
            chunks_processed=15,
            execution_time_ms=1250.5,
        )

        assert response.success is True
        assert response.embeddings_count == 15
        assert response.chunks_processed == 15
        assert response.execution_time_ms == 1250.5


class TestGenerateTagsResponse:
    """Tests for GenerateTagsResponse schema"""

    def test_successful_response(self) -> None:
        """Test creating a successful tags response"""
        response = GenerateTagsResponse(
            success=True,
            document_id="doc_123",
            path="test.md",
            tags=["ai", "ml", "python"],
            merged=True,
            execution_time_ms=850.2,
        )

        assert response.success is True
        assert len(response.tags) == 3
        assert response.merged is True


class TestCommitToGitResponse:
    """Tests for CommitToGitResponse schema"""

    def test_successful_response(self) -> None:
        """Test creating a successful commit response"""
        response = CommitToGitResponse(
            success=True, commit_hash="abc123", files_committed=1, pushed=False, branch="main"
        )

        assert response.success is True
        assert response.commit_hash == "abc123"
        assert response.files_committed == 1
        assert response.pushed is False
        assert response.branch == "main"


class TestErrorResponse:
    """Tests for ErrorResponse schema"""

    def test_error_response(self) -> None:
        """Test creating an error response"""
        response = ErrorResponse(error="Document not found", error_code="DOCUMENT_NOT_FOUND")

        assert response.success is False
        assert response.error == "Document not found"
        assert response.error_code == "DOCUMENT_NOT_FOUND"
