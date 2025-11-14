"""
Tests for Processing Manager
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest
import pytest_asyncio

from prismweave_mcp.managers.processing_manager import ProcessingManager
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
        (docs_root / "tech").mkdir()

        yield docs_root


@pytest.fixture
def mock_document_processor():
    """Create mock DocumentProcessor"""
    from haystack import Document as HaystackDocument

    mock = MagicMock()
    # Mock process_document to return Haystack Documents
    mock.process_document.return_value = [
        HaystackDocument(content="chunk 1", meta={"source": "test.md"}),
        HaystackDocument(content="chunk 2", meta={"source": "test.md"}),
    ]
    return mock


@pytest.fixture
def mock_embedding_store():
    """Create mock EmbeddingStore"""

    mock = MagicMock()
    mock.get_document_count.return_value = 0
    mock.add_document = MagicMock()
    mock.get_file_document_count = MagicMock(return_value=0)
    mock.remove_file_documents = MagicMock(return_value=True)
    return mock


@pytest_asyncio.fixture
async def processing_manager(test_config, temp_docs_dir, mock_document_processor, mock_embedding_store):
    """Create processing manager with temp directory"""
    # Override docs root in config
    test_config.mcp.paths.documents_root = str(temp_docs_dir)

    manager = ProcessingManager(test_config, mock_document_processor, mock_embedding_store)
    await manager.initialize()
    yield manager


class TestGenerateEmbeddings:
    """Tests for generate_embeddings"""

    @pytest.mark.asyncio
    async def test_generate_embeddings_success(self, processing_manager, temp_docs_dir, mock_embedding_store):
        """Test successful embedding generation"""
        # Create test document
        doc_path = temp_docs_dir / "documents" / "test.md"
        doc_path.write_text(
            """---
id: doc_1
title: Test Document
---

This is test content.""",
            encoding="utf-8",
        )

        # Mock that no embeddings exist yet
        mock_embedding_store.get_file_document_count.return_value = 0

        # Generate embeddings
        result = await processing_manager.generate_embeddings(doc_path)

        assert result["success"] is True
        assert result["chunks_processed"] == 2  # Mock returns 2 chunks
        # Verify add_document was called
        mock_embedding_store.add_document.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_embeddings_force_regenerate(self, processing_manager, temp_docs_dir, mock_embedding_store):
        """Test force regenerating existing embeddings"""

        doc_path = temp_docs_dir / "documents" / "test.md"
        doc_path.write_text(
            """---
id: doc_1
title: Test Document
---

Content.""",
            encoding="utf-8",
        )

        # Mock that embeddings already exist
        mock_embedding_store.get_file_document_count.return_value = 3

        # Force regenerate
        result = await processing_manager.generate_embeddings(doc_path, force_regenerate=True)

        assert result["success"] is True
        mock_embedding_store.remove_file_documents.assert_called_once_with(doc_path)
        mock_embedding_store.add_document.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_embeddings_skip_existing(self, processing_manager, temp_docs_dir, mock_embedding_store):
        """Test skipping when embeddings already exist"""

        doc_path = temp_docs_dir / "documents" / "test.md"
        doc_path.write_text("---\nid: doc_1\n---\nContent.", encoding="utf-8")

        # Mock that embeddings exist
        mock_embedding_store.get_file_document_count.return_value = 2

        # Generate without force
        result = await processing_manager.generate_embeddings(doc_path, force_regenerate=False)

        assert result["success"] is True
        assert result["chunks_processed"] == 2
        assert "already exist" in result["message"]
        # Should not add documents
        mock_embedding_store.add_document.assert_not_called()
        mock_embedding_store.remove_file_documents.assert_not_called()

    @pytest.mark.asyncio
    async def test_generate_embeddings_nonexistent_file(self, processing_manager, mock_document_processor):
        """Test handling of nonexistent file"""
        nonexistent_path = Path("documents/nonexistent.md")

        # Mock processor to raise error for nonexistent file
        mock_document_processor.process_document.side_effect = FileNotFoundError("File not found")

        result = await processing_manager.generate_embeddings(nonexistent_path)

        assert result["success"] is False
        assert "Error" in result["message"]

    @pytest.mark.asyncio
    async def test_generate_embeddings_invalid_path(self, processing_manager, mock_document_processor):
        """Test handling of invalid path"""
        invalid_path = Path("../../etc/passwd")

        # Mock processor to raise error
        mock_document_processor.process_document.side_effect = ValueError("Invalid path")

        result = await processing_manager.generate_embeddings(invalid_path)

        assert result["success"] is False
        assert "Error" in result["message"]


class TestGenerateTags:
    """Tests for generate_tags"""

    @pytest.mark.asyncio
    async def test_generate_tags_basic(self, processing_manager, temp_docs_dir):
        """Test basic tag generation"""
        doc_path = temp_docs_dir / "documents" / "test.md"
        doc_path.write_text(
            """---
id: doc_1
title: Machine Learning Article
---

This article discusses neural networks and deep learning.""",
            encoding="utf-8",
        )

        result = await processing_manager.generate_tags(doc_path, max_tags=5)

        assert result["success"] is True
        assert isinstance(result["tags"], list)
        assert len(result["tags"]) > 0
        assert len(result["tags"]) <= 5

    @pytest.mark.asyncio
    async def test_generate_tags_with_max_limit(self, processing_manager, temp_docs_dir):
        """Test tag generation with max limit"""
        doc_path = temp_docs_dir / "documents" / "test.md"
        doc_path.write_text("---\nid: doc_1\n---\nContent about AI and ML.", encoding="utf-8")

        result = await processing_manager.generate_tags(doc_path, max_tags=3)

        assert result["success"] is True
        assert len(result["tags"]) <= 3

    @pytest.mark.asyncio
    async def test_generate_tags_nonexistent_file(self, processing_manager):
        """Test tag generation for nonexistent file"""
        nonexistent_path = Path("documents/nonexistent.md")

        result = await processing_manager.generate_tags(nonexistent_path)

        assert result["success"] is False
        assert result["tags"] == []
        assert "Error" in result["message"]


class TestAutoProcessDocument:
    """Tests for auto_process_document"""

    @pytest.mark.asyncio
    async def test_auto_process_both(self, processing_manager, temp_docs_dir, mock_embedding_store):
        """Test auto-processing with both embeddings and tags"""
        doc_path = temp_docs_dir / "documents" / "test.md"
        doc_path.write_text(
            """---
id: doc_1
title: Test Document
tags: [existing]
---

Content.""",
            encoding="utf-8",
        )

        mock_embedding_store.get_file_document_count.return_value = 0

        result = await processing_manager.auto_process_document(
            doc_path, generate_embeddings=True, generate_tags=True, update_metadata=True
        )

        assert result["success"] is True
        assert result["embeddings_result"] is not None
        assert result["embeddings_result"]["success"] is True
        assert result["tags_result"] is not None
        assert result["tags_result"]["success"] is True

    @pytest.mark.asyncio
    async def test_auto_process_embeddings_only(self, processing_manager, temp_docs_dir, mock_embedding_store):
        """Test auto-processing with embeddings only"""
        doc_path = temp_docs_dir / "documents" / "test.md"
        doc_path.write_text("---\nid: doc_1\n---\nContent.", encoding="utf-8")

        mock_embedding_store.get_file_document_count.return_value = 0

        result = await processing_manager.auto_process_document(doc_path, generate_embeddings=True, generate_tags=False)

        assert result["success"] is True
        assert result["embeddings_result"] is not None
        assert result["embeddings_result"]["success"] is True
        assert result["tags_result"] is None

    @pytest.mark.asyncio
    async def test_auto_process_tags_only(self, processing_manager, temp_docs_dir):
        """Test auto-processing with tags only"""
        doc_path = temp_docs_dir / "documents" / "test.md"
        doc_path.write_text("---\nid: doc_1\n---\nContent.", encoding="utf-8")

        result = await processing_manager.auto_process_document(
            doc_path, generate_embeddings=False, generate_tags=True, update_metadata=True
        )

        assert result["success"] is True
        assert result["embeddings_result"] is None
        assert result["tags_result"] is not None
        assert result["tags_result"]["success"] is True

    @pytest.mark.asyncio
    async def test_auto_process_no_metadata_update(self, processing_manager, temp_docs_dir, mock_embedding_store):
        """Test auto-processing without metadata update"""
        doc_path = temp_docs_dir / "documents" / "test.md"
        doc_path.write_text("---\nid: doc_1\ntags: [test]\n---\nContent.", encoding="utf-8")

        mock_embedding_store.get_file_document_count.return_value = 0

        result = await processing_manager.auto_process_document(
            doc_path, generate_embeddings=True, generate_tags=True, update_metadata=False
        )

        # Metadata update is not yet implemented, so no change to file
        # Just verify the processing completed
        assert result["success"] is True
        # Frontmatter should remain unchanged
        content = doc_path.read_text(encoding="utf-8")
        assert "tags: [test]" in content


class TestGetProcessingStatus:
    """Tests for get_processing_status"""

    @pytest.mark.asyncio
    async def test_get_status_with_embeddings(self, processing_manager, temp_docs_dir, mock_embedding_store):
        """Test getting status for document with embeddings"""

        doc_path = temp_docs_dir / "documents" / "test.md"
        doc_path.write_text("---\nid: doc_1\n---\nContent.", encoding="utf-8")

        # Mock existing embeddings
        mock_embedding_store.get_file_document_count.return_value = 2

        status = await processing_manager.get_processing_status(doc_path)

        assert status["document_id"] == str(doc_path)
        assert status["has_embeddings"] is True
        assert status["embedding_count"] == 2

    @pytest.mark.asyncio
    async def test_get_status_without_embeddings(self, processing_manager, temp_docs_dir, mock_embedding_store):
        """Test getting status for document without embeddings"""
        doc_path = temp_docs_dir / "documents" / "test.md"
        doc_path.write_text("---\nid: doc_1\n---\nContent.", encoding="utf-8")

        mock_embedding_store.get_file_document_count.return_value = 0

        status = await processing_manager.get_processing_status(doc_path)

        assert status["document_id"] == str(doc_path)
        assert status["has_embeddings"] is False
        assert status["embedding_count"] == 0

    @pytest.mark.asyncio
    async def test_get_status_nonexistent(self, processing_manager, mock_embedding_store):
        """Test getting status for nonexistent document"""
        nonexistent_path = Path("documents/nonexistent.md")

        # Mock error for nonexistent document
        mock_embedding_store.get_file_document_count.side_effect = Exception("Document not found")

        status = await processing_manager.get_processing_status(nonexistent_path)

        assert status["document_id"] == str(nonexistent_path)
        assert status["has_embeddings"] is False
        assert "error" in status


class TestRemoveEmbeddings:
    """Tests for remove_embeddings"""

    @pytest.mark.asyncio
    async def test_remove_embeddings_success(self, processing_manager, temp_docs_dir, mock_embedding_store):
        """Test successful embedding removal"""
        doc_path = temp_docs_dir / "documents" / "test.md"
        doc_path.write_text("---\nid: doc_1\n---\nContent.", encoding="utf-8")

        mock_embedding_store.get_file_document_count.return_value = 2
        mock_embedding_store.remove_file_documents.return_value = True

        result = await processing_manager.remove_embeddings(doc_path)

        assert result["success"] is True
        assert result["chunks_removed"] == 2
        mock_embedding_store.remove_file_documents.assert_called_once_with(doc_path)

    @pytest.mark.asyncio
    async def test_remove_embeddings_no_embeddings(self, processing_manager, temp_docs_dir, mock_embedding_store):
        """Test removing embeddings when none exist"""
        doc_path = temp_docs_dir / "documents" / "test.md"
        doc_path.write_text("---\nid: doc_1\n---\nContent.", encoding="utf-8")

        mock_embedding_store.get_file_document_count.return_value = 0
        mock_embedding_store.remove_file_documents.return_value = False

        result = await processing_manager.remove_embeddings(doc_path)

        assert result["success"] is False
        assert result["chunks_removed"] == 0
        mock_embedding_store.remove_file_documents.assert_called_once_with(doc_path)

    @pytest.mark.asyncio
    async def test_remove_embeddings_nonexistent_file(self, processing_manager, mock_embedding_store):
        """Test removing embeddings for nonexistent file"""
        nonexistent_path = Path("documents/nonexistent.md")

        # Mock error
        mock_embedding_store.get_file_document_count.side_effect = Exception("Document not found")

        result = await processing_manager.remove_embeddings(nonexistent_path)

        assert result["success"] is False
        assert "Error" in result["message"]
