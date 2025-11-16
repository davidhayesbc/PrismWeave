"""
Tests for Search Tools (MCP Tool Layer)

Tests for search and retrieval MCP tool implementations.
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest
import pytest_asyncio
from haystack import Document as HaystackDocument

from prismweave_mcp.schemas.requests import GetDocumentRequest, ListDocumentsRequest, SearchDocumentsRequest
from prismweave_mcp.schemas.responses import DocumentMetadata, SearchResult
from prismweave_mcp.tools.search import SearchTools
from src.core.config import Config, MCPConfig, MCPPathsConfig, MCPSearchConfig


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
        search=MCPSearchConfig(max_results=20, similarity_threshold=0.6, default_filters={}),
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
async def search_tools(test_config, temp_docs_dir):
    """Create search tools with temp directory"""
    test_config.mcp.paths.documents_root = str(temp_docs_dir)
    tools = SearchTools(test_config)
    # Don't initialize - let tests do it as needed
    return tools


class TestSearchDocuments:
    """Tests for search_documents tool"""

    @pytest.mark.asyncio
    async def test_search_basic(self, search_tools, temp_docs_dir):
        """Test basic search operation"""
        # Create test document
        doc_path = temp_docs_dir / "documents" / "test.md"
        doc_path.write_text(
            """---
id: search_test_1
title: Test Document
tags: [test]
---

This is test content.""",
            encoding="utf-8",
        )

        # Mock search manager
        mock_result = SearchResult(
            document_id="search_test_1",
            path="documents/test.md",
            score=0.85,
            excerpt="This is test content.",
            title="Test Document",
        )

        await search_tools.initialize()
        search_tools.search_manager.search_documents = MagicMock(return_value=([mock_result], 1))

        request = SearchDocumentsRequest(query="test content")

        response = await search_tools.search_documents(request)

        assert "error" not in response
        assert response["query"] == "test content"
        assert response["total_results"] == 1
        assert len(response["results"]) == 1
        assert response["results"][0]["title"] == "Test Document"

    @pytest.mark.asyncio
    async def test_search_with_filters(self, search_tools, temp_docs_dir):
        """Test search with tag and category filters"""
        await search_tools.initialize()

        mock_result = SearchResult(
            document_id="filtered_doc", path="tech/article.md", score=0.9, excerpt="Content", title="Tech Article"
        )

        search_tools.search_manager.search_documents = MagicMock(return_value=([mock_result], 1))

        request = SearchDocumentsRequest(query="technology", tags=["python"], category="tech")

        response = await search_tools.search_documents(request)

        assert "error" not in response

        # Verify filters were passed
        search_tools.search_manager.search_documents.assert_called_once()
        call_args = search_tools.search_manager.search_documents.call_args
        filters = call_args[1]["filters"]
        assert filters["tags"] == ["python"]
        assert filters["category"] == "tech"

    @pytest.mark.asyncio
    async def test_search_with_max_results(self, search_tools, temp_docs_dir):
        """Test search with max_results limit"""
        await search_tools.initialize()

        # Create multiple mock results
        mock_results = [
            SearchResult(document_id=f"doc_{i}", path=f"doc{i}.md", score=0.9 - i * 0.1, excerpt="", title=f"Doc {i}")
            for i in range(5)
        ]

        search_tools.search_manager.search_documents = MagicMock(return_value=(mock_results[:3], 3))

        request = SearchDocumentsRequest(query="test", max_results=3)

        response = await search_tools.search_documents(request)

        assert "error" not in response
        assert len(response["results"]) == 3

    @pytest.mark.asyncio
    async def test_search_with_similarity_threshold(self, search_tools, temp_docs_dir):
        """Test search with custom similarity threshold"""
        await search_tools.initialize()

        mock_result = SearchResult(
            document_id="high_score", path="doc.md", score=0.95, excerpt="Content", title="High Score Doc"
        )

        search_tools.search_manager.search_documents = MagicMock(return_value=([mock_result], 1))

        request = SearchDocumentsRequest(query="test", similarity_threshold=0.9)

        response = await search_tools.search_documents(request)

        assert "error" not in response

        # Verify threshold was passed
        call_args = search_tools.search_manager.search_documents.call_args
        assert call_args[1]["similarity_threshold"] == 0.9

    @pytest.mark.asyncio
    async def test_search_auto_initializes(self, test_config, temp_docs_dir):
        """Test search auto-initializes if not initialized"""
        test_config.mcp.paths.documents_root = str(temp_docs_dir)
        tools = SearchTools(test_config)

        assert tools._initialized is False

        # Mock search manager to avoid actual search
        mock_manager = MagicMock()
        mock_manager.search_documents.return_value = ([], 0)

        # Mock initialize to inject our mock
        async def mock_init():
            tools.search_manager = mock_manager
            tools._initialized = True

        tools.initialize = mock_init

        request = SearchDocumentsRequest(query="test")
        response = await tools.search_documents(request)

        assert tools._initialized is True

    @pytest.mark.asyncio
    async def test_search_exception_handling(self, search_tools, temp_docs_dir):
        """Test search handles exceptions gracefully"""
        await search_tools.initialize()

        search_tools.search_manager.search_documents = MagicMock(side_effect=Exception("Search error"))

        request = SearchDocumentsRequest(query="test")

        response = await search_tools.search_documents(request)

        assert "error" in response
        assert response["error_code"] == "SEARCH_FAILED"
        assert "Search error" in response["error"]


class TestGetDocument:
    """Tests for get_document tool"""

    @pytest.mark.asyncio
    async def test_get_document_by_id(self, search_tools, temp_docs_dir):
        """Test getting document by ID"""
        doc_path = temp_docs_dir / "documents" / "test.md"
        doc_path.write_text(
            """---
id: get_test_1
title: Test Document
---

Content here.""",
            encoding="utf-8",
        )

        request = GetDocumentRequest(document_id="get_test_1", include_content=True)

        response = await search_tools.get_document(request)

        assert "error" not in response
        assert response["document"]["id"] == "get_test_1"
        assert response["document"]["metadata"]["title"] == "Test Document"
        assert "Content here." in response["document"]["content"]

    @pytest.mark.asyncio
    async def test_get_document_without_content(self, search_tools, temp_docs_dir):
        """Test getting document without content"""
        doc_path = temp_docs_dir / "documents" / "test.md"
        doc_path.write_text("---\nid: get_test_2\ntitle: No Content\n---\nSome content.", encoding="utf-8")

        request = GetDocumentRequest(document_id="get_test_2", include_content=False)

        response = await search_tools.get_document(request)

        assert "error" not in response
        assert response["document"]["metadata"]["title"] == "No Content"
        assert response["document"]["content"] == ""  # Content should be empty

    @pytest.mark.asyncio
    async def test_get_document_by_path(self, search_tools, temp_docs_dir):
        """Test getting document by path"""
        doc_path = temp_docs_dir / "documents" / "test.md"
        doc_path.write_text("---\nid: get_test_3\ntitle: Path Test\n---\nContent.", encoding="utf-8")

        request = GetDocumentRequest(path="documents/test.md", include_content=True)

        response = await search_tools.get_document(request)

        assert "error" not in response
        assert response["document"]["metadata"]["title"] == "Path Test"

    @pytest.mark.asyncio
    async def test_get_document_not_found(self, search_tools):
        """Test getting nonexistent document"""
        request = GetDocumentRequest(document_id="nonexistent_doc")

        response = await search_tools.get_document(request)

        assert "error" in response
        assert response["error_code"] == "DOCUMENT_NOT_FOUND"

    @pytest.mark.asyncio
    async def test_get_document_exception_handling(self, search_tools):
        """Test get_document handles exceptions"""
        search_tools.document_manager.get_document_by_id = MagicMock(side_effect=Exception("Get error"))

        request = GetDocumentRequest(document_id="test_doc")

        response = await search_tools.get_document(request)

        assert "error" in response
        assert response["error_code"] == "DOCUMENT_RETRIEVAL_FAILED"


class TestListDocuments:
    """Tests for list_documents tool"""

    @pytest.mark.asyncio
    async def test_list_all_documents(self, search_tools, temp_docs_dir):
        """Test listing all documents"""
        # Create multiple documents
        for i in range(3):
            doc_path = temp_docs_dir / "documents" / f"doc{i}.md"
            doc_path.write_text(f"---\nid: list_doc_{i}\ntitle: Document {i}\n---\nContent.", encoding="utf-8")

        request = ListDocumentsRequest(limit=50, offset=0)

        response = await search_tools.list_documents(request)

        assert "error" not in response
        assert response["total_count"] >= 3
        assert len(response["documents"]) >= 3

    @pytest.mark.asyncio
    async def test_list_with_category_filter(self, search_tools, temp_docs_dir):
        """Test listing documents with category filter"""
        # Create documents in different categories
        tech_doc = temp_docs_dir / "tech" / "tech.md"
        tech_doc.write_text("---\nid: tech_doc\ntitle: Tech\n---\nContent.", encoding="utf-8")

        general_doc = temp_docs_dir / "documents" / "general.md"
        general_doc.write_text("---\nid: gen_doc\ntitle: General\n---\nContent.", encoding="utf-8")

        request = ListDocumentsRequest(category="tech")

        response = await search_tools.list_documents(request)

        assert "error" not in response
        assert response["category"] == "tech"

    @pytest.mark.asyncio
    async def test_list_with_tag_filter(self, search_tools, temp_docs_dir):
        """Test listing documents with tag filter"""
        doc1 = temp_docs_dir / "documents" / "doc1.md"
        doc1.write_text(
            """---
id: tag_doc_1
title: Python Doc
tags: [python, programming]
---
Content.""",
            encoding="utf-8",
        )

        request = ListDocumentsRequest(tags=["python"])

        response = await search_tools.list_documents(request)

        assert "error" not in response
        # Should have at least the python doc
        assert response["total_count"] >= 1

    @pytest.mark.asyncio
    async def test_list_with_pagination(self, search_tools, temp_docs_dir):
        """Test listing with limit and offset"""
        # Create multiple documents
        for i in range(10):
            doc_path = temp_docs_dir / "documents" / f"doc{i}.md"
            doc_path.write_text(f"---\nid: page_doc_{i}\ntitle: Doc {i}\n---\nContent.", encoding="utf-8")

        # First page
        request1 = ListDocumentsRequest(limit=5, offset=0)
        response1 = await search_tools.list_documents(request1)

        assert "error" not in response1
        assert len(response1["documents"]) <= 5

        # Second page
        request2 = ListDocumentsRequest(limit=5, offset=5)
        response2 = await search_tools.list_documents(request2)

        assert "error" not in response2

    @pytest.mark.asyncio
    async def test_list_exception_handling(self, search_tools):
        """Test list_documents handles exceptions"""
        search_tools.document_manager.list_documents = MagicMock(side_effect=Exception("List error"))

        request = ListDocumentsRequest()

        response = await search_tools.list_documents(request)

        assert "error" in response
        assert response["error_code"] == "DOCUMENT_LIST_FAILED"


class TestGetDocumentMetadata:
    """Tests for get_document_metadata tool"""

    @pytest.mark.asyncio
    async def test_get_metadata(self, search_tools, temp_docs_dir):
        """Test getting document metadata"""
        doc_path = temp_docs_dir / "documents" / "test.md"
        doc_path.write_text(
            """---
id: meta_test_1
title: Metadata Test
tags: [test, metadata]
word_count: 100
---

Content.""",
            encoding="utf-8",
        )

        request = GetDocumentRequest(document_id="meta_test_1")

        response = await search_tools.get_document_metadata(request)

        assert "error" not in response
        assert response["success"] is True
        assert response["metadata"]["title"] == "Metadata Test"
        assert "test" in response["metadata"]["tags"]

    @pytest.mark.asyncio
    async def test_get_metadata_not_found(self, search_tools):
        """Test getting metadata for nonexistent document"""
        request = GetDocumentRequest(document_id="nonexistent")

        response = await search_tools.get_document_metadata(request)

        assert "error" in response
        assert response["error_code"] == "DOCUMENT_NOT_FOUND"

    @pytest.mark.asyncio
    async def test_get_metadata_exception_handling(self, search_tools):
        """Test get_document_metadata handles exceptions"""
        search_tools.document_manager.get_document_metadata = MagicMock(side_effect=Exception("Metadata error"))

        request = GetDocumentRequest(document_id="test")

        response = await search_tools.get_document_metadata(request)

        assert "error" in response
        assert response["error_code"] == "METADATA_RETRIEVAL_FAILED"


class TestSearchToolsInitialization:
    """Tests for search tools initialization"""

    @pytest.mark.asyncio
    async def test_initialize(self, test_config, temp_docs_dir):
        """Test search tools initialization"""
        test_config.mcp.paths.documents_root = str(temp_docs_dir)
        tools = SearchTools(test_config)

        assert tools._initialized is False
        assert tools.search_manager is None

        await tools.initialize()

        assert tools._initialized is True
        assert tools.search_manager is not None

    @pytest.mark.asyncio
    async def test_initialize_sets_embedding_store(self, test_config, temp_docs_dir):
        """Test initialization sets embedding store on document manager"""
        test_config.mcp.paths.documents_root = str(temp_docs_dir)
        tools = SearchTools(test_config)

        await tools.initialize()

        # Document manager should have embedding store from search manager
        assert tools.document_manager.embedding_store == tools.search_manager.embedding_store

    @pytest.mark.asyncio
    async def test_multiple_initialize_calls(self, test_config, temp_docs_dir):
        """Test multiple initialization calls are safe"""
        test_config.mcp.paths.documents_root = str(temp_docs_dir)
        tools = SearchTools(test_config)

        await tools.initialize()
        await tools.initialize()

        # Should still be initialized
        assert tools._initialized is True
