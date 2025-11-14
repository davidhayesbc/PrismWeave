# PrismWeave MCP Server - VS Code Configuration

## Update Your MCP Configuration

The server now uses HTTP/SSE transport. Update your VS Code MCP configuration file.

### Configuration File Location

The MCP configuration is typically located at:

**VS Code Insiders (Linux):**

```
~/.config/Code - Insiders/User/mcp.json
```

**VS Code (Linux):**

```
~/.config/Code/User/mcp.json
```

**VS Code Insiders (macOS):**

```
~/Library/Application Support/Code - Insiders/User/mcp.json
```

**VS Code (macOS):**

```
~/Library/Application Support/Code/User/mcp.json
```

**VS Code (Windows):**

```
%APPDATA%\Code\User\mcp.json
```

### New Configuration (HTTP/SSE)

Replace your current PrismWeave MCP configuration with:

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

### Old Configuration (stdio - no longer used)

```json
{
  "mcpServers": {
    "prismweave": {
      "command": "python",
      "args": ["-m", "mcp.prismweave_server"],
      "cwd": "/path/to/PrismWeave/ai-processing"
    }
  }
}
```

## Starting the Server

### Option 1: Manual Start (Recommended for Development)

```bash
cd /home/dhayes/Source/PrismWeave/ai-processing
source .venv/bin/activate
python -m mcp.prismweave_server
```

The server will start and display:

```
Starting PrismWeave MCP Server on http://127.0.0.1:8000
SSE endpoint: http://127.0.0.1:8000/sse
Messages endpoint: http://127.0.0.1:8000/messages
```

### Option 2: Background Service

To run as a systemd service (Linux):

Create `/etc/systemd/system/prismweave-mcp.service`:

```ini
[Unit]
Description=PrismWeave MCP Server
After=network.target

[Service]
Type=simple
User=dhayes
WorkingDirectory=/home/dhayes/Source/PrismWeave/ai-processing
Environment="PATH=/home/dhayes/Source/PrismWeave/ai-processing/.venv/bin"
ExecStart=/home/dhayes/Source/PrismWeave/ai-processing/.venv/bin/python -m mcp.prismweave_server
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Then:

```bash
sudo systemctl daemon-reload
sudo systemctl enable prismweave-mcp
sudo systemctl start prismweave-mcp
sudo systemctl status prismweave-mcp
```

### Option 3: Custom Port

```bash
python -m mcp.prismweave_server --port 8080
```

Update your config to match:

```json
{
  "url": "http://127.0.0.1:8080/sse"
}
```

## Testing the Connection

### Test 1: Check Server is Running

```bash
curl http://127.0.0.1:8000/sse
```

You should see an SSE connection established.

### Test 2: Run Test Script

```bash
cd /home/dhayes/Source/PrismWeave/ai-processing
python mcp/test_http_server.py
```

### Test 3: VS Code Connection

1. Restart VS Code after updating config
2. Open VS Code Output panel (Ctrl+Shift+U)
3. Select "MCP Servers" from dropdown
4. Look for "prismweave" connection logs

## Advantages of HTTP/SSE

✅ **Multiple Clients** - Multiple VS Code windows can connect simultaneously  
✅ **Better Debugging** - Can test with curl/Postman  
✅ **Persistent** - Server stays running, faster reconnection  
✅ **Standard Protocol** - Works with any HTTP client  
✅ **Error Handling** - HTTP status codes for better error reporting

## Troubleshooting

### Server won't start - Port already in use

```bash
# Check what's using the port
lsof -i :8000

# Use a different port
python -m mcp.prismweave_server --port 8001
```

### VS Code can't connect

1. Check server is running:

   ```bash
   ps aux | grep prismweave_server
   ```

2. Check server logs for errors

3. Verify config URL matches server port

4. Restart VS Code

### ChromaDB errors

The server will start but search may be limited. Check:

```bash
ls -la /home/dhayes/Source/PrismWeaveDocs/.prismweave/chroma_db/
```

Ensure directory exists and has write permissions.

## Migration Checklist

- [ ] Stop any running stdio-based MCP server
- [ ] Update `mcp.json` configuration file
- [ ] Start HTTP/SSE server
- [ ] Test connection with test script
- [ ] Restart VS Code
- [ ] Verify MCP tools are available in VS Code
- [ ] (Optional) Set up systemd service for auto-start
