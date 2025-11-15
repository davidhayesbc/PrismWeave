#!/usr/bin/env python3
"""
Rebuild ChromaDB Embeddings Database

This script clears the existing ChromaDB database and rebuilds it from scratch,
ensuring all documents have proper embeddings with consistent metadata.
"""

import shutil
import sys
from pathlib import Path

from src.core.config import load_config
from src.core.document_processor import DocumentProcessor
from src.core.embedding_store import EmbeddingStore


def rebuild_embeddings(clear_db: bool = True):
    """
    Rebuild the embeddings database

    Args:
        clear_db: If True, delete existing database before rebuilding
    """
    print("Loading configuration...")
    config = load_config()

    # Get ChromaDB path
    chroma_path = Path(config.chroma_db_path).expanduser().resolve()

    if clear_db and chroma_path.exists():
        print(f"Clearing existing database at {chroma_path}...")
        try:
            shutil.rmtree(chroma_path)
            print("✓ Database cleared")
        except Exception as e:
            print(f"✗ Failed to clear database: {e}")
            return False

    print("\nInitializing embedding store...")
    embedding_store = EmbeddingStore(config)

    print("Initializing document processor...")
    processor = DocumentProcessor(config)

    # Get documents root
    docs_root = Path(config.mcp.paths.documents_root).expanduser().resolve()
    print(f"\nScanning documents in: {docs_root}")

    # Find all markdown files
    markdown_files = list(docs_root.rglob("*.md"))
    print(f"Found {len(markdown_files)} markdown files")

    processed_count = 0
    error_count = 0

    for i, file_path in enumerate(markdown_files, 1):
        try:
            # Show progress
            rel_path = file_path.relative_to(docs_root)
            print(f"\n[{i}/{len(markdown_files)}] Processing: {rel_path}")

            # Process document to get chunks
            chunks = processor.process_document(file_path)

            if chunks:
                # Add chunks to embedding store
                embedding_store.add_document(file_path, chunks)
                print(f"  ✓ Created {len(chunks)} chunks")
                processed_count += 1
            else:
                print("  ✗ No chunks created")
                error_count += 1

        except Exception as e:
            print(f"  ✗ Error: {e}")
            error_count += 1

    print("\n" + "=" * 60)
    print("REBUILD SUMMARY")
    print("=" * 60)
    print(f"Total files: {len(markdown_files)}")
    print(f"Successfully processed: {processed_count}")
    print(f"Errors: {error_count}")

    # Verify the database
    print("\nVerifying database...")
    status = embedding_store.verify_embeddings()

    if status["status"] == "success":
        print("✓ Database verified")
        print(f"  Collection: {status['collection_name']}")
        print(f"  Total chunks: {status['document_count']}")
        print(f"  Unique documents: {len(embedding_store.get_unique_source_files())}")
    else:
        print(f"✗ Database verification failed: {status.get('error')}")
        return False

    return True


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Rebuild ChromaDB embeddings database")
    parser.add_argument("--keep-db", action="store_true", help="Keep existing database (add to it instead of clearing)")

    args = parser.parse_args()

    print("=" * 60)
    print("PRISMWEAVE EMBEDDINGS DATABASE REBUILD")
    print("=" * 60)

    if not args.keep_db:
        print("\nWARNING: This will DELETE the existing database!")
        response = input("Continue? (yes/no): ")
        if response.lower() != "yes":
            print("Aborted.")
            sys.exit(0)

    success = rebuild_embeddings(clear_db=not args.keep_db)

    if success:
        print("\n✓ Database rebuild completed successfully!")
        sys.exit(0)
    else:
        print("\n✗ Database rebuild failed!")
        sys.exit(1)
