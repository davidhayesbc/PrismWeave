"""
Simplified configuration management for PrismWeave AI processing
Clean, straightforward configuration without complex fallback mechanisms
"""

import yaml
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)

@dataclass
class OllamaConfig:
    """Configuration for Ollama LLM server"""
    host: str = "http://localhost:11434"
    timeout: int = 60

    # Simple model mapping - one model per purpose
    models: Dict[str, str] = field(default_factory=lambda: {
        "large": "llama3.1:8b",
        "medium": "phi3:mini",
        "small": "phi3:mini",
        "embedding": "nomic-embed-text"
    })

@dataclass
class ProcessingConfig:
    """Configuration for document processing"""
    max_concurrent: int = 3
    chunk_size: int = 1000
    chunk_overlap: int = 200
    min_chunk_size: int = 100

    # Processing timeouts
    summary_timeout: int = 120
    tagging_timeout: int = 60
    categorization_timeout: int = 30

    # Content filtering
    min_word_count: int = 50
    max_word_count: int = 50000

    # Output settings
    max_summary_length: int = 500
    max_tags: int = 10

@dataclass
class VectorConfig:
    """Configuration for vector database"""
    collection_name: str = "documents"
    persist_directory: str = "./chroma_db"
    embedding_function: str = "sentence-transformers"

    # Search settings
    max_results: int = 10
    similarity_threshold: float = 0.7

@dataclass
class Config:
    """Main configuration container"""
    ollama: OllamaConfig = field(default_factory=OllamaConfig)
    processing: ProcessingConfig = field(default_factory=ProcessingConfig)
    vector: VectorConfig = field(default_factory=VectorConfig)

    # Logging
    log_level: str = "INFO"
    log_file: Optional[str] = None

    @classmethod
    def from_file(cls, config_path: Path) -> 'Config':
        """Load configuration from YAML file"""
        logger.info(f"Loading configuration from: {config_path}")

        if not config_path.exists():
            logger.warning(f"Config file not found: {config_path}, using defaults")
            return cls()

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}

            logger.debug(f"Loaded config data: {list(data.keys())}")
            return cls.from_dict(data)

        except Exception as e:
            logger.error(f"Failed to load config from {config_path}: {e}")
            logger.info("Using default configuration")
            return cls()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Config':
        """Create configuration from dictionary"""
        config = cls()

        # Update Ollama config
        if 'ollama' in data:
            ollama_data = data['ollama']
            config.ollama.host = ollama_data.get('host', config.ollama.host)
            config.ollama.timeout = ollama_data.get('timeout', config.ollama.timeout)

            # Update models if provided
            if 'models' in ollama_data:
                config.ollama.models.update(ollama_data['models'])

        # Update processing config
        if 'processing' in data:
            proc_data = data['processing']
            for key, value in proc_data.items():
                if hasattr(config.processing, key):
                    setattr(config.processing, key, value)

        # Update vector config
        if 'vector' in data:
            vector_data = data['vector']
            for key, value in vector_data.items():
                if hasattr(config.vector, key):
                    setattr(config.vector, key, value)

        # Update top-level settings
        config.log_level = data.get('log_level', config.log_level)
        config.log_file = data.get('log_file', config.log_file)

        return config

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'ollama': {
                'host': self.ollama.host,
                'timeout': self.ollama.timeout,
                'models': self.ollama.models
            },
            'processing': {
                'max_concurrent': self.processing.max_concurrent,
                'chunk_size': self.processing.chunk_size,
                'chunk_overlap': self.processing.chunk_overlap,
                'min_chunk_size': self.processing.min_chunk_size,
                'summary_timeout': self.processing.summary_timeout,
                'tagging_timeout': self.processing.tagging_timeout,
                'categorization_timeout': self.processing.categorization_timeout,
                'min_word_count': self.processing.min_word_count,
                'max_word_count': self.processing.max_word_count,
                'max_summary_length': self.processing.max_summary_length,
                'max_tags': self.processing.max_tags
            },
            'vector': {
                'collection_name': self.vector.collection_name,
                'persist_directory': self.vector.persist_directory,
                'embedding_function': self.vector.embedding_function,
                'max_results': self.vector.max_results,
                'similarity_threshold': self.vector.similarity_threshold
            },
            'log_level': self.log_level,
            'log_file': self.log_file
        }

    def save_to_file(self, config_path: Path) -> bool:
        """Save configuration to YAML file"""
        try:
            config_path.parent.mkdir(parents=True, exist_ok=True)

            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.safe_dump(
                    self.to_dict(),
                    f,
                    default_flow_style=False,
                    sort_keys=True
                )

            logger.info(f"Configuration saved to: {config_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to save config to {config_path}: {e}")
            return False

    def get_model(self, purpose: str) -> str:
        """Get model name for a specific purpose"""
        model = self.ollama.models.get(purpose)
        if not model:
            logger.warning(f"No model configured for purpose: {purpose}")
            # Return medium model as fallback
            return self.ollama.models.get('medium', 'phi3:mini')
        return model

    def validate(self) -> List[str]:
        """Validate configuration and return list of issues"""
        issues = []

        # Check required models
        required_purposes = ['large', 'medium', 'small', 'embedding']
        for purpose in required_purposes:
            if purpose not in self.ollama.models:
                issues.append(f"Missing model for purpose: {purpose}")

        # Check numeric values
        if self.ollama.timeout <= 0:
            issues.append("Ollama timeout must be positive")

        if self.processing.max_concurrent <= 0:
            issues.append("Max concurrent must be positive")

        if self.processing.chunk_size <= 0:
            issues.append("Chunk size must be positive")

        if self.processing.chunk_overlap >= self.processing.chunk_size:
            issues.append("Chunk overlap must be less than chunk size")

        if self.vector.similarity_threshold < 0 or self.vector.similarity_threshold > 1:
            issues.append("Similarity threshold must be between 0 and 1")

        return issues

    def is_valid(self) -> bool:
        """Check if configuration is valid"""
        return len(self.validate()) == 0

# Global configuration instance
_global_config: Optional[Config] = None

def get_config() -> Config:
    """Get the global configuration instance"""
    global _global_config
    if _global_config is None:
        _global_config = load_config()
    return _global_config

def load_config(config_path: Optional[Path] = None) -> Config:
    """Load configuration from file or create default"""
    if config_path is None:
        # Look for config files in order of preference
        possible_paths = [
            Path("config.yaml"),
            Path("config.simplified.yaml"),
            Path("ai-processing/config.yaml"),
            Path("ai-processing/config.simplified.yaml")
        ]

        for path in possible_paths:
            if path.exists():
                config_path = path
                break
        else:
            logger.info("No config file found, using defaults")
            return Config()

    return Config.from_file(config_path)

def set_config(config: Config):
    """Set the global configuration instance"""
    global _global_config
    _global_config = config

def reload_config(config_path: Optional[Path] = None):
    """Reload configuration from file"""
    global _global_config
    _global_config = load_config(config_path)
    logger.info("Configuration reloaded")

# Convenience functions
def get_model_for_purpose(purpose: str) -> str:
    """Get model name for a specific purpose"""
    return get_config().get_model(purpose)

def get_ollama_host() -> str:
    """Get Ollama server host"""
    return get_config().ollama.host

def get_processing_config() -> ProcessingConfig:
    """Get processing configuration"""
    return get_config().processing

def get_vector_config() -> VectorConfig:
    """Get vector database configuration"""
    return get_config().vector
