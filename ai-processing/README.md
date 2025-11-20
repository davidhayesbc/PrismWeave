# PrismWeave AI Processing Module

AI processing and backend services for PrismWeave document management system.

## Features

- Document embedding generation using Ollama
- Vector similarity search with ChromaDB
- FastAPI HTTP server for visualization layer
- MCP (Model Context Protocol) server for AI agent integration
- Git-based document tracking and synchronization

## Installation

```bash
uv sync
```

## Usage

### CLI Commands

```bash
# Process documents and generate embeddings
prismweave-cli process

# Build visualization index
prismweave-cli visualize build-index

# Run API server
prismweave-api
```

### API Server

```bash
# Development mode with hot reload
.venv/bin/python -m uvicorn src.api.app:app --reload --port 8000

# Production mode
prismweave-api
```

API documentation available at http://localhost:8000/docs

### MCP Server

```bash
# Run MCP server
prismweave-mcp

# Run with inspector for debugging
prismweave-mcp-inspector
```

## Configuration

Edit `config.yaml` to configure:
- Document paths
- Ollama model settings
- ChromaDB location
- Git repository settings

## Development

```bash
# Run tests
.venv/bin/python -m pytest tests/ -v

# Run with coverage
.venv/bin/python -m pytest tests/ --cov=src --cov-report=html
```

## License

MIT
