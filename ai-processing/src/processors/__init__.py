"""
Processors package for document processing components
"""

try:
    from .langchain_document_processor import (
        LangChainDocumentProcessor,
        DocumentAnalysis,
        ChunkMetadata,
        ProcessedDocument
    )
    __all__ = [
        "LangChainDocumentProcessor",
        "DocumentAnalysis", 
        "ChunkMetadata",
        "ProcessedDocument"
    ]
except ImportError as e:
    # Handle import errors gracefully for testing environment
    print(f"Warning: Could not import processors components: {e}")
    __all__ = []
