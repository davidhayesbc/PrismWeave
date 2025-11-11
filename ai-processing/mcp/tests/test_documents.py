"""
Tests for Document MCP Tools
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from mcp.schemas.requests import CreateDocumentRequest, UpdateDocumentRequest
from mcp.tools.documents import DocumentTools
from src.core.config import Config


@pytest.fixture
def mock_config(tmp_path):
    """Create a mock configuration with temp directory"""
    config = MagicMock(spec=Config)
    test_docs_dir = str(tmp_path / "documents")
    config.documents_dir = test_docs_dir
    # Add mcp.paths for DocumentManager
    config.mcp = MagicMock()
    config.mcp.paths = MagicMock()
    config.mcp.paths.documents_root = test_docs_dir
    # Add required Config attributes
    config.ollama = MagicMock()
    config.processing = MagicMock()
    config.vector = MagicMock()
    return config


@pytest.fixture
def document_tools(mock_config):
    """Create DocumentTools instance"""
    return DocumentTools(mock_config)


@pytest.mark.asyncio
class TestDocumentTools:
    """Test suite for DocumentTools"""

    async def test_create_document_simple_success(self, document_tools):
        """Test simple document creation without auto-processing"""
        document_tools.document_manager.create_document = MagicMock(
            return_value={
                "success": True,
                "document_id": "doc1",
                "file_path": "/test/doc1.md",
                "message": "Created",
            }
        )

        request = CreateDocumentRequest(title="Test Doc", content="Test content", auto_process=False)

        result = await document_tools.create_document(request)

        assert result["success"] is True
        assert result["document_id"] == "doc1"
        assert result["file_path"] == "/test/doc1.md"
        assert result["processing_result"] is None
        assert result["commit_result"] is None

    async def test_create_document_with_metadata(self, document_tools):
        """Test document creation with metadata and tags"""
        document_tools.document_manager.create_document = MagicMock(
            return_value={"success": True, "document_id": "doc1", "file_path": "/test/doc1.md"}
        )

        request = CreateDocumentRequest(
            title="Test Doc",
            content="Test content",
            metadata={"author": "Test User"},
            tags=["python", "ai"],
            category="tech",
        )

        result = await document_tools.create_document(request)

        document_tools.document_manager.create_document.assert_called_once_with(
            title="Test Doc",
            content="Test content",
            metadata={"author": "Test User"},
            tags=["python", "ai"],
            category="tech",
        )

    async def test_create_document_with_auto_process(self, document_tools):
        """Test document creation with auto-processing"""
        document_tools.document_manager.create_document = MagicMock(
            return_value={"success": True, "document_id": "doc1", "file_path": "/test/doc1.md"}
        )

        # Mock processing manager
        mock_processing = AsyncMock()
        mock_processing.generate_embeddings = AsyncMock(return_value={"success": True})
        mock_processing.generate_tags = AsyncMock(return_value={"success": True, "tags": ["auto-tag1", "auto-tag2"]})

        with patch.object(document_tools, "_ensure_processing_manager", return_value=mock_processing):
            request = CreateDocumentRequest(title="Test Doc", content="Test content", auto_process=True)

            result = await document_tools.create_document(request)

            assert result["processing_result"]["embeddings_generated"] is True
            assert result["processing_result"]["tags_generated"] is True
            assert result["processing_result"]["generated_tags"] == ["auto-tag1", "auto-tag2"]

    async def test_create_document_with_auto_commit(self, document_tools):
        """Test document creation with auto-commit"""
        document_tools.document_manager.create_document = MagicMock(
            return_value={"success": True, "document_id": "doc1", "file_path": "/test/doc1.md"}
        )

        # Mock git manager
        mock_git = AsyncMock()
        mock_git.commit_changes = MagicMock(return_value={"success": True, "commit_sha": "abc123", "pushed": False})

        with patch.object(document_tools, "_ensure_git_manager", return_value=mock_git):
            request = CreateDocumentRequest(
                title="Test Doc", content="Test content", auto_commit=True, commit_message="Custom commit"
            )

            result = await document_tools.create_document(request)

            assert result["commit_result"]["committed"] is True
            assert result["commit_result"]["commit_sha"] == "abc123"
            mock_git.commit_changes.assert_called_once_with(
                message="Custom commit", files=["/test/doc1.md"], push=False
            )

    async def test_create_document_with_auto_push(self, document_tools):
        """Test document creation with auto-commit and push"""
        document_tools.document_manager.create_document = MagicMock(
            return_value={"success": True, "document_id": "doc1", "file_path": "/test/doc1.md"}
        )

        mock_git = AsyncMock()
        mock_git.commit_changes = MagicMock(return_value={"success": True, "commit_sha": "abc123", "pushed": True})

        with patch.object(document_tools, "_ensure_git_manager", return_value=mock_git):
            request = CreateDocumentRequest(title="Test Doc", content="Test content", auto_commit=True, auto_push=True)

            result = await document_tools.create_document(request)

            assert result["commit_result"]["pushed"] is True
            mock_git.commit_changes.assert_called_once_with(
                message="Create document: Test Doc", files=["/test/doc1.md"], push=True
            )

    async def test_create_document_processing_error(self, document_tools):
        """Test document creation when processing fails"""
        document_tools.document_manager.create_document = MagicMock(
            return_value={"success": True, "document_id": "doc1", "file_path": "/test/doc1.md"}
        )

        mock_processing = AsyncMock()
        mock_processing.generate_embeddings = AsyncMock(side_effect=Exception("Processing failed"))

        with patch.object(document_tools, "_ensure_processing_manager", return_value=mock_processing):
            request = CreateDocumentRequest(title="Test Doc", content="Test content", auto_process=True)

            result = await document_tools.create_document(request)

            # Should still succeed with error in processing result
            assert result["success"] is True
            assert "error" in result["processing_result"]

    async def test_create_document_creation_failure(self, document_tools):
        """Test document creation failure"""
        document_tools.document_manager.create_document = MagicMock(
            return_value={"success": False, "error": "Creation failed"}
        )

        request = CreateDocumentRequest(title="Test Doc", content="Test content")

        result = await document_tools.create_document(request)

        assert "error_type" in result
        assert result["error_type"] == "CreationError"

    async def test_create_document_exception(self, document_tools):
        """Test document creation exception handling"""
        document_tools.document_manager.create_document = MagicMock(side_effect=Exception("Unexpected error"))

        request = CreateDocumentRequest(title="Test Doc", content="Test content")

        result = await document_tools.create_document(request)

        assert "error_type" in result
        assert result["error_type"] == "CreationError"

    async def test_update_document_simple(self, document_tools):
        """Test simple document update"""
        document_tools.document_manager.update_document = MagicMock(
            return_value={
                "success": True,
                "document_id": "doc1",
                "file_path": "/test/doc1.md",
                "message": "Updated",
            }
        )

        request = UpdateDocumentRequest(document_id="doc1", content="Updated content")

        result = await document_tools.update_document(request)

        assert result["success"] is True
        assert result["document_id"] == "doc1"
        assert result["updates_applied"] == ["content"]
        assert result["embedding_result"] is None

    async def test_update_document_multiple_fields(self, document_tools):
        """Test updating multiple document fields"""
        document_tools.document_manager.update_document = MagicMock(
            return_value={"success": True, "document_id": "doc1", "file_path": "/test/doc1.md"}
        )

        request = UpdateDocumentRequest(
            document_id="doc1",
            title="New Title",
            content="New content",
            tags=["updated", "tags"],
            category="updated-category",
        )

        result = await document_tools.update_document(request)

        assert set(result["updates_applied"]) == {"title", "content", "tags", "category"}

    async def test_update_document_with_regenerate_embeddings(self, document_tools):
        """Test document update with embedding regeneration"""
        document_tools.document_manager.update_document = MagicMock(
            return_value={"success": True, "document_id": "doc1", "file_path": "/test/doc1.md"}
        )

        mock_processing = AsyncMock()
        mock_processing.generate_embeddings = AsyncMock(return_value={"success": True, "embedding_count": 5})

        with patch.object(document_tools, "_ensure_processing_manager", return_value=mock_processing):
            request = UpdateDocumentRequest(document_id="doc1", content="Updated content", regenerate_embeddings=True)

            result = await document_tools.update_document(request)

            assert result["embedding_result"]["regenerated"] is True
            assert result["embedding_result"]["embedding_count"] == 5
            mock_processing.generate_embeddings.assert_called_once_with(
                document_id="doc1", document_path=None, force_regenerate=True
            )

    async def test_update_document_embedding_error(self, document_tools):
        """Test document update when embedding regeneration fails"""
        document_tools.document_manager.update_document = MagicMock(
            return_value={"success": True, "document_id": "doc1", "file_path": "/test/doc1.md"}
        )

        mock_processing = AsyncMock()
        mock_processing.generate_embeddings = AsyncMock(side_effect=Exception("Embedding failed"))

        with patch.object(document_tools, "_ensure_processing_manager", return_value=mock_processing):
            request = UpdateDocumentRequest(document_id="doc1", content="Updated content", regenerate_embeddings=True)

            result = await document_tools.update_document(request)

            # Should still succeed with error in embedding result
            assert result["success"] is True
            assert "error" in result["embedding_result"]

    async def test_update_document_failure(self, document_tools):
        """Test document update failure"""
        document_tools.document_manager.update_document = MagicMock(
            return_value={"success": False, "error": "Update failed"}
        )

        request = UpdateDocumentRequest(document_id="doc1", content="Updated")

        result = await document_tools.update_document(request)

        assert "error_type" in result
        assert result["error_type"] == "UpdateError"

    async def test_update_document_exception(self, document_tools):
        """Test document update exception handling"""
        document_tools.document_manager.update_document = MagicMock(side_effect=Exception("Unexpected error"))

        request = UpdateDocumentRequest(document_id="doc1", content="Updated")

        result = await document_tools.update_document(request)

        assert "error_type" in result
        assert result["error_type"] == "UpdateError"

    async def test_update_document_by_path(self, document_tools):
        """Test updating document by path instead of ID"""
        document_tools.document_manager.update_document = MagicMock(
            return_value={"success": True, "file_path": "/test/doc1.md"}
        )

        request = UpdateDocumentRequest(path="/test/doc1.md", content="Updated content")

        result = await document_tools.update_document(request)

        assert result["success"] is True
        document_tools.document_manager.update_document.assert_called_once_with(
            document_id=None, document_path="/test/doc1.md", updates={"content": "Updated content"}
        )
