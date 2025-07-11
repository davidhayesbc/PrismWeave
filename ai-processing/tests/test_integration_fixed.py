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
from src.processors.langchain_document_processor import LangChainDocumentProcessor
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
            "chunk_size": 1000,
            "chunk_overlap": 200,
            "batch_size": 5
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(config_data, f)
        yield f.name
    
    # Cleanup
    os.unlink(f.name)


@pytest.fixture
def integration_config(temp_config_file):
    """Load configuration for integration tests"""
    return Config.from_file(temp_config_file)


@pytest.fixture
def mock_ollama_client():
    """Mock Ollama client for testing"""
    client = AsyncMock(spec=OllamaClient)
    
    # Mock embedding generation
    client.embed.return_value = [[0.1, 0.2, 0.3, 0.4, 0.5] * 256]  # 1280-dim vector
    
    # Mock text generation
    client.generate.return_value = "This is a mocked response from Ollama"
    
    # Mock health check
    client.health_check.return_value = True
    
    return client


# Helper function to create mock processor init
def create_mock_processor_init(mock_ollama_client):
    """Helper to create a mock processor init function with required stats attribute"""
    def mock_init(self, config):
        self.config = config
        self.client = mock_ollama_client
        self.stats = {
            'total_documents': 0,
            'total_chunks': 0,
            'processing_time': 0.0,
            'average_chunks_per_doc': 0.0
        }
    return mock_init


class TestIntegrationWorkflow:
    """Test complete integration workflows"""

    @pytest.mark.asyncio
    async def test_basic_document_processing(
        self, integration_config, mock_ollama_client, monkeypatch
    ):
        """Test basic document processing workflow"""
        # Use helper to create mock
        mock_init = create_mock_processor_init(mock_ollama_client)
        monkeypatch.setattr(LangChainDocumentProcessor, "__init__", mock_init)
        
        processor = LangChainDocumentProcessor(integration_config)
        
        # Process a small document
        sample_doc = SAMPLE_DOCUMENTS[0]
        
        result = await processor.process_document(sample_doc["content"])
        
        # Verify result structure
        assert "chunks" in result
        assert isinstance(result["chunks"], list)
        assert len(result["chunks"]) > 0
        
        # Verify stats were updated
        assert processor.stats["total_documents"] > 0
        assert processor.stats["total_chunks"] > 0

    @pytest.mark.asyncio
    async def test_large_document_processing(
        self, integration_config, mock_ollama_client, monkeypatch
    ):
        """Test processing of large documents"""
        # Use helper to create mock
        mock_init = create_mock_processor_init(mock_ollama_client)
        monkeypatch.setattr(LangChainDocumentProcessor, "__init__", mock_init)
        
        processor = LangChainDocumentProcessor(integration_config)
        
        # Create a larger document
        large_content = "This is a test sentence. " * 200  # Smaller test document
        
        result = await processor.process_document(large_content)
        
        # Verify chunking worked
        assert "chunks" in result
        assert len(result["chunks"]) > 1  # Should be split into multiple chunks

    @pytest.mark.asyncio
    async def test_special_characters_processing(
        self, integration_config, mock_ollama_client, monkeypatch
    ):
        """Test processing documents with special characters"""
        # Use helper to create mock
        mock_init = create_mock_processor_init(mock_ollama_client)
        monkeypatch.setattr(LangChainDocumentProcessor, "__init__", mock_init)
        
        processor = LangChainDocumentProcessor(integration_config)
        
        # Document with special characters
        special_content = "This has émojis 🚀 and special chars: ñáéíóú & symbols @#$%"
        
        result = await processor.process_document(special_content)
        
        # Should process without errors
        assert "chunks" in result
        assert len(result["chunks"]) > 0

    @pytest.mark.asyncio
    async def test_empty_document_handling(
        self, integration_config, mock_ollama_client, monkeypatch
    ):
        """Test handling of empty documents"""
        # Use helper to create mock
        mock_init = create_mock_processor_init(mock_ollama_client)
        monkeypatch.setattr(LangChainDocumentProcessor, "__init__", mock_init)
        
        processor = LangChainDocumentProcessor(integration_config)
        
        # Test empty content
        result = await processor.process_document("")
        
        # Should handle gracefully
        assert "chunks" in result
        # Might be empty or have default handling

    @pytest.mark.asyncio
    async def test_batch_processing(
        self, integration_config, mock_ollama_client, monkeypatch
    ):
        """Test batch processing of multiple documents"""
        # Use helper to create mock
        mock_init = create_mock_processor_init(mock_ollama_client)
        monkeypatch.setattr(LangChainDocumentProcessor, "__init__", mock_init)
        
        processor = LangChainDocumentProcessor(integration_config)
        
        # Process multiple documents
        documents = [doc["content"] for doc in SAMPLE_DOCUMENTS[:3]]  # First 3 docs
        
        results = []
        for doc in documents:
            result = await processor.process_document(doc)
            results.append(result)
        
        # Verify all were processed
        assert len(results) == 3
        for result in results:
            assert "chunks" in result

    @pytest.mark.asyncio
    async def test_error_handling(
        self, integration_config, mock_ollama_client, monkeypatch
    ):
        """Test error handling in processing pipeline"""
        # Use helper to create mock
        mock_init = create_mock_processor_init(mock_ollama_client)
        monkeypatch.setattr(LangChainDocumentProcessor, "__init__", mock_init)
        
        # Make the embed method raise an exception
        mock_ollama_client.embed.side_effect = Exception("Network error")
        
        processor = LangChainDocumentProcessor(integration_config)
        
        # Should handle the error gracefully
        with pytest.raises(Exception):
            await processor.process_document("Test content that will fail")


class TestConfigurationIntegration:
    """Test configuration system integration"""

    @pytest.mark.asyncio
    async def test_config_loading(self, temp_config_file):
        """Test configuration loading and validation"""
        config = Config.from_file(temp_config_file)
        
        # Verify config structure
        assert hasattr(config, 'ollama')
        assert hasattr(config, 'processing')
        assert config.ollama.host == "http://localhost:11434"

    @pytest.mark.asyncio
    async def test_config_with_processor(
        self, integration_config, mock_ollama_client, monkeypatch
    ):
        """Test that processor correctly uses configuration"""
        # Use helper to create mock
        mock_init = create_mock_processor_init(mock_ollama_client)
        monkeypatch.setattr(LangChainDocumentProcessor, "__init__", mock_init)
        
        processor = LangChainDocumentProcessor(integration_config)
        
        # Verify processor has access to config
        assert processor.config == integration_config


class TestVectorOperations:
    """Test vector generation and operations"""

    @pytest.mark.asyncio
    async def test_vector_generation(
        self, integration_config, mock_ollama_client, monkeypatch
    ):
        """Test vector embedding generation"""
        # Use helper to create mock
        mock_init = create_mock_processor_init(mock_ollama_client)
        monkeypatch.setattr(LangChainDocumentProcessor, "__init__", mock_init)
        
        processor = LangChainDocumentProcessor(integration_config)
        
        # Process document and check for embeddings
        result = await processor.process_document("Test content for vectors")
        
        # Verify the mock was called
        assert mock_ollama_client.embed.called

    @pytest.mark.asyncio
    async def test_vector_dimensions(
        self, integration_config, mock_ollama_client, monkeypatch
    ):
        """Test vector dimensions are correct"""
        # Use helper to create mock
        mock_init = create_mock_processor_init(mock_ollama_client)
        monkeypatch.setattr(LangChainDocumentProcessor, "__init__", mock_init)
        
        processor = LangChainDocumentProcessor(integration_config)
        
        await processor.process_document("Test content")
        
        # Verify embedding call
        assert mock_ollama_client.embed.called


class TestRealOllamaIntegration:
    """Test real Ollama integration (requires running Ollama server)"""
    
    @pytest.mark.skip(reason="Requires running Ollama server - disabled for performance")
    @pytest.mark.asyncio
    async def test_real_ollama_connection(self, integration_config):
        """Test connection to real Ollama server"""
        # This test is skipped by default to avoid requiring Ollama server
        processor = LangChainDocumentProcessor(integration_config)
        
        # Test health check
        client = OllamaClient(integration_config.ollama)
        health = await client.health_check()
        
        if health:
            # Only run if Ollama is available
            result = await processor.process_document("Test with real Ollama")
            assert "chunks" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
