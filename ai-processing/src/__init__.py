"""
PrismWeave AI Processing - Simplified
Core module for document processing and embedding storage
"""

from .core import Config, DocumentProcessor, EmbeddingStore, load_config, process_documents

__version__ = "0.1.0"
__author__ = "PrismWeave Team"

# Main API exports
__all__ = ["DocumentProcessor", "EmbeddingStore", "Config", "load_config", "process_documents"]
