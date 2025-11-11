"""
PrismWeave Core - Simplified Document Processing and Embedding Storage

This module provides a simplified interface for processing documents and storing embeddings
using Haystack and Ollama for local AI processing.
"""

from pathlib import Path
from typing import Optional

from .config import Config, load_config
from .document_processor import DocumentProcessor
from .embedding_store import EmbeddingStore

__all__ = ["DocumentProcessor", "EmbeddingStore", "Config", "load_config", "process_documents"]


def process_documents(input_dir: str, embeddings_dir: Optional[str] = None, config_path: Optional[str] = None):
    """
    Process all documents in a directory and store embeddings.

    Args:
        input_dir: Directory containing documents to process
        embeddings_dir: Directory to store ChromaDB embeddings (optional)
        config_path: Path to config file (optional)
    """

    # Load configuration
    if config_path:
        config = load_config(Path(config_path))
    else:
        config = load_config()

    # Override embeddings directory if provided
    if embeddings_dir:
        config.chroma_db_path = embeddings_dir

    # Initialize processor and store
    processor = DocumentProcessor(config)
    store = EmbeddingStore(config)

    # Process all documents
    input_path = Path(input_dir)
    if not input_path.exists():
        raise ValueError(f"Input directory does not exist: {input_dir}")

    print(f"Processing documents from: {input_path}")
    print(f"Storing embeddings in: {config.chroma_db_path}")

    # Find all supported document files
    supported_extensions = {".md", ".txt", ".pdf", ".docx", ".html", ".htm"}
    documents = []

    for ext in supported_extensions:
        documents.extend(input_path.rglob(f"*{ext}"))

    if not documents:
        print("No supported documents found.")
        return

    print(f"Found {len(documents)} documents to process.")

    # Process each document
    processed_count = 0
    error_count = 0

    for doc_path in documents:
        try:
            print(f"Processing: {doc_path.name}")

            # Load and process document
            chunks = processor.process_document(doc_path)

            # Store embeddings
            store.add_document(doc_path, chunks)

            processed_count += 1

        except (OSError, ValueError, RuntimeError) as e:
            print(f"Error processing {doc_path.name}: {e}")
            error_count += 1

    print("\nProcessing complete:")
    print("  Successfully processed: {processed_count}")
    print("  Errors: {error_count}")

    # Verify embeddings
    print("\nVerifying embeddings...")
    verification_result = store.verify_embeddings()
    print(f"Verification result: {verification_result}")
