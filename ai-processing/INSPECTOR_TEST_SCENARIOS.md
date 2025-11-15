# MCP Inspector - Quick Test Scenarios

## Scenario 1: Document Search & Discovery

**Goal**: Find relevant documents using semantic search

### Step 1: Search for Documents

```json
Tool: search_documents
{
  "query": "python programming tutorials",
  "max_results": 5,
  "similarity_threshold": 0.6
}
```

**Expected**: List of relevant documents with similarity scores

### Step 2: Get Full Document

```json
Tool: get_document
{
  "document_id": "<copy from search results>",
  "include_content": true
}
```

**Expected**: Complete document with metadata and content

---

## Scenario 2: Create & Process New Document

**Goal**: Create a document and generate AI enhancements

### Step 1: Create Document

```json
Tool: create_document
{
  "title": "Quick Start Guide for AI Tools",
  "content": "# Quick Start\n\n## Introduction\n\nThis guide covers essential AI development tools and frameworks.\n\n## Key Tools\n\n1. **Ollama** - Local LLM inference\n2. **ChromaDB** - Vector database\n3. **LangChain** - AI orchestration\n\n## Getting Started\n\nInstall Ollama and pull a model to begin experimenting with local AI.",
  "category": "guides",
  "tags": ["ai", "tools", "quickstart"]
}
```

**Expected**: Document ID and file path

### Step 2: Generate Embeddings

```json
Tool: generate_embeddings
{
  "document_id": "<from step 1>",
  "model": "nomic-embed-text",
  "force_regenerate": false
}
```

**Expected**: Embedding count and model confirmation

### Step 3: Generate AI Tags

```json
Tool: generate_tags
{
  "document_id": "<from step 1>",
  "max_tags": 7,
  "force_regenerate": true
}
```

**Expected**: AI-generated tags with confidence score

### Step 4: Verify Searchability

```json
Tool: search_documents
{
  "query": "local AI development tools",
  "max_results": 5
}
```

**Expected**: Your new document should appear in results

---

## Scenario 3: Document Collection Management

**Goal**: Browse and manage document collection

### Step 1: List All Documents

```json
Tool: list_documents
{
  "limit": 20,
  "offset": 0
}
```

**Expected**: First 20 documents with metadata

### Step 2: Filter by Category

```json
Tool: list_documents
{
  "category": "tech",
  "limit": 10
}
```

**Expected**: Documents in "tech" category

### Step 3: Paginate Through Collection

```json
Tool: list_documents
{
  "limit": 10,
  "offset": 10
}
```

**Expected**: Next 10 documents (page 2)

---

## Scenario 4: Document Update Workflow

**Goal**: Update existing document metadata

### Step 1: Find Document to Update

```json
Tool: search_documents
{
  "query": "test document",
  "max_results": 1
}
```

### Step 2: Get Current Metadata

```json
Tool: get_document_metadata
{
  "document_id": "<from search>"
}
```

### Step 3: Update Document

```json
Tool: update_document
{
  "document_id": "<from search>",
  "title": "Updated: Test Document v2",
  "tags": ["updated", "test", "v2", "revised"],
  "category": "testing-updated"
}
```

**Expected**: Confirmation of updated fields

### Step 4: Regenerate Embeddings

```json
Tool: generate_embeddings
{
  "document_id": "<same ID>",
  "force_regenerate": true
}
```

**Expected**: New embeddings generated

---

## Scenario 5: Error Handling Tests

**Goal**: Verify proper error responses

### Test 1: Invalid Document ID

```json
Tool: get_document
{
  "document_id": "invalid_doc_id_12345",
  "include_content": true
}
```

**Expected**: Error response with "DOCUMENT_NOT_FOUND" code

### Test 2: Empty Search Query

```json
Tool: search_documents
{
  "query": "",
  "max_results": 5
}
```

**Expected**: Should handle gracefully or return error

### Test 3: Invalid Parameters

```json
Tool: list_documents
{
  "limit": -10,
  "offset": -5
}
```

**Expected**: Validation error or empty results

---

## Scenario 6: Performance Testing

**Goal**: Test system performance with various loads

### Test 1: Large Result Set

```json
Tool: search_documents
{
  "query": "document",
  "max_results": 100
}
```

**Expected**: Should return results quickly (< 2 seconds)

### Test 2: High Similarity Threshold

```json
Tool: search_documents
{
  "query": "very specific unique phrase",
  "similarity_threshold": 0.95
}
```

**Expected**: Fewer, more precise results

### Test 3: Batch Document Listing

```json
Tool: list_documents
{
  "limit": 100
}
```

**Expected**: Fast retrieval of metadata

---

## Quick Reference: Common Operations

### Find a Specific Topic

```json
search_documents { "query": "your topic", "max_results": 10 }
```

### Browse Documents

```json
list_documents { "limit": 20, "offset": 0 }
```

### Create Test Document

```json
create_document {
  "title": "Test",
  "content": "# Test\n\nContent here",
  "tags": ["test"]
}
```

### Get Document Details

```json
get_document { "document_id": "doc_id", "include_content": true }
```

### Update Tags

```json
update_document {
  "document_id": "doc_id",
  "tags": ["new", "tags"]
}
```

### Generate Embeddings

```json
generate_embeddings { "document_id": "doc_id" }
```

### AI Tag Generation

```json
generate_tags { "document_id": "doc_id", "max_tags": 5 }
```

---

## Troubleshooting Common Issues

### Issue: "Connection refused"

- **Cause**: Server not running or wrong port
- **Fix**: Ensure server started via inspector.sh

### Issue: "Document not found"

- **Cause**: Invalid document ID
- **Fix**: Use list_documents or search_documents to find valid IDs

### Issue: "Embedding generation failed"

- **Cause**: Ollama not running
- **Fix**: Start Ollama Docker container

### Issue: "Slow search responses"

- **Cause**: Large collection or complex query
- **Fix**: Reduce max_results, increase similarity_threshold

---

## Tips for Effective Testing

1. **Start Simple**: Begin with search and list operations
2. **Save Document IDs**: Keep track of created document IDs for testing updates
3. **Test Edge Cases**: Try empty strings, invalid IDs, extreme values
4. **Monitor Performance**: Note response times for different operations
5. **Use Browser DevTools**: Check network tab for detailed request/response data
6. **Test Error Paths**: Verify proper error handling and messages
7. **Clean Up**: Remove test documents after experimentation

---

## Next Steps

After testing with the inspector:

1. ✓ Verify all tools work as expected
2. ✓ Document any issues or unexpected behavior
3. ✓ Test integration with VS Code MCP client
4. ✓ Run automated test suite to validate changes
5. ✓ Update documentation based on findings

**Happy Testing! 🧪**
