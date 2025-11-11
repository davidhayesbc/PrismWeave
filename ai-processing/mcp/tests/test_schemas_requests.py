"""
Tests for MCP request schemas
"""

import pytest
from pydantic import ValidationError

from mcp.schemas.requests import (
    CommitToGitRequest,
    CreateDocumentRequest,
    GenerateEmbeddingsRequest,
    GenerateTagsRequest,
    GetDocumentMetadataRequest,
    GetDocumentRequest,
    ListDocumentsRequest,
    SearchDocumentsRequest,
    UpdateDocumentRequest,
)


class TestSearchDocumentsRequest:
    """Tests for SearchDocumentsRequest schema"""

    def test_valid_request(self) -> None:
        """Test creating a valid search request"""
        request = SearchDocumentsRequest(query="machine learning", max_results=10, similarity_threshold=0.7)

        assert request.query == "machine learning"
        assert request.max_results == 10
        assert request.similarity_threshold == 0.7
        assert request.include_content is True

    def test_default_values(self) -> None:
        """Test default values"""
        request = SearchDocumentsRequest(query="test")

        assert request.max_results == 20
        assert request.similarity_threshold == 0.6
        assert request.filters is None
        assert request.include_content is True

    def test_invalid_max_results(self) -> None:
        """Test validation of max_results"""
        with pytest.raises(ValidationError):
            SearchDocumentsRequest(query="test", max_results=0)

        with pytest.raises(ValidationError):
            SearchDocumentsRequest(query="test", max_results=101)

    def test_invalid_similarity_threshold(self) -> None:
        """Test validation of similarity_threshold"""
        with pytest.raises(ValidationError):
            SearchDocumentsRequest(query="test", similarity_threshold=-0.1)

        with pytest.raises(ValidationError):
            SearchDocumentsRequest(query="test", similarity_threshold=1.1)


class TestGetDocumentRequest:
    """Tests for GetDocumentRequest schema"""

    def test_valid_with_document_id(self) -> None:
        """Test creating request with document_id"""
        request = GetDocumentRequest(document_id="doc_123")
        assert request.document_id == "doc_123"
        assert request.path is None

    def test_valid_with_path(self) -> None:
        """Test creating request with path"""
        request = GetDocumentRequest(path="documents/test.md")
        assert request.path == "documents/test.md"
        assert request.document_id is None

    def test_missing_both_identifiers(self) -> None:
        """Test validation when neither document_id nor path provided"""
        with pytest.raises(ValueError, match="Either document_id or path must be provided"):
            GetDocumentRequest()


class TestListDocumentsRequest:
    """Tests for ListDocumentsRequest schema"""

    def test_valid_request(self) -> None:
        """Test creating a valid list request"""
        request = ListDocumentsRequest(directory="generated", limit=50, sort_by="date")

        assert request.directory == "generated"
        assert request.limit == 50
        assert request.sort_by == "date"

    def test_default_values(self) -> None:
        """Test default values"""
        request = ListDocumentsRequest()

        assert request.directory is None
        assert request.pattern is None
        assert request.limit == 100
        assert request.offset == 0
        assert request.sort_by == "date"
        assert request.sort_order == "desc"

    def test_invalid_sort_by(self) -> None:
        """Test validation of sort_by field"""
        with pytest.raises(ValidationError):
            ListDocumentsRequest(sort_by="invalid_field")

    def test_invalid_sort_order(self) -> None:
        """Test validation of sort_order field"""
        with pytest.raises(ValidationError):
            ListDocumentsRequest(sort_order="invalid_order")


class TestCreateDocumentRequest:
    """Tests for CreateDocumentRequest schema"""

    def test_valid_request(self) -> None:
        """Test creating a valid document creation request"""
        request = CreateDocumentRequest(
            title="Test Article", content="# Test\n\nContent here", tags=["ai", "ml"], category="tech"
        )

        assert request.title == "Test Article"
        assert request.content == "# Test\n\nContent here"
        assert request.tags == ["ai", "ml"]
        assert request.category == "tech"

    def test_default_values(self) -> None:
        """Test default values"""
        request = CreateDocumentRequest(title="Test", content="Content")

        assert request.tags == []
        assert request.category is None
        assert request.auto_process is True
        assert request.auto_commit is False
        assert request.filename is None

    def test_tag_normalization(self) -> None:
        """Test that tags are normalized (lowercase, trimmed)"""
        request = CreateDocumentRequest(title="Test", content="Content", tags=["  AI  ", "Machine Learning", "Python"])

        assert "ai" in request.tags
        assert "machine learning" in request.tags
        assert "python" in request.tags

    def test_empty_title_validation(self) -> None:
        """Test validation of empty title"""
        with pytest.raises(ValidationError):
            CreateDocumentRequest(title="", content="Content")


class TestUpdateDocumentRequest:
    """Tests for UpdateDocumentRequest schema"""

    def test_valid_request(self) -> None:
        """Test creating a valid update request"""
        request = UpdateDocumentRequest(path="generated/test.md", content="New content", tags=["updated"])

        assert request.path == "generated/test.md"
        assert request.content == "New content"
        assert request.tags == ["updated"]

    def test_missing_identifier(self) -> None:
        """Test validation when no identifier provided"""
        with pytest.raises(ValueError, match="Either document_id or path must be provided"):
            UpdateDocumentRequest(content="New content")

    def test_missing_update_fields(self) -> None:
        """Test validation when no fields to update"""
        with pytest.raises(ValueError, match="At least one field to update must be provided"):
            UpdateDocumentRequest(path="test.md")


class TestGenerateEmbeddingsRequest:
    """Tests for GenerateEmbeddingsRequest schema"""

    def test_valid_request(self) -> None:
        """Test creating a valid embeddings request"""
        request = GenerateEmbeddingsRequest(path="documents/test.md", force_regenerate=True)

        assert request.path == "documents/test.md"
        assert request.force_regenerate is True

    def test_missing_identifier(self) -> None:
        """Test validation when no identifier provided"""
        with pytest.raises(ValueError, match="Either document_id or path must be provided"):
            GenerateEmbeddingsRequest()


class TestGenerateTagsRequest:
    """Tests for GenerateTagsRequest schema"""

    def test_valid_request(self) -> None:
        """Test creating a valid tags request"""
        request = GenerateTagsRequest(path="documents/test.md", max_tags=10, merge_with_existing=False)

        assert request.path == "documents/test.md"
        assert request.max_tags == 10
        assert request.merge_with_existing is False

    def test_default_values(self) -> None:
        """Test default values"""
        request = GenerateTagsRequest(document_id="doc_123")

        assert request.max_tags == 5
        assert request.merge_with_existing is True

    def test_max_tags_validation(self) -> None:
        """Test validation of max_tags"""
        with pytest.raises(ValidationError):
            GenerateTagsRequest(path="test.md", max_tags=0)

        with pytest.raises(ValidationError):
            GenerateTagsRequest(path="test.md", max_tags=21)


class TestCommitToGitRequest:
    """Tests for CommitToGitRequest schema"""

    def test_valid_request(self) -> None:
        """Test creating a valid git commit request"""
        request = CommitToGitRequest(message="Add new document", paths=["generated/test.md"], push=True)

        assert request.message == "Add new document"
        assert request.paths == ["generated/test.md"]
        assert request.push is True

    def test_default_values(self) -> None:
        """Test default values"""
        request = CommitToGitRequest(message="Test commit")

        assert request.paths is None
        assert request.push is False
        assert request.branch is None

    def test_empty_message_validation(self) -> None:
        """Test validation of empty commit message"""
        with pytest.raises(ValidationError):
            CommitToGitRequest(message="")
