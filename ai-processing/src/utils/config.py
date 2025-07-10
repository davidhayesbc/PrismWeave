"""
Configuration management for PrismWeave AI processing
Handles loading and validation of configuration settings
"""

import yaml
import os
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from loguru import logger

@dataclass
class OllamaConfig:
    """Ollama server configuration"""
    host: str = "http://localhost:11434"
    timeout: int = 30
    models: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ProcessingConfig:
    """Document processing configuration"""
    batch_size: int = 5
    max_concurrent: int = 2
    retry_attempts: int = 3
    retry_delay: float = 1.0
    min_content_length: int = 100
    max_content_length: int = 50000
    chunk_size: int = 1000
    chunk_overlap: int = 200
    quality_thresholds: Dict[str, float] = field(default_factory=lambda: {
        "high": 8.0, "medium": 5.0, "low": 2.0
    })

@dataclass
class VectorDBConfig:
    """Vector database configuration"""
    type: str = "chroma"
    chroma: Dict[str, Any] = field(default_factory=dict)
    sqlite: Dict[str, Any] = field(default_factory=dict)
    search: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SearchConfig:
    """Search configuration"""
    semantic_weight: float = 0.7
    keyword_weight: float = 0.3
    ranking: Dict[str, float] = field(default_factory=lambda: {
        "recency_weight": 0.1, "quality_weight": 0.3, "relevance_weight": 0.6
    })
    snippet_length: int = 200
    max_snippets: int = 3

class Config:
    """Main configuration class for PrismWeave AI processing"""

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._find_config_file()
        self._raw_config: Dict[str, Any] = {}
        self.ollama: OllamaConfig = OllamaConfig()
        self.processing: ProcessingConfig = ProcessingConfig()
        self.vector_db: VectorDBConfig = VectorDBConfig()
        self.search: SearchConfig = SearchConfig()

        self.load_config()

    def _find_config_file(self) -> str:
        """Find the configuration file in the project"""
        possible_paths = [
            "config.yaml",
            "../config.yaml",
            "../../config.yaml",
            os.path.expanduser("~/.prismweave/config.yaml")
        ]

        for path in possible_paths:
            if os.path.exists(path):
                return path

        # Return default path if none found
        return "config.yaml"

    def load_config(self) -> None:
        """Load configuration from YAML file"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self._raw_config = yaml.safe_load(f) or {}
                logger.info(f"Loaded configuration from {self.config_path}")
            else:
                logger.warning(f"Configuration file not found: {self.config_path}")
                self._raw_config = {}

            self._parse_config()

        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            self._raw_config = {}

    def _parse_config(self) -> None:
        """Parse raw configuration into structured objects"""
        try:
            # Parse Ollama configuration
            ollama_config = self._raw_config.get('ollama', {})
            self.ollama = OllamaConfig(
                host=ollama_config.get('host', "http://localhost:11434"),
                timeout=ollama_config.get('timeout', 30),
                models=ollama_config.get('models', {})
            )

            # Parse processing configuration
            proc_config = self._raw_config.get('processing', {})
            self.processing = ProcessingConfig(
                batch_size=proc_config.get('batch_size', 5),
                max_concurrent=proc_config.get('max_concurrent', 2),
                retry_attempts=proc_config.get('retry_attempts', 3),
                retry_delay=proc_config.get('retry_delay', 1.0),
                min_content_length=proc_config.get('min_content_length', 100),
                max_content_length=proc_config.get('max_content_length', 50000),
                chunk_size=proc_config.get('chunk_size', 1000),
                chunk_overlap=proc_config.get('chunk_overlap', 200),
                quality_thresholds=proc_config.get('quality_thresholds', {
                    "high": 8.0, "medium": 5.0, "low": 2.0
                })
            )

            # Parse vector database configuration
            vdb_config = self._raw_config.get('vector_db', {})
            self.vector_db = VectorDBConfig(
                type=vdb_config.get('type', 'chroma'),
                chroma=vdb_config.get('chroma', {}),
                sqlite=vdb_config.get('sqlite', {}),
                search=vdb_config.get('search', {})
            )

            # Parse search configuration
            search_config = self._raw_config.get('search', {})
            self.search = SearchConfig(
                semantic_weight=search_config.get('semantic_weight', 0.7),
                keyword_weight=search_config.get('keyword_weight', 0.3),
                ranking=search_config.get('ranking', {
                    "recency_weight": 0.1, "quality_weight": 0.3, "relevance_weight": 0.6
                }),
                snippet_length=search_config.get('snippet_length', 200),
                max_snippets=search_config.get('max_snippets', 3)
            )

        except Exception as e:
            logger.error(f"Failed to parse configuration: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value by key"""
        return self._raw_config.get(key, default)

    def get_model_config(self, model_type: str) -> Dict[str, Any]:
        """Get model configuration for a specific type"""
        return self.ollama.models.get(model_type, {})

    def get_documents_path(self) -> Path:
        """Get the documents directory path"""
        docs_path = self.get('integration', {}).get('documents_path', '../PrismWeaveDocs/documents')
        return Path(docs_path).resolve()

    def get_output_path(self, output_type: str) -> Path:
        """Get output directory path for specific type"""
        output_config = self.get('integration', {}).get('output', {})
        output_path = output_config.get(output_type, f'../.prismweave/{output_type}')
        return Path(output_path).resolve()

    def save_config(self, output_path: Optional[str] = None) -> None:
        """Save current configuration to file"""
        save_path = output_path or self.config_path
        try:
            with open(save_path, 'w', encoding='utf-8') as f:
                yaml.dump(self._raw_config, f, default_flow_style=False, sort_keys=False)
            logger.info(f"Configuration saved to {save_path}")
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")

# Global configuration instance
_config_instance: Optional[Config] = None

def get_config() -> Config:
    """Get the global configuration instance"""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance

def reload_config(config_path: Optional[str] = None) -> Config:
    """Reload the global configuration"""
    global _config_instance
    _config_instance = Config(config_path)
    return _config_instance
