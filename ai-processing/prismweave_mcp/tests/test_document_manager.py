"""
Tests for Document Manager

Comprehensive tests for document CRUD operations, metadata handling,
and document lifecycle management.
"""

import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from prismweave_mcp.managers.document_manager import DocumentManager
from src.core.config import Config, MCPConfig, MCPPathsConfig, MCPCreationConfig


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
def document_manager(test_config, temp_docs_dir):
    """Create document manager with temp directory"""
    test_config.mcp.paths.documents_root = str(temp_docs_dir)
    return DocumentManager(test_config)


class TestDocumentManagerGetByID:
    """Tests for get_document_by_id"""

    def test_get_existing_document(self, document_manager, temp_docs_dir):
        """Test getting an existing document by ID"""
        # Create test document
        doc_path = temp_docs_dir / "documents" / "test.md"
        doc_path.write_text(
            """---
id: doc_test_123
title: Test Document
tags: [test, sample]
created_date: '2025-01-01T10:00:00'
---

This is test content.""",
            encoding="utf-8",
        )

        document = document_manager.get_document_by_id("doc_test_123")

        assert document is not None
        assert document.id == "doc_test_123"
        assert document.metadata.title == "Test Document"
        assert "test" in document.metadata.tags
        assert "This is test content." in document.content

    def test_get_nonexistent_document(self, document_manager):
        """Test getting a document that doesn't exist"""
        document = document_manager.get_document_by_id("nonexistent_id")

        assert document is None

    def test_get_document_with_embedding_store(self, document_manager, temp_docs_dir):
        """Test getting document when embedding store is available"""
        # Create mock embedding store
        mock_store = MagicMock()
        mock_store.document_store.filter_documents.return_value = [
            MagicMock(meta={"source_file": str(temp_docs_dir / "documents" / "test.md")})
        ]

        document_manager.embedding_store = mock_store

        # Create test document
        doc_path = temp_docs_dir / "documents" / "test.md"
        doc_path.write_text(
            """---
id: doc_embed_123
title: Embedded Document
---

Content.""",
            encoding="utf-8",
        )

        document = document_manager.get_document_by_id("doc_embed_123")

        assert document is not None
        assert document.id == "doc_embed_123"


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
        document_manager.create_document(title="Test", content="This is test content for duplicate test.", custom_filename="duplicate.md")

        # Try to create duplicate
        with pytest.raises(ValueError, match="already exists"):
            document_manager.create_document(title="Test2", content="This is more test content.", custom_filename="duplicate.md")

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

    def test_get_metadata_by_id(self, document_manager, temp_docs_dir):
        """Test getting metadata by ID"""
        doc_path = temp_docs_dir / "documents" / "test.md"
        doc_path.write_text(
            """---
id: meta_doc_1
title: Metadata Test
tags: [test]
---
Content.""",
            encoding="utf-8",
        )

        metadata = document_manager.get_document_metadata(document_id="meta_doc_1")

        assert metadata is not None
        assert metadata.title == "Metadata Test"
        assert "test" in metadata.tags

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
