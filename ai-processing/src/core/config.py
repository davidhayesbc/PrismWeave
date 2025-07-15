"""
Configuration management for PrismWeave AI processing
"""

import yaml
from pathlib import Path
from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    """Configuration for PrismWeave document processing"""
    
    # Ollama settings
    ollama_host: str = "http://localhost:11434"
    ollama_timeout: int = 60
    embedding_model: str = "nomic-embed-text:latest"
    
    # Document processing settings
    chunk_size: int = 1000  # Smaller chunks for web documents
    chunk_overlap: int = 200
    
    # ChromaDB settings
    chroma_db_path: str = "../../PrismWeaveDocs/.prismweave/chroma_db"
    collection_name: str = "documents"
    
    def validate(self) -> list[str]:
        """Validate configuration and return any issues"""
        issues = []
        
        if not self.ollama_host:
            issues.append("Ollama host cannot be empty")
        
        if self.chunk_size <= 0:
            issues.append("Chunk size must be positive")
            
        if self.chunk_overlap >= self.chunk_size:
            issues.append("Chunk overlap must be less than chunk size")
            
        if not self.embedding_model:
            issues.append("Embedding model cannot be empty")
            
        return issues
    
    @classmethod
    def from_file(cls, config_path: Path) -> 'Config':
        """Load configuration from YAML file"""
        return load_config(config_path)


def load_config(config_path: Optional[Path] = None) -> Config:
    """Load configuration from YAML file or use defaults"""
    
    if config_path is None:
        # Look for config.yaml in the ai-processing directory
        config_path = Path(__file__).parent.parent.parent / "config.yaml"
    
    if not config_path.exists():
        print(f"Config file not found at {config_path}, using defaults")
        return Config()
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        
        # Extract relevant values with fallbacks to defaults
        config = Config()
        
        # Ollama settings
        if 'ollama' in config_data:
            ollama_config = config_data['ollama']
            config.ollama_host = ollama_config.get('host', config.ollama_host)
            config.ollama_timeout = ollama_config.get('timeout', config.ollama_timeout)
            
            if 'models' in ollama_config:
                config.embedding_model = ollama_config['models'].get('embedding', config.embedding_model)
        
        # Processing settings
        if 'processing' in config_data:
            processing_config = config_data['processing']
            config.chunk_size = processing_config.get('chunk_size', config.chunk_size)
            config.chunk_overlap = processing_config.get('chunk_overlap', config.chunk_overlap)
        
        # Vector database settings
        if 'vector' in config_data:
            vector_config = config_data['vector']
            config.chroma_db_path = vector_config.get('persist_directory', config.chroma_db_path)
            config.collection_name = vector_config.get('collection_name', config.collection_name)
        
        return config
        
    except Exception as e:
        print(f"Error loading config from {config_path}: {e}")
        print("Using default configuration")
        return Config()
