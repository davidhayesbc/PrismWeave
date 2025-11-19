"""
Tests for EmbeddingStore - ChromaDB integration
"""

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from haystack import Document

from src.core.config import Config
from src.core.embedding_store import EmbeddingStore


class TestEmbeddingStoreInitialization:
    """Test EmbeddingStore initialization"""

    def test_store_initialization(self):
        """Test that EmbeddingStore can be initialized"""
        config = Config()

        # Use a temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            config.chroma_db_path = temp_dir

            store = EmbeddingStore(config)

            assert store.config == config
            assert store.document_embedder is not None
            assert store.text_embedder is not None
            assert store.document_store is not None
            assert Path(temp_dir).exists()

    def test_store_creates_directory(self):
        """Test that EmbeddingStore creates persist directory if it doesn't exist"""
        config = Config()

        with tempfile.TemporaryDirectory() as temp_dir:
            # Use a subdirectory that doesn't exist yet
            persist_dir = Path(temp_dir) / "new_chroma_db"
            config.chroma_db_path = str(persist_dir)

            store = EmbeddingStore(config)

            assert persist_dir.exists()
            assert persist_dir.is_dir()


class TestMetadataCleaning:
    """Test metadata cleaning functionality"""

    def test_clean_metadata_strings(self):
        """Test cleaning metadata with string values"""
        config = Config()

        with tempfile.TemporaryDirectory() as temp_dir:
            config.chroma_db_path = temp_dir
            store = EmbeddingStore(config)

            metadata = {"title": "Test Document", "author": "Test Author", "category": "test"}

            cleaned = store._clean_metadata(metadata)

            assert cleaned == metadata

    def test_clean_metadata_removes_none(self):
        """Test that None values are removed from metadata"""
        config = Config()

        with tempfile.TemporaryDirectory() as temp_dir:
            config.chroma_db_path = temp_dir
            store = EmbeddingStore(config)

            metadata = {"title": "Test Document", "author": None, "category": "test"}

            cleaned = store._clean_metadata(metadata)

            assert "author" not in cleaned
            assert "title" in cleaned
            assert "category" in cleaned

    def test_clean_metadata_converts_lists(self):
        """Test that list values are converted to comma-separated strings"""
        config = Config()

        with tempfile.TemporaryDirectory() as temp_dir:
            config.chroma_db_path = temp_dir
            store = EmbeddingStore(config)

            metadata = {"tags": ["tag1", "tag2", "tag3"], "categories": ["cat1", "cat2"]}

            cleaned = store._clean_metadata(metadata)

            assert cleaned["tags"] == "tag1, tag2, tag3"
            assert cleaned["categories"] == "cat1, cat2"

    def test_clean_metadata_converts_other_types(self):
        """Test that other types are converted to strings"""
        config = Config()

        with tempfile.TemporaryDirectory() as temp_dir:
            config.chroma_db_path = temp_dir
            store = EmbeddingStore(config)

            metadata = {"count": 42, "ratio": 3.14, "enabled": True, "data": {"key": "value"}}

            cleaned = store._clean_metadata(metadata)

            assert cleaned["count"] == 42
            assert cleaned["ratio"] == 3.14
            assert cleaned["enabled"] == True
            assert isinstance(cleaned["data"], str)


class TestDocumentOperations:
    """Test document add/remove operations"""

    def test_add_document_creates_chunks(self):
        """Test adding document chunks to the store (requires Ollama)"""
        config = Config()

        with tempfile.TemporaryDirectory() as temp_dir:
            config.chroma_db_path = temp_dir

            # Create a temporary markdown file
            test_file = Path(temp_dir) / "test.md"
            test_file.write_text("# Test Document\n\nThis is test content.")

            store = EmbeddingStore(config)

            # Create test chunks
            chunks = [
                Document(content="Test content chunk 1", meta={"title": "Test Doc", "chunk_index": 0}),
                Document(content="Test content chunk 2", meta={"title": "Test Doc", "chunk_index": 1}),
            ]

            # Add documents (this will actually try to generate embeddings)
            # We'll skip this for now if Ollama isn't available
            try:
                store.add_document(test_file, chunks)

                # Verify documents were added
                count = store.get_document_count()
                assert count == 2
            except Exception as e:
                # Skip test if Ollama is not available or model not found
                error_msg = str(e).lower()
                if "connect" in error_msg or "ollama" in error_msg or "not found" in error_msg or "404" in error_msg:
                    pytest.skip(f"Ollama not available or model not installed: {e}")
                else:
                    raise

    def test_get_document_count(self):
        """Test getting document count from store"""
        config = Config()

        with tempfile.TemporaryDirectory() as temp_dir:
            config.chroma_db_path = temp_dir
            store = EmbeddingStore(config)

            # New store should have 0 documents
            count = store.get_document_count()
            assert count == 0

    def test_get_unique_source_files(self):
        """Test getting unique source files"""
        config = Config()

        with tempfile.TemporaryDirectory() as temp_dir:
            config.chroma_db_path = temp_dir
            store = EmbeddingStore(config)

            # Empty store should return empty list
            sources = store.get_unique_source_files()
            assert sources == []


class TestVerification:
    """Test embedding verification functionality"""

    def test_verify_empty_collection(self):
        """Test verification on empty collection"""
        config = Config()

        with tempfile.TemporaryDirectory() as temp_dir:
            config.chroma_db_path = temp_dir
            store = EmbeddingStore(config)

            result = store.verify_embeddings()

            assert result["status"] == "success"
            assert result["document_count"] == 0
            assert result["search_functional"] is None
            assert result["collection_name"] == config.collection_name

    def test_verify_returns_collection_info(self):
        """Test that verification returns collection information"""
        config = Config()

        with tempfile.TemporaryDirectory() as temp_dir:
            config.chroma_db_path = temp_dir
            store = EmbeddingStore(config)

            result = store.verify_embeddings()

            assert "status" in result
            assert "document_count" in result
            assert "search_functional" in result
            assert "collection_name" in result
            assert "persist_directory" in result


class TestCollectionManagement:
    """Test collection clear and management operations"""

    def test_clear_collection(self):
        """Test clearing the collection"""
        config = Config()

        with tempfile.TemporaryDirectory() as temp_dir:
            config.chroma_db_path = temp_dir
            store = EmbeddingStore(config)

            # Clear should work even on empty collection
            store.clear_collection()

            # Verify collection is still accessible
            count = store.get_document_count()
            assert count == 0

    def test_list_documents_empty(self):
        """Test listing documents from empty collection"""
        config = Config()

        with tempfile.TemporaryDirectory() as temp_dir:
            config.chroma_db_path = temp_dir
            store = EmbeddingStore(config)

            documents = store.list_documents()

            assert documents == []

    def test_list_documents_with_limit(self):
        """Test listing documents with max limit"""
        config = Config()

        with tempfile.TemporaryDirectory() as temp_dir:
            config.chroma_db_path = temp_dir
            store = EmbeddingStore(config)

            documents = store.list_documents(max_documents=10)

            assert isinstance(documents, list)
            assert len(documents) <= 10


class TestSearchOperations:
    """Test search functionality"""

    def test_search_empty_collection(self):
        """Test search on empty collection"""
        config = Config()

        with tempfile.TemporaryDirectory() as temp_dir:
            config.chroma_db_path = temp_dir
            store = EmbeddingStore(config)

            try:
                results = store.search_similar("test query", k=5)
                assert results == []
            except Exception as e:
                # Skip if Ollama not available
                if "connect" in str(e).lower() or "ollama" in str(e).lower():
                    pytest.skip("Ollama not available for testing")
                else:
                    raise


class TestFileOperations:
    """Test file-specific operations"""

    def test_get_file_document_count(self):
        """Test getting document count for specific file"""
        config = Config()

        with tempfile.TemporaryDirectory() as temp_dir:
            config.chroma_db_path = temp_dir
            test_file = Path(temp_dir) / "test.md"
            test_file.write_text("test")

            store = EmbeddingStore(config)

            count = store.get_file_document_count(test_file)
            assert count == 0  # No documents added yet

    def test_remove_file_documents_nonexistent(self):
        """Test removing documents for non-existent file"""
        config = Config()

        with tempfile.TemporaryDirectory() as temp_dir:
            config.chroma_db_path = temp_dir
            test_file = Path(temp_dir) / "nonexistent.md"

            store = EmbeddingStore(config)

            result = store.remove_file_documents(test_file)
            assert result == False  # No documents found to remove


class TestArticleEmbedding:
    """Tests for article-level embedding aggregation."""

    def test_get_article_embedding_empty_returns_none(self):
        config = Config()

        with tempfile.TemporaryDirectory() as temp_dir:
            config.chroma_db_path = temp_dir
            store = EmbeddingStore(config)

            embedding = store.get_article_embedding(Path(temp_dir) / "missing.md")
            assert embedding is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
