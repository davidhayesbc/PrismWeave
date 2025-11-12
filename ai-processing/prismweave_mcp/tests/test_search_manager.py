"""
Tests for Search Manager
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock

import pytest
from haystack import Document as HaystackDocument

from prismweave_mcp.managers.search_manager import SearchManager
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


@pytest.fixture
def mock_embedding_store():
    """Create mock embedding store"""
    mock_store = Mock()
    mock_store.verify_embeddings.return_value = {
        "status": "success",
        "document_count": 10,
        "search_functional": True,
        "collection_name": "test_collection",
        "persist_directory": "/test/path",
    }
    mock_store.get_unique_source_files.return_value = [
        "/test/docs/doc1.md",
        "/test/docs/doc2.md",
    ]
    return mock_store


@pytest.fixture
def search_manager(test_config, temp_docs_dir, mock_embedding_store):
    """Create search manager with mocked embedding store"""
    test_config.mcp.paths.documents_root = str(temp_docs_dir)
    return SearchManager(test_config, embedding_store=mock_embedding_store)


class TestSearchManagerInitialization:
    """Tests for search manager initialization"""

    @pytest.mark.asyncio
    async def test_initialize_success(self, search_manager, mock_embedding_store):
        """Test successful initialization"""
        await search_manager.initialize()

        # Verify embedding store was checked
        mock_embedding_store.verify_embeddings.assert_called_once()

    @pytest.mark.asyncio
    async def test_initialize_failure(self, test_config, temp_docs_dir):
        """Test initialization failure"""
        mock_store = Mock()
        mock_store.verify_embeddings.return_value = {"status": "error", "error": "Test error"}

        test_config.mcp.paths.documents_root = str(temp_docs_dir)
        manager = SearchManager(test_config, embedding_store=mock_store)

        with pytest.raises(RuntimeError, match="verification failed"):
            await manager.initialize()


class TestSearchDocuments:
    """Tests for search_documents"""

    def test_basic_search(self, search_manager, mock_embedding_store, temp_docs_dir):
        """Test basic search without filters"""
        # Create sample document
        doc_path = temp_docs_dir / "documents" / "test.md"
        doc_path.write_text(
            """---
id: doc_1
title: Test Document
tags: [test, sample]
created_date: '2025-01-01T10:00:00'
---

This is test content.""",
            encoding="utf-8",
        )

        # Mock search results
        mock_doc = HaystackDocument(
            content="This is test content.",
            meta={
                "id": "doc_1",
                "title": "Test Document",
                "source_file": str(doc_path),
                "tags": ["test", "sample"],
                "created_date": "2025-01-01T10:00:00",
            },
        )

        mock_embedding_store.search_similar_with_scores.return_value = [(mock_doc, 0.85)]

        # Perform search
        results, total = search_manager.search_documents("test query")

        # Verify results
        assert len(results) == 1
        assert total == 1
        assert results[0].title == "Test Document"
        assert results[0].similarity_score == 0.85

    def test_search_with_similarity_threshold(self, search_manager, mock_embedding_store, temp_docs_dir):
        """Test search respects similarity threshold"""
        doc_path = temp_docs_dir / "documents" / "test.md"
        doc_path.write_text(
            """---
id: doc_1
title: Low Score Document
---

Content.""",
            encoding="utf-8",
        )

        # Mock results with low score
        mock_doc = HaystackDocument(
            content="Content.", meta={"id": "doc_1", "title": "Low Score Document", "source_file": str(doc_path)}
        )

        mock_embedding_store.search_similar_with_scores.return_value = [
            (mock_doc, 0.3)  # Below default threshold of 0.6
        ]

        # Perform search
        results, total = search_manager.search_documents("test query")

        # Results should be filtered out
        assert len(results) == 0
        assert total == 0

    def test_search_with_tag_filter(self, search_manager, mock_embedding_store, temp_docs_dir):
        """Test search with tag filtering"""
        doc1_path = temp_docs_dir / "documents" / "doc1.md"
        doc1_path.write_text(
            """---
id: doc_1
title: Python Doc
tags: [python, programming]
---

Python content.""",
            encoding="utf-8",
        )

        doc2_path = temp_docs_dir / "documents" / "doc2.md"
        doc2_path.write_text(
            """---
id: doc_2
title: JavaScript Doc
tags: [javascript, programming]
---

JavaScript content.""",
            encoding="utf-8",
        )

        # Mock search results
        mock_doc1 = HaystackDocument(
            content="Python content.",
            meta={
                "id": "doc_1",
                "title": "Python Doc",
                "source_file": str(doc1_path),
                "tags": ["python", "programming"],
            },
        )

        mock_doc2 = HaystackDocument(
            content="JavaScript content.",
            meta={
                "id": "doc_2",
                "title": "JavaScript Doc",
                "source_file": str(doc2_path),
                "tags": ["javascript", "programming"],
            },
        )

        mock_embedding_store.search_similar_with_scores.return_value = [
            (mock_doc1, 0.9),
            (mock_doc2, 0.8),
        ]

        # Search with tag filter
        results, total = search_manager.search_documents("programming", filters={"tags": ["python"]})

        # Only Python doc should match
        assert len(results) == 1
        assert results[0].title == "Python Doc"

    def test_search_with_category_filter(self, search_manager, mock_embedding_store, temp_docs_dir):
        """Test search with category filtering"""
        tech_doc = temp_docs_dir / "tech" / "tech-doc.md"
        tech_doc.write_text(
            """---
id: doc_tech
title: Tech Document
---

Tech content.""",
            encoding="utf-8",
        )

        regular_doc = temp_docs_dir / "documents" / "regular.md"
        regular_doc.write_text(
            """---
id: doc_reg
title: Regular Document
---

Regular content.""",
            encoding="utf-8",
        )

        # Mock results
        mock_tech = HaystackDocument(
            content="Tech content.", meta={"id": "doc_tech", "title": "Tech Document", "source_file": str(tech_doc)}
        )

        mock_reg = HaystackDocument(
            content="Regular content.",
            meta={"id": "doc_reg", "title": "Regular Document", "source_file": str(regular_doc)},
        )

        mock_embedding_store.search_similar_with_scores.return_value = [
            (mock_tech, 0.9),
            (mock_reg, 0.8),
        ]

        # Search with category filter
        results, total = search_manager.search_documents("content", filters={"category": "tech"})

        # Only tech doc should match
        assert len(results) == 1
        assert results[0].title == "Tech Document"

    def test_search_with_generated_filter(self, search_manager, mock_embedding_store, temp_docs_dir):
        """Test search with generated status filter"""
        generated_doc = temp_docs_dir / "generated" / "gen-doc.md"
        generated_doc.write_text(
            """---
id: doc_gen
title: Generated Document
generated: true
---

Generated content.""",
            encoding="utf-8",
        )

        captured_doc = temp_docs_dir / "documents" / "captured.md"
        captured_doc.write_text(
            """---
id: doc_cap
title: Captured Document
---

Captured content.""",
            encoding="utf-8",
        )

        # Mock results
        mock_gen = HaystackDocument(
            content="Generated content.",
            meta={"id": "doc_gen", "title": "Generated Document", "source_file": str(generated_doc)},
        )

        mock_cap = HaystackDocument(
            content="Captured content.",
            meta={"id": "doc_cap", "title": "Captured Document", "source_file": str(captured_doc)},
        )

        mock_embedding_store.search_similar_with_scores.return_value = [
            (mock_gen, 0.9),
            (mock_cap, 0.8),
        ]

        # Search for generated only
        results, total = search_manager.search_documents("content", filters={"generated": True})

        assert len(results) == 1
        assert results[0].title == "Generated Document"

        # Search for captured only
        results, total = search_manager.search_documents("content", filters={"generated": False})

        assert len(results) == 1
        assert results[0].title == "Captured Document"

    def test_search_with_date_filter(self, search_manager, mock_embedding_store, temp_docs_dir):
        """Test search with date range filtering"""
        old_doc = temp_docs_dir / "documents" / "old.md"
        old_doc.write_text(
            """---
id: doc_old
title: Old Document
created_date: '2024-01-01T10:00:00'
---

Old content.""",
            encoding="utf-8",
        )

        new_doc = temp_docs_dir / "documents" / "new.md"
        new_doc.write_text(
            """---
id: doc_new
title: New Document
created_date: '2025-06-01T10:00:00'
---

New content.""",
            encoding="utf-8",
        )

        # Mock results
        mock_old = HaystackDocument(
            content="Old content.",
            meta={
                "id": "doc_old",
                "title": "Old Document",
                "source_file": str(old_doc),
                "created_date": "2024-01-01T10:00:00",
            },
        )

        mock_new = HaystackDocument(
            content="New content.",
            meta={
                "id": "doc_new",
                "title": "New Document",
                "source_file": str(new_doc),
                "created_date": "2025-06-01T10:00:00",
            },
        )

        mock_embedding_store.search_similar_with_scores.return_value = [
            (mock_new, 0.9),
            (mock_old, 0.8),
        ]

        # Search with date filter
        results, total = search_manager.search_documents("content", filters={"date_from": "2025-01-01T00:00:00"})

        # Only new doc should match
        assert len(results) == 1
        assert results[0].title == "New Document"

    def test_search_max_results_limit(self, search_manager, mock_embedding_store, temp_docs_dir):
        """Test max results limit"""
        # Create multiple documents
        mock_results = []
        for i in range(10):
            doc_path = temp_docs_dir / "documents" / f"doc{i}.md"
            doc_path.write_text(f"---\nid: doc_{i}\ntitle: Doc {i}\n---\n\nContent {i}.", encoding="utf-8")

            mock_doc = HaystackDocument(
                content=f"Content {i}.", meta={"id": f"doc_{i}", "title": f"Doc {i}", "source_file": str(doc_path)}
            )
            mock_results.append((mock_doc, 0.9 - i * 0.01))

        mock_embedding_store.search_similar_with_scores.return_value = mock_results

        # Search with limit
        results, total = search_manager.search_documents("content", max_results=5)

        assert len(results) == 5
        assert total == 5

    def test_search_deduplicates_documents(self, search_manager, mock_embedding_store, temp_docs_dir):
        """Test that search deduplicates results from same document"""
        doc_path = temp_docs_dir / "documents" / "test.md"
        doc_path.write_text(
            """---
id: doc_1
title: Test Document
---

Content.""",
            encoding="utf-8",
        )

        # Mock multiple chunks from same document
        mock_doc1 = HaystackDocument(
            content="Content chunk 1.",
            meta={"id": "doc_1", "title": "Test Document", "source_file": str(doc_path), "chunk_index": 0},
        )

        mock_doc2 = HaystackDocument(
            content="Content chunk 2.",
            meta={"id": "doc_1", "title": "Test Document", "source_file": str(doc_path), "chunk_index": 1},
        )

        mock_embedding_store.search_similar_with_scores.return_value = [
            (mock_doc1, 0.9),
            (mock_doc2, 0.85),
        ]

        # Search
        results, total = search_manager.search_documents("content")

        # Should only get one result (deduplicated)
        assert len(results) == 1
        assert results[0].title == "Test Document"


class TestSnippetGeneration:
    """Tests for snippet generation"""

    def test_generate_snippet_short_content(self, search_manager):
        """Test snippet generation with short content"""
        content = "This is a short piece of content."
        snippet = search_manager._generate_snippet(content, "content", max_length=200)

        assert snippet == content

    def test_generate_snippet_with_query_match(self, search_manager):
        """Test snippet generation centered around query"""
        content = (
            "Start of content. "
            + "Some text. " * 20
            + "Important query match here. "
            + "Some more text. " * 20
            + "End."
        )

        snippet = search_manager._generate_snippet(content, "query match", max_length=100)

        assert "query match" in snippet.lower()
        assert "..." in snippet  # Should have ellipsis

    def test_generate_snippet_no_query_match(self, search_manager):
        """Test snippet generation when query not found"""
        content = "A" * 300  # Long content without query

        snippet = search_manager._generate_snippet(content, "nonexistent query", max_length=100)

        assert len(snippet) <= 100


class TestGetSearchStats:
    """Tests for get_search_stats"""

    def test_get_stats(self, search_manager, mock_embedding_store):
        """Test getting search statistics"""
        stats = search_manager.get_search_stats()

        assert stats["total_chunks"] == 10
        assert stats["unique_documents"] == 2
        assert stats["collection_name"] == "test_collection"
        assert stats["search_functional"] is True
        assert "/test/path" in stats["persist_directory"]
