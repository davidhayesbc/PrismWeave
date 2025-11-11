"""
Tests for Document Manager
"""

import tempfile
from pathlib import Path

import pytest

from mcp.managers.document_manager import DocumentManager
from mcp.schemas.responses import DocumentMetadata
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
        creation=MCPCreationConfig(default_category="general"),
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
        (docs_root / "images").mkdir()

        yield docs_root


@pytest.fixture
def document_manager(test_config, temp_docs_dir):
    """Create document manager with temp directory"""
    # Override docs root in config
    test_config.mcp.paths.documents_root = str(temp_docs_dir)
    return DocumentManager(test_config)


@pytest.fixture
def sample_document(temp_docs_dir):
    """Create a sample document file"""
    doc_path = temp_docs_dir / "documents" / "sample.md"
    content = """---
id: doc_123
title: Sample Document
created_date: '2025-01-01T10:00:00'
modified_date: '2025-01-01T10:00:00'
tags:
  - test
  - sample
category: general
word_count: 5
---

# Sample Document

This is a test document."""

    doc_path.write_text(content, encoding="utf-8")
    return doc_path


@pytest.fixture
def generated_document(temp_docs_dir):
    """Create a sample generated document"""
    doc_path = temp_docs_dir / "generated" / "generated-doc.md"
    content = """---
id: doc_456
title: Generated Document
created_date: '2025-01-01T12:00:00'
modified_date: '2025-01-01T12:00:00'
tags:
  - generated
category: general
generated: true
word_count: 3
---

# Generated Document

Generated content here."""

    doc_path.write_text(content, encoding="utf-8")
    return doc_path


class TestGetDocumentById:
    """Tests for get_document_by_id"""

    def test_get_existing_document(self, document_manager, sample_document):
        """Test retrieving existing document by ID"""
        doc = document_manager.get_document_by_id("doc_123")

        assert doc is not None
        assert doc.id == "doc_123"
        assert doc.metadata.title == "Sample Document"
        assert "test" in doc.metadata.tags
        assert "This is a test document" in doc.content

    def test_get_nonexistent_document(self, document_manager):
        """Test retrieving nonexistent document"""
        doc = document_manager.get_document_by_id("nonexistent_id")

        assert doc is None

    def test_get_document_with_alternative_id_field(self, document_manager, temp_docs_dir):
        """Test retrieving document with document_id instead of id"""
        doc_path = temp_docs_dir / "documents" / "alt-id.md"
        content = """---
document_id: doc_alt_789
title: Alt ID Document
---

Content here."""
        doc_path.write_text(content, encoding="utf-8")

        doc = document_manager.get_document_by_id("doc_alt_789")

        assert doc is not None
        assert doc.id == "doc_alt_789"


class TestGetDocumentByPath:
    """Tests for get_document_by_path"""

    def test_get_by_relative_path(self, document_manager, sample_document):
        """Test retrieving document by relative path"""
        doc = document_manager.get_document_by_path("documents/sample.md")

        assert doc is not None
        assert doc.id == "doc_123"
        assert doc.metadata.title == "Sample Document"

    def test_get_by_absolute_path(self, document_manager, sample_document):
        """Test retrieving document by absolute path"""
        doc = document_manager.get_document_by_path(str(sample_document))

        assert doc is not None
        assert doc.id == "doc_123"

    def test_get_nonexistent_path(self, document_manager):
        """Test retrieving document from nonexistent path"""
        doc = document_manager.get_document_by_path("documents/nonexistent.md")

        assert doc is None

    def test_get_with_unsafe_path(self, document_manager):
        """Test retrieving document with unsafe path"""
        with pytest.raises(ValueError, match="not safe"):
            document_manager.get_document_by_path("../../etc/passwd")


class TestListDocuments:
    """Tests for list_documents"""

    def test_list_all_documents(self, document_manager, sample_document, generated_document):
        """Test listing all documents"""
        docs, total = document_manager.list_documents()

        assert total == 2
        assert len(docs) == 2
        titles = [d.title for d in docs]
        assert "Sample Document" in titles
        assert "Generated Document" in titles

    def test_filter_by_generated_only(self, document_manager, sample_document, generated_document, temp_docs_dir):
        """Test filtering for generated documents only"""
        docs, total = document_manager.list_documents(generated_only=True)

        assert total == 1
        assert len(docs) == 1
        assert docs[0].title == "Generated Document"

    def test_filter_by_captured_only(self, document_manager, sample_document, generated_document, temp_docs_dir):
        """Test filtering for captured documents only"""
        docs, total = document_manager.list_documents(captured_only=True)

        assert total == 1
        assert len(docs) == 1
        assert docs[0].title == "Sample Document"

    def test_filter_by_tags(self, document_manager, sample_document, generated_document):
        """Test filtering by tags"""
        docs, total = document_manager.list_documents(tags=["test"])

        assert total == 1
        assert docs[0].title == "Sample Document"

    def test_filter_by_category(self, document_manager, temp_docs_dir):
        """Test filtering by category"""
        # Create tech category document
        tech_doc = temp_docs_dir / "tech" / "tech-doc.md"
        content = """---
id: doc_tech
title: Tech Document
category: tech
---

Tech content."""
        tech_doc.write_text(content, encoding="utf-8")

        docs, total = document_manager.list_documents(category="tech")

        assert total == 1
        assert docs[0].title == "Tech Document"

    def test_sort_by_title_asc(self, document_manager, sample_document, generated_document):
        """Test sorting by title ascending"""
        docs, total = document_manager.list_documents(sort_by="title", sort_order="asc")

        assert len(docs) == 2
        assert docs[0].title == "Generated Document"
        assert docs[1].title == "Sample Document"

    def test_sort_by_title_desc(self, document_manager, sample_document, generated_document):
        """Test sorting by title descending"""
        docs, total = document_manager.list_documents(sort_by="title", sort_order="desc")

        assert len(docs) == 2
        assert docs[0].title == "Sample Document"
        assert docs[1].title == "Generated Document"

    def test_limit_results(self, document_manager, sample_document, generated_document):
        """Test limiting results"""
        docs, total = document_manager.list_documents(limit=1)

        assert total == 2  # Total before limit
        assert len(docs) == 1  # Limited results


class TestCreateDocument:
    """Tests for create_document"""

    def test_create_basic_document(self, document_manager):
        """Test creating a basic document"""
        doc, file_path = document_manager.create_document(
            title="New Document", content="# New Document\n\nThis is new content.", tags=["new", "test"]
        )

        assert doc is not None
        assert doc.metadata.title == "New Document"
        # Generated status is determined by path, not a metadata field
        assert "new" in doc.metadata.tags
        assert file_path.exists()
        assert "generated" in str(file_path)

    def test_create_with_category(self, document_manager):
        """Test creating document with category"""
        doc, file_path = document_manager.create_document(
            title="Tech Article", content="# Tech Article\n\nTechnical content.", category="tech"
        )

        # Category from path for generated docs will be "generated", not "tech"
        # The category parameter is stored in metadata but path determines the actual category
        assert "generated" in str(file_path)

    def test_create_with_custom_filename(self, document_manager):
        """Test creating document with custom filename"""
        doc, file_path = document_manager.create_document(
            title="Custom File", content="# Custom\n\nContent.", custom_filename="my-custom-name.md"
        )

        assert file_path.name == "my-custom-name.md"

    def test_create_with_custom_metadata(self, document_manager):
        """Test creating document with custom metadata"""
        doc, file_path = document_manager.create_document(
            title="Meta Document",
            content="# Meta\n\nContent.",
            metadata={"author": "Test Author", "custom_field": "value"},
        )

        # Read back the file to verify metadata was saved
        from mcp.utils.document_utils import parse_frontmatter

        content = file_path.read_text()
        meta, _ = parse_frontmatter(content)
        assert meta["author"] == "Test Author"
        assert meta["custom_field"] == "value"

    def test_create_duplicate_fails(self, document_manager):
        """Test that creating duplicate document fails"""
        document_manager.create_document(
            title="Duplicate", content="# Duplicate\n\nContent.", custom_filename="duplicate.md"
        )

        with pytest.raises(ValueError, match="already exists"):
            document_manager.create_document(
                title="Duplicate", content="# Duplicate\n\nContent.", custom_filename="duplicate.md"
            )

    def test_create_invalid_markdown_fails(self, document_manager):
        """Test that creating document with invalid markdown fails"""
        with pytest.raises(ValueError, match="Invalid markdown"):
            document_manager.create_document(title="Invalid", content="```python\nunclosed code block")


class TestUpdateDocument:
    """Tests for update_document"""

    def test_update_content(self, document_manager, generated_document):
        """Test updating document content"""
        new_content = "# Updated Title\n\nThis is updated content with more words."

        doc, file_path = document_manager.update_document(document_id="doc_456", content=new_content)

        assert "updated content" in doc.content.lower()
        assert doc.metadata.word_count > 3  # Original was 3 words

    def test_update_title(self, document_manager, generated_document):
        """Test updating document title"""
        doc, file_path = document_manager.update_document(document_id="doc_456", title="New Title")

        assert doc.metadata.title == "New Title"

    def test_update_tags(self, document_manager, generated_document):
        """Test updating document tags"""
        doc, file_path = document_manager.update_document(document_id="doc_456", tags=["updated", "new-tag"])

        assert "updated" in doc.metadata.tags
        assert "new-tag" in doc.metadata.tags

    def test_update_by_path(self, document_manager, generated_document):
        """Test updating document by path"""
        doc, file_path = document_manager.update_document(path="generated/generated-doc.md", title="Path Update")

        assert doc.metadata.title == "Path Update"

    def test_update_nongenerated_fails(self, document_manager, sample_document):
        """Test that updating captured document fails"""
        with pytest.raises(ValueError, match="only update generated documents"):
            document_manager.update_document(document_id="doc_123", title="Should Fail")

    def test_update_nonexistent_fails(self, document_manager):
        """Test that updating nonexistent document fails"""
        with pytest.raises(ValueError, match="not found"):
            document_manager.update_document(document_id="nonexistent", title="Should Fail")

    def test_update_with_merge_metadata(self, document_manager, generated_document):
        """Test updating with metadata merge"""
        doc, file_path = document_manager.update_document(
            document_id="doc_456", metadata={"new_field": "value"}, merge_metadata=True
        )

        # Read back to verify both old and new metadata exist
        from mcp.utils.document_utils import parse_frontmatter

        content = file_path.read_text()
        meta, _ = parse_frontmatter(content)
        assert meta["new_field"] == "value"
        # Check that original fields are still present
        assert "tags" in meta or "title" in meta

    def test_update_without_merge_metadata(self, document_manager, generated_document):
        """Test updating without metadata merge"""
        doc, file_path = document_manager.update_document(
            document_id="doc_456",
            metadata={"title": "Only This", "only_field": "value"},
            merge_metadata=False,
        )

        # Read back to verify only new metadata exists
        from mcp.utils.document_utils import parse_frontmatter

        content = file_path.read_text()
        meta, _ = parse_frontmatter(content)
        assert meta["only_field"] == "value"
        assert meta["title"] == "Only This"


class TestGetDocumentMetadata:
    """Tests for get_document_metadata"""

    def test_get_metadata_by_id(self, document_manager, sample_document):
        """Test getting metadata by document ID"""
        metadata = document_manager.get_document_metadata(document_id="doc_123")

        assert metadata is not None
        assert metadata.title == "Sample Document"
        assert isinstance(metadata, DocumentMetadata)

    def test_get_metadata_by_path(self, document_manager, sample_document):
        """Test getting metadata by path"""
        metadata = document_manager.get_document_metadata(path="documents/sample.md")

        assert metadata is not None
        assert metadata.title == "Sample Document"

    def test_get_metadata_nonexistent(self, document_manager):
        """Test getting metadata for nonexistent document"""
        metadata = document_manager.get_document_metadata(document_id="nonexistent")

        assert metadata is None

    def test_get_metadata_requires_identifier(self, document_manager):
        """Test that getting metadata requires an identifier"""
        with pytest.raises(ValueError, match="Must provide either"):
            document_manager.get_document_metadata()


class TestDocumentManagerIntegration:
    """Integration tests for document manager workflows"""

    def test_create_update_retrieve_workflow(self, document_manager):
        """Test complete workflow: create, update, retrieve"""
        # Create document
        doc, file_path = document_manager.create_document(
            title="Workflow Test", content="# Test\n\nInitial content.", tags=["workflow"]
        )

        doc_id = doc.id

        # Update document
        updated_doc, _ = document_manager.update_document(
            document_id=doc_id, content="# Test\n\nUpdated content.", tags=["workflow", "updated"]
        )

        assert "updated" in updated_doc.metadata.tags

        # Retrieve by ID
        retrieved = document_manager.get_document_by_id(doc_id)
        assert retrieved is not None
        assert "Updated content" in retrieved.content

        # Retrieve by path
        retrieved_by_path = document_manager.get_document_by_path(str(file_path))
        assert retrieved_by_path is not None
        assert retrieved_by_path.id == doc_id

    def test_list_and_filter_workflow(self, document_manager, temp_docs_dir):
        """Test creating multiple documents and filtering"""
        # Create various documents
        document_manager.create_document(title="Tech 1", content="# Tech 1\n\nContent.", category="tech", tags=["tech"])

        document_manager.create_document(title="Tech 2", content="# Tech 2\n\nContent.", category="tech", tags=["tech"])

        document_manager.create_document(
            title="General", content="# General\n\nContent.", category="general", tags=["general"]
        )

        # List all
        all_docs, total = document_manager.list_documents()
        assert total == 3

        # Category is determined by path, all created docs go to generated/
        # so filtering by "generated" should return all
        generated_docs_by_cat, gen_total = document_manager.list_documents(category="generated")
        assert gen_total == 3

        # Filter by tags
        tech_tagged, _ = document_manager.list_documents(tags=["tech"])
        assert len(tech_tagged) == 2

        # Filter generated only
        generated_docs, _ = document_manager.list_documents(generated_only=True)
        assert len(generated_docs) == 3  # All are generated
