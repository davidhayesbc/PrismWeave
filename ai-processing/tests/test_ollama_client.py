"""
Test configuration for Ollama client
"""

import pytest
import asyncio
import aiohttp
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path
import tempfile
import shutil
import json
import time
from typing import Dict, Any, List

# Import test utilities
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from models.ollama_client import OllamaClient, GenerationResult, ollama_client
from tests import TEST_CONFIG


class TestOllamaClient:
    """Test suite for OllamaClient"""

    @pytest.fixture
    def client_config(self):
        """Provide client configuration"""
        return {
            'host': 'http://localhost:11434',
            'timeout': 30
        }

    @pytest.fixture
    async def mock_client(self, client_config):
        """Create a mock Ollama client"""
        client = OllamaClient(**client_config)
        # Mock the session and ollama client
        client._session = AsyncMock()
        client._ollama_client = MagicMock()
        return client

    @pytest.fixture
    def mock_models_response(self):
        """Mock response for list models"""
        class MockModel:
            def __init__(self, name: str, size: int = 1000000):
                self.model = name
                self.size = size
                self.modified_at = "2024-01-01T00:00:00Z"
                self.details = {}

        class MockListResponse:
            def __init__(self, models: List[MockModel]):
                self.models = models

        return MockListResponse([
            MockModel("llama3.1:8b", 8000000000),
            MockModel("phi3:mini", 2000000000),
            MockModel("nomic-embed-text", 500000000)
        ])

    def test_init(self, client_config):
        """Test OllamaClient initialization"""
        client = OllamaClient(**client_config)
        assert client.host == "http://localhost:11434"
        assert client.timeout == 30
        assert client._session is None
        assert client._ollama_client is None
        assert client._available_models == {}

    def test_init_with_trailing_slash(self):
        """Test initialization with trailing slash in host"""
        client = OllamaClient(host="http://localhost:11434/")
        assert client.host == "http://localhost:11434"

    @pytest.mark.asyncio
    async def test_context_manager(self, client_config):
        """Test async context manager"""
        client = OllamaClient(**client_config)
        
        with patch('aiohttp.ClientSession') as mock_session_class:
            mock_session = AsyncMock()
            mock_session_class.return_value = mock_session
            
            with patch('ollama.Client') as mock_ollama_class:
                mock_ollama = MagicMock()
                mock_ollama_class.return_value = mock_ollama
                
                async with client as c:
                    assert c is client
                    assert client._session is not None
                    assert client._ollama_client is not None
                
                # Verify session was closed
                mock_session.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_ensure_session(self, mock_client):
        """Test session initialization"""
        with patch('aiohttp.ClientSession') as mock_session_class:
            mock_session = AsyncMock()
            mock_session_class.return_value = mock_session
            
            with patch('ollama.Client') as mock_ollama_class:
                mock_ollama = MagicMock()
                mock_ollama_class.return_value = mock_ollama
                
                await mock_client._ensure_session()
                
                assert mock_client._session == mock_session
                assert mock_client._ollama_client == mock_ollama

    @pytest.mark.asyncio
    async def test_list_models_success(self, mock_client, mock_models_response):
        """Test successful model listing"""
        mock_client._ollama_client.list.return_value = mock_models_response
        
        models = await mock_client.list_models()
        
        assert len(models) == 3
        assert "llama3.1:8b" in models
        assert "phi3:mini" in models
        assert "nomic-embed-text" in models
        
        # Verify model data structure
        llama_model = models["llama3.1:8b"]
        assert llama_model["name"] == "llama3.1:8b"
        assert llama_model["size"] == 8000000000

    @pytest.mark.asyncio
    async def test_list_models_error(self, mock_client):
        """Test model listing with error"""
        mock_client._ollama_client.list.side_effect = Exception("Connection failed")
        
        models = await mock_client.list_models()
        
        assert models == {}

    @pytest.mark.asyncio
    async def test_model_exists_true(self, mock_client):
        """Test model existence check - model exists"""
        mock_client._available_models = {
            "llama3.1:8b": {"name": "llama3.1:8b"},
            "phi3:mini": {"name": "phi3:mini"}
        }
        
        exists = await mock_client.model_exists("llama3.1:8b")
        assert exists is True
        
        # Test base name matching
        exists = await mock_client.model_exists("llama3.1")
        assert exists is True

    @pytest.mark.asyncio
    async def test_model_exists_false(self, mock_client):
        """Test model existence check - model doesn't exist"""
        mock_client._available_models = {
            "llama3.1:8b": {"name": "llama3.1:8b"}
        }
        
        exists = await mock_client.model_exists("nonexistent:model")
        assert exists is False

    @pytest.mark.asyncio
    async def test_model_exists_empty_name(self, mock_client):
        """Test model existence check with empty name"""
        exists = await mock_client.model_exists("")
        assert exists is False
        
        exists = await mock_client.model_exists(None)
        assert exists is False

    @pytest.mark.asyncio
    async def test_pull_model_success(self, mock_client):
        """Test successful model pulling"""
        mock_client._ollama_client.pull.return_value = None
        
        result = await mock_client.pull_model("phi3:mini")
        
        assert result is True
        mock_client._ollama_client.pull.assert_called_once_with("phi3:mini")

    @pytest.mark.asyncio
    async def test_pull_model_error(self, mock_client):
        """Test model pulling with error"""
        mock_client._ollama_client.pull.side_effect = Exception("Pull failed")
        
        result = await mock_client.pull_model("nonexistent:model")
        
        assert result is False

    @pytest.mark.asyncio
    async def test_generate_single_success(self, mock_client):
        """Test successful single generation"""
        # Mock model exists
        mock_client.model_exists = AsyncMock(return_value=True)
        
        # Mock HTTP response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {
            "response": "Test response",
            "model": "phi3:mini",
            "created_at": "2024-01-01T00:00:00Z",
            "done": True,
            "total_duration": 1000000,
            "eval_count": 10
        }
        
        mock_client._session.post.return_value.__aenter__.return_value = mock_response
        
        result = await mock_client.generate(
            model="phi3:mini",
            prompt="Test prompt"
        )
        
        assert isinstance(result, GenerationResult)
        assert result.response == "Test response"
        assert result.model == "phi3:mini"
        assert result.done is True

    @pytest.mark.asyncio
    async def test_generate_model_not_found(self, mock_client):
        """Test generation with model not found"""
        mock_client.model_exists = AsyncMock(return_value=False)
        mock_client.pull_model = AsyncMock(return_value=False)
        
        with pytest.raises(Exception) as exc_info:
            await mock_client.generate(
                model="nonexistent:model",
                prompt="Test prompt"
            )
        
        assert "not available" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_generate_http_error(self, mock_client):
        """Test generation with HTTP error"""
        mock_client.model_exists = AsyncMock(return_value=True)
        
        # Mock HTTP error response
        mock_response = AsyncMock()
        mock_response.status = 500
        mock_response.text.return_value = "Internal server error"
        
        mock_client._session.post.return_value.__aenter__.return_value = mock_response
        
        with pytest.raises(Exception) as exc_info:
            await mock_client.generate(
                model="phi3:mini",
                prompt="Test prompt"
            )
        
        assert "Generation failed: 500" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_embed_success(self, mock_client):
        """Test successful embedding generation"""
        mock_client.model_exists = AsyncMock(return_value=True)
        
        # Mock HTTP response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {
            "embedding": [0.1, 0.2, 0.3, 0.4, 0.5]
        }
        
        mock_client._session.post.return_value.__aenter__.return_value = mock_response
        
        embeddings = await mock_client.embed(
            model="nomic-embed-text",
            input_text="Test text"
        )
        
        assert len(embeddings) == 1
        assert embeddings[0] == [0.1, 0.2, 0.3, 0.4, 0.5]

    @pytest.mark.asyncio
    async def test_embed_multiple_texts(self, mock_client):
        """Test embedding generation with multiple texts"""
        mock_client.model_exists = AsyncMock(return_value=True)
        
        # Mock HTTP response for each text
        responses = [
            {"embedding": [0.1, 0.2, 0.3]},
            {"embedding": [0.4, 0.5, 0.6]}
        ]
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.side_effect = responses
        
        mock_client._session.post.return_value.__aenter__.return_value = mock_response
        
        embeddings = await mock_client.embed(
            model="nomic-embed-text",
            input_text=["Text 1", "Text 2"]
        )
        
        assert len(embeddings) == 2
        assert embeddings[0] == [0.1, 0.2, 0.3]
        assert embeddings[1] == [0.4, 0.5, 0.6]

    @pytest.mark.asyncio
    async def test_health_check_healthy(self, mock_client):
        """Test health check when service is healthy"""
        # Mock successful tags response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_client._session.get.return_value.__aenter__.return_value = mock_response
        
        # Mock list_models to return some models
        mock_client.list_models = AsyncMock(return_value={
            "phi3:mini": {"name": "phi3:mini"},
            "llama3.1:8b": {"name": "llama3.1:8b"}
        })
        
        health = await mock_client.health_check()
        
        assert health["status"] == "healthy"
        assert health["host"] == mock_client.host
        assert health["models_available"] == 2
        assert "phi3:mini" in health["models"]

    @pytest.mark.asyncio
    async def test_health_check_unhealthy_http_error(self, mock_client):
        """Test health check with HTTP error"""
        mock_response = AsyncMock()
        mock_response.status = 404
        mock_client._session.get.return_value.__aenter__.return_value = mock_response
        
        health = await mock_client.health_check()
        
        assert health["status"] == "unhealthy"
        assert health["host"] == mock_client.host
        assert "HTTP 404" in health["error"]

    @pytest.mark.asyncio
    async def test_health_check_unhealthy_exception(self, mock_client):
        """Test health check with connection exception"""
        mock_client._session.get.side_effect = Exception("Connection refused")
        
        health = await mock_client.health_check()
        
        assert health["status"] == "unhealthy"
        assert health["host"] == mock_client.host
        assert "Connection refused" in health["error"]

    @pytest.mark.asyncio
    async def test_chat_success(self, mock_client):
        """Test successful chat completion"""
        mock_client.model_exists = AsyncMock(return_value=True)
        
        # Mock HTTP response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {
            "message": {
                "role": "assistant",
                "content": "Hello! How can I help you?"
            },
            "done": True
        }
        
        mock_client._session.post.return_value.__aenter__.return_value = mock_response
        
        messages = [
            {"role": "user", "content": "Hello"}
        ]
        
        result = await mock_client.chat(
            model="phi3:mini",
            messages=messages
        )
        
        assert result["message"]["content"] == "Hello! How can I help you?"
        assert result["done"] is True

    @pytest.mark.asyncio
    async def test_cache_refresh(self, mock_client, mock_models_response):
        """Test model cache refresh logic"""
        # Initially no cache
        assert mock_client._model_cache_time is None
        assert await mock_client._should_refresh_cache() is True
        
        # Set cache time to recent
        mock_client._model_cache_time = time.time()
        assert await mock_client._should_refresh_cache() is False
        
        # Set cache time to old
        mock_client._model_cache_time = time.time() - 400  # Older than 300s
        assert await mock_client._should_refresh_cache() is True

    @pytest.mark.asyncio
    async def test_ollama_client_context_manager(self):
        """Test the convenience context manager function"""
        with patch('aiohttp.ClientSession') as mock_session_class:
            mock_session = AsyncMock()
            mock_session_class.return_value = mock_session
            
            with patch('ollama.Client') as mock_ollama_class:
                mock_ollama = MagicMock()
                mock_ollama_class.return_value = mock_ollama
                
                async with ollama_client() as client:
                    assert isinstance(client, OllamaClient)
                    assert client.host == "http://localhost:11434"
                    assert client.timeout == 60


class TestGenerationResult:
    """Test suite for GenerationResult dataclass"""

    def test_init(self):
        """Test GenerationResult initialization"""
        result = GenerationResult(
            response="Test response",
            model="phi3:mini",
            created_at="2024-01-01T00:00:00Z"
        )
        
        assert result.response == "Test response"
        assert result.model == "phi3:mini"
        assert result.created_at == "2024-01-01T00:00:00Z"
        assert result.done is True
        assert result.total_duration == 0

    def test_init_with_all_fields(self):
        """Test GenerationResult with all fields"""
        result = GenerationResult(
            response="Complete response",
            model="llama3.1:8b",
            created_at="2024-01-01T00:00:00Z",
            done=True,
            total_duration=5000000,
            load_duration=1000000,
            prompt_eval_count=10,
            eval_count=50,
            eval_duration=4000000
        )
        
        assert result.response == "Complete response"
        assert result.model == "llama3.1:8b"
        assert result.total_duration == 5000000
        assert result.prompt_eval_count == 10
        assert result.eval_count == 50


# Integration tests that require a running Ollama instance
@pytest.mark.integration
class TestOllamaClientIntegration:
    """Integration tests for OllamaClient (requires running Ollama)"""

    @pytest.fixture
    def integration_client(self):
        """Create client for integration testing"""
        return OllamaClient(host="http://localhost:11434", timeout=30)

    @pytest.mark.asyncio
    async def test_real_health_check(self, integration_client):
        """Test health check against real Ollama instance"""
        health = await integration_client.health_check()
        
        # Should either be healthy or unhealthy, not crash
        assert health["status"] in ["healthy", "unhealthy"]
        assert health["host"] == "http://localhost:11434"

    @pytest.mark.asyncio
    async def test_real_list_models(self, integration_client):
        """Test listing models from real Ollama instance"""
        async with integration_client:
            models = await integration_client.list_models()
            
            # Should return dict (empty if no models, populated if models exist)
            assert isinstance(models, dict)

# Performance tests
@pytest.mark.slow
class TestOllamaClientPerformance:
    """Performance tests for OllamaClient"""

    @pytest.mark.asyncio
    async def test_concurrent_requests(self, mock_client):
        """Test concurrent request handling"""
        # Mock successful responses
        mock_client.model_exists = AsyncMock(return_value=True)
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {
            "response": "Test response",
            "model": "phi3:mini",
            "created_at": "2024-01-01T00:00:00Z",
            "done": True
        }
        
        mock_client._session.post.return_value.__aenter__.return_value = mock_response
        
        # Run multiple concurrent generations
        tasks = []
        for i in range(5):
            task = mock_client.generate(
                model="phi3:mini",
                prompt=f"Test prompt {i}"
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 5
        for result in results:
            assert isinstance(result, GenerationResult)
            assert result.response == "Test response"


if __name__ == "__main__":
    pytest.main([__file__])
