# ✅ PrismWeave MCP Server - Development Setup Complete

## What Was Done

### 1. ✅ Removed Outdated Code

- Deleted `/ai-processing/mcp/` folder (old stdio-based implementation)
- Kept `/ai-processing/prismweave_mcp/` (current FastMCP HTTP/SSE implementation)

### 2. ✅ Installed Hot Reload Dependencies

- Added `watchdog>=6.0.0` for file watching
- Added `pytest-watch>=4.2.0` for test watching
- Updated `pyproject.toml` with dev dependencies

### 3. ✅ Created Development Scripts

#### `dev.sh` - Hot Reload Development Server

- Watches `prismweave_mcp/` and `src/` directories
- Auto-restarts on `.py` file changes
- Ignores cache directories
- **Usage**: `./dev.sh`

#### `verify-setup.sh` - Setup Verification

- Checks all dependencies
- Validates configuration
- Tests server module
- **Usage**: `./verify-setup.sh`

### 4. ✅ Added VS Code Integration

#### Tasks (`.vscode/tasks.json`)

- **MCP Server: Run with Hot Reload** - Development mode ⭐
- **MCP Server: Run** - Standard mode
- **MCP Server: Run with Debug Logging** - Extra logging

#### Debug Configurations (`.vscode/launch.json`)

- **Debug MCP Server** - Full debugging with breakpoints
- **Debug MCP Server with Breakpoints** - Stop on entry
- **Debug Current Python File** - Debug any Python file

### 5. ✅ Enhanced Server Module

- Added CLI argument parsing (`--debug`, `--port`, `--host`)
- Added proper `main()` function
- Updated script entry point in `pyproject.toml`

### 6. ✅ Created Documentation

- **DEV_GUIDE.md** - Comprehensive development guide
- **QUICK_START.md** - Quick reference for common tasks
- **README_SETUP.md** - This file

## Quick Start

### Start Development Server

```bash
cd /home/dhayes/Source/PrismWeave/ai-processing
./dev.sh
```

### Verify Setup

```bash
./verify-setup.sh
```

### Debug in VS Code

Press **F5** or Run → **"Debug MCP Server"**

## Development Workflow

### 1. Start Hot Reload Server

```bash
./dev.sh
```

### 2. Make Code Changes

Edit files in `prismweave_mcp/` or `src/`

### 3. Save File

Server automatically restarts (usually < 2 seconds)

### 4. Test Changes

- Changes immediately available
- No manual restart needed
- Check terminal for any errors

## Testing Workflow

### Run Tests Once

```bash
uv run pytest tests/
```

### Watch Mode (TDD)

```bash
uv run pytest-watch tests/
```

Changes to test files or source code automatically trigger test runs.

## VS Code Integration

### Run Server as Task

1. **Ctrl+Shift+P**
2. **"Tasks: Run Task"**
3. Select **"MCP Server: Run with Hot Reload"**

### Debug with Breakpoints

1. Set breakpoints in your Python code
2. Press **F5**
3. Server starts with debugger attached
4. Execution pauses at breakpoints

### MCP Client Configuration

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

## Why NOT Docker?

Docker was **intentionally NOT used** because:

1. ❌ **stdio transport incompatibility** - MCP uses direct process communication
2. ❌ **Debugging complexity** - Extra layers make breakpoints harder
3. ❌ **Slower file watching** - Volume sync adds latency
4. ❌ **Unnecessary overhead** - Local Python is faster and simpler
5. ✅ **Hot reload works perfectly** - Direct file system access

Docker is better for:

- Production deployment
- Multi-service applications
- Cross-platform testing

For **local development**, native Python + UV + watchdog is superior.

## File Structure

```
ai-processing/
├── dev.sh                    # ⭐ Hot reload dev server
├── verify-setup.sh           # Setup verification
├── DEV_GUIDE.md             # Detailed dev guide
├── QUICK_START.md           # Quick reference
├── README_SETUP.md          # This file
├── prismweave_mcp/          # MCP server implementation
│   ├── server.py            # Main entry point
│   ├── tools/               # MCP tools
│   ├── managers/            # Business logic
│   ├── schemas/             # Request/response types
│   └── utils/               # Helpers
├── src/                     # Core AI processing
├── tests/                   # Test suite
├── config.yaml              # Configuration
└── pyproject.toml           # Dependencies & config
```

## Common Commands

```bash
# Development
./dev.sh                                    # Start with hot reload ⭐
uv run python -m prismweave_mcp.server      # Start normally
uv run python -m prismweave_mcp.server --debug  # Debug mode

# Testing
uv run pytest tests/                        # Run all tests
uv run pytest tests/ --cov=src             # With coverage
uv run pytest-watch tests/                  # Watch mode

# Utilities
./verify-setup.sh                           # Verify setup
uv sync                                     # Install/update deps
```

## Next Steps

1. ✅ Setup complete - verified by `verify-setup.sh`
2. 🚀 Run `./dev.sh` to start developing
3. 📖 Read `DEV_GUIDE.md` for detailed information
4. 🐛 Use F5 in VS Code for debugging
5. 📝 Check `QUICK_START.md` for quick reference

## Troubleshooting

### Server won't start

```bash
# Check port availability
lsof -i :8000

# Use different port
uv run python -m prismweave_mcp.server --port 8001
```

### Hot reload not working

```bash
# Verify watchdog is installed
uv sync

# Check dev.sh permissions
chmod +x dev.sh

# Run with verbose output
./dev.sh
```

### VS Code can't connect

1. Ensure server is running: `ps aux | grep prismweave`
2. Check URL in `mcp.json` matches server port
3. Restart VS Code
4. Check server logs in terminal

## Resources

- **DEV_GUIDE.md** - Full development guide
- **QUICK_START.md** - Quick reference
- **prismweave_mcp/README.md** - Architecture overview
- **prismweave_mcp/TROUBLESHOOTING.md** - Common issues
- **docs/MCP_SERVER_ARCHITECTURE.md** - Design documentation

---

**🎉 You're all set! Happy coding!**

Run `./dev.sh` to start developing with hot reload.
