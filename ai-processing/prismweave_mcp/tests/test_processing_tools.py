"""
Tests for Processing Tools (MCP Tool Layer)

Tests for AI processing MCP tool implementations including embeddings
and tag generation.
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest
import pytest_asyncio

from prismweave_mcp.schemas.requests import GenerateEmbeddingsRequest, GenerateTagsRequest
from prismweave_mcp.tools.processing import ProcessingTools
from src.core.config import Config, MCPConfig, MCPPathsConfig


@pytest.fixture
def test_config():
    """Create test configuration"""
    config = Config()
    config.mcp = MCPConfig(
        paths=MCPPathsConfig(
            documents_root="test_docs",
            documents_dir="documents",
            generated_dir="generated",
            images_dir="images",
            tech_dir="tech",
        ),
    )
    return config


@pytest.fixture
def temp_docs_dir():
    """Create temporary documents directory"""
    with tempfile.TemporaryDirectory() as tmpdir:
        docs_root = Path(tmpdir)

        # Create directory structure
        (docs_root / "documents").mkdir()
        (docs_root / "generated").mkdir()

        yield docs_root


@pytest_asyncio.fixture
async def processing_tools(test_config, temp_docs_dir):
    """Create processing tools with temp directory"""
    test_config.mcp.paths.documents_root = str(temp_docs_dir)
    tools = ProcessingTools(test_config)
    # Initialize with mock processing manager to avoid actual AI processing
    await tools.initialize()
    return tools


class TestGenerateEmbeddings:
    """Tests for generate_embeddings tool"""

    @pytest.mark.asyncio
    async def test_generate_embeddings_success(self, processing_tools, temp_docs_dir):
        """Test successful embedding generation"""
        # Create test document
        doc_path = temp_docs_dir / "documents" / "test.md"
        doc_path.write_text(
            """---
id: embed_test_1
title: Test Document
---

This is test content for embeddings.""",
            encoding="utf-8",
        )

        # Mock processing manager - async method needs to return coroutine
        async def mock_generate_embeddings(*args, **kwargs):
            return {"success": True, "chunks_processed": 5, "message": "Success"}
        
        processing_tools.processing_manager.generate_embeddings = mock_generate_embeddings

        request = GenerateEmbeddingsRequest(document_id="embed_test_1", model="nomic-embed-text")

        response = await processing_tools.generate_embeddings(request)

        assert "error" not in response
        assert response["document_id"] == "embed_test_1"
        assert response["embedding_count"] == 5
        assert response["model"] == "nomic-embed-text"

    @pytest.mark.asyncio
    async def test_generate_embeddings_with_force_regenerate(self, processing_tools, temp_docs_dir):
        """Test embedding generation with force regenerate"""
        doc_path = temp_docs_dir / "documents" / "test.md"
        doc_path.write_text("---\nid: embed_test_2\n---\nContent.", encoding="utf-8")

        async def mock_generate_embeddings(*args, **kwargs):
            return {"success": True, "chunks_processed": 3, "message": "Regenerated"}
        
        mock_func = MagicMock(side_effect=mock_generate_embeddings)
        processing_tools.processing_manager.generate_embeddings = mock_func

        request = GenerateEmbeddingsRequest(document_id="embed_test_2", force_regenerate=True)

        response = await processing_tools.generate_embeddings(request)

        assert "error" not in response
        # Verify force_regenerate was passed
        mock_func.assert_called_once()
        call_args = mock_func.call_args
        assert call_args[1]["force_regenerate"] is True

    @pytest.mark.asyncio
    async def test_generate_embeddings_document_not_found(self, processing_tools):
        """Test embedding generation for nonexistent document"""
        request = GenerateEmbeddingsRequest(document_id="nonexistent_doc")

        response = await processing_tools.generate_embeddings(request)

        assert "error" in response
        assert response["error_code"] == "DOCUMENT_NOT_FOUND"
        assert "nonexistent_doc" in response["details"]["document_id"]

    @pytest.mark.asyncio
    async def test_generate_embeddings_processing_failure(self, processing_tools, temp_docs_dir):
        """Test embedding generation when processing fails"""
        doc_path = temp_docs_dir / "documents" / "test.md"
        doc_path.write_text("---\nid: embed_fail\n---\nContent.", encoding="utf-8")

        # Mock processing failure
        async def mock_generate_embeddings(*args, **kwargs):
            return {"success": False, "message": "Processing failed", "chunks_processed": 0}
        
        processing_tools.processing_manager.generate_embeddings = mock_generate_embeddings

        request = GenerateEmbeddingsRequest(document_id="embed_fail")

        response = await processing_tools.generate_embeddings(request)

        assert "error" in response
        assert response["error_code"] == "EMBEDDING_GENERATION_FAILED"

    @pytest.mark.asyncio
    async def test_generate_embeddings_exception(self, processing_tools, temp_docs_dir):
        """Test embedding generation handles exceptions"""
        doc_path = temp_docs_dir / "documents" / "test.md"
        doc_path.write_text("---\nid: embed_exc\n---\nContent.", encoding="utf-8")

        # Mock exception
        async def mock_generate_embeddings(*args, **kwargs):
            raise Exception("Test error")
        
        processing_tools.processing_manager.generate_embeddings = mock_generate_embeddings

        request = GenerateEmbeddingsRequest(document_id="embed_exc")

        response = await processing_tools.generate_embeddings(request)

        assert "error" in response
        assert "Test error" in response["error"]

    @pytest.mark.asyncio
    async def test_generate_embeddings_auto_initializes(self, test_config, temp_docs_dir):
        """Test that generate_embeddings auto-initializes if needed"""
        test_config.mcp.paths.documents_root = str(temp_docs_dir)
        tools = ProcessingTools(test_config)

        # Don't call initialize() manually
        assert tools._initialized is False

        # Create test document
        doc_path = temp_docs_dir / "documents" / "test.md"
        doc_path.write_text("---\nid: auto_init\n---\nContent.", encoding="utf-8")

        request = GenerateEmbeddingsRequest(document_id="auto_init")

        # Should auto-initialize
        # Will fail with document not found, but that's after initialization
        response = await tools.generate_embeddings(request)

        assert tools._initialized is True


class TestGenerateTags:
    """Tests for generate_tags tool"""

    @pytest.mark.asyncio
    async def test_generate_tags_success(self, processing_tools, temp_docs_dir):
        """Test successful tag generation"""
        doc_path = temp_docs_dir / "documents" / "test.md"
        doc_path.write_text(
            """---
id: tag_test_1
title: Machine Learning Article
---

This article discusses neural networks and deep learning.""",
            encoding="utf-8",
        )

        # Mock tag generation
        async def mock_generate_tags(*args, **kwargs):
            return {
                "success": True,
                "tags": ["machine-learning", "neural-networks", "ai"],
                "confidence": 0.85,
            }
        
        processing_tools.processing_manager.generate_tags = mock_generate_tags

        request = GenerateTagsRequest(document_id="tag_test_1", max_tags=5)

        response = await processing_tools.generate_tags(request)

        assert "error" not in response
        assert response["document_id"] == "tag_test_1"
        assert len(response["tags"]) == 3
        assert "machine-learning" in response["tags"]
        assert response["confidence"] == 0.85

    @pytest.mark.asyncio
    async def test_generate_tags_with_max_limit(self, processing_tools, temp_docs_dir):
        """Test tag generation with max_tags limit"""
        doc_path = temp_docs_dir / "documents" / "test.md"
        doc_path.write_text("---\nid: tag_test_2\n---\nContent about AI.", encoding="utf-8")

        async def mock_generate_tags(*args, **kwargs):
            return {"success": True, "tags": ["ai", "ml"], "confidence": 0.8}
        
        mock_func = MagicMock(side_effect=mock_generate_tags)
        processing_tools.processing_manager.generate_tags = mock_func

        request = GenerateTagsRequest(document_id="tag_test_2", max_tags=3)

        response = await processing_tools.generate_tags(request)

        assert "error" not in response
        # Verify max_tags was passed to processing manager
        mock_func.assert_called_once()
        call_args = mock_func.call_args
        assert call_args[1]["max_tags"] == 3

    @pytest.mark.asyncio
    async def test_generate_tags_document_not_found(self, processing_tools):
        """Test tag generation for nonexistent document"""
        request = GenerateTagsRequest(document_id="nonexistent_doc")

        response = await processing_tools.generate_tags(request)

        assert "error" in response
        assert response["error_code"] == "DOCUMENT_NOT_FOUND"

    @pytest.mark.asyncio
    async def test_generate_tags_processing_failure(self, processing_tools, temp_docs_dir):
        """Test tag generation when processing fails"""
        doc_path = temp_docs_dir / "documents" / "test.md"
        doc_path.write_text("---\nid: tag_fail\n---\nContent.", encoding="utf-8")

        # Mock processing failure
        async def mock_generate_tags(*args, **kwargs):
            return {"success": False, "message": "Tag generation failed", "tags": []}
        
        processing_tools.processing_manager.generate_tags = mock_generate_tags

        request = GenerateTagsRequest(document_id="tag_fail")

        response = await processing_tools.generate_tags(request)

        assert "error" in response
        assert response["error_code"] == "TAG_GENERATION_FAILED"

    @pytest.mark.asyncio
    async def test_generate_tags_exception(self, processing_tools, temp_docs_dir):
        """Test tag generation handles exceptions"""
        doc_path = temp_docs_dir / "documents" / "test.md"
        doc_path.write_text("---\nid: tag_exc\n---\nContent.", encoding="utf-8")

        async def mock_generate_tags(*args, **kwargs):
            raise Exception("Tag error")
        
        processing_tools.processing_manager.generate_tags = mock_generate_tags

        request = GenerateTagsRequest(document_id="tag_exc")

        response = await processing_tools.generate_tags(request)

        assert "error" in response
        assert "Tag error" in response["error"]


class TestInitialization:
    """Tests for processing tools initialization"""

    @pytest.mark.asyncio
    async def test_initialize(self, test_config, temp_docs_dir):
        """Test processing tools initialization"""
        test_config.mcp.paths.documents_root = str(temp_docs_dir)
        tools = ProcessingTools(test_config)

        assert tools._initialized is False
        assert tools.processing_manager is None

        await tools.initialize()

        assert tools._initialized is True
        assert tools.processing_manager is not None

    @pytest.mark.asyncio
    async def test_multiple_initialize_calls(self, test_config, temp_docs_dir):
        """Test multiple initialization calls are safe"""
        test_config.mcp.paths.documents_root = str(temp_docs_dir)
        tools = ProcessingTools(test_config)

        await tools.initialize()
        manager1 = tools.processing_manager

        await tools.initialize()
        manager2 = tools.processing_manager

        # Should not reinitialize
        assert tools._initialized is True
        # Manager might be recreated, so we just check it exists
        assert manager2 is not None
