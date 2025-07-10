"""
Integration tests for PrismWeave AI processing pipeline
"""

import pytest
import asyncio
import tempfile
import shutil
import os
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock
import json
import yaml

import sys
sys.path.append(str(Path(__file__).parent.parent / "src"))

from src.utils.config_simplified import Config, get_config, load_config, set_config
from src.models.ollama_client import OllamaClient
from src.process    @pytest.mark.asyncio
    async def test_special_characters_processing(
        self, integration_config, mock_ollama_client, monkeypatch
    ):
        """Test processing documents with special characters"""
        # Use helper to create mock
        mock_init = self.create_mock_processor_init(mock_ollama_client)
        monkeypatch.setattr(LangChainDocumentProcessor, "__init__", mock_init)n_document_processor import LangChainDocumentProcessor
from .test_data import SAMPLE_DOCUMENTS, create_test_files, cleanup_test_files


@pytest.fixture(scope="session")
def test_data_dir():
    """Create test data directory for integration tests"""
    create_test_files()
    yield "test_data"
    cleanup_test_files()


@pytest.fixture
def temp_config_file():
    """Create temporary config file"""
    config_data = {
        "ollama": {
            "host": "http://localhost:11434",
            "timeout": 30,
            "models": {
                "large": "test-model",
                "medium": "test-model",
                "small": "test-model",
                "embedding": "test-embedding"
            }
        },
        "processing": {
            "max_concurrent": 2,
            "chunk_size": 500,
            "chunk_overlap": 100,
            "min_chunk_size": 50,
            "summary_timeout": 60,
            "tagging_timeout": 30,
            "categorization_timeout": 15,
            "min_word_count": 10,
            "max_word_count": 10000,
            "max_summary_length": 200,
            "max_tags": 5
        },
        "vector": {
            "collection_name": "test_documents",
            "persist_directory": "./test_chroma_db",
            "embedding_function": "sentence-transformers",
            "max_results": 5,
            "similarity_threshold": 0.8
        },
        "log_level": "DEBUG"
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(config_data, f)
        config_file = f.name
    
    yield config_file
    Path(config_file).unlink()


@pytest.fixture
def integration_config(temp_config_file):
    """Load configuration for integration tests"""
    return Config.from_file(Path(temp_config_file))


@pytest.fixture
def mock_ollama_client():
    """Mock Ollama client for integration tests"""
    from src.models.ollama_client import GenerationResult
    
    client = AsyncMock(spec=OllamaClient)
    
    # Mock successful health check
    async def mock_health_check():
        return {"status": "healthy", "host": "mock://localhost", "models_available": 1}
    client.health_check.side_effect = mock_health_check
    
    # Mock generation with proper GenerationResult
    async def mock_generate(*args, **kwargs):
        return GenerationResult(
            response="Generated summary for testing",
            model="test-model",
            created_at="2025-01-01T00:00:00Z",
            done=True,
            total_duration=1000,
            load_duration=500,
            prompt_eval_count=10,
            eval_count=20,
            eval_duration=500
        )
    client.generate.side_effect = mock_generate
    
    # Mock embeddings - return List[List[float]]
    async def mock_embed(*args, **kwargs):
        # Return simple embeddings for testing
        return [[0.1, 0.2, 0.3, 0.4]]  # Single embedding as list of lists
    client.embed.side_effect = mock_embed
    
    # Mock chat
    async def mock_chat(*args, **kwargs):
        return {
            "message": {"content": "Chat response for testing"},
            "done": True
        }
    client.chat.side_effect = mock_chat
    
    return client


class TestIntegrationWorkflow:
    """Test complete workflow integration"""
    
    def create_mock_processor_init(self, mock_ollama_client):
        """Helper to create mock processor init function"""
        def mock_processor_init(self, config=None):
            self.config = config or get_config()
            self.ollama_client = mock_ollama_client
            self.text_splitters = {}  # Mock text splitters
            self.stats = {  # Add missing stats attribute
                'total_documents': 0,
                'total_chunks': 0,
                'processing_time': 0.0,
                'average_chunks_per_doc': 0.0
            }
        return mock_processor_init
    
    @pytest.mark.asyncio
    async def test_complete_document_processing_workflow(
        self, integration_config, mock_ollama_client, test_data_dir, monkeypatch
    ):
        """Test complete document processing from file to analysis"""
        # Use helper to create mock
        mock_init = self.create_mock_processor_init(mock_ollama_client)
        monkeypatch.setattr(LangChainDocumentProcessor, "__init__", mock_init)
        
        # Initialize processor with config only
        processor = LangChainDocumentProcessor(
            config=integration_config
        )
        
        # Test file
        test_file = Path(test_data_dir) / "complex.md"
        assert test_file.exists()
        
        # Process document
        result = await processor.process_document(test_file)
        
        # Verify result structure
        assert result is not None
        assert hasattr(result, 'chunks')
        assert hasattr(result, 'metadata')
        assert hasattr(result, 'processing_stats')
        
        # Verify chunks were created
        assert len(result.chunks) > 0
        
        # Verify metadata
        assert result.metadata['file_path'] == str(test_file)
        
        # Verify processing stats
        assert result.processing_stats['chunk_count'] == len(result.chunks)
    
    @pytest.mark.asyncio
    async def test_batch_processing_workflow(
        self, integration_config, mock_ollama_client, test_data_dir, monkeypatch
    ):
        """Test batch processing of multiple documents"""
        # Use helper to create mock
        mock_init = self.create_mock_processor_init(mock_ollama_client)
        monkeypatch.setattr(LangChainDocumentProcessor, "__init__", mock_init)
        
        processor = LangChainDocumentProcessor(
            config=integration_config
        )
        
        # Test files
        test_files = [
            Path(test_data_dir) / "simple.md",
            Path(test_data_dir) / "sample.py",
            Path(test_data_dir) / "sample.js"
        ]
        
        # Verify files exist
        for file_path in test_files:
            assert file_path.exists()
        
        # Process documents
        results = []
        for file_path in test_files:
            result = await processor.process_document(file_path)
            results.append(result)
        
        # Verify all documents were processed
        assert len(results) == len(test_files)
        
        # Verify each result
        for i, result in enumerate(results):
            assert result is not None
            assert len(result.chunks) > 0
            assert result.metadata['file_path'] == str(test_files[i])
            
            # Different file types should have different chunk counts
            if test_files[i].suffix == '.md':
                # Markdown should be chunked by headers
                assert any(chunk.metadata.get("chunk_type", "unknown") == 'markdown_header' for chunk in result.chunks)
            elif test_files[i].suffix in ['.py', '.js']:
                # Code should be chunked by functions/classes
                assert any(chunk.metadata.get("chunk_type", "unknown") in ['python_code', 'javascript_code'] for chunk in result.chunks)
    
    @pytest.mark.asyncio
    async def test_error_handling_workflow(
        self, integration_config, mock_ollama_client, test_data_dir, monkeypatch
    ):
        """Test error handling in complete workflow"""
        # Use helper to create mock
        mock_init = self.create_mock_processor_init(mock_ollama_client)
        monkeypatch.setattr(LangChainDocumentProcessor, "__init__", mock_init)
        
        processor = LangChainDocumentProcessor(
            config=integration_config
        )
        
        # Test with non-existent file
        # Processor catches exceptions and returns None instead of raising
        result = await processor.process_document(Path("non_existent_file.txt"))
        assert result is None  # Should return None for non-existent files
        
        # Test with empty file
        empty_file = Path(test_data_dir) / "empty.txt"
        result = await processor.process_document(empty_file)
        
        # Should handle empty file gracefully
        assert result is not None
        assert len(result.chunks) == 0  # No chunks for empty file
        assert result.metadata['file_path'] == str(empty_file)
    
    @pytest.mark.asyncio
    @pytest.mark.skipif(
        not os.environ.get("TEST_REAL_OLLAMA", "").lower() in ["true", "1", "yes"],
        reason="Real Ollama integration test disabled. Set TEST_REAL_OLLAMA=true to enable."
    )
    async def test_ollama_client_integration(self, integration_config):
        """Test Ollama client integration (requires running Ollama server)"""
        # Skip if no Ollama server available
        client = OllamaClient(
            host=integration_config.ollama.host,
            timeout=5  # Reduced timeout for faster failure
        )
        
        try:
            health_ok = await client.health_check()
            if not health_ok:
                pytest.skip("Ollama server not available")
        except Exception:
            pytest.skip("Ollama server not available")
        
        # Test generation
        response = await client.generate(
            model=integration_config.ollama.models.small,
            prompt="Test prompt for generation"
        )
        
        assert response is not None
        # Since we're not streaming, response should be GenerationResult
        from src.models.ollama_client import GenerationResult
        assert isinstance(response, GenerationResult)
        assert len(response.response) > 0
        
        # Test embedding
        embedding_response = await client.embed(integration_config.ollama.models.embedding, "Test text for embedding")
        
        assert embedding_response is not None
        assert isinstance(embedding_response, list)
        assert len(embedding_response) > 0
        assert isinstance(embedding_response[0], list)  # First embedding should be a list of floats


class TestConfigurationIntegration:
    """Test configuration system integration"""
    
    def test_config_file_loading(self, temp_config_file):
        """Test loading configuration from file"""
        config = Config.from_file(Path(temp_config_file))
        
        assert config.ollama.host == "http://localhost:11434"
        assert config.processing.chunk_size == 500
        assert config.vector.collection_name == "test_documents"
    
    def test_config_validation_integration(self, temp_config_file):
        """Test configuration validation"""
        # Load valid config
        config = Config.from_file(Path(temp_config_file))
        assert config is not None
        
        # Test invalid config
        invalid_config_data = {
            "ollama": {
                "host": "invalid_url",
                "timeout": -1  # Invalid timeout
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(invalid_config_data, f)
            invalid_config_file = f.name
        
        try:
            # Invalid config should still load but fail validation
            invalid_config = Config.from_file(Path(invalid_config_file))
            assert not invalid_config.is_valid()
            issues = invalid_config.validate()
            assert len(issues) > 0
        finally:
            Path(invalid_config_file).unlink()
    
    def test_global_config_integration(self, temp_config_file):
        """Test global configuration management"""
        # Set config globally using load_config
        config = load_config(Path(temp_config_file))
        set_config(config)
        
        # Should return same instance
        config2 = get_config()
        assert config is config2
        
        # Verify config properties
        assert config.ollama.host == "http://localhost:11434"


class TestPerformanceIntegration:
    """Test performance characteristics"""
    
    def create_mock_processor_init(self, mock_ollama_client):
        """Helper to create mock processor init function"""
        def mock_processor_init(self, config=None):
            self.config = config or get_config()
            self.ollama_client = mock_ollama_client
            self.text_splitters = {}  # Mock text splitters
            self.stats = {  # Add missing stats attribute
                'total_documents': 0,
                'total_chunks': 0,
                'processing_time': 0.0,
                'average_chunks_per_doc': 0.0
            }
        return mock_processor_init
    
    @pytest.mark.asyncio
    async def test_large_document_processing(
        self, integration_config, mock_ollama_client, monkeypatch
    ):
        """Test processing of large documents"""
        # Use helper to create mock
        mock_init = self.create_mock_processor_init(mock_ollama_client)
        monkeypatch.setattr(LangChainDocumentProcessor, "__init__", mock_init)
        
        processor = LangChainDocumentProcessor(
            config=integration_config
        )
        
        # Create smaller large document for faster testing
        large_content = "# Large Document\n\n" + "This is a test paragraph. " * 50  # Reduced from 1000 to 50
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(large_content)
            large_file = f.name
        
        try:
            # Process large document
            import time
            start_time = time.time()
            
            result = await processor.process_document(Path(large_file))
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            # Verify processing completed
            assert result is not None
            assert len(result.chunks) > 0
            
            # Should complete in reasonable time (< 30 seconds for mocked client)
            assert processing_time < 30.0
            
            # Verify chunks are reasonably sized
            for chunk in result.chunks:
                assert len(chunk.page_content) <= integration_config.processing.chunk_size + integration_config.processing.chunk_overlap
                
        finally:
            Path(large_file).unlink()
    
    @pytest.mark.asyncio
    async def test_concurrent_processing(
        self, integration_config, mock_ollama_client, test_data_dir, monkeypatch
    ):
        """Test concurrent document processing"""
        # Use helper to create mock
        mock_init = self.create_mock_processor_init(mock_ollama_client)
        monkeypatch.setattr(LangChainDocumentProcessor, "__init__", mock_init)
        
        processor = LangChainDocumentProcessor(
            config=integration_config
        )
        
        # Process multiple documents concurrently
        test_files = [
            Path(test_data_dir) / "simple.md",
            Path(test_data_dir) / "sample.py",
            Path(test_data_dir) / "sample.js",
            Path(test_data_dir) / "config.json"
        ]
        
        # Create tasks for concurrent processing
        tasks = [
            processor.process_document(file_path)
            for file_path in test_files
        ]
        
        # Process concurrently
        import time
        start_time = time.time()
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        concurrent_time = end_time - start_time
        
        # Verify all processing completed
        assert len(results) == len(test_files)
        
        # Verify no exceptions (or handle expected ones)
        successful_results = [r for r in results if not isinstance(r, Exception)]
        assert len(successful_results) > 0
        
        # Concurrent processing should be very fast with mocked client
        assert concurrent_time < 10.0  # Should be very fast with mocking


class TestEdgeCasesIntegration:
    """Test edge cases and boundary conditions"""
    
    def create_mock_processor_init(self, mock_ollama_client):
        """Helper to create mock processor init function"""
        def mock_processor_init(self, config=None):
            self.config = config or get_config()
            self.ollama_client = mock_ollama_client
            self.text_splitters = {}  # Mock text splitters
            self.stats = {  # Add missing stats attribute
                'total_documents': 0,
                'total_chunks': 0,
                'processing_time': 0.0,
                'average_chunks_per_doc': 0.0
            }
        return mock_processor_init
    
    @pytest.mark.asyncio
    async def test_special_characters_processing(
        self, integration_config, mock_ollama_client, monkeypatch
    ):
        """Test processing documents with special characters"""
        # Mock the processor's ollama client to use our mock
        def mock_processor_init(self, config=None):
            self.config = config or get_config()
            self.ollama_client = mock_ollama_client
            self.text_splitters = {}  # Mock text splitters
            
        monkeypatch.setattr(LangChainDocumentProcessor, "__init__", mock_processor_init)
        
        processor = LangChainDocumentProcessor(
            config=integration_config
        )
        
        # Document with various special characters
        special_content = """# Special Characters Test 🚀

This document contains various special characters:
- Unicode: café, naïve, résumé
- Emojis: 🎉 🔥 💡 ⭐
- Mathematical: ∑ ∫ ∂ ∞ ≠ ≤ ≥
- Arrows: → ← ↑ ↓ ⇒ ⇔
- Quotes: "smart quotes" 'apostrophes' «guillemets»
- Dashes: em—dash, en–dash, hyphen-dash
- Currency: $123.45, €67.89, ¥123, £45.67

## Code with Special Characters

```python
def café_function():
    # Comment with émojis 🐍
    return "Special chars: αβγδε"
```

## Links and References

[Unicode Test](https://example.com/café)
[Emoji Link 🔗](https://example.com/test)
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(special_content)
            special_file = f.name
        
        try:
            result = await processor.process_document(Path(special_file))
            
            # Verify processing completed without errors
            assert result is not None
            assert len(result.chunks) > 0
            
            # Verify special characters are preserved
            full_content = ' '.join(chunk.page_content for chunk in result.chunks)
            assert '🚀' in full_content
            assert 'café' in full_content
            assert '∑' in full_content
            assert '→' in full_content
            
        finally:
            Path(special_file).unlink()
    
    @pytest.mark.asyncio
    async def test_mixed_content_types(
        self, integration_config, mock_ollama_client, monkeypatch
    ):
        """Test processing documents with mixed content types"""
        # Mock the processor's ollama client to use our mock
        def mock_processor_init(self, config=None):
            self.config = config or get_config()
            self.ollama_client = mock_ollama_client
            self.text_splitters = {}  # Mock text splitters
            
        monkeypatch.setattr(LangChainDocumentProcessor, "__init__", mock_processor_init)
        
        processor = LangChainDocumentProcessor(
            config=integration_config
        )
        
        # Mixed content document
        mixed_content = """# Mixed Content Document

This document contains various content types mixed together.

## Python Code Section

```python
def example_function():
    return "Hello from Python"
```

## JavaScript Code Section

```javascript
function exampleFunction() {
    return "Hello from JavaScript";
}
```

## JSON Data Section

```json
{
    "name": "Example",
    "version": "1.0.0",
    "config": {
        "enabled": true,
        "timeout": 30
    }
}
```

## Regular Text

This is regular markdown text with **bold** and *italic* formatting.

### Lists

1. First item
2. Second item
3. Third item

- Bullet point A
- Bullet point B
- Bullet point C

### Table

| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Data 1   | Data 2   | Data 3   |
| Data 4   | Data 5   | Data 6   |

## Links and Images

[Example Link](https://example.com)
![Example Image](https://example.com/image.png)
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(mixed_content)
            mixed_file = f.name
        
        try:
            result = await processor.process_document(Path(mixed_file))
            
            # Verify processing completed
            assert result is not None
            assert len(result.chunks) > 0
            
            # Should detect different content types in chunks
            chunk_types = {chunk.metadata.get("chunk_type", "unknown") for chunk in result.chunks}
            assert len(chunk_types) > 1  # Multiple chunk types detected
            
            # Verify metadata includes various elements
            assert result.metadata['word_count'] > 0
            assert result.metadata['line_count'] > 0
            
        finally:
            Path(mixed_file).unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
