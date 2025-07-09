"""
PrismWeave AI Processing Pipeline
Core module for document analysis and semantic search
"""

from .models.ollama_client import OllamaClient
from .processors.langchain_document_processor import LangChainDocumentProcessor as DocumentProcessor
from .search.semantic_search import SemanticSearch
from .utils.config_simplified import Config

__version__ = "0.1.0"
__author__ = "PrismWeave Team"

# Main API exports
__all__ = [
    "OllamaClient",
    "DocumentProcessor", 
    "SemanticSearch",
    "Config"
]
