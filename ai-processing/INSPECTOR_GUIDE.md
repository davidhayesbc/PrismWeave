# MCP Inspector - Manual Testing Guide

The MCP Inspector is a web-based tool for manually testing and debugging your MCP server tools.

## Quick Start

### 1. Launch the Inspector

**Recommended (launches both server and inspector)**:

```bash
cd ai-processing
./run mcp
# Or: uv run prismweave-mcp-inspector
# Or: Press F5 in VS Code
```

**Alternative methods**:

```bash
# Run server only with different transports
./run mcp-server  # SSE transport (production)
./run mcp-stdio   # stdio transport (for inspector)
./run mcp-debug   # With debug logging

# Manual launch
source .venv/bin/activate
npx @modelcontextprotocol/inspector python -m prismweave_mcp.server --transport stdio
```

### 2. Open in Browser

The inspector will automatically open at: **http://localhost:6274**

If it doesn't open automatically, manually navigate to that URL.

## Using the Inspector

### Interface Overview

The MCP Inspector provides a web UI with three main sections:

1. **Tools Panel** (left) - Lists all available MCP tools
2. **Request Panel** (center) - Configure and send tool requests
3. **Response Panel** (right) - View tool responses

### Testing Tools

#### 1. Search Documents

**Tool**: `search_documents`

**Parameters**:

```json
{
  "query": "machine learning",
  "max_results": 5,
  "similarity_threshold": 0.6
}
```

**Expected Response**:

```json
{
  "query": "machine learning",
  "results": [
    {
      "document_id": "chunk_...",
      "score": 0.85,
      "excerpt": "..."
    }
  ],
  "total_results": 10
}
```

#### 2. List Documents

**Tool**: `list_documents`

**Parameters**:

```json
{
  "limit": 10,
  "offset": 0
}
```

#### 3. Get Document

**Tool**: `get_document`

**Parameters**:

```json
{
  "document_id": "doc_abc123",
  "include_content": true
}
```

#### 4. Create Document

**Tool**: `create_document`

**Parameters**:

```json
{
  "title": "Test Document from Inspector",
  "content": "# Test\n\nThis is a test document.",
  "category": "testing",
  "tags": ["test", "inspector"]
}
```

#### 5. Update Document

**Tool**: `update_document`

**Parameters**:

```json
{
  "document_id": "doc_abc123",
  "title": "Updated Title",
  "tags": ["updated", "test"]
}
```

#### 6. Generate Embeddings

**Tool**: `generate_embeddings`

**Parameters**:

```json
{
  "document_id": "doc_abc123",
  "model": "nomic-embed-text",
  "force_regenerate": false
}
```

#### 7. Generate Tags

**Tool**: `generate_tags`

**Parameters**:

```json
{
  "document_id": "doc_abc123",
  "max_tags": 5,
  "force_regenerate": false
}
```

#### 8. Get Document Metadata

**Tool**: `get_document_metadata`

**Parameters**:

```json
{
  "document_id": "doc_abc123"
}
```

#### 9. Commit to Git

**Tool**: `commit_to_git`

**Parameters**:

```json
{
  "commit_message": "Add new document",
  "file_paths": ["generated/testing/test.md"],
  "push": false
}
```

⚠️ **Warning**: This actually commits to git. Use with caution!

## Testing Workflow

### Basic Workflow

1. **Search** for existing documents
2. **Get** a document to see its structure
3. **Create** a new test document
4. **Generate** embeddings for the document
5. **Generate** tags for the document
6. **Update** the document with new information
7. **Search** again to verify the document is searchable

### Example Session

```bash
# 1. Start inspector
./inspector.sh

# 2. In browser (http://localhost:6274):

# Test 1: Search for documents
Tool: search_documents
{
  "query": "programming python",
  "max_results": 3
}

# Test 2: Create a test document
Tool: create_document
{
  "title": "Inspector Test Document",
  "content": "# Testing\n\nThis document was created via MCP Inspector.\n\n## Features\n\n- Manual testing\n- Interactive debugging",
  "category": "testing",
  "tags": ["inspector", "test", "manual"]
}

# Response will include document_id, use it for next steps

# Test 3: Generate embeddings
Tool: generate_embeddings
{
  "document_id": "<from previous response>",
  "model": "nomic-embed-text"
}

# Test 4: Search for the new document
Tool: search_documents
{
  "query": "inspector testing",
  "max_results": 5
}
```

## Troubleshooting

### Inspector Won't Start

**Error**: `npx: command not found`

**Solution**: Install Node.js:

```bash
# Ubuntu/Debian
sudo apt install nodejs npm

# Or use nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install node
```

### Server Errors

**Error**: Module not found

**Solution**: Ensure virtual environment is activated:

```bash
source .venv/bin/activate
uv sync
```

### Ollama Connection Failed

**Error**: Connection refused to localhost:11434

**Solution**: Start Ollama:

```bash
# Check if Ollama container is running
docker ps | grep ollama

# Start it if needed
docker start ollama-official
```

### ChromaDB Errors

**Error**: Collection not found

**Solution**: Check ChromaDB path in `config.yaml`:

```yaml
vector:
  persist_directory: '../../PrismWeaveDocs/.prismweave/chroma_db'
```

## Tips & Best Practices

### 1. Use the Console

Open browser DevTools (F12) to see detailed logs and network requests.

### 2. Save Test Cases

Copy successful requests to save as test cases for future reference.

### 3. Check Responses

Always verify the response structure matches the expected schema.

### 4. Test Error Cases

Try invalid inputs to ensure proper error handling:

- Non-existent document IDs
- Invalid query parameters
- Missing required fields

### 5. Monitor Performance

Use the browser's Network tab to check response times for different operations.

## Advanced Usage

### Custom Transport

To test with SSE transport instead of stdio:

```bash
# Terminal 1: Start server with SSE
python -m prismweave_mcp.server --transport sse --port 3000

# Terminal 2: Use inspector with SSE endpoint
npx @modelcontextprotocol/inspector http://localhost:3000/sse
```

### Debug Logging

Enable debug logging for detailed output:

```bash
npx @modelcontextprotocol/inspector python -m prismweave_mcp.server --debug --transport stdio
```

### Inspect Tool Schemas

The inspector automatically shows the JSON schema for each tool, including:

- Required parameters
- Optional parameters
- Parameter types
- Default values
- Descriptions

## Integration with VS Code

While the inspector runs, you can also:

1. Keep VS Code open with the MCP server configured
2. Compare results between VS Code and Inspector
3. Debug issues by checking both interfaces

## Resources

- [MCP Inspector Documentation](https://github.com/modelcontextprotocol/inspector)
- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [PrismWeave MCP Server README](./README.md)
- [Troubleshooting Guide](./prismweave_mcp/TROUBLESHOOTING.md)
