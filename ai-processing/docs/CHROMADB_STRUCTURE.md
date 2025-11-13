# ChromaDB Database Structure and Querying Guide

## Overview

PrismWeave uses **ChromaDB** through **Haystack's integration** to store document embeddings for semantic search. This document explains the database structure, metadata schema, and how to query it directly.

## Database Location

- **Persist Directory**: `../../PrismWeaveDocs/.prismweave/chroma_db`
- **Collection Name**: `documents`
- **Access**: Through Haystack's `ChromaDocumentStore` wrapper

## Collection Structure

### Current State

- **Total Chunks**: 6,468 document chunks
- **Unique Documents**: Multiple source documents chunked for embeddings
- **Vector Dimensions**: 768 (nomic-embed-text model)

## Document Chunk Schema

Each chunk stored in ChromaDB has the following structure:

### Core Fields

```python
{
    "id": str,              # Haystack document UUID
    "content": str,         # Text content of the chunk
    "embedding": [float],   # 768-dimensional vector from nomic-embed-text
    "meta": {               # Metadata dictionary (see below)
        # ... metadata fields
    }
}
```

### Metadata Schema

Each document chunk includes extensive metadata:

```python
{
    # File Information
    "source_file": str,        # Full path to original markdown file
    "file_path": str,          # Alternative/legacy path field
    "chunk_id": str,           # Unique identifier: "{filename}_{index}_{uuid}"
    "chunk_index": int,        # Position in document (0-based)
    "total_chunks": int,       # Total number of chunks for this document

    # Document Content
    "title": str,              # Document title (from frontmatter or filename)
    "content_preview": str,    # First 200 chars of content
    "content_length": int,     # Length of chunk content

    # Document Metadata (from frontmatter)
    "tags": str,               # Comma-separated tag list
    "category": str,           # Document category (tech/general/generated)
    "created_date": str,       # ISO format datetime
    "source_url": str,         # Original web URL if captured
    "author": str,             # Document author
    "word_count": int,         # Total words in original document
    "reading_time": int,       # Estimated reading time in minutes

    # Search Metadata (added during retrieval)
    "score": float,            # Similarity score (0.0-1.0) - added by retriever

    # Processing Metadata
    "document_id": str,        # Logical document ID (may differ from chunk ID)
    "id": str                  # Duplicate of root id for convenience
}
```

## Database Architecture

### Haystack Integration Layer

```
┌─────────────────────────────────────────────────┐
│          PrismWeave Application                 │
│  (SearchManager, DocumentManager, MCP Tools)    │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│         EmbeddingStore (Wrapper)                │
│  - Document chunking and preparation            │
│  - Metadata cleaning and normalization          │
│  - Git tracking integration                     │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│    Haystack ChromaDocumentStore                 │
│  - Document CRUD operations                     │
│  - Filtering and retrieval                      │
│  - Embedding management                         │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│          ChromaDB (Persistent)                  │
│  - Vector storage and indexing                  │
│  - HNSW approximate nearest neighbor search     │
│  - SQLite-based metadata storage                │
└─────────────────────────────────────────────────┘
```

### Component Breakdown

1. **EmbeddingStore** (`src/core/embedding_store.py`)
   - High-level wrapper around Haystack's ChromaDocumentStore
   - Handles document chunking, metadata cleaning, and Git tracking
   - Methods: `add_document()`, `search_similar()`, `remove_file_documents()`

2. **Haystack ChromaDocumentStore**
   - Official Haystack integration for ChromaDB
   - Provides: `write_documents()`, `filter_documents()`, `count_documents()`
   - Auto-handles embeddings when used with `OllamaDocumentEmbedder`

3. **ChromaDB**
   - Vector database with HNSW indexing for fast similarity search
   - Persists to disk at configured `persist_directory`
   - Stores both vectors and metadata in SQLite

## Querying ChromaDB

### Method 1: Through EmbeddingStore (Recommended)

This is the primary interface used by PrismWeave:

```python
from src.core.embedding_store import EmbeddingStore
from src.core.config import Config

# Initialize
config = Config()
store = EmbeddingStore(config)

# 1. Semantic Search
results = store.search_similar("machine learning", k=10)
for doc in results:
    print(f"Title: {doc.meta['title']}")
    print(f"Snippet: {doc.content[:200]}")
    print(f"Source: {doc.meta['source_file']}")

# 2. Search with Scores
results_with_scores = store.search_similar_with_scores("AI concepts", k=5)
for doc, score in results_with_scores:
    print(f"Score: {score:.3f} - {doc.meta['title']}")

# 3. List All Documents
documents = store.list_documents(max_documents=100)
for doc_info in documents:
    print(f"ID: {doc_info['id']}")
    print(f"Metadata: {doc_info['metadata']}")
    print(f"Preview: {doc_info['content_preview']}")

# 4. Get Statistics
print(f"Total chunks: {store.get_document_count()}")
print(f"Unique files: {len(store.get_unique_source_files())}")

# 5. Verify Database Health
status = store.verify_embeddings()
print(f"Status: {status['status']}")
print(f"Documents: {status['document_count']}")
print(f"Search works: {status['search_functional']}")
```

### Method 2: Through SearchManager (MCP Layer)

Used by MCP server tools for advanced filtering:

```python
from prismweave_mcp.managers.search_manager import SearchManager
from src.core.config import Config

config = Config()
manager = SearchManager(config)
await manager.initialize()

# Search with filters
results, total = manager.search_documents(
    query="machine learning",
    max_results=20,
    similarity_threshold=0.7,
    filters={
        "tags": ["ai", "python"],      # Must have all these tags
        "category": "tech",             # Must be in tech category
        "generated": False,             # Exclude generated content
        "date_from": "2025-01-01",     # Minimum date
        "date_to": "2025-12-31"        # Maximum date
    }
)

# Results are SearchResult objects with structured metadata
for result in results:
    print(f"Score: {result.score:.3f}")
    print(f"Title: {result.metadata.title}")
    print(f"Excerpt: {result.excerpt}")
    print(f"Tags: {result.metadata.tags}")
```

### Method 3: Direct ChromaDB Access (Low-Level)

For advanced debugging or custom queries:

```python
import chromadb
from pathlib import Path

# Connect to existing ChromaDB
persist_dir = Path("../../PrismWeaveDocs/.prismweave/chroma_db")
client = chromadb.PersistentClient(path=str(persist_dir))

# Get collection
collection = client.get_collection(name="documents")

# 1. Get collection info
print(f"Total items: {collection.count()}")

# 2. Query by metadata
results = collection.get(
    where={"source_file": {"$contains": "simonwillison"}},
    limit=10
)
print(f"Found {len(results['ids'])} documents")

# 3. Peek at random documents
sample = collection.peek(limit=5)
for i, doc_id in enumerate(sample['ids']):
    print(f"\nDocument {i+1}:")
    print(f"  ID: {doc_id}")
    print(f"  Metadata: {sample['metadatas'][i]}")
    print(f"  Content preview: {sample['documents'][i][:100]}")

# 4. Query with embedding (requires computing embedding first)
# Note: You need to generate embedding using same model (nomic-embed-text)
# query_embedding = [...]  # 768-dimensional vector
# results = collection.query(
#     query_embeddings=[query_embedding],
#     n_results=10
# )

# 5. Get all metadata for a specific file
results = collection.get(
    where={"source_file": "/path/to/document.md"},
    include=["metadatas", "documents"]
)

# 6. Filter by tags (ChromaDB metadata filtering)
results = collection.get(
    where={"tags": {"$contains": "machine-learning"}},
    limit=20
)
```

### Method 4: Through Haystack ChromaDocumentStore

For operations using Haystack abstractions:

```python
from haystack_integrations.document_stores.chroma import ChromaDocumentStore
from pathlib import Path

# Initialize document store
persist_dir = Path("../../PrismWeaveDocs/.prismweave/chroma_db")
document_store = ChromaDocumentStore(
    collection_name="documents",
    persist_path=str(persist_dir)
)

# 1. Count documents
count = document_store.count_documents()
print(f"Total documents: {count}")

# 2. Filter documents by metadata
filtered_docs = document_store.filter_documents(
    filters={"source_file": "/path/to/document.md"}
)

# 3. Get all documents
all_docs = document_store.filter_documents(filters={})
for doc in all_docs[:5]:
    print(f"ID: {doc.id}")
    print(f"Content length: {len(doc.content)}")
    print(f"Metadata: {doc.meta}")

# 4. Delete documents
doc_ids = ["doc_id_1", "doc_id_2"]
document_store.delete_documents(doc_ids)

# 5. Get unique source files
all_docs = document_store.filter_documents(filters={})
source_files = set(doc.meta.get("source_file") for doc in all_docs if "source_file" in doc.meta)
print(f"Unique source files: {len(source_files)}")
```

## Common Query Patterns

### Find All Chunks for a Specific Document

```python
# Method 1: EmbeddingStore
from pathlib import Path

file_path = Path("../../PrismWeaveDocs/documents/2025-08-11-simonwillison.net-blog-s-1528.md")
chunk_count = store.get_file_document_count(file_path)
print(f"Document has {chunk_count} chunks")

# Method 2: ChromaDocumentStore
filters = {"source_file": str(file_path)}
chunks = document_store.filter_documents(filters=filters)
print(f"Found {len(chunks)} chunks")
```

### Search Within a Category

```python
# Through SearchManager with category filter
results, total = manager.search_documents(
    query="AI developments",
    filters={"category": "tech"}
)
```

### Find Documents by Tags

```python
# Through SearchManager
results, total = manager.search_documents(
    query="AI",
    filters={"tags": ["machine-learning", "python"]}  # Documents must have BOTH tags
)
```

### Get Recently Added Documents

```python
# Through SearchManager with date filter
from datetime import datetime, timedelta

week_ago = (datetime.now() - timedelta(days=7)).isoformat()
results, total = manager.search_documents(
    query="",  # Empty query returns all
    filters={"date_from": week_ago},
    max_results=50
)
```

### Find All Documents from a Specific Website

```python
# Direct ChromaDB query
results = collection.get(
    where={"source_url": {"$contains": "simonwillison.net"}},
    include=["metadatas", "documents"]
)

# Group by source_file to get unique documents
unique_docs = {}
for i, metadata in enumerate(results['metadatas']):
    source_file = metadata['source_file']
    if source_file not in unique_docs:
        unique_docs[source_file] = metadata

print(f"Found {len(unique_docs)} unique documents from simonwillison.net")
```

## ChromaDB Query Operators

ChromaDB supports various metadata filtering operators:

```python
# Equality
{"category": "tech"}

# Contains (substring match)
{"source_file": {"$contains": "simonwillison"}}

# Greater than / Less than
{"word_count": {"$gt": 1000}}
{"word_count": {"$lt": 5000}}

# In (one of many values)
{"category": {"$in": ["tech", "general"]}}

# Not equal
{"category": {"$ne": "generated"}}

# Logical AND
{"$and": [
    {"category": "tech"},
    {"tags": {"$contains": "ai"}}
]}

# Logical OR
{"$or": [
    {"category": "tech"},
    {"category": "general"}
]}
```

## Metadata Cleaning Rules

EmbeddingStore automatically cleans metadata before storage:

```python
def _clean_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Cleaning rules:
    1. None values are removed
    2. Simple types (str, int, float, bool) are kept as-is
    3. Lists are converted to comma-separated strings
    4. Other types are converted to strings
    """
```

This ensures ChromaDB compatibility since ChromaDB only supports:

- Strings
- Integers
- Floats
- Booleans

## Database Maintenance

### Verify Database Health

```python
status = store.verify_embeddings()

# Returns:
{
    "status": "success" | "error",
    "document_count": 6468,
    "search_functional": True,
    "collection_name": "documents",
    "persist_directory": "/path/to/chroma_db",
    "error": "error message if failed"
}
```

### Clear All Documents

```python
store.clear_collection()
```

### Remove Specific Document

```python
from pathlib import Path

file_path = Path("../../PrismWeaveDocs/documents/document-to-remove.md")
success = store.remove_file_documents(file_path)
```

### Get Statistics

```python
# Via SearchManager
stats = manager.get_search_stats()

# Returns:
{
    "total_chunks": 6468,
    "unique_documents": 123,
    "collection_name": "documents",
    "search_functional": True,
    "persist_directory": "/path/to/chroma_db"
}
```

## MCP Tool Integration

The MCP server exposes these ChromaDB operations through tools:

1. **search_documents**: Semantic search with filtering
2. **list_documents**: Browse available documents
3. **get_document**: Retrieve specific document by ID
4. **get_document_metadata**: Get metadata without full content
5. **create_document**: Add new document (generates embeddings)
6. **update_document**: Update existing document (regenerates embeddings if needed)
7. **generate_embeddings**: Manually trigger embedding generation
8. **generate_tags**: AI-powered tag generation
9. **commit_to_git**: Commit changes to Git repository

All these tools interact with ChromaDB through the abstraction layers.

## Performance Considerations

### Indexing

- ChromaDB uses HNSW (Hierarchical Navigable Small World) graphs for fast approximate nearest neighbor search
- Vector search is O(log n) complexity
- Metadata filtering is done after vector search

### Optimization Tips

1. **Chunk Size**: Current setting of 1000 chars with 200 overlap is optimized for web documents
2. **Similarity Threshold**: 0.6 default provides good balance between precision and recall
3. **Max Results**: Limit to reasonable numbers (20-50) for UI responsiveness
4. **Metadata Filtering**: Apply filters after search for best performance

### Storage

- Each 768-dimensional vector: ~3KB
- 6,468 chunks: ~19.4 MB of vector data
- Metadata adds minimal overhead (~1KB per chunk)
- Total database size: ~25-30 MB for current collection

## Troubleshooting

### Database Not Found

```python
# Ensure persist directory exists
persist_dir = Path(config.chroma_db_path)
persist_dir.mkdir(parents=True, exist_ok=True)
```

### No Search Results

```python
# 1. Verify documents exist
count = store.get_document_count()
print(f"Documents in database: {count}")

# 2. Lower similarity threshold
results = manager.search_documents(
    query="your query",
    similarity_threshold=0.3  # Lower threshold
)

# 3. Check if embeddings were generated
status = store.verify_embeddings()
print(f"Search functional: {status['search_functional']}")
```

### Metadata Not Showing

```python
# Verify metadata was stored during add_document
filters = {"source_file": str(file_path)}
docs = document_store.filter_documents(filters=filters)
if docs:
    print(f"First chunk metadata: {docs[0].meta}")
```

## Advanced Topics

### Custom Embedding Models

To use a different embedding model:

```yaml
# config.yaml
ollama:
  models:
    embedding: 'custom-model-name'
```

Note: Changing models requires re-embedding all documents.

### Multiple Collections

ChromaDB supports multiple collections:

```python
# Create separate collection for generated content
generated_store = ChromaDocumentStore(
    collection_name="generated_documents",
    persist_path=str(persist_dir)
)
```

### Backup and Migration

```python
# Export all documents
all_docs = store.list_documents()

# Save to JSON for backup
import json
with open("chromadb_backup.json", "w") as f:
    json.dump(all_docs, f, indent=2)

# Restore to new collection
# (requires re-embedding with add_document)
```

## Summary

ChromaDB in PrismWeave provides:

- ✅ Fast semantic search across 6,468+ document chunks
- ✅ Rich metadata filtering (tags, categories, dates, URLs)
- ✅ Persistent storage with automatic indexing
- ✅ Haystack integration for embeddings and retrieval
- ✅ MCP server tools for easy integration
- ✅ Multiple query interfaces (EmbeddingStore, SearchManager, direct ChromaDB)

For most use cases, use **SearchManager** for filtered semantic search or **EmbeddingStore** for direct database operations.
