# PrismWeave MCP Server - Quick Reference

## Start Server

### Development (Hot Reload) - **Recommended**

```bash
cd ai-processing
./run dev
```

Auto-restarts when you save Python files. Perfect for development!

### Standard

```bash
cd ai-processing
uv run python -m prismweave_mcp.server
```

### Debug Mode

```bash
cd ai-processing
uv run python -m prismweave_mcp.server --debug
```

### Custom Port

```bash
cd ai-processing
uv run python -m prismweave_mcp.server --port 8001
```

## VS Code Integration

### Tasks (Ctrl+Shift+P → "Tasks: Run Task")

- **MCP Server: Run with Hot Reload** ⭐ Best for development
- **MCP Server: Run** - Standard mode
- **MCP Server: Run with Debug Logging** - Extra logging

### Debugging (F5 or Run → Debug)

- **Debug MCP Server** - Full debugging
- **Debug MCP Server with Breakpoints** - Stop on entry

## Testing

```bash
cd ai-processing

# Run all tests
uv run pytest tests/

# Run with coverage
uv run pytest tests/ --cov=src --cov-report=html

# Watch mode (auto-run on changes)
uv run pytest-watch tests/

# Specific test
uv run pytest tests/prismweave_mcp/test_search.py -v
```

## Configuration

Edit `config.yaml` for settings:

- Ollama models and host
- Vector database path
- Processing parameters

## Troubleshooting

### Check if server is running

```bash
ps aux | grep prismweave_mcp
lsof -i :8000
```

### View logs

Server logs to console by default. Check terminal output.

### Restart server

If using hot reload: Just save a Python file
If running manually: Ctrl+C and restart

### Clean ChromaDB

```bash
rm -rf ../../PrismWeaveDocs/.prismweave/chroma_db
```

## VS Code MCP Configuration

Location: `~/.config/Code - Insiders/User/mcp.json`

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

1. **search_documents** - Semantic search
2. **get_document** - Get by ID/path
3. **list_documents** - Browse with filters
4. **create_document** - Create new document
5. **update_document** - Update existing
6. **generate_embeddings** - Create vectors
7. **generate_tags** - AI tagging
8. **commit_to_git** - Version control

## Development Tips

✅ Use `./run dev` for instant feedback  
✅ Set breakpoints and use F5 for debugging  
✅ Check `DEV_GUIDE.md` for detailed info  
✅ Use smaller models (phi3:mini) for faster testing  
✅ Run pytest-watch for TDD workflow

## Need Help?

- Check `DEV_GUIDE.md` - Full development guide
- See `TROUBLESHOOTING.md` - Common issues
- Review `prismweave_mcp/README.md` - Architecture
