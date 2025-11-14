# PrismWeave MCP Server

MCP (Model Context Protocol) server for PrismWeave document management and AI processing.

## Transport Options

The server now supports HTTP/SSE transport using FastMCP, which is more suitable for web-based clients and provides better scalability than stdio.

### HTTP/SSE Mode (Default)

The server runs as an HTTP server with Server-Sent Events (SSE) for streaming responses.

**Start the server:**

```bash
cd ai-processing
python -m mcp.prismweave_server
```

**With custom configuration:**

```bash
python -m mcp.prismweave_server --host 0.0.0.0 --port 8000 --debug
```

**Command-line options:**

- `--host`: Host to bind to (default: 127.0.0.1)
- `--port`: Port to bind to (default: 8000)
- `--debug`: Enable debug logging

**Endpoints:**

- SSE endpoint: `http://127.0.0.1:8000/sse`
- Messages endpoint: `http://127.0.0.1:8000/messages`

### VS Code Configuration

Update your VS Code MCP settings (`~/.config/Code - Insiders/User/mcp.json` or similar):

```json
{
  "mcpServers": {
    "prismweave": {
      "transport": {
        "type": "sse",
        "url": "http://127.0.0.1:8000/sse"
      }
    }
  }
}
```

## Available Tools

### Search & Retrieval

1. **search_documents** - Semantic search across documents
   - Parameters: query, max_results, similarity_threshold, filters
2. **get_document** - Get document by ID or path
   - Parameters: document_id, path, include_content

3. **list_documents** - List documents with filters
   - Parameters: category, tags, date range, limit, offset

4. **get_document_metadata** - Get metadata without content
   - Parameters: document_id, path

### Document Management

5. **create_document** - Create new generated document
   - Parameters: title, content, category, tags, metadata

6. **update_document** - Update existing document
   - Parameters: document_id, path, title, content, tags

### AI Processing

7. **generate_embeddings** - Generate vector embeddings
   - Parameters: document_id, path, force

8. **generate_tags** - AI-powered tag generation
   - Parameters: document_id, path, merge_existing, max_tags

### Version Control

9. **commit_to_git** - Commit changes to repository
   - Parameters: message, paths, push

## Architecture

The server uses FastMCP which provides:

- Built-in HTTP/SSE transport
- Automatic tool registration
- Lifecycle management
- Error handling
- Type validation

## Development

### Running in Development Mode

```bash
cd ai-processing
source .venv/bin/activate
python -m mcp.prismweave_server --debug
```

### Testing the Server

You can test the server using curl:

```bash
# Test SSE endpoint
curl -N http://127.0.0.1:8000/sse

# List available tools
curl http://127.0.0.1:8000/messages
```

## Migration from stdio

If you were previously using stdio transport, the main changes are:

1. **Server runs as HTTP service** instead of stdin/stdout pipe
2. **Configuration uses URL** instead of command
3. **Multiple clients** can connect simultaneously
4. **Better error handling** with HTTP status codes

### Old stdio configuration:

```json
{
  "prismweave": {
    "command": "python",
    "args": ["-m", "mcp.prismweave_server"]
  }
}
```

### New HTTP/SSE configuration:

```json
{
  "prismweave": {
    "transport": {
      "type": "sse",
      "url": "http://127.0.0.1:8000/sse"
    }
  }
}
```

## Troubleshooting

### Server won't start

Check if port is already in use:

```bash
lsof -i :8000
```

Use a different port:

```bash
python -m mcp.prismweave_server --port 8001
```

### Connection refused

Make sure the server is running:

```bash
ps aux | grep prismweave_server
```

Check server logs for errors.

### ChromaDB initialization fails

The server will start but search functionality may be limited. Check:

- ChromaDB database path in config.yaml
- Write permissions on the database directory
- Available disk space

## Performance

HTTP/SSE transport provides:

- **Better scalability** - Multiple clients can connect
- **Connection pooling** - Reduced overhead for repeated requests
- **Streaming responses** - Real-time updates for long operations
- **Standard protocols** - Works with any HTTP client

## Security

By default, the server binds to `127.0.0.1` (localhost only). To allow remote connections:

```bash
python -m mcp.prismweave_server --host 0.0.0.0 --port 8000
```

⚠️ **Warning**: Only expose to trusted networks. The server does not include authentication by default.
