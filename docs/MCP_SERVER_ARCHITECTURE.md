# PrismWeave MCP Server - Architecture Design

**Date**: November 11, 2025  
**Status**: Design Phase  
**Language**: Python  
**Transport**: Stdio

---

## Executive Summary

A Model Context Protocol (MCP) server that provides LLM agents with access to the PrismWeaveDocs repository through semantic search, document retrieval, and AI-powered document generation capabilities.

### Core Principles

- **Thin Wrapper**: Delegates to existing `ai-processing` module
- **Atomic Tools**: LLM orchestrates workflows with granular control
- **Read-Write Separation**: Captured documents (read-only) vs Generated documents (read-write)
- **Automatic Processing**: New documents auto-tagged and embedded

---

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    VS Code / LLM Client                  │
└───────────────────────┬─────────────────────────────────┘
                        │ stdio (JSON-RPC)
                        │
┌───────────────────────▼─────────────────────────────────┐
│              PrismWeave MCP Server (Python)              │
│  ┌─────────────────────────────────────────────────┐   │
│  │  MCP Tools Layer (mcp Python SDK)               │   │
│  │  - search_documents                             │   │
│  │  - get_document                                 │   │
│  │  - list_documents                               │   │
│  │  - create_document                              │   │
│  │  - update_document (generated only)             │   │
│  │  - generate_embeddings                          │   │
│  │  - generate_tags                                │   │
│  │  - commit_to_git                                │   │
│  └─────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Business Logic Layer                           │   │
│  │  - Document Manager (CRUD operations)           │   │
│  │  - Search Manager (semantic search)             │   │
│  │  - Processing Manager (AI pipeline)             │   │
│  │  - Git Manager (version control)                │   │
│  └─────────────────────────────────────────────────┘   │
└───────────────────────┬─────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
┌───────▼──────┐ ┌─────▼─────┐ ┌──────▼────────┐
│  Existing    │ │  ChromaDB  │ │ PrismWeaveDocs│
│ai-processing │ │  (Vectors) │ │  Repository   │
│   Module     │ │            │ │               │
│ - Ollama     │ │            │ │ /documents/   │
│ - Processors │ │            │ │ /generated/   │
│ - Config     │ │            │ │ /images/      │
└──────────────┘ └────────────┘ └───────────────┘
```

---

## MCP Tools Specification

### 1. Search & Retrieval Tools

#### `search_documents`

**Purpose**: Semantic search using vector embeddings

**Input Schema**:

```json
{
  "query": "string (required) - Natural language search query",
  "max_results": "integer (optional, default: 10) - Maximum results",
  "similarity_threshold": "float (optional, default: 0.6) - Minimum similarity",
  "filter_generated": "boolean (optional, default: false) - Include generated docs",
  "filter_tags": "array[string] (optional) - Filter by tags",
  "date_range": {
    "start": "string (optional) - ISO date",
    "end": "string (optional) - ISO date"
  }
}
```

**Output Schema**:

```json
{
  "results": [
    {
      "document_id": "string - Document identifier",
      "path": "string - Relative path in PrismWeaveDocs",
      "title": "string - Document title",
      "snippet": "string - Relevant excerpt",
      "similarity_score": "float - Cosine similarity (0-1)",
      "metadata": {
        "url": "string - Source URL (if captured)",
        "tags": "array[string]",
        "category": "string",
        "created_at": "string - ISO timestamp"
      }
    }
  ],
  "total_found": "integer",
  "query_embedding_time_ms": "integer"
}
```

---

#### `get_document`

**Purpose**: Retrieve full document content by ID or path

**Input Schema**:

```json
{
  "document_id": "string (optional) - Document ID",
  "path": "string (optional) - Relative path from PrismWeaveDocs",
  "include_metadata": "boolean (optional, default: true)"
}
```

_Note: Exactly one of `document_id` or `path` must be provided_

**Output Schema**:

```json
{
  "document_id": "string",
  "path": "string",
  "content": "string - Full markdown content",
  "metadata": {
    "title": "string",
    "url": "string (optional)",
    "tags": "array[string]",
    "category": "string",
    "created_at": "string",
    "modified_at": "string",
    "is_generated": "boolean",
    "word_count": "integer"
  },
  "frontmatter": "string - YAML frontmatter"
}
```

---

#### `list_documents`

**Purpose**: Browse documents with filtering

**Input Schema**:

```json
{
  "filter": {
    "tags": "array[string] (optional)",
    "category": "string (optional)",
    "is_generated": "boolean (optional)",
    "date_range": {
      "start": "string (optional)",
      "end": "string (optional)"
    },
    "search_title": "string (optional) - Text search in titles"
  },
  "sort_by": "string (optional) - created_at|modified_at|title (default: created_at)",
  "sort_order": "string (optional) - asc|desc (default: desc)",
  "limit": "integer (optional, default: 50)",
  "offset": "integer (optional, default: 0)"
}
```

**Output Schema**:

```json
{
  "documents": [
    {
      "document_id": "string",
      "path": "string",
      "title": "string",
      "summary": "string (optional) - First 200 chars",
      "tags": "array[string]",
      "category": "string",
      "created_at": "string",
      "modified_at": "string",
      "is_generated": "boolean",
      "word_count": "integer"
    }
  ],
  "total": "integer - Total matching documents",
  "limit": "integer",
  "offset": "integer"
}
```

---

#### `get_document_metadata`

**Purpose**: Retrieve only metadata/frontmatter without full content

**Input Schema**: Same as `get_document`

**Output Schema**:

```json
{
  "document_id": "string",
  "path": "string",
  "metadata": {
    /* same as get_document */
  },
  "frontmatter": "string - YAML frontmatter"
}
```

---

### 2. Document Creation & Modification Tools

#### `create_document`

**Purpose**: Create new AI-generated document in `generated/` folder

**Input Schema**:

```json
{
  "title": "string (required) - Document title",
  "content": "string (required) - Markdown content",
  "tags": "array[string] (optional) - Initial tags",
  "category": "string (optional) - Document category",
  "metadata": {
    "description": "string (optional)",
    "sources": "array[string] (optional) - Source document IDs/URLs",
    "custom": "object (optional) - Additional metadata"
  },
  "auto_process": "boolean (optional, default: true) - Auto-generate tags/embeddings"
}
```

**Output Schema**:

```json
{
  "document_id": "string - Generated document ID",
  "path": "string - Saved to PrismWeaveDocs/generated/...",
  "created_at": "string",
  "auto_processed": "boolean",
  "processing_results": {
    "tags_generated": "array[string] (if auto_process=true)",
    "embeddings_created": "boolean",
    "git_committed": "boolean"
  }
}
```

---

#### `update_document`

**Purpose**: Update existing document (ONLY generated documents)

**Input Schema**:

```json
{
  "document_id": "string (required)",
  "updates": {
    "title": "string (optional)",
    "content": "string (optional)",
    "tags": "array[string] (optional)",
    "category": "string (optional)",
    "metadata": "object (optional) - Merged with existing"
  },
  "regenerate_embeddings": "boolean (optional, default: true)"
}
```

**Output Schema**:

```json
{
  "document_id": "string",
  "path": "string",
  "modified_at": "string",
  "changes_applied": "array[string] - Fields that were updated",
  "embeddings_regenerated": "boolean"
}
```

**Error**: Returns error if document is not in `generated/` folder

---

### 3. AI Processing Tools

#### `generate_embeddings`

**Purpose**: Create vector embeddings for a document

**Input Schema**:

```json
{
  "document_id": "string (required)",
  "force_regenerate": "boolean (optional, default: false) - Regenerate if exists"
}
```

**Output Schema**:

```json
{
  "document_id": "string",
  "embeddings_created": "boolean",
  "chunks_processed": "integer",
  "model_used": "string - Embedding model name",
  "processing_time_ms": "integer"
}
```

---

#### `generate_tags`

**Purpose**: AI-generated tags and categorization

**Input Schema**:

```json
{
  "document_id": "string (required)",
  "merge_with_existing": "boolean (optional, default: true)",
  "model": "string (optional) - Override default model"
}
```

**Output Schema**:

```json
{
  "document_id": "string",
  "generated_tags": "array[string]",
  "category": "string",
  "confidence": "float (0-1)",
  "existing_tags": "array[string] (if merge_with_existing)",
  "final_tags": "array[string]"
}
```

---

### 4. Version Control Tools

#### `commit_to_git`

**Purpose**: Commit changes to PrismWeaveDocs repository

**Input Schema**:

```json
{
  "paths": "array[string] (optional) - Specific paths to commit (default: all changes)",
  "message": "string (required) - Commit message",
  "auto_push": "boolean (optional, default: false)"
}
```

**Output Schema**:

```json
{
  "commit_hash": "string",
  "files_committed": "array[string]",
  "timestamp": "string",
  "pushed": "boolean"
}
```

---

## File Structure

```
PrismWeave/
├── ai-processing/
│   ├── mcp/                          # NEW: MCP Server implementation
│   │   ├── __init__.py
│   │   ├── server.py                 # Main MCP server entry point
│   │   ├── tools/                    # MCP tool implementations
│   │   │   ├── __init__.py
│   │   │   ├── search.py             # Search & retrieval tools
│   │   │   ├── documents.py          # Document CRUD tools
│   │   │   ├── processing.py         # AI processing tools
│   │   │   └── git.py                # Version control tools
│   │   ├── managers/                 # Business logic layer
│   │   │   ├── __init__.py
│   │   │   ├── document_manager.py   # Document operations
│   │   │   ├── search_manager.py     # Search operations
│   │   │   ├── processing_manager.py # AI processing
│   │   │   └── git_manager.py        # Git operations
│   │   ├── schemas/                  # Pydantic schemas
│   │   │   ├── __init__.py
│   │   │   ├── requests.py           # Tool input schemas
│   │   │   └── responses.py          # Tool output schemas
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── document_utils.py     # Document parsing helpers
│   │       └── path_utils.py         # Path resolution
│   ├── src/                          # Existing AI processing
│   ├── tests/
│   │   └── mcp/                      # NEW: MCP server tests
│   │       ├── test_server.py
│   │       ├── test_tools.py
│   │       └── test_managers.py
│   ├── config.yaml                   # Shared config
│   └── pyproject.toml                # Add mcp dependencies
│
└── PrismWeaveDocs/
    ├── documents/                    # Captured documents (READ-ONLY via MCP)
    ├── generated/                    # AI-generated documents (READ-WRITE via MCP)
    │   ├── .gitkeep
    │   └── README.md                 # Explain purpose of this folder
    ├── images/
    └── .prismweave/
        └── chroma_db/                # Vector database
```

---

## Configuration

### Extend `config.yaml`

```yaml
# Existing ollama, vector, processing sections...

# NEW: MCP Server configuration
mcp:
  server_name: 'prismweave-docs'
  version: '1.0.0'

  # Document paths (relative to PrismWeaveDocs)
  paths:
    documents_dir: 'documents' # Captured (read-only)
    generated_dir: 'generated' # Generated (read-write)
    images_dir: 'images'

  # Search defaults
  search:
    default_max_results: 10
    default_similarity_threshold: 0.6
    max_query_length: 1000

  # Document creation
  creation:
    auto_process: true # Auto-generate tags/embeddings
    auto_commit: false # Require explicit commit
    filename_template: '{date}-{slug}.md'

  # Git integration
  git:
    enabled: true
    auto_add: true # Auto-add new files
    commit_template: 'AI-generated: {title}'

  # Rate limiting
  rate_limits:
    search_per_minute: 60
    create_per_minute: 10
    embedding_per_minute: 30
```

---

## Dependencies

### Add to `pyproject.toml`

```toml
[project]
dependencies = [
    # Existing dependencies...
    "mcp>=0.9.0",              # MCP Python SDK
    "pydantic>=2.0.0",         # Schema validation
    "gitpython>=3.1.0",        # Git operations
]

[project.optional-dependencies]
mcp = [
    "pytest-asyncio>=0.21.0",  # Async testing
]
```

---

## Integration with Existing Components

### 1. Reuse Existing Modules

**Search Manager** leverages:

- `src/core/embedding_store.py` - ChromaDB operations
- `src/models/ollama_client.py` - Embedding generation

**Processing Manager** leverages:

- `src/processors/` - Document analysis
- `src/core/document_analyzer.py` - Tagging/categorization

**Document Manager** leverages:

- `src/utils/config_simplified.py` - Configuration
- Existing file I/O patterns

### 2. Shared Configuration

- Single `config.yaml` for entire PrismWeave ecosystem
- MCP server reads ollama, vector, processing sections
- New `mcp` section for server-specific config

### 3. Consistent Data Models

- Reuse existing document metadata structures
- Extend with MCP-specific fields (document_id, is_generated)

---

## Error Handling Strategy

### Standard Error Response

```json
{
  "error": {
    "code": "string - ERROR_CODE",
    "message": "string - Human-readable message",
    "details": "object (optional) - Additional context"
  }
}
```

### Error Codes

- `DOCUMENT_NOT_FOUND` - Document ID/path doesn't exist
- `INVALID_INPUT` - Schema validation failed
- `PERMISSION_DENIED` - Attempted to modify captured document
- `EMBEDDING_FAILED` - Vector generation error
- `GIT_ERROR` - Repository operation failed
- `PROCESSING_ERROR` - AI processing failed
- `RATE_LIMIT_EXCEEDED` - Too many requests
- `INTERNAL_ERROR` - Unexpected server error

---

## Security Considerations

### Path Traversal Prevention

- Validate all paths are within PrismWeaveDocs
- Reject paths containing `..` or absolute paths
- Normalize paths before filesystem operations

### Document Protection

- **Captured documents**: Read-only enforcement in `update_document`
- **Generated documents**: Full CRUD access
- Check `is_generated` flag before modifications

### Resource Limits

- Rate limiting on expensive operations (search, embeddings)
- Maximum document size limits
- Query length restrictions

### Git Safety

- Validate commit messages
- Prevent force pushes
- Require explicit confirmation for destructive operations

---

## Testing Strategy

### Unit Tests

- Each MCP tool with mocked dependencies
- Schema validation tests
- Error handling tests
- Path validation tests

### Integration Tests

- Full workflow: create → embed → search → retrieve
- Git operations with test repository
- ChromaDB integration tests

### MCP Protocol Tests

- Stdio transport communication
- JSON-RPC message handling
- Error response formatting

### Performance Tests

- Search latency benchmarks
- Embedding generation time
- Concurrent request handling

---

## VS Code Integration

### MCP Configuration for VS Code

**File**: `.vscode/mcp-settings.json` (or user settings)

```json
{
  "mcp.servers": {
    "prismweave-docs": {
      "command": "python",
      "args": ["/home/dhayes/Source/PrismWeave/ai-processing/mcp/server.py"],
      "env": {
        "PYTHONPATH": "/home/dhayes/Source/PrismWeave/ai-processing"
      },
      "enabled": true
    }
  }
}
```

### Usage Examples

**Search documents**:

```
User: "Find documents about MCP servers"
→ Tool: search_documents(query="MCP servers", max_results=5)
→ Response: [list of relevant documents]
```

**Create synthesized document**:

```
User: "Create a guide combining insights from docs X, Y, Z"
→ LLM:
  1. search_documents(query="topic X")
  2. get_document(document_id="X")
  3. get_document(document_id="Y")
  4. [Synthesize content using RAG]
  5. create_document(title="New Guide", content="...", auto_process=true)
→ Response: Document created with embeddings
```

---

## Monitoring & Observability

### Logging

- Structured logging with context (tool name, document_id, etc.)
- Separate log levels: DEBUG, INFO, WARNING, ERROR
- Log file: `ai-processing/logs/mcp-server.log`

### Metrics to Track

- Tool invocation counts
- Search latency percentiles
- Embedding generation time
- Git operation success/failure rates
- Document creation rate

### Health Checks

- ChromaDB connection status
- Ollama availability
- Git repository status
- Disk space in PrismWeaveDocs

---

## Future Enhancements

### Phase 2 Features

- [ ] Document similarity recommendations
- [ ] Automatic document clustering
- [ ] Multi-modal search (text + images)
- [ ] Document versioning history
- [ ] Batch operations (bulk tagging, etc.)
- [ ] Export tools (PDF, HTML)

### Phase 3 Features

- [ ] HTTP/SSE transport option
- [ ] Multi-user support
- [ ] Webhook notifications
- [ ] Advanced analytics dashboard
- [ ] Custom embedding models

---

## Success Criteria

### Functional Requirements

- ✅ Search documents with semantic similarity
- ✅ Retrieve full document content
- ✅ Create new generated documents
- ✅ Auto-generate tags and embeddings
- ✅ Git integration for version control
- ✅ Read-only protection for captured docs

### Non-Functional Requirements

- Search latency < 500ms for typical queries
- Support 10,000+ documents in vector DB
- 99% uptime for stdio server
- Clear error messages for all failure modes

### Developer Experience

- Simple VS Code integration
- Comprehensive documentation
- Easy local testing
- Minimal configuration required

---

## Next Steps

See [MCP_SERVER_IMPLEMENTATION_PLAN.md](./MCP_SERVER_IMPLEMENTATION_PLAN.md) for detailed implementation roadmap.
