"""
PrismWeave AI Processing Pipeline
Core module for document analysis and semantic search
"""

from .models.ollama_client import OllamaClient
from .processors.document_processor import DocumentProcessor
from .search.semantic_search import SemanticSearch
from .utils.config import Config

__version__ = "0.1.0"
__author__ = "PrismWeave Team"

# Main API exports
__all__ = [
    "OllamaClient",
    "DocumentProcessor", 
    "SemanticSearch",
    "Config"
]
