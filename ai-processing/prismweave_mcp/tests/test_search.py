"""
Tests for Search MCP Tools
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from prismweave_mcp.schemas.requests import GetDocumentRequest, ListDocumentsRequest, SearchDocumentsRequest
from prismweave_mcp.tools.search import SearchTools
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
    config.vector = MagicMock()
    config.vector.collection_name = "test_collection"
    # Add required Config attributes
    config.ollama = MagicMock()
    config.processing = MagicMock()
    return config


@pytest.fixture
def search_tools(mock_config):
    """Create SearchTools instance"""
    return SearchTools(mock_config)


@pytest.mark.asyncio
class TestSearchTools:
    """Test suite for SearchTools"""

    async def test_initialize(self, search_tools):
        """Test initialization of search manager"""
        with patch("prismweave_mcp.tools.search.SearchManager") as MockSearchManager:
            mock_manager = AsyncMock()
            mock_manager.initialize = AsyncMock()
            MockSearchManager.return_value = mock_manager

            await search_tools.initialize()

            assert search_tools._initialized is True
            assert search_tools.search_manager is not None
            mock_manager.initialize.assert_called_once()

    async def test_search_documents_success(self, search_tools):
        """Test successful document search"""
        # Mock search manager
        search_tools.search_manager = AsyncMock()
        search_tools._initialized = True
        search_tools.search_manager.search_documents = AsyncMock(
            return_value={
                "results": [{"document_id": "doc1", "title": "Test Doc", "score": 0.95, "snippet": "test content"}],
                "total_results": 1,
            }
        )

        request = SearchDocumentsRequest(
            query="test query", max_results=10, similarity_threshold=0.7, filters={"tags": ["python"]}
        )

        result = await search_tools.search_documents(request)

        assert result["success"] is True
        assert len(result["results"]) == 1
        assert result["total_found"] == 1
        assert result["query"] == "test query"

    async def test_search_documents_initialization(self, search_tools):
        """Test search documents initializes manager if needed"""
        with patch("prismweave_mcp.tools.search.SearchManager") as MockSearchManager:
            mock_manager = AsyncMock()
            mock_manager.initialize = AsyncMock()
            mock_manager.search_documents = AsyncMock(return_value={"results": [], "total_results": 0})
            MockSearchManager.return_value = mock_manager

            request = SearchDocumentsRequest(query="test")

            await search_tools.search_documents(request)

            assert search_tools._initialized is True
            mock_manager.initialize.assert_called_once()

    async def test_search_documents_error(self, search_tools):
        """Test search documents error handling"""
        search_tools.search_manager = AsyncMock()
        search_tools._initialized = True
        search_tools.search_manager.search_documents = AsyncMock(side_effect=Exception("Search failed"))

        request = SearchDocumentsRequest(query="test query")

        result = await search_tools.search_documents(request)

        assert result["success"] is False
        assert "error" in result
        assert "error_code" in result
        assert result["error_code"] == "SEARCH_FAILED"
        assert "Search failed" in result["error"]

    async def test_get_document_by_id_success(self, search_tools):
        """Test successful document retrieval by ID"""
        search_tools.document_manager.get_document_by_id = MagicMock(
            return_value={
                "id": "doc1",
                "title": "Test Document",
                "content": "Test content",
                "metadata": {"tags": ["python"]},
                "file_path": "/test/doc1.md",
                "created_at": "2024-01-01",
                "updated_at": "2024-01-02",
            }
        )

        request = GetDocumentRequest(document_id="doc1")

        result = await search_tools.get_document(request)

        assert result["success"] is True
        assert result["document"]["id"] == "doc1"
        assert result["document"]["path"] == "/test/doc1.md"
        assert result["document"]["content"] == "Test content"

    async def test_get_document_by_path_success(self, search_tools):
        """Test successful document retrieval by path"""
        search_tools.document_manager.get_document_by_path = MagicMock(
            return_value={
                "id": "doc1",
                "title": "Test Document",
                "content": "Test content",
                "metadata": {},
                "file_path": "/test/doc1.md",
            }
        )

        request = GetDocumentRequest(path="/test/doc1.md")

        result = await search_tools.get_document(request)

        assert result["success"] is True
        assert result["document"]["id"] == "doc1"
        assert result["document"]["path"] == "/test/doc1.md"

    async def test_get_document_not_found(self, search_tools):
        """Test document not found"""
        search_tools.document_manager.get_document_by_id = MagicMock(return_value=None)

        request = GetDocumentRequest(document_id="nonexistent")

        result = await search_tools.get_document(request)

        assert result["success"] is False
        assert "error" in result
        assert result["error_code"] == "DOCUMENT_NOT_FOUND"
        assert "not found" in result["error"]

    async def test_get_document_no_identifier(self, search_tools):
        """Test get document without ID or path - should fail validation"""
        # This should fail at the Pydantic validation level before reaching the tool
        with pytest.raises(Exception):  # Pydantic ValidationError
            request = GetDocumentRequest()
            await search_tools.get_document(request)

    async def test_list_documents_success(self, search_tools):
        """Test successful document listing"""
        search_tools.document_manager.list_documents = MagicMock(
            return_value=[
                {
                    "id": "doc1",
                    "title": "Doc 1",
                    "tags": ["python"],
                    "file_path": "test/doc1.md",
                    "size_bytes": 100,
                },
                {
                    "id": "doc2",
                    "title": "Doc 2",
                    "tags": ["javascript"],
                    "file_path": "test/doc2.md",
                    "size_bytes": 200,
                },
            ]
        )

        request = ListDocumentsRequest(directory="test", sort_by="title", limit=10)

        result = await search_tools.list_documents(request)

        assert result["success"] is True
        assert result["total_count"] == 2
        assert len(result["documents"]) == 2
        assert result["offset"] == 0
        assert result["limit"] == 10

    async def test_list_documents_with_filters(self, search_tools):
        """Test document listing with multiple filters"""
        search_tools.document_manager.list_documents = MagicMock(return_value=[])

        request = ListDocumentsRequest(
            directory="generated",
            pattern="*.md",
            sort_by="date",  # Valid sort_by value
            sort_order="desc",
            limit=50,
        )

        result = await search_tools.list_documents(request)

        # DocumentManager is called with compatible parameters
        search_tools.document_manager.list_documents.assert_called_once()
        assert result["success"] is True

    async def test_list_documents_error(self, search_tools):
        """Test list documents error handling"""
        search_tools.document_manager.list_documents = MagicMock(side_effect=Exception("Database error"))

        request = ListDocumentsRequest()

        result = await search_tools.list_documents(request)

        assert result["success"] is False
        assert "error" in result
        assert result["error_code"] == "DOCUMENT_LIST_FAILED"
        assert "Database error" in result["error"]

    async def test_get_document_metadata_by_id(self, search_tools):
        """Test getting document metadata by ID"""
        search_tools.document_manager.get_document_metadata = MagicMock(
            return_value={"tags": ["python"], "category": "tech", "word_count": 500}
        )

        request = GetDocumentRequest(document_id="doc1")

        result = await search_tools.get_document_metadata(request)

        assert result["success"] is True
        assert result["metadata"]["tags"] == ["python"]
        assert result["metadata"]["category"] == "tech"

    async def test_get_document_metadata_by_path(self, search_tools):
        """Test getting document metadata by path"""
        search_tools.document_manager.get_document_metadata = MagicMock(
            return_value={"tags": ["javascript"], "category": "web"}
        )

        request = GetDocumentRequest(path="/test/doc.md")

        result = await search_tools.get_document_metadata(request)

        assert result["success"] is True
        assert result["metadata"]["tags"] == ["javascript"]

    async def test_get_document_metadata_not_found(self, search_tools):
        """Test metadata retrieval for non-existent document"""
        search_tools.document_manager.get_document_metadata = MagicMock(return_value=None)

        request = GetDocumentRequest(document_id="nonexistent")

        result = await search_tools.get_document_metadata(request)

        assert "error" in result
        assert result["error_code"] == "DOCUMENT_NOT_FOUND"

    async def test_get_document_metadata_error(self, search_tools):
        """Test metadata retrieval error handling"""
        search_tools.document_manager.get_document_metadata = MagicMock(side_effect=Exception("Metadata error"))

        request = GetDocumentRequest(document_id="doc1")

        result = await search_tools.get_document_metadata(request)

        assert "error" in result
        assert result["error_code"] == "METADATA_RETRIEVAL_FAILED"
