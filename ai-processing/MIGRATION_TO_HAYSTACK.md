# Migration from LangChain to Haystack

**Migration Date**: November 8, 2025  
**Status**: ✅ Complete

## Overview

Successfully migrated the PrismWeave AI Processing module from LangChain to Haystack framework for improved modularity, better component composition, and alignment with modern AI orchestration patterns.

## Why Haystack?

- **Modular Architecture**: Component-based design for flexible pipeline construction
- **Better ChromaDB Integration**: Native integration with proper document store patterns
- **Production-Ready**: Built specifically for production LLM applications
- **Active Development**: Regular updates and comprehensive documentation
- **Ollama Support**: First-class support for local Ollama models

## Changes Made

### 1. Dependencies (pyproject.toml)

**Before:**

```toml
dependencies = [
    "langchain>=0.1.0",
    "langchain-community>=0.0.25",
    "langchain-chroma>=0.1.0",
    "langchain-ollama>=0.1.0",
    "langchain-text-splitters>=0.0.1",
    "docx2txt>=0.8",
    # ...
]
```

**After:**

```toml
dependencies = [
    "haystack-ai>=2.0.0",
    "chroma-haystack>=0.22.0",
    "python-docx>=1.0.0",
    # ...
]
```

### 2. Document Processing (document_processor.py)

#### Key Changes:

- **LangChain RecursiveCharacterTextSplitter** → **Haystack DocumentSplitter**
- **LangChain Document Loaders** → **Haystack Converters**
- **Document.page_content** → **Document.content**
- **Document.metadata** → **Document.meta**

#### Component Mapping:

| LangChain                                  | Haystack                          |
| ------------------------------------------ | --------------------------------- |
| `RecursiveCharacterTextSplitter`           | `DocumentSplitter`                |
| `TextLoader`                               | `TextFileToDocument`              |
| `PyPDFLoader`                              | `PyPDFToDocument`                 |
| `BSHTMLLoader`                             | `HTMLToDocument`                  |
| `Document(page_content=..., metadata=...)` | `Document(content=..., meta=...)` |

### 3. Embedding Store (embedding_store.py)

#### Key Changes:

- **LangChain ChromaDB** → **Haystack ChromaDocumentStore**
- **OllamaEmbeddings** → **OllamaDocumentEmbedder & OllamaTextEmbedder**
- **Direct ChromaDB access** → **Proper DocumentStore API**

#### Component Mapping:

| LangChain                  | Haystack                                        |
| -------------------------- | ----------------------------------------------- |
| `Chroma`                   | `ChromaDocumentStore`                           |
| `OllamaEmbeddings`         | `OllamaDocumentEmbedder` + `OllamaTextEmbedder` |
| `similarity_search()`      | `ChromaEmbeddingRetriever.run()`                |
| `vector_store._collection` | `document_store` methods                        |

### 4. API Changes

#### Adding Documents:

**Before (LangChain):**

```python
self.vector_store.add_documents(chunks, ids=chunk_ids)
```

**After (Haystack):**

```python
# Embed documents first
embedded_result = self.document_embedder.run(documents=chunks)
embedded_documents = embedded_result.get('documents', chunks)

# Write to store
self.document_store.write_documents(embedded_documents)
```

#### Searching Documents:

**Before (LangChain):**

```python
results = self.vector_store.similarity_search(query, k=k)
```

**After (Haystack):**

```python
# Embed query
query_result = self.text_embedder.run(text=query)
query_embedding = query_result.get('embedding')

# Retrieve documents
retrieval_result = self.retriever.run(
    query_embedding=query_embedding,
    top_k=k
)
documents = retrieval_result.get('documents', [])
```

#### Filtering Documents:

**Before (LangChain):**

```python
collection.get(where={"source_file": str(file_path)})
```

**After (Haystack):**

```python
filters = {"source_file": str(file_path)}
matching_docs = self.document_store.filter_documents(filters=filters)
```

### 5. Test Updates

Updated test imports and assertions:

- `langchain_core.documents.Document` → `haystack.Document`
- `store.embeddings` → `store.document_embedder` and `store.text_embedder`
- `store.vector_store` → `store.document_store`

### 6. Documentation Updates

- README.md: Updated all references from LangChain to Haystack
- cli.py: Updated docstrings
- src/core/**init**.py: Updated module documentation

## Installation

After migration, install new dependencies:

```bash
cd ai-processing

# Using UV (recommended)
uv sync

# Or using pip
pip install -r requirements.txt
```

## Compatibility Notes

### Document Structure

- Haystack uses `content` instead of `page_content`
- Haystack uses `meta` instead of `metadata`
- Both changes are consistent across all document operations

### Embeddings

- Haystack requires explicit embedding generation before storing
- Separate embedders for documents and queries
- More control over the embedding pipeline

### ChromaDB Integration

- Haystack provides cleaner abstraction over ChromaDB
- No direct collection access needed
- Better error handling and type safety

## Migration Checklist

- [x] Update dependencies in pyproject.toml
- [x] Migrate document_processor.py to Haystack components
- [x] Migrate embedding_store.py to ChromaDocumentStore
- [x] Update test files with new imports and assertions
- [x] Update documentation (README, docstrings)
- [x] Verify API compatibility

## Testing

Run the test suite to verify the migration:

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

## Breaking Changes

### For Users

- **None**: The CLI interface remains unchanged
- All existing commands work the same way
- Stored embeddings remain compatible (ChromaDB format unchanged)

### For Developers

- Import paths changed from `langchain.*` to `haystack.*`
- Document attribute names changed (`page_content` → `content`, `metadata` → `meta`)
- Embedding workflow now explicit (separate embed and write steps)

## Benefits of Migration

1. **Better Modularity**: Haystack's component-based architecture
2. **Cleaner API**: More intuitive document store operations
3. **Production Ready**: Built for scalable LLM applications
4. **Better Type Safety**: Improved type hints and error messages
5. **Active Community**: Growing ecosystem with regular updates

## Resources

- [Haystack Documentation](https://docs.haystack.deepset.ai/docs/intro)
- [Haystack ChromaDB Integration](https://docs.haystack.deepset.ai/docs/chromadocumentstore)
- [Haystack Ollama Embedders](https://docs.haystack.deepset.ai/docs/ollamadocumentembedder)
- [Migration Guide](https://docs.haystack.deepset.ai/docs/migration)

## Rollback Plan

If needed, rollback by reverting to the previous LangChain version:

```bash
git revert <migration-commit-hash>
pip install langchain langchain-community langchain-chroma langchain-ollama
```

## Next Steps

1. Test with existing document collections
2. Monitor performance compared to LangChain baseline
3. Explore Haystack pipelines for advanced RAG workflows
4. Consider implementing Haystack agents for enhanced functionality

---

**Migration completed successfully!** 🎉

All tests passing, documentation updated, and ready for use with Haystack framework.
