"""
Test configuration and utilities management
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, mock_open
from typing import Dict, Any

# Import test utilities
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.config_simplified import (
    Config, OllamaConfig, ProcessingConfig, VectorConfig,
    get_config, load_config, set_config, reload_config,
    get_model_for_purpose, get_ollama_host, get_processing_config, get_vector_config
)
from tests import TEST_CONFIG


class TestOllamaConfig:
    """Test suite for OllamaConfig"""

    def test_default_initialization(self):
        """Test default OllamaConfig initialization"""
        config = OllamaConfig()
        
        assert config.host == "http://localhost:11434"
        assert config.timeout == 60
        assert "large" in config.models
        assert "medium" in config.models
        assert "small" in config.models
        assert "embedding" in config.models

    def test_custom_initialization(self):
        """Test OllamaConfig with custom values"""
        custom_models = {
            "large": "custom-large:latest",
            "medium": "custom-medium:latest",
            "small": "custom-small:latest",
            "embedding": "custom-embed:latest"
        }
        
        config = OllamaConfig(
            host="http://remote:11434",
            timeout=120,
            models=custom_models
        )
        
        assert config.host == "http://remote:11434"
        assert config.timeout == 120
        assert config.models == custom_models


class TestProcessingConfig:
    """Test suite for ProcessingConfig"""

    def test_default_initialization(self):
        """Test default ProcessingConfig initialization"""
        config = ProcessingConfig()
        
        assert config.max_concurrent == 3
        assert config.chunk_size == 1000
        assert config.chunk_overlap == 200
        assert config.min_chunk_size == 100
        assert config.summary_timeout == 120
        assert config.tagging_timeout == 60
        assert config.categorization_timeout == 30
        assert config.min_word_count == 50
        assert config.max_word_count == 50000
        assert config.max_summary_length == 500
        assert config.max_tags == 10

    def test_custom_initialization(self):
        """Test ProcessingConfig with custom values"""
        config = ProcessingConfig(
            max_concurrent=5,
            chunk_size=1500,
            chunk_overlap=300,
            min_word_count=25
        )
        
        assert config.max_concurrent == 5
        assert config.chunk_size == 1500
        assert config.chunk_overlap == 300
        assert config.min_word_count == 25


class TestVectorConfig:
    """Test suite for VectorConfig"""

    def test_default_initialization(self):
        """Test default VectorConfig initialization"""
        config = VectorConfig()
        
        assert config.collection_name == "documents"
        assert config.persist_directory == "./chroma_db"
        assert config.embedding_function == "sentence-transformers"
        assert config.max_results == 10
        assert config.similarity_threshold == 0.7

    def test_custom_initialization(self):
        """Test VectorConfig with custom values"""
        config = VectorConfig(
            collection_name="test_docs",
            persist_directory="/tmp/test_chroma",
            max_results=20,
            similarity_threshold=0.8
        )
        
        assert config.collection_name == "test_docs"
        assert config.persist_directory == "/tmp/test_chroma"
        assert config.max_results == 20
        assert config.similarity_threshold == 0.8


class TestConfig:
    """Test suite for main Config class"""

    def test_default_initialization(self):
        """Test default Config initialization"""
        config = Config()
        
        assert isinstance(config.ollama, OllamaConfig)
        assert isinstance(config.processing, ProcessingConfig)
        assert isinstance(config.vector, VectorConfig)
        assert config.log_level == "INFO"
        assert config.log_file is None

    def test_from_dict_empty(self):
        """Test Config.from_dict with empty dictionary"""
        config = Config.from_dict({})
        
        # Should use all defaults
        assert config.ollama.host == "http://localhost:11434"
        assert config.processing.max_concurrent == 3
        assert config.vector.collection_name == "documents"

    def test_from_dict_partial(self):
        """Test Config.from_dict with partial data"""
        data = {
            'ollama': {
                'host': 'http://custom:11434',
                'timeout': 90
            },
            'processing': {
                'max_concurrent': 5,
                'chunk_size': 1500
            },
            'log_level': 'DEBUG'
        }
        
        config = Config.from_dict(data)
        
        assert config.ollama.host == "http://custom:11434"
        assert config.ollama.timeout == 90
        assert config.processing.max_concurrent == 5
        assert config.processing.chunk_size == 1500
        assert config.processing.min_chunk_size == 100  # Default preserved
        assert config.log_level == "DEBUG"

    def test_from_dict_with_models(self):
        """Test Config.from_dict with custom models"""
        data = {
            'ollama': {
                'models': {
                    'large': 'custom-llama:70b',
                    'medium': 'custom-phi:7b'
                }
            }
        }
        
        config = Config.from_dict(data)
        
        assert config.ollama.models['large'] == 'custom-llama:70b'
        assert config.ollama.models['medium'] == 'custom-phi:7b'
        # Should preserve defaults for unspecified models
        assert 'small' in config.ollama.models
        assert 'embedding' in config.ollama.models

    def test_to_dict(self):
        """Test Config.to_dict conversion"""
        config = Config()
        data = config.to_dict()
        
        assert 'ollama' in data
        assert 'processing' in data
        assert 'vector' in data
        assert 'log_level' in data
        assert 'log_file' in data
        
        # Check structure
        assert 'host' in data['ollama']
        assert 'models' in data['ollama']
        assert 'max_concurrent' in data['processing']
        assert 'collection_name' in data['vector']

    def test_from_file_nonexistent(self):
        """Test Config.from_file with nonexistent file"""
        config = Config.from_file(Path("/nonexistent/config.yaml"))
        
        # Should return default config
        assert config.ollama.host == "http://localhost:11434"
        assert config.processing.max_concurrent == 3

    def test_from_file_success(self):
        """Test Config.from_file with valid YAML file"""
        yaml_content = """
ollama:
  host: http://test:11434
  timeout: 45
  models:
    large: test-llama:8b
    medium: test-phi:mini

processing:
  max_concurrent: 4
  chunk_size: 800

vector:
  collection_name: test_collection

log_level: DEBUG
"""
        
        with patch("builtins.open", mock_open(read_data=yaml_content)):
            with patch("pathlib.Path.exists", return_value=True):
                config = Config.from_file(Path("test_config.yaml"))
        
        assert config.ollama.host == "http://test:11434"
        assert config.ollama.timeout == 45
        assert config.ollama.models['large'] == "test-llama:8b"
        assert config.processing.max_concurrent == 4
        assert config.processing.chunk_size == 800
        assert config.vector.collection_name == "test_collection"
        assert config.log_level == "DEBUG"

    def test_from_file_yaml_error(self):
        """Test Config.from_file with invalid YAML"""
        invalid_yaml = "invalid: yaml: content: ["
        
        with patch("builtins.open", mock_open(read_data=invalid_yaml)):
            with patch("pathlib.Path.exists", return_value=True):
                config = Config.from_file(Path("invalid_config.yaml"))
        
        # Should return default config on error
        assert config.ollama.host == "http://localhost:11434"

    def test_save_to_file_success(self):
        """Test Config.save_to_file successful save"""
        config = Config()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.yaml"
            
            result = config.save_to_file(config_path)
            
            assert result is True
            assert config_path.exists()
            
            # Verify content is valid YAML
            import yaml
            with open(config_path, 'r', encoding='utf-8') as f:
                loaded_data = yaml.safe_load(f)
            
            assert 'ollama' in loaded_data
            assert 'processing' in loaded_data

    def test_save_to_file_error(self):
        """Test Config.save_to_file with error"""
        config = Config()
        
        # Try to save to read-only location
        with patch("builtins.open", side_effect=PermissionError("Permission denied")):
            result = config.save_to_file(Path("/readonly/config.yaml"))
            
            assert result is False

    def test_get_model_existing(self):
        """Test get_model with existing purpose"""
        config = Config()
        
        model = config.get_model("large")
        assert model == config.ollama.models["large"]

    def test_get_model_nonexistent(self):
        """Test get_model with nonexistent purpose"""
        config = Config()
        
        model = config.get_model("nonexistent")
        # Should return medium model as fallback
        assert model == config.ollama.models["medium"]

    def test_validate_valid_config(self):
        """Test validate with valid configuration"""
        config = Config()
        issues = config.validate()
        
        assert issues == []
        assert config.is_valid() is True

    def test_validate_invalid_timeout(self):
        """Test validate with invalid timeout"""
        config = Config()
        config.ollama.timeout = -1
        
        issues = config.validate()
        assert len(issues) > 0
        assert any("timeout must be positive" in issue for issue in issues)
        assert config.is_valid() is False

    def test_validate_invalid_chunk_overlap(self):
        """Test validate with invalid chunk overlap"""
        config = Config()
        config.processing.chunk_overlap = 1500  # Greater than chunk_size (1000)
        
        issues = config.validate()
        assert len(issues) > 0
        assert any("overlap must be less than" in issue for issue in issues)

    def test_validate_invalid_similarity_threshold(self):
        """Test validate with invalid similarity threshold"""
        config = Config()
        config.vector.similarity_threshold = 1.5  # Greater than 1.0
        
        issues = config.validate()
        assert len(issues) > 0
        assert any("Similarity threshold must be between 0 and 1" in issue for issue in issues)

    def test_validate_missing_models(self):
        """Test validate with missing models"""
        config = Config()
        config.ollama.models = {"large": "llama3:8b"}  # Missing other required models
        
        issues = config.validate()
        assert len(issues) > 0
        assert any("Missing model for purpose: medium" in issue for issue in issues)


class TestGlobalConfigFunctions:
    """Test suite for global configuration functions"""

    def setup_method(self):
        """Reset global config before each test"""
        import utils.config_simplified
        utils.config_simplified._global_config = None

    def test_get_config_default(self):
        """Test get_config returns default config"""
        with patch("utils.config_simplified.load_config") as mock_load:
            mock_config = Config()
            mock_load.return_value = mock_config
            
            config = get_config()
            
            assert config is mock_config
            mock_load.assert_called_once()

    def test_get_config_cached(self):
        """Test get_config returns cached config"""
        # Set global config
        test_config = Config()
        set_config(test_config)
        
        with patch("utils.config_simplified.load_config") as mock_load:
            config = get_config()
            
            assert config is test_config
            mock_load.assert_not_called()

    def test_set_config(self):
        """Test set_config functionality"""
        test_config = Config()
        set_config(test_config)
        
        assert get_config() is test_config

    def test_load_config_with_path(self):
        """Test load_config with specific path"""
        yaml_content = """
ollama:
  host: http://test:11434
log_level: DEBUG
"""
        
        with patch("builtins.open", mock_open(read_data=yaml_content)):
            with patch("pathlib.Path.exists", return_value=True):
                config = load_config(Path("test_config.yaml"))
        
        assert config.ollama.host == "http://test:11434"
        assert config.log_level == "DEBUG"

    def test_load_config_search_paths(self):
        """Test load_config searches multiple paths"""
        yaml_content = """
log_level: DEBUG
"""
        
        def mock_exists():
            return True  # Simulate that the first config file exists
        
        with patch("builtins.open", mock_open(read_data=yaml_content)):
            with patch("pathlib.Path.exists", side_effect=mock_exists):
                config = load_config()
        
        assert config.log_level == "DEBUG"

    def test_load_config_no_files(self):
        """Test load_config when no config files exist"""
        with patch("pathlib.Path.exists", return_value=False):
            config = load_config()
        
        # Should return default config
        assert config.ollama.host == "http://localhost:11434"

    def test_reload_config(self):
        """Test reload_config functionality"""
        # Set initial config
        initial_config = Config()
        set_config(initial_config)
        
        yaml_content = """
log_level: DEBUG
"""
        
        with patch("builtins.open", mock_open(read_data=yaml_content)):
            with patch("pathlib.Path.exists", return_value=True):
                reload_config(Path("new_config.yaml"))
        
        # Should have new config
        new_config = get_config()
        assert new_config is not initial_config
        assert new_config.log_level == "DEBUG"

    def test_get_model_for_purpose(self):
        """Test get_model_for_purpose convenience function"""
        test_config = Config()
        test_config.ollama.models["large"] = "test-model:8b"
        set_config(test_config)
        
        model = get_model_for_purpose("large")
        assert model == "test-model:8b"

    def test_get_ollama_host(self):
        """Test get_ollama_host convenience function"""
        test_config = Config()
        test_config.ollama.host = "http://test:11434"
        set_config(test_config)
        
        host = get_ollama_host()
        assert host == "http://test:11434"

    def test_get_processing_config(self):
        """Test get_processing_config convenience function"""
        test_config = Config()
        set_config(test_config)
        
        proc_config = get_processing_config()
        assert proc_config is test_config.processing

    def test_get_vector_config(self):
        """Test get_vector_config convenience function"""
        test_config = Config()
        set_config(test_config)
        
        vector_config = get_vector_config()
        assert vector_config is test_config.vector


class TestConfigEdgeCases:
    """Test edge cases and error conditions"""

    def test_config_with_none_values(self):
        """Test config handling with None values"""
        data = {
            'ollama': {
                'host': None,
                'timeout': None
            },
            'log_level': None
        }
        
        config = Config.from_dict(data)
        
        # Should preserve defaults for None values
        assert config.ollama.host == "http://localhost:11434"
        assert config.ollama.timeout == 60
        assert config.log_level == "INFO"

    def test_config_with_invalid_types(self):
        """Test config handling with invalid data types"""
        data = {
            'ollama': {
                'timeout': "invalid"  # Should be int
            },
            'processing': {
                'max_concurrent': "also_invalid"  # Should be int
            }
        }
        
        config = Config.from_dict(data)
        
        # Should handle gracefully and use defaults
        assert config.ollama.timeout == 60
        assert config.processing.max_concurrent == 3

    def test_deep_config_update(self):
        """Test that config updates don't affect nested dictionaries"""
        config1 = Config()
        config1.ollama.models["large"] = "model1"
        
        data = {'ollama': {'models': {'medium': 'model2'}}}
        config2 = Config.from_dict(data)
        
        # config2 should have the update plus defaults
        assert config2.ollama.models["medium"] == "model2"
        assert "large" in config2.ollama.models  # Should have default
        
        # config1 should be unchanged
        assert config1.ollama.models["large"] == "model1"


if __name__ == "__main__":
    pytest.main([__file__])
