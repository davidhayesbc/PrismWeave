# Quick Start Guide: HTTP/SSE MCP Server

## ✅ Migration Complete!

Your PrismWeave MCP server has been switched from stdio to HTTP/SSE transport.

## Starting the Server

### 1. Start the MCP Server

```bash
cd /home/dhayes/Source/PrismWeave/ai-processing
source .venv/bin/activate
python mcp/prismweave_server.py
```

You should see:

```
INFO - Starting PrismWeave MCP Server on http://127.0.0.1:8000
INFO - SSE endpoint: http://127.0.0.1:8000/sse
INFO - Messages endpoint: http://127.0.0.1:8000/messages
```

### 2. Update VS Code MCP Configuration

Edit your MCP configuration file:

**File:** `~/.config/Code - Insiders/User/mcp.json`

**Old (stdio - remove this):**

```json
{
  "mcpServers": {
    "prismweave": {
      "command": "python",
      "args": ["-m", "mcp.prismweave_server"],
      "cwd": "/home/dhayes/Source/PrismWeave/ai-processing"
    }
  }
}
```

**New (HTTP/SSE - use this):**

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

### 3. Restart VS Code

After updating the configuration, restart VS Code for the changes to take effect.

## Testing the Connection

### Quick Test

```bash
# Test if server is running
curl http://127.0.0.1:8000/sse

# Or use the test script
cd /home/dhayes/Source/PrismWeave/ai-processing
python mcp/test_http_server.py
```

## Server Options

### Custom Port

```bash
python mcp/prismweave_server.py --port 8080
```

Update config to: `"url": "http://127.0.0.1:8080/sse"`

### Debug Mode

```bash
python mcp/prismweave_server.py --debug
```

### Remote Access (careful!)

```bash
python mcp/prismweave_server.py --host 0.0.0.0
```

## Next Steps

1. ✅ Server is running with HTTP/SSE
2. ⏭️ Update your `mcp.json` configuration
3. ⏭️ Restart VS Code
4. ⏭️ Test MCP tools in VS Code

## Benefits of HTTP/SSE

- ✅ Multiple clients can connect simultaneously
- ✅ Better debugging with standard HTTP tools
- ✅ Server stays running (faster reconnection)
- ✅ Standard protocol (works with any HTTP client)
- ✅ Better error handling with HTTP status codes

## Troubleshooting

### Port Already in Use

```bash
# Find what's using port 8000
lsof -i :8000

# Use different port
python mcp/prismweave_server.py --port 8001
```

### VS Code Can't Connect

1. Check server is running: `ps aux | grep prismweave_server`
2. Check config URL matches server port
3. Check VS Code Output > MCP Servers for error logs
4. Restart VS Code

## Documentation

- Full documentation: `mcp/README.md`
- Configuration guide: `mcp/CONFIGURATION.md`
- Test script: `mcp/test_http_server.py`
