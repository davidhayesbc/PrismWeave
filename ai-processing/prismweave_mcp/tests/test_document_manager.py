"""
Tests for Document Manager

Comprehensive tests for document CRUD operations, metadata handling,
and document lifecycle management.
"""

import tempfile
from pathlib import Path

import pytest

from prismweave_mcp.managers.document_manager import DocumentManager
from src.core.config import Config, MCPConfig, MCPCreationConfig, MCPPathsConfig
from src.core.embedding_store import EmbeddingStore


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


@pytest.fixture
def test_chroma_db_dir():
    """Create temporary ChromaDB directory"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def test_embedding_store(test_config, test_chroma_db_dir, temp_docs_dir):
    """Create test embedding store with ChromaDB"""
    # Update config to use test ChromaDB path
    test_config.chroma_db_path = test_chroma_db_dir
    test_config.collection_name = "test_documents"
    test_config.ollama_host = "http://localhost:11434"
    test_config.embedding_model = "nomic-embed-text"

    # Create embedding store
    embedding_store = EmbeddingStore(test_config)

    # Populate with test documents
    from haystack import Document

    test_docs = [
        Document(
            content="This is a test document about Python programming.",
            meta={
                "id": "test_doc_1",
                "title": "Python Guide",
                "source_file": str(temp_docs_dir / "documents" / "python-guide.md"),
                "tags": "python, programming",
            },
        ),
        Document(
            content="This document covers JavaScript fundamentals.",
            meta={
                "id": "test_doc_2",
                "title": "JavaScript Basics",
                "source_file": str(temp_docs_dir / "documents" / "js-basics.md"),
                "tags": "javascript, programming",
            },
        ),
        Document(
            content="A comprehensive guide to Docker containers.",
            meta={
                "id": "test_doc_3",
                "title": "Docker Guide",
                "source_file": str(temp_docs_dir / "tech" / "docker-guide.md"),
                "tags": "docker, devops",
            },
        ),
    ]

    # Write documents directly to the store without embeddings for faster tests
    try:
        embedding_store.document_store.write_documents(test_docs)
    except Exception as e:
        # If write fails (e.g., ChromaDB not available), continue with empty store
        print(f"Warning: Failed to populate test embedding store: {e}")

    yield embedding_store

    # Cleanup
    try:
        embedding_store.clear_collection()
    except Exception:
        pass


@pytest.fixture
def sample_test_documents(temp_docs_dir):
    """Create sample test documents on disk"""
    # Document 1: Python guide
    doc1_path = temp_docs_dir / "documents" / "python-guide.md"
    doc1_path.write_text(
        """---
id: test_doc_1
title: Python Guide
tags: [python, programming]
created_date: '2025-01-01T10:00:00'
word_count: 10
---

This is a test document about Python programming.""",
        encoding="utf-8",
    )

    # Document 2: JavaScript basics
    doc2_path = temp_docs_dir / "documents" / "js-basics.md"
    doc2_path.write_text(
        """---
id: test_doc_2
title: JavaScript Basics
tags: [javascript, programming]
created_date: '2025-01-02T10:00:00'
word_count: 7
---

This document covers JavaScript fundamentals.""",
        encoding="utf-8",
    )

    # Document 3: Docker guide (in tech folder)
    doc3_path = temp_docs_dir / "tech" / "docker-guide.md"
    doc3_path.write_text(
        """---
id: test_doc_3
title: Docker Guide
tags: [docker, devops]
created_date: '2025-01-03T10:00:00'
word_count: 7
category: tech
---

A comprehensive guide to Docker containers.""",
        encoding="utf-8",
    )

    return [doc1_path, doc2_path, doc3_path]


@pytest.fixture
def document_manager(test_config, temp_docs_dir):
    """Create document manager with temp directory (no embedding store)"""
    test_config.mcp.paths.documents_root = str(temp_docs_dir)
    return DocumentManager(test_config)


@pytest.fixture
def document_manager_with_embeddings(test_config, temp_docs_dir, test_embedding_store, sample_test_documents):
    """Create document manager with embedding store and sample documents"""
    test_config.mcp.paths.documents_root = str(temp_docs_dir)
    return DocumentManager(test_config, embedding_store=test_embedding_store)


class TestDocumentManagerGetByID:
    """Tests for get_document_by_id"""

    def test_get_existing_document_with_embedding_store(self, document_manager_with_embeddings):
        """Test getting an existing document by ID using embedding store"""
        document = document_manager_with_embeddings.get_document_by_id("test_doc_1")

        assert document is not None
        assert document.id == "test_doc_1"
        assert document.metadata.title == "Python Guide"
        assert "python" in document.metadata.tags
        assert "This is a test document about Python programming." in document.content

    def test_get_nonexistent_document(self, document_manager_with_embeddings):
        """Test getting a document that doesn't exist"""
        document = document_manager_with_embeddings.get_document_by_id("nonexistent_id")

        assert document is None

    def test_get_document_without_embedding_store(self, document_manager, temp_docs_dir, sample_test_documents):
        """Test getting document when embedding store is not available returns None"""
        # Without embedding store, get_document_by_id should return None
        # Users should use get_document_by_path instead
        document = document_manager.get_document_by_id("test_doc_2")

        assert document is None


class TestDocumentManagerGetByPath:
    """Tests for get_document_by_path"""

    def test_get_by_relative_path(self, document_manager, temp_docs_dir):
        """Test getting document by relative path"""
        doc_path = temp_docs_dir / "documents" / "test.md"
        doc_path.write_text(
            """---
id: doc_path_123
title: Path Document
---

Content.""",
            encoding="utf-8",
        )

        document = document_manager.get_document_by_path("documents/test.md")

        assert document is not None
        assert document.metadata.title == "Path Document"

    def test_get_by_absolute_path(self, document_manager, temp_docs_dir):
        """Test getting document by absolute path"""
        doc_path = temp_docs_dir / "documents" / "test.md"
        doc_path.write_text("---\nid: doc_abs\n---\nContent.", encoding="utf-8")

        document = document_manager.get_document_by_path(str(doc_path))

        assert document is not None

    def test_get_by_path_outside_root(self, document_manager):
        """Test getting document outside root raises error"""
        with pytest.raises(ValueError, match="not safe or outside documents root"):
            document_manager.get_document_by_path("../../etc/passwd")

    def test_get_nonexistent_path(self, document_manager):
        """Test getting document that doesn't exist"""
        document = document_manager.get_document_by_path("documents/nonexistent.md")

        assert document is None


class TestDocumentManagerList:
    """Tests for list_documents"""

    def test_list_all_documents(self, document_manager, temp_docs_dir):
        """Test listing all documents"""
        # Create multiple documents
        for i in range(3):
            doc_path = temp_docs_dir / "documents" / f"doc{i}.md"
            doc_path.write_text(f"---\nid: doc_{i}\ntitle: Document {i}\n---\nContent {i}.", encoding="utf-8")

        documents, total = document_manager.list_documents()

        assert len(documents) == 3
        assert total == 3

    def test_list_with_category_filter(self, document_manager, temp_docs_dir):
        """Test listing documents with category filter"""
        # Create documents in different categories
        tech_doc = temp_docs_dir / "tech" / "tech-doc.md"
        tech_doc.write_text("---\nid: tech_doc\ntitle: Tech\n---\nContent.", encoding="utf-8")

        general_doc = temp_docs_dir / "documents" / "general.md"
        general_doc.write_text("---\nid: general_doc\ntitle: General\n---\nContent.", encoding="utf-8")

        documents, total = document_manager.list_documents(category="tech")

        assert len(documents) == 1
        assert documents[0].title == "Tech"

    def test_list_with_tag_filter(self, document_manager, temp_docs_dir):
        """Test listing documents with tag filter"""
        # Create documents with different tags
        doc1 = temp_docs_dir / "documents" / "doc1.md"
        doc1.write_text(
            """---
id: doc_1
title: Python Doc
tags: [python, programming]
---
Content.""",
            encoding="utf-8",
        )

        doc2 = temp_docs_dir / "documents" / "doc2.md"
        doc2.write_text(
            """---
id: doc_2
title: JavaScript Doc
tags: [javascript, programming]
---
Content.""",
            encoding="utf-8",
        )

        documents, total = document_manager.list_documents(tags=["python"])

        assert len(documents) == 1
        assert documents[0].title == "Python Doc"

    def test_list_generated_only(self, document_manager, temp_docs_dir):
        """Test listing generated documents only"""
        # Create generated and captured documents
        gen_doc = temp_docs_dir / "generated" / "generated.md"
        gen_doc.write_text("---\nid: gen_doc\ntitle: Generated\n---\nContent.", encoding="utf-8")

        cap_doc = temp_docs_dir / "documents" / "captured.md"
        cap_doc.write_text("---\nid: cap_doc\ntitle: Captured\n---\nContent.", encoding="utf-8")

        documents, total = document_manager.list_documents(generated_only=True)

        assert len(documents) == 1
        assert documents[0].title == "Generated"

    def test_list_with_sorting(self, document_manager, temp_docs_dir):
        """Test listing with different sort options"""
        # Create documents with different dates
        doc1 = temp_docs_dir / "documents" / "doc1.md"
        doc1.write_text(
            """---
id: doc_1
title: Older Document
created_date: '2024-01-01T10:00:00'
---
Content.""",
            encoding="utf-8",
        )

        doc2 = temp_docs_dir / "documents" / "doc2.md"
        doc2.write_text(
            """---
id: doc_2
title: Newer Document
created_date: '2025-01-01T10:00:00'
---
Content.""",
            encoding="utf-8",
        )

        # Sort by date descending (newest first)
        documents, _ = document_manager.list_documents(sort_by="created_date", sort_order="desc")

        assert documents[0].title == "Newer Document"
        assert documents[1].title == "Older Document"

    def test_list_with_limit(self, document_manager, temp_docs_dir):
        """Test listing with limit"""
        # Create multiple documents
        for i in range(5):
            doc_path = temp_docs_dir / "documents" / f"doc{i}.md"
            doc_path.write_text(f"---\nid: doc_{i}\ntitle: Document {i}\n---\nContent.", encoding="utf-8")

        documents, total = document_manager.list_documents(limit=3)

        assert len(documents) == 3
        assert total == 5  # Total count before limit


class TestDocumentManagerCreate:
    """Tests for create_document"""

    def test_create_basic_document(self, document_manager, temp_docs_dir):
        """Test creating a basic document"""
        document, file_path = document_manager.create_document(
            title="New Document", content="# Test\n\nContent here.", tags=["test"]
        )

        assert document.metadata.title == "New Document"
        assert "test" in document.metadata.tags
        assert file_path.exists()
        assert file_path.parent == temp_docs_dir / "generated"

    def test_create_with_category(self, document_manager, temp_docs_dir):
        """Test creating document in specific category"""
        document, file_path = document_manager.create_document(
            title="Tech Article", content="This is test content for a tech article.", category="tech"
        )

        assert file_path.parent == temp_docs_dir / "generated" / "tech"
        assert file_path.exists()

    def test_create_with_custom_filename(self, document_manager, temp_docs_dir):
        """Test creating document with custom filename"""
        document, file_path = document_manager.create_document(
            title="Custom", content="This is custom content for testing.", custom_filename="custom-name.md"
        )

        assert file_path.name == "custom-name.md"

    def test_create_duplicate_raises_error(self, document_manager, temp_docs_dir):
        """Test creating duplicate document raises error"""
        # Create first document
        document_manager.create_document(
            title="Test", content="This is test content for duplicate test.", custom_filename="duplicate.md"
        )

        # Try to create duplicate
        with pytest.raises(ValueError, match="already exists"):
            document_manager.create_document(
                title="Test2", content="This is more test content.", custom_filename="duplicate.md"
            )

    def test_create_with_invalid_markdown(self, document_manager):
        """Test creating document with invalid markdown raises error"""
        with pytest.raises(ValueError, match="Invalid markdown"):
            document_manager.create_document(title="Test", content="")  # Empty content

    def test_create_with_metadata(self, document_manager, temp_docs_dir):
        """Test creating document with additional metadata"""
        custom_metadata = {"author": "John Doe", "source_url": "https://example.com"}

        document, file_path = document_manager.create_document(
            title="Test", content="This is test content with custom metadata.", metadata=custom_metadata
        )

        # Read file and verify metadata
        content = file_path.read_text(encoding="utf-8")
        assert "author: John Doe" in content
        assert "source_url: https://example.com" in content


class TestDocumentManagerUpdate:
    """Tests for update_document"""

    def test_update_title(self, document_manager, temp_docs_dir):
        """Test updating document title"""
        # Create document
        doc_path = temp_docs_dir / "generated" / "test.md"
        doc_path.write_text(
            """---
id: doc_update_1
title: Original Title
---
Content.""",
            encoding="utf-8",
        )

        # Update title
        document, _ = document_manager.update_document(document_id="doc_update_1", title="Updated Title")

        assert document.metadata.title == "Updated Title"

    def test_update_content(self, document_manager, temp_docs_dir):
        """Test updating document content"""
        doc_path = temp_docs_dir / "generated" / "test.md"
        doc_path.write_text("---\nid: doc_update_2\n---\nOld content.", encoding="utf-8")

        document, _ = document_manager.update_document(document_id="doc_update_2", content="New content.")

        assert "New content." in document.content

    def test_update_tags(self, document_manager, temp_docs_dir):
        """Test updating document tags"""
        doc_path = temp_docs_dir / "generated" / "test.md"
        doc_path.write_text("---\nid: doc_update_3\ntags: [old]\n---\nContent.", encoding="utf-8")

        document, _ = document_manager.update_document(document_id="doc_update_3", tags=["new", "updated"])

        assert "new" in document.metadata.tags
        assert "updated" in document.metadata.tags

    def test_update_captured_document_raises_error(self, document_manager, temp_docs_dir):
        """Test updating captured document raises error"""
        # Create captured document (not in generated/)
        doc_path = temp_docs_dir / "documents" / "captured.md"
        doc_path.write_text("---\nid: cap_doc\n---\nContent.", encoding="utf-8")

        with pytest.raises(ValueError, match="read-only"):
            document_manager.update_document(document_id="cap_doc", title="New Title")

    def test_update_nonexistent_document(self, document_manager):
        """Test updating nonexistent document raises error"""
        with pytest.raises(ValueError, match="not found"):
            document_manager.update_document(document_id="nonexistent", title="Title")

    def test_update_with_merge_metadata(self, document_manager, temp_docs_dir):
        """Test updating document with metadata merge"""
        doc_path = temp_docs_dir / "generated" / "test.md"
        doc_path.write_text(
            """---
id: doc_update_4
title: Test
author: John
---
Content.""",
            encoding="utf-8",
        )

        document, _ = document_manager.update_document(
            document_id="doc_update_4", metadata={"source_url": "https://example.com"}, merge_metadata=True
        )

        # Author should still be present
        content = doc_path.read_text(encoding="utf-8")
        assert "author: John" in content
        assert "source_url: https://example.com" in content


class TestDocumentManagerGetMetadata:
    """Tests for get_document_metadata"""

    def test_get_metadata_by_id(self, document_manager_with_embeddings):
        """Test getting metadata by ID"""
        metadata = document_manager_with_embeddings.get_document_metadata(document_id="test_doc_1")

        assert metadata is not None
        assert metadata.title == "Python Guide"
        assert "python" in metadata.tags

    def test_get_metadata_by_path(self, document_manager, temp_docs_dir):
        """Test getting metadata by path"""
        doc_path = temp_docs_dir / "documents" / "test.md"
        doc_path.write_text("---\nid: meta_doc_2\ntitle: Path Metadata\n---\nContent.", encoding="utf-8")

        metadata = document_manager.get_document_metadata(path="documents/test.md")

        assert metadata is not None
        assert metadata.title == "Path Metadata"

    def test_get_metadata_nonexistent(self, document_manager):
        """Test getting metadata for nonexistent document"""
        metadata = document_manager.get_document_metadata(document_id="nonexistent")

        assert metadata is None

    def test_get_metadata_requires_id_or_path(self, document_manager):
        """Test that getting metadata requires ID or path"""
        with pytest.raises(ValueError, match="Must provide either"):
            document_manager.get_document_metadata()
