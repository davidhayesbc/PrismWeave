#!/bin/bash
# Development script for PrismWeave MCP Server with hot reload
# Watches for Python file changes and automatically restarts the server

echo "🚀 Starting PrismWeave MCP Server in development mode with hot reload..."
echo "📝 Watching directories: prismweave_mcp/, src/"
echo "🔄 Server will auto-restart when Python files change"
echo ""

uv run watchmedo auto-restart \
  --directory=./prismweave_mcp \
  --directory=./src \
  --pattern="*.py" \
  --recursive \
  --ignore-patterns="*/__pycache__/*;*.pyc;*/.pytest_cache/*" \
  -- python -m prismweave_mcp.server --debug --transport sse
