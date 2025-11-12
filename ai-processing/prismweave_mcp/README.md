# PrismWeave MCP Server

**Model Context Protocol server for PrismWeave document management and AI processing**

The PrismWeave MCP server exposes document management, semantic search, and AI processing capabilities through the Model Context Protocol, enabling seamless integration with AI assistants and development tools like VS Code.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Tool Reference](#tool-reference)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)

---

## Features

### Document Management

- **Search**: Semantic search across all documents with filtering
- **Retrieve**: Get full document content and metadata
- **List**: Browse documents with pagination
- **Create**: Generate new synthesized documents
- **Update**: Modify existing generated documents

### AI Processing

- **Embeddings**: Generate vector embeddings for semantic search
- **Tag Generation**: Automatically extract relevant tags using AI
- **Auto-Processing**: Combined workflow for tags + embeddings

### Version Control

- **Git Integration**: Commit changes with optional push to remote

---

## Installation

### Prerequisites

1. **Python 3.10+** with UV package manager
2. **Ollama** running locally (`http://localhost:11434`)
3. **PrismWeaveDocs** repository cloned
4. **ChromaDB** initialized with document embeddings

### Install Dependencies

```bash
# Navigate to ai-processing directory
cd /home/dhayes/Source/PrismWeave/ai-processing

# Install dependencies using UV
uv sync

# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

### Verify Installation

```bash
# Check Python environment
python --version  # Should be 3.10+

# Verify Ollama is running
curl http://localhost:11434/api/tags

# Test MCP server import
python -c "from prismweave_mcp import server; print('MCP server OK')"
```

---

## Configuration

### Configuration File

The MCP server uses `ai-processing/config.yaml` for all settings:

```yaml
# Ollama Configuration
ollama:
  host: http://localhost:11434
  timeout: 60
  models:
    large: 'llama3.1:8b' # Complex analysis
    medium: 'phi3:mini' # Standard processing
    small: 'phi3:mini' # Quick tasks
    embedding: 'nomic-embed-text' # Vector embeddings

# MCP Server Paths
mcp:
  paths:
    documents_root: '../../PrismWeaveDocs'
    generated_folder: 'generated'
    images_folder: 'images'

  # Search Defaults
  search:
    max_results: 20
    similarity_threshold: 0.6
    default_filters: {}

  # Document Creation
  creation:
    default_tags: []
    auto_process: true
    auto_commit: false

  # Git Integration
  git:
    auto_push: false
    commit_message_template: 'Add {title}'
    push_on_commit: false

  # Rate Limiting
  rate_limiting:
    enabled: false
    requests_per_minute: 60

# Vector Database
vector:
  collection_name: 'documents'
  persist_directory: '../../PrismWeaveDocs/.prismweave/chroma_db'
  max_results: 20
  similarity_threshold: 0.6
```

### Environment-Specific Configuration

For different environments, create additional config files:

```bash
# Development
config.dev.yaml

# Production
config.prod.yaml

# Testing
config.test.yaml
```

Load specific config:

```python
from prismweave_mcp.utils.config_manager import load_config

config = load_config('config.prod.yaml')
```

---

## Usage

### Starting the MCP Server

#### Option 1: Direct Python Execution

```bash
cd /home/dhayes/Source/PrismWeave/ai-processing
python -m prismweave_mcp.server
```

#### Option 2: FastMCP CLI

```bash
fastmcp run prismweave_mcp.server
```

#### Option 3: VS Code Integration

Configure in VS Code settings (see [VS Code Integration Guide](./VS_CODE_INTEGRATION.md)):

```json
{
  "mcp.servers": {
    "prismweave": {
      "command": "python",
      "args": ["-m", "prismweave_mcp.server"],
      "cwd": "/home/dhayes/Source/PrismWeave/ai-processing"
    }
  }
}
```

### Basic Workflow

1. **Search for documents**:

   ```
   Use search_documents to find relevant content
   ```

2. **Retrieve full document**:

   ```
   Use get_document to read complete document
   ```

3. **Create synthesized content**:

   ```
   Use create_document with auto_process=true
   ```

4. **Commit to Git**:
   ```
   Use commit_to_git to version control changes
   ```

---

## Tool Reference

### Search & Retrieval Tools

#### `search_documents`

Semantic search across all documents with filtering capabilities.

**Parameters**:

- `query` (string, required): Search query text
- `max_results` (integer, optional): Maximum results to return (default: 20)
- `filters` (object, optional): Filter criteria
  - `tags` (array of strings): Filter by tags
  - `date_range` (object): Filter by date
    - `start` (string): ISO 8601 start date
    - `end` (string): ISO 8601 end date
  - `is_generated` (boolean): Filter generated vs captured
  - `category` (string): Filter by category

**Returns**:

- `results` (array): Search results with snippets
- `total` (integer): Total matching documents
- `query` (string): Original query

**Example**:

```json
{
  "query": "machine learning concepts",
  "max_results": 10,
  "filters": {
    "tags": ["ai", "ml"],
    "is_generated": false
  }
}
```

---

#### `get_document`

Retrieve full document content by ID or path.

**Parameters**:

- `document_id` (string, optional): Unique document identifier
- `document_path` (string, optional): Relative path to document
- `include_metadata` (boolean, optional): Include full metadata (default: true)

**Returns**:

- `document_id` (string): Document identifier
- `title` (string): Document title
- `content` (string): Full markdown content
- `metadata` (object): Document metadata
- `path` (string): File path

**Example**:

```json
{
  "document_path": "documents/2025-01-15-example-article.md",
  "include_metadata": true
}
```

---

#### `list_documents`

List documents with optional filtering and pagination.

**Parameters**:

- `limit` (integer, optional): Maximum documents to return (default: 50)
- `offset` (integer, optional): Pagination offset (default: 0)
- `filters` (object, optional): Same as search_documents
- `sort_by` (string, optional): Sort field (default: "created_at")
- `sort_order` (string, optional): "asc" or "desc" (default: "desc")

**Returns**:

- `documents` (array): List of document summaries
- `total` (integer): Total matching documents
- `limit` (integer): Applied limit
- `offset` (integer): Applied offset

**Example**:

```json
{
  "limit": 20,
  "filters": {
    "is_generated": true
  },
  "sort_by": "created_at",
  "sort_order": "desc"
}
```

---

#### `get_document_metadata`

Retrieve only document metadata without full content.

**Parameters**:

- `document_id` (string, optional): Unique document identifier
- `document_path` (string, optional): Relative path to document

**Returns**:

- `metadata` (object): Document metadata only

**Example**:

```json
{
  "document_id": "doc_abc123"
}
```

---

### Document Creation Tools

#### `create_document`

Create a new synthesized document in the generated/ folder.

**Parameters**:

- `title` (string, required): Document title
- `content` (string, required): Markdown content
- `tags` (array of strings, optional): Document tags
- `metadata` (object, optional): Additional metadata
- `auto_process` (boolean, optional): Auto-generate tags/embeddings (default: true)
- `auto_commit` (boolean, optional): Auto-commit to git (default: false)

**Returns**:

- `document_id` (string): Created document ID
- `path` (string): File path
- `created_at` (string): Creation timestamp
- `processing_results` (object, optional): Processing results if auto_process=true

**Example**:

```json
{
  "title": "Introduction to Vector Databases",
  "content": "# Introduction to Vector Databases\n\nVector databases...",
  "tags": ["database", "vectors"],
  "auto_process": true,
  "auto_commit": false
}
```

---

#### `update_document`

Update an existing document in the generated/ folder.

**Parameters**:

- `document_id` (string, optional): Document identifier
- `document_path` (string, optional): Document path
- `title` (string, optional): New title
- `content` (string, optional): New content
- `tags` (array of strings, optional): New tags
- `metadata` (object, optional): Metadata updates
- `regenerate_embeddings` (boolean, optional): Regenerate embeddings (default: false)

**Returns**:

- `document_id` (string): Updated document ID
- `path` (string): File path
- `updated_at` (string): Update timestamp
- `changes` (array): List of changed fields

**Example**:

```json
{
  "document_path": "generated/2025-01-15-vector-databases.md",
  "content": "# Updated content...",
  "regenerate_embeddings": true
}
```

---

### AI Processing Tools

#### `generate_embeddings`

Generate vector embeddings for a document.

**Parameters**:

- `document_id` (string, optional): Document identifier
- `document_path` (string, optional): Document path
- `force_regenerate` (boolean, optional): Regenerate if exists (default: false)

**Returns**:

- `document_id` (string): Document ID
- `embeddings_count` (integer): Number of embeddings generated
- `model_used` (string): Embedding model name
- `processing_time` (float): Time in seconds

**Example**:

```json
{
  "document_path": "documents/2025-01-15-example.md",
  "force_regenerate": false
}
```

---

#### `generate_tags`

Generate AI-suggested tags for a document.

**Parameters**:

- `document_id` (string, optional): Document identifier
- `document_path` (string, optional): Document path
- `num_tags` (integer, optional): Number of tags to generate (default: 5)
- `merge_existing` (boolean, optional): Merge with existing tags (default: true)

**Returns**:

- `document_id` (string): Document ID
- `generated_tags` (array): AI-generated tags
- `merged_tags` (array): Final merged tags
- `model_used` (string): AI model name

**Example**:

```json
{
  "document_path": "generated/2025-01-15-article.md",
  "num_tags": 5,
  "merge_existing": true
}
```

---

### Version Control Tools

#### `commit_to_git`

Commit changes to the PrismWeaveDocs git repository.

**Parameters**:

- `message` (string, required): Commit message
- `paths` (array of strings, optional): Specific paths to commit
- `push` (boolean, optional): Push to remote after commit (default: false)

**Returns**:

- `commit_hash` (string): Git commit hash
- `message` (string): Commit message
- `files_changed` (integer): Number of files changed
- `pushed` (boolean): Whether pushed to remote

**Example**:

```json
{
  "message": "Add new article on vector databases",
  "paths": ["generated/2025-01-15-vector-databases.md"],
  "push": false
}
```

---

## Examples

### Example 1: Search and Synthesize

**Workflow**: Search for related documents, then create synthesized article

```python
# 1. Search for relevant documents
search_result = await search_documents(
    query="machine learning fundamentals",
    max_results=10,
    filters={"tags": ["ai", "ml"]}
)

# 2. Read top results
documents = []
for result in search_result.results[:3]:
    doc = await get_document(document_id=result.document_id)
    documents.append(doc)

# 3. Create synthesized article
new_doc = await create_document(
    title="Machine Learning Fundamentals Overview",
    content=synthesized_content,
    tags=["ai", "ml", "synthesis"],
    auto_process=True,
    auto_commit=True
)
```

---

### Example 2: Batch Processing

**Workflow**: Process multiple documents with embeddings

```python
# 1. List all documents without embeddings
docs = await list_documents(
    filters={"has_embeddings": False},
    limit=100
)

# 2. Generate embeddings for each
for doc in docs.documents:
    result = await generate_embeddings(
        document_id=doc.document_id
    )
    print(f"Generated {result.embeddings_count} embeddings for {doc.title}")

# 3. Commit all changes
await commit_to_git(
    message="Add embeddings for batch processing",
    push=True
)
```

---

### Example 3: Document Update Workflow

**Workflow**: Update document, regenerate tags and embeddings

```python
# 1. Get existing document
doc = await get_document(
    document_path="generated/2025-01-01-article.md"
)

# 2. Update content
updated = await update_document(
    document_path=doc.path,
    content=new_content,
    regenerate_embeddings=True
)

# 3. Generate fresh tags
tags_result = await generate_tags(
    document_id=updated.document_id,
    num_tags=7,
    merge_existing=False
)

# 4. Commit changes
await commit_to_git(
    message=f"Update: {doc.title}",
    paths=[updated.path]
)
```

---

## Troubleshooting

### Common Issues

#### Server Won't Start

**Problem**: `ModuleNotFoundError: No module named 'prismweave_mcp'`

**Solution**:

```bash
# Ensure you're in the ai-processing directory
cd /home/dhayes/Source/PrismWeave/ai-processing

# Activate virtual environment
source .venv/bin/activate

# Reinstall dependencies
uv sync
```

---

#### Ollama Connection Failed

**Problem**: `Cannot connect to Ollama at http://localhost:11434`

**Solution**:

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama if not running
ollama serve

# Verify models are available
ollama list
```

---

#### ChromaDB Not Found

**Problem**: `ChromaDB collection 'documents' not found`

**Solution**:

```bash
# Initialize ChromaDB with existing documents
cd /home/dhayes/Source/PrismWeave/ai-processing
python -m src.core.embedding_store --init

# Or run document processor to create embeddings
python cli/prismweave.py vector-init
```

---

#### Permission Denied (Git)

**Problem**: `Cannot commit to git: permission denied`

**Solution**:

```bash
# Check git repository permissions
cd /home/dhayes/Source/PrismWeaveDocs
git status

# Ensure you have write permissions
ls -la .git/

# Configure git if needed
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

---

For more troubleshooting help, see [TROUBLESHOOTING.md](./TROUBLESHOOTING.md).

---

## Architecture

### Component Overview

```
prismweave_mcp/
├── server.py              # FastMCP server with @mcp.tool() decorators
├── managers/              # Business logic layer
│   ├── document_manager.py   # Document CRUD operations
│   ├── search_manager.py     # Semantic search with ChromaDB
│   ├── processing_manager.py # AI processing (tags, embeddings)
│   └── git_manager.py        # Git operations
├── tools/                 # MCP tool implementations
│   ├── search.py             # Search & retrieval tools
│   ├── documents.py          # Document creation tools
│   ├── processing.py         # AI processing tools
│   └── git.py                # Git tools
├── schemas/               # Pydantic request/response schemas
│   ├── requests.py
│   └── responses.py
└── utils/                 # Utilities and helpers
    ├── config_manager.py
    ├── document_utils.py
    ├── path_utils.py
    └── error_handling.py
```

### Data Flow

```
VS Code / AI Assistant
         ↓
    MCP Protocol
         ↓
   FastMCP Server (server.py)
         ↓
    Tool Layer (tools/)
         ↓
   Manager Layer (managers/)
         ↓
External Systems (Ollama, ChromaDB, Git)
```

---

## Development

### Running Tests

```bash
# Run all tests
pytest prismweave_mcp/tests/

# Run with coverage
pytest prismweave_mcp/tests/ --cov=prismweave_mcp --cov-report=html

# Run specific test file
pytest prismweave_mcp/tests/test_server.py -v
```

### Code Quality

```bash
# Format code
black prismweave_mcp/
isort prismweave_mcp/

# Type checking
mypy prismweave_mcp/

# Linting
ruff check prismweave_mcp/
```

---

## Contributing

See main [PrismWeave Contributing Guide](../../CONTRIBUTING.md) for:

- Code style guidelines
- Testing requirements
- Pull request process
- Development workflow

---

## License

Part of the PrismWeave project. See [LICENSE](../../LICENSE) for details.

---

## Support

- **Documentation**: [VS Code Integration Guide](./VS_CODE_INTEGRATION.md)
- **Troubleshooting**: [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)
- **Issues**: [GitHub Issues](https://github.com/davidhayesbc/PrismWeave/issues)
- **Implementation Status**: [IMPLEMENTATION_STATUS.md](./IMPLEMENTATION_STATUS.md)

---

**Version**: 1.0.0  
**Last Updated**: November 11, 2025
