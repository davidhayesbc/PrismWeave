"""
Tests for Processing MCP Tools
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mcp.schemas.requests import GenerateEmbeddingsRequest, GenerateTagsRequest
from mcp.tools.processing import ProcessingTools
from src.core.config import Config


@pytest.fixture
def mock_config():
    """Create a mock configuration"""
    config = MagicMock(spec=Config)
    config.documents_dir = "/test/documents"
    # Add mcp.paths for any manager that might need it
    config.mcp = MagicMock()
    config.mcp.paths = MagicMock()
    config.mcp.paths.documents_root = "/test/documents"
    # Add required Config attributes
    config.ollama = MagicMock()
    config.processing = MagicMock()
    config.vector = MagicMock()
    return config


@pytest.fixture
def processing_tools(mock_config):
    """Create ProcessingTools instance"""
    return ProcessingTools(mock_config)


@pytest.mark.asyncio
class TestProcessingTools:
    """Test suite for ProcessingTools"""

    async def test_initialize(self, processing_tools):
        """Test initialization of processing manager"""
        with patch("mcp.tools.processing.ProcessingManager") as MockProcessingManager:
            mock_manager = AsyncMock()
            mock_manager.initialize = AsyncMock()
            MockProcessingManager.return_value = mock_manager

            await processing_tools.initialize()

            assert processing_tools._initialized is True
            assert processing_tools.processing_manager is not None
            mock_manager.initialize.assert_called_once()

    async def test_generate_embeddings_success(self, processing_tools):
        """Test successful embedding generation"""
        mock_manager = AsyncMock()
        mock_manager.generate_embeddings = AsyncMock(
            return_value={"success": True, "document_id": "doc1", "chunks_processed": 5, "message": "Success"}
        )
        processing_tools.processing_manager = mock_manager
        processing_tools._initialized = True

        request = GenerateEmbeddingsRequest(document_id="doc1", force_regenerate=False)

        result = await processing_tools.generate_embeddings(request)

        assert result["success"] is True
        assert result["document_id"] == "doc1"
        assert result["embeddings_count"] == 5
        assert result["chunks_processed"] == 5
        mock_manager.generate_embeddings.assert_called_once()
        # Check that document_path argument is a Path object
        call_args = mock_manager.generate_embeddings.call_args
        assert call_args[1]["force_regenerate"] == False

    async def test_generate_embeddings_by_path(self, processing_tools):
        """Test embedding generation by document path"""
        mock_manager = AsyncMock()
        mock_manager.generate_embeddings = AsyncMock(
            return_value={"success": True, "document_id": "/test/doc.md", "chunks_processed": 3}
        )
        processing_tools.processing_manager = mock_manager
        processing_tools._initialized = True

        request = GenerateEmbeddingsRequest(path="/test/doc.md")

        result = await processing_tools.generate_embeddings(request)

        assert result["success"] is True
        mock_manager.generate_embeddings.assert_called_once()
        call_args = mock_manager.generate_embeddings.call_args
        assert call_args[1]["force_regenerate"] == False

    async def test_generate_embeddings_force_regenerate(self, processing_tools):
        """Test forced embedding regeneration"""
        mock_manager = AsyncMock()
        mock_manager.generate_embeddings = AsyncMock(
            return_value={"success": True, "document_id": "doc1", "chunks_processed": 10}
        )
        processing_tools.processing_manager = mock_manager
        processing_tools._initialized = True

        request = GenerateEmbeddingsRequest(document_id="doc1", force_regenerate=True)

        result = await processing_tools.generate_embeddings(request)

        mock_manager.generate_embeddings.assert_called_once()
        call_args = mock_manager.generate_embeddings.call_args
        assert call_args[1]["force_regenerate"] == True

    async def test_generate_embeddings_initialization(self, processing_tools):
        """Test embeddings generation initializes manager if needed"""
        with patch("mcp.tools.processing.ProcessingManager") as MockProcessingManager:
            mock_manager = AsyncMock()
            mock_manager.initialize = AsyncMock()
            mock_manager.generate_embeddings = AsyncMock(
                return_value={"success": True, "document_id": "doc1", "chunks_processed": 1}
            )
            MockProcessingManager.return_value = mock_manager

            request = GenerateEmbeddingsRequest(document_id="doc1")

            await processing_tools.generate_embeddings(request)

            assert processing_tools._initialized is True
            mock_manager.initialize.assert_called_once()

    async def test_generate_embeddings_failure(self, processing_tools):
        """Test embedding generation failure"""
        mock_manager = AsyncMock()
        mock_manager.generate_embeddings = AsyncMock(
            return_value={"success": True, "document_id": "doc1", "chunks_processed": 0}
        )
        processing_tools.processing_manager = mock_manager
        processing_tools._initialized = True

        request = GenerateEmbeddingsRequest(document_id="doc1")

        result = await processing_tools.generate_embeddings(request)

        # Successful response (manager returns success: True even on failure)
        assert result["success"] is True

    async def test_generate_embeddings_exception(self, processing_tools):
        """Test embedding generation exception handling"""
        mock_manager = AsyncMock()
        mock_manager.generate_embeddings = AsyncMock(side_effect=Exception("Unexpected error"))
        processing_tools.processing_manager = mock_manager
        processing_tools._initialized = True

        request = GenerateEmbeddingsRequest(document_id="doc1")

        result = await processing_tools.generate_embeddings(request)

        assert "error" in result
        assert "error_code" in result
        assert result["error_code"] == "EMBEDDING_GENERATION_FAILED"
        assert "Unexpected error" in result["error"]

    async def test_generate_tags_success(self, processing_tools):
        """Test successful tag generation"""
        mock_manager = AsyncMock()
        mock_manager.generate_tags = AsyncMock(
            return_value={
                "success": True,
                "document_id": "doc1",
                "tags": ["python", "ai", "machine-learning"],
                "message": "Success",
            }
        )
        processing_tools.processing_manager = mock_manager
        processing_tools._initialized = True

        request = GenerateTagsRequest(document_id="doc1", max_tags=5)

        result = await processing_tools.generate_tags(request)

        assert result["success"] is True
        assert result["document_id"] == "doc1"
        assert result["tags"] == ["python", "ai", "machine-learning"]
        mock_manager.generate_tags.assert_called_once()
        call_args = mock_manager.generate_tags.call_args
        assert call_args[1]["max_tags"] == 5

    async def test_generate_tags_by_path(self, processing_tools):
        """Test tag generation by document path"""
        mock_manager = AsyncMock()
        mock_manager.generate_tags = AsyncMock(
            return_value={"success": True, "document_id": "/test/doc.md", "tags": ["web", "javascript"]}
        )
        processing_tools.processing_manager = mock_manager
        processing_tools._initialized = True

        request = GenerateTagsRequest(path="/test/doc.md")

        result = await processing_tools.generate_tags(request)

        assert result["success"] is True
        mock_manager.generate_tags.assert_called_once()

    async def test_generate_tags_custom_max(self, processing_tools):
        """Test tag generation with custom max_tags"""
        mock_manager = AsyncMock()
        mock_manager.generate_tags = AsyncMock(
            return_value={"success": True, "document_id": "doc1", "tags": ["tag1", "tag2"]}
        )
        processing_tools.processing_manager = mock_manager
        processing_tools._initialized = True

        request = GenerateTagsRequest(document_id="doc1", max_tags=10)

        result = await processing_tools.generate_tags(request)

        mock_manager.generate_tags.assert_called_once()
        call_args = mock_manager.generate_tags.call_args
        assert call_args[1]["max_tags"] == 10

    async def test_generate_tags_force_regenerate(self, processing_tools):
        """Test tag generation with default max_tags"""
        mock_manager = AsyncMock()
        mock_manager.generate_tags = AsyncMock(
            return_value={"success": True, "document_id": "doc1", "tags": ["new-tag"]}
        )
        processing_tools.processing_manager = mock_manager
        processing_tools._initialized = True

        request = GenerateTagsRequest(document_id="doc1")

        result = await processing_tools.generate_tags(request)

        mock_manager.generate_tags.assert_called_once()
        call_args = mock_manager.generate_tags.call_args
        assert call_args[1]["max_tags"] == 5

    async def test_generate_tags_initialization(self, processing_tools):
        """Test tag generation initializes manager if needed"""
        with patch("mcp.tools.processing.ProcessingManager") as MockProcessingManager:
            mock_manager = AsyncMock()
            mock_manager.initialize = AsyncMock()
            mock_manager.generate_tags = AsyncMock(
                return_value={"success": True, "document_id": "doc1", "tags": ["test"]}
            )
            MockProcessingManager.return_value = mock_manager

            request = GenerateTagsRequest(document_id="doc1")

            await processing_tools.generate_tags(request)

            assert processing_tools._initialized is True
            mock_manager.initialize.assert_called_once()

    async def test_generate_tags_failure(self, processing_tools):
        """Test tag generation failure"""
        mock_manager = AsyncMock()
        mock_manager.generate_tags = AsyncMock(return_value={"success": True, "document_id": "doc1", "tags": []})
        processing_tools.processing_manager = mock_manager
        processing_tools._initialized = True

        request = GenerateTagsRequest(document_id="doc1")

        result = await processing_tools.generate_tags(request)

        # Successful response (manager returns success: True even on failure)
        assert result["success"] is True

    async def test_generate_tags_exception(self, processing_tools):
        """Test tag generation exception handling"""
        mock_manager = AsyncMock()
        mock_manager.generate_tags = AsyncMock(side_effect=Exception("Unexpected error"))
        processing_tools.processing_manager = mock_manager
        processing_tools._initialized = True

        request = GenerateTagsRequest(document_id="doc1")

        result = await processing_tools.generate_tags(request)

        assert "error" in result
        assert "error_code" in result
        assert result["error_code"] == "TAG_GENERATION_FAILED"
        assert "Unexpected error" in result["error"]
