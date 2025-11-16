"""
Tests for Document Tools (MCP Tool Layer)

Tests for the MCP tool implementations for document operations.
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest
import pytest_asyncio

from prismweave_mcp.schemas.requests import CreateDocumentRequest, UpdateDocumentRequest
from prismweave_mcp.tools.documents import DocumentTools
from src.core.config import Config, MCPConfig, MCPCreationConfig, MCPPathsConfig


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
        creation=MCPCreationConfig(
            default_category="general",
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
        (docs_root / "tech").mkdir()

        yield docs_root


@pytest_asyncio.fixture
async def document_tools(test_config, temp_docs_dir):
    """Create document tools with temp directory"""
    test_config.mcp.paths.documents_root = str(temp_docs_dir)
    return DocumentTools(test_config)


class TestCreateDocument:
    """Tests for create_document tool"""

    @pytest.mark.asyncio
    async def test_create_basic_document(self, document_tools, temp_docs_dir):
        """Test creating a basic document"""
        request = CreateDocumentRequest(title="Test Document", content="# Test\n\nContent here.", tags=["test"])

        response = await document_tools.create_document(request)

        assert "error" not in response
        assert "document_id" in response
        assert "path" in response

        # Verify file was created
        created_path = Path(response["path"])
        assert created_path.exists()

    @pytest.mark.asyncio
    async def test_create_with_category(self, document_tools, temp_docs_dir):
        """Test creating document with category"""
        request = CreateDocumentRequest(
            title="Tech Article", content="# Tech\n\nTechnical content.", category="tech", tags=["tech"]
        )

        response = await document_tools.create_document(request)

        assert "error" not in response
        assert "tech" in response["path"]

    @pytest.mark.asyncio
    async def test_create_with_metadata(self, document_tools, temp_docs_dir):
        """Test creating document with additional metadata"""
        request = CreateDocumentRequest(
            title="Article",
            content="This is a complete article with proper content length.",
            additional_metadata={"author": "Test", "source_url": "https://example.com"},
        )

        response = await document_tools.create_document(request)

        assert "error" not in response

        # Verify metadata was saved
        created_path = Path(response["path"])
        content = created_path.read_text(encoding="utf-8")
        assert "author: Test" in content
        assert "source_url: https://example.com" in content

    @pytest.mark.asyncio
    async def test_create_empty_content_returns_error(self, document_tools):
        """Test creating document with empty content returns error"""
        request = CreateDocumentRequest(title="Empty", content="")

        response = await document_tools.create_document(request)

        assert "error" in response
        assert "error_code" in response
        assert response["error_code"] == "DOCUMENT_CREATION_EXCEPTION"

    @pytest.mark.asyncio
    async def test_create_with_default_tags(self, document_tools, temp_docs_dir):
        """Test creating document with default empty tags"""
        request = CreateDocumentRequest(title="No Tags", content="This is content without any tags specified.")

        response = await document_tools.create_document(request)

        assert "error" not in response

    @pytest.mark.asyncio
    async def test_create_exception_handling(self, document_tools, temp_docs_dir):
        """Test create handles exceptions gracefully"""
        # Mock the document manager to raise an exception
        document_tools.document_manager.create_document = MagicMock(side_effect=Exception("Test error"))

        request = CreateDocumentRequest(title="Test", content="This is test content for exception handling.")

        response = await document_tools.create_document(request)

        assert "error" in response
        assert "Test error" in response["error"]
        assert response["error_code"] == "DOCUMENT_CREATION_EXCEPTION"


class TestUpdateDocument:
    """Tests for update_document tool"""

    @pytest.mark.asyncio
    async def test_update_title(self, document_tools, temp_docs_dir):
        """Test updating document title"""
        # Create document first
        doc_path = temp_docs_dir / "generated" / "test.md"
        doc_path.write_text(
            """---
id: update_test_1
title: Original Title
---
Content.""",
            encoding="utf-8",
        )

        request = UpdateDocumentRequest(document_id="update_test_1", title="Updated Title")

        response = await document_tools.update_document(request)

        assert "error" not in response
        assert response["document_id"] == "update_test_1"
        assert "title" in response["updated_fields"]

        # Verify update
        content = doc_path.read_text(encoding="utf-8")
        assert "Updated Title" in content

    @pytest.mark.asyncio
    async def test_update_content(self, document_tools, temp_docs_dir):
        """Test updating document content"""
        doc_path = temp_docs_dir / "generated" / "test.md"
        doc_path.write_text("---\nid: update_test_2\n---\nOld content.", encoding="utf-8")

        request = UpdateDocumentRequest(document_id="update_test_2", content="New content here.")

        response = await document_tools.update_document(request)

        assert "error" not in response
        assert "content" in response["updated_fields"]

        # Verify update
        content = doc_path.read_text(encoding="utf-8")
        assert "New content here." in content

    @pytest.mark.asyncio
    async def test_update_tags(self, document_tools, temp_docs_dir):
        """Test updating document tags"""
        doc_path = temp_docs_dir / "generated" / "test.md"
        doc_path.write_text("---\nid: update_test_3\ntags: [old]\n---\nContent.", encoding="utf-8")

        request = UpdateDocumentRequest(document_id="update_test_3", tags=["new", "updated"])

        response = await document_tools.update_document(request)

        assert "error" not in response
        assert "tags" in response["updated_fields"]

    @pytest.mark.asyncio
    async def test_update_category(self, document_tools, temp_docs_dir):
        """Test updating document category"""
        doc_path = temp_docs_dir / "generated" / "test.md"
        doc_path.write_text("---\nid: update_test_4\ncategory: old\n---\nContent.", encoding="utf-8")

        request = UpdateDocumentRequest(document_id="update_test_4", category="tech")

        response = await document_tools.update_document(request)

        assert "error" not in response
        assert "category" in response["updated_fields"]

    @pytest.mark.asyncio
    async def test_update_multiple_fields(self, document_tools, temp_docs_dir):
        """Test updating multiple fields at once"""
        doc_path = temp_docs_dir / "generated" / "test.md"
        doc_path.write_text("---\nid: update_test_5\ntitle: Old\n---\nOld content.", encoding="utf-8")

        request = UpdateDocumentRequest(
            document_id="update_test_5", title="New Title", content="New content.", tags=["updated"]
        )

        response = await document_tools.update_document(request)

        assert "error" not in response
        assert "title" in response["updated_fields"]
        assert "content" in response["updated_fields"]
        assert "tags" in response["updated_fields"]

    @pytest.mark.asyncio
    async def test_update_with_additional_metadata(self, document_tools, temp_docs_dir):
        """Test updating with additional metadata"""
        doc_path = temp_docs_dir / "generated" / "test.md"
        doc_path.write_text("---\nid: update_test_6\n---\nContent.", encoding="utf-8")

        request = UpdateDocumentRequest(
            document_id="update_test_6", additional_metadata={"author": "Jane Doe", "version": "2.0"}
        )

        response = await document_tools.update_document(request)

        assert "error" not in response
        assert "metadata" in response["updated_fields"]

    @pytest.mark.asyncio
    async def test_update_nonexistent_document(self, document_tools):
        """Test updating nonexistent document returns error"""
        request = UpdateDocumentRequest(document_id="nonexistent", title="New Title")

        response = await document_tools.update_document(request)

        assert "error" in response
        assert response["error_code"] == "DOCUMENT_UPDATE_EXCEPTION"

    @pytest.mark.asyncio
    async def test_update_captured_document_returns_error(self, document_tools, temp_docs_dir):
        """Test updating captured document returns error"""
        # Create captured document (not in generated/)
        doc_path = temp_docs_dir / "documents" / "captured.md"
        doc_path.write_text("---\nid: captured_doc\n---\nContent.", encoding="utf-8")

        request = UpdateDocumentRequest(document_id="captured_doc", title="New Title")

        response = await document_tools.update_document(request)

        assert "error" in response
        assert "read-only" in response["error"]

    @pytest.mark.asyncio
    async def test_update_exception_handling(self, document_tools):
        """Test update handles exceptions gracefully"""
        document_tools.document_manager.update_document = MagicMock(side_effect=Exception("Update failed"))

        request = UpdateDocumentRequest(document_id="test_doc", title="Title")

        response = await document_tools.update_document(request)

        assert "error" in response
        assert "Update failed" in response["error"]


class TestLazyInitialization:
    """Tests for lazy initialization of managers"""

    @pytest.mark.asyncio
    async def test_processing_manager_lazy_init(self, document_tools):
        """Test processing manager is lazily initialized"""
        assert document_tools.processing_manager is None
        assert document_tools._processing_initialized is False

        # Trigger initialization
        await document_tools._ensure_processing_manager()

        assert document_tools.processing_manager is not None
        assert document_tools._processing_initialized is True

    @pytest.mark.asyncio
    async def test_git_manager_lazy_init(self, document_tools):
        """Test git manager is lazily initialized"""
        assert document_tools.git_manager is None
        assert document_tools._git_initialized is False

        # Trigger initialization
        await document_tools._ensure_git_manager()

        assert document_tools.git_manager is not None
        assert document_tools._git_initialized is True

    @pytest.mark.asyncio
    async def test_multiple_init_calls_safe(self, document_tools):
        """Test multiple initialization calls are safe"""
        manager1 = await document_tools._ensure_processing_manager()
        manager2 = await document_tools._ensure_processing_manager()

        assert manager1 is manager2  # Should be same instance
