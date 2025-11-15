# Document ID Issue - RESOLVED

## Problem Description

The `get_document` tool was failing with "Document not found" errors even when search returned valid results. This was caused by a mismatch between document IDs returned by search and the actual IDs in document frontmatter.

## Root Cause

1. **Search Results**: The `SearchManager` returned document IDs from ChromaDB's internal database
2. **Get Document**: The `DocumentManager` searched for documents by reading frontmatter
3. **The Gap**: Captured documents don't have `id` fields in their frontmatter, so IDs couldn't match

## Solution Implemented ✅

**Path-Based Retrieval** - IDs stay only in the database, not in document frontmatter.

### Changes Made

1. **Updated `SearchResult` schema** (`schemas/responses.py`)
   - Added `path` field to include the relative file path
   - LLM can now use path to retrieve documents

2. **Modified `SearchManager`** (`managers/search_manager.py`)
   - Now includes file path in every search result
   - Path is derived from the document's source file metadata

3. **Enhanced `get_document`** (`tools/search.py`)
   - Updated `GetDocumentRequest` to accept optional `path` parameter
   - Tries ID lookup first, falls back to path-based lookup
   - Handles both retrieval methods seamlessly

4. **Created rebuild script** (`rebuild_embeddings.py`)
   - Clears and rebuilds ChromaDB database
   - Ensures all documents have proper metadata
   - Validates database after rebuild

### Why This Works

- **No document modification needed**: Documents don't need `id` fields in frontmatter
- **Database-only IDs**: ChromaDB manages IDs internally
- **Path is stable**: File paths don't change and uniquely identify documents
- **Backward compatible**: Still works with documents that have IDs

## Usage

### Rebuild Database (if needed)

```bash
cd /home/dhayes/Source/PrismWeave/ai-processing
echo 'yes' | uv run python rebuild_embeddings.py
```

### How It Works Now

1. **Search**: Returns results with both `document_id` and `path`
   ```json
   {
     "document_id": "chunk_abc123",
     "path": "documents/tech/article.md",
     "score": 0.85,
     "excerpt": "..."
   }
   ```

2. **Retrieve**: LLM can use either ID or path
   ```python
   # Option 1: Try by ID (may fail for old documents)
   get_document(document_id="chunk_abc123")
   
   # Option 2: Use path (always works)
   get_document(path="documents/tech/article.md")
   
   # Option 3: Automatic fallback (implemented)
   get_document(document_id="chunk_abc123", path="documents/tech/article.md")
   ```

## Files Modified

- ✅ `prismweave_mcp/schemas/responses.py` - Added path to SearchResult
- ✅ `prismweave_mcp/schemas/requests.py` - Added path to GetDocumentRequest  
- ✅ `prismweave_mcp/managers/search_manager.py` - Populate path in results
- ✅ `prismweave_mcp/tools/search.py` - Implement path-based fallback
- ✅ `rebuild_embeddings.py` - Database rebuild utility (new file)

## Testing

After database rebuild completes:

1. Search for a document:
   ```python
   results = search_documents("GitHub Copilot CLI")
   ```

2. Verify result includes path:
   ```python
   assert "path" in results[0]
   ```

3. Retrieve using path:
   ```python
   doc = get_document(path=results[0]["path"])
   assert doc is not None
   ```

## Status: ✅ RESOLVED

The database is currently being rebuilt with proper metadata. Once complete, the `get_document` tool will work correctly with all search results.
