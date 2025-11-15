# 🔧 Fix: FastMCP Transport Mode

## Problem

When running `./dev.sh`, FastMCP was starting in **stdio mode** instead of **SSE (HTTP) mode**, which is required for VS Code MCP integration.

## Root Cause

FastMCP defaults to stdio transport when `run()` is called without explicit transport parameters. The server needed to explicitly specify `transport="sse"` when calling `mcp.run()`.

## Solution Applied

### 1. Updated `server.py` main() function

Added explicit transport selection:

```python
if args.transport == "sse":
    logger.info(f"HTTP Server: http://{args.host}:{args.port}")
    logger.info(f"SSE endpoint: http://{args.host}:{args.port}/sse")
    # Run with SSE transport (HTTP server)
    mcp.run(transport="sse", host=args.host, port=args.port)
else:
    logger.info("Running with stdio transport")
    # Run with stdio transport
    mcp.run(transport="stdio")
```

### 2. Added `--transport` CLI argument

- Default: `sse` (HTTP/SSE mode)
- Options: `sse` or `stdio`
- Usage: `python -m prismweave_mcp.server --transport sse`

### 3. Updated `dev.sh`

Added explicit `--transport sse` flag:

```bash
-- python -m prismweave_mcp.server --debug --transport sse
```

### 4. Updated VS Code Tasks

All MCP server tasks now include `--transport sse`:

- MCP Server: Run
- MCP Server: Run with Debug Logging
- MCP Server: Run with Hot Reload (via dev.sh)

### 5. Updated Debug Configurations

Added `"args": ["--debug", "--transport", "sse"]` to:

- Debug MCP Server
- Debug MCP Server with Breakpoints

## Verification

Run the server and check the output:

```bash
./dev.sh
```

You should now see:

```
Starting PrismWeave MCP Server
Transport: sse
HTTP Server: http://127.0.0.1:8000
SSE endpoint: http://127.0.0.1:8000/sse
```

Instead of the previous stdio mode startup.

## What Changed

| File                       | Change                                          |
| -------------------------- | ----------------------------------------------- |
| `prismweave_mcp/server.py` | Added transport parameter to `mcp.run()` calls  |
| `dev.sh`                   | Added `--transport sse` flag                    |
| `.vscode/tasks.json`       | Added `--transport sse` to all MCP server tasks |
| `.vscode/launch.json`      | Added `--transport sse` to debug configurations |

## Testing

1. **Run dev server**:

   ```bash
   ./dev.sh
   ```

   Should show "Transport: sse" and "HTTP Server: http://127.0.0.1:8000"

2. **Run via VS Code task**:
   - Ctrl+Shift+P → "Tasks: Run Task" → "MCP Server: Run with Hot Reload"
   - Check terminal output for SSE mode confirmation

3. **Debug in VS Code**:
   - Press F5
   - Server should start in SSE mode with debugger attached

## VS Code MCP Configuration

No changes needed to your `mcp.json`:

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

The server now correctly runs in HTTP/SSE mode and VS Code can connect properly! 🎉
