# PrismWeave MCP Server - Development Guide

## Quick Start

### 1. Install Dependencies

```bash
cd ai-processing
uv sync
```

### 2. Run the Server

#### Option A: Hot Reload Development (Recommended)

```bash
./dev.sh
```

Changes to Python files will automatically restart the server.

#### Option B: Standard Run

```bash
uv run python -m prismweave_mcp.server
```

#### Option C: With Debug Logging

```bash
uv run python -m prismweave_mcp.server --debug
```

### 3. VS Code Integration

The server is configured in VS Code at:

```
~/.config/Code - Insiders/User/mcp.json
```

Example configuration:

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

## Development Workflow

### Hot Reload Mode

The `dev.sh` script uses `watchdog` to monitor file changes and automatically restart the server:

- Watches: `prismweave_mcp/` and `src/` directories
- Auto-restarts on `.py` file changes
- Ignores: `__pycache__`, `.pyc`, `.pytest_cache`

### VS Code Tasks

Available tasks (Ctrl+Shift+P → "Tasks: Run Task"):

1. **MCP Server: Run with Hot Reload** - Development mode with auto-restart
2. **MCP Server: Run** - Standard mode
3. **MCP Server: Run with Debug Logging** - Extra logging output

### Debugging

#### Using VS Code Debugger

1. Set breakpoints in your Python files
2. Press F5 or Run → "Debug MCP Server"
3. The server will start with debugger attached
4. Code execution will pause at breakpoints

Available debug configurations:

- **Debug MCP Server** - Full debugging with external libraries
- **Debug MCP Server with Breakpoints** - Stop on entry, your code only
- **Debug Current Python File** - Debug the currently open file

#### Using Print/Logging

```python
import logging
logger = logging.getLogger(__name__)

# In your code
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
```

Run with debug logging:

```bash
./dev.sh  # Already has debug mode enabled
```

## Testing

### Run Tests

```bash
# All tests
uv run pytest tests/

# With coverage
uv run pytest tests/ --cov=src --cov-report=html

# Specific test file
uv run pytest tests/prismweave_mcp/test_tools.py -v

# Watch mode (auto-run on changes)
uv run pytest-watch tests/
```

### VS Code Test Tasks

Use "Tasks: Run Task":

- **AI Processing: Run Tests**
- **AI Processing: Run Tests with Coverage**

## Architecture

```
ai-processing/
├── prismweave_mcp/          # MCP Server implementation
│   ├── server.py            # Main server entry point
│   ├── tools/               # MCP tool implementations
│   │   ├── search.py        # Search & retrieval
│   │   ├── documents.py     # Document CRUD
│   │   ├── processing.py    # AI processing
│   │   └── git.py           # Version control
│   ├── managers/            # Business logic
│   ├── schemas/             # Request/response schemas
│   └── utils/               # Helpers
├── src/                     # Core AI processing
├── tests/                   # Test suite
├── config.yaml              # Configuration
└── dev.sh                   # Hot reload script
```

## Configuration

Edit `config.yaml` to change:

- Ollama host and models
- Vector database settings
- Processing parameters
- MCP server options

## Common Issues

### Server won't start

```bash
# Check if port is in use
lsof -i :8000

# Use different port
python -m prismweave_mcp.server --port 8001
```

### Hot reload not working

```bash
# Ensure watchdog is installed
uv sync

# Check dev.sh is executable
chmod +x dev.sh

# Run manually to see errors
uv run watchmedo auto-restart --directory=./prismweave_mcp --pattern="*.py" --recursive -- python -m prismweave_mcp.server
```

### VS Code can't connect

1. Ensure server is running: `ps aux | grep prismweave`
2. Check server logs for errors
3. Verify URL in `mcp.json` matches server port
4. Try restarting VS Code

### ChromaDB errors

```bash
# Check database path
cat config.yaml | grep persist_directory

# Verify permissions
ls -la ../../PrismWeaveDocs/.prismweave/

# Clean and reinitialize (WARNING: deletes embeddings)
rm -rf ../../PrismWeaveDocs/.prismweave/chroma_db
```

## Performance Tips

### Use Smaller Models for Development

In `config.yaml`:

```yaml
ollama:
  models:
    small: 'phi3:mini' # Fast, good for testing
    embedding: 'nomic-embed-text' # Required for search
```

### Disable Auto-processing

When creating many test documents:

```python
create_document(..., auto_process=False)
```

### Use Test Database

Create separate config for testing to avoid polluting production data.

## Next Steps

1. Read [ARCHITECTURE.md](../docs/MCP_SERVER_ARCHITECTURE.md) for design details
2. Check [IMPLEMENTATION_STATUS.md](prismweave_mcp/IMPLEMENTATION_STATUS.md) for progress
3. Review [VS_CODE_INTEGRATION.md](prismweave_mcp/VS_CODE_INTEGRATION.md) for client setup

## Contributing

1. Create feature branch
2. Make changes with hot reload running
3. Add tests for new features
4. Run test suite
5. Update documentation
6. Submit PR

---

**Happy coding! 🚀**
