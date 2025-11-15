#!/bin/bash
# Test script to verify MCP server development setup

set -e

echo "🧪 PrismWeave MCP Server Setup Verification"
echo "==========================================="
echo ""

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: Run this from the ai-processing directory"
    exit 1
fi

echo "✅ Directory check passed"

# Check virtual environment
if [ ! -d ".venv" ]; then
    echo "❌ Error: Virtual environment not found. Run: uv sync"
    exit 1
fi

echo "✅ Virtual environment exists"

# Check key dependencies
echo ""
echo "📦 Checking dependencies..."

if ! .venv/bin/python -c "import fastmcp" 2>/dev/null; then
    echo "❌ fastmcp not installed. Run: uv sync"
    exit 1
fi
echo "  ✅ fastmcp"

if ! .venv/bin/python -c "import watchdog" 2>/dev/null; then
    echo "❌ watchdog not installed. Run: uv sync"
    exit 1
fi
echo "  ✅ watchdog"

if ! .venv/bin/python -c "import prismweave_mcp" 2>/dev/null; then
    echo "❌ prismweave_mcp module not found"
    exit 1
fi
echo "  ✅ prismweave_mcp module"

# Check config file
if [ ! -f "config.yaml" ]; then
    echo "❌ config.yaml not found"
    exit 1
fi
echo "✅ config.yaml exists"

# Check dev.sh script
if [ ! -x "dev.sh" ]; then
    echo "❌ dev.sh not executable. Run: chmod +x dev.sh"
    exit 1
fi
echo "✅ dev.sh is executable"

# Test server help
echo ""
echo "🔧 Testing server module..."
if uv run python -m prismweave_mcp.server --help > /dev/null 2>&1; then
    echo "✅ Server module loads successfully"
else
    echo "❌ Server module failed to load"
    exit 1
fi

# Check VS Code config
VSCODE_CONFIG="$HOME/.config/Code - Insiders/User/mcp.json"
if [ -f "$VSCODE_CONFIG" ]; then
    echo "✅ VS Code MCP config exists"
else
    echo "⚠️  VS Code MCP config not found at: $VSCODE_CONFIG"
    echo "   You'll need to configure this for VS Code integration"
fi

echo ""
echo "✅ All checks passed!"
echo ""
echo "🚀 You're ready to start developing!"
echo ""
echo "Quick commands:"
echo "  ./dev.sh                          - Start with hot reload"
echo "  uv run python -m prismweave_mcp.server --debug  - Start with debug logging"
echo "  uv run pytest tests/              - Run tests"
echo ""
echo "VS Code:"
echo "  F5                                - Debug server"
echo "  Ctrl+Shift+P → Tasks: Run Task    - Run tasks"
echo ""
