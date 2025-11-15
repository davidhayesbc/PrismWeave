#!/usr/bin/env python3
"""
Launch both MCP Server and Inspector together.

This script starts the MCP server in SSE mode (for Inspector web UI to connect to)
and also provides the stdio command for the Inspector's proxy server.
"""

import os
import subprocess
import sys
import time
from pathlib import Path


def main():
    """Launch MCP server (SSE) and Inspector together."""

    # Change to ai-processing directory if needed
    ai_processing = Path(__file__).parent
    os.chdir(ai_processing)

    print("🚀 Launching PrismWeave MCP Server + Inspector")
    print("=" * 50)
    print()

    # Start the MCP server in background (SSE transport for web UI)
    print("📡 Starting MCP Server (SSE transport on port 8000)...")
    print()

    server_process = subprocess.Popen(
        [sys.executable, "-m", "prismweave_mcp.server", "--transport", "sse"],
        # Don't capture output so we can see the FastMCP banner
        stdout=None,
        stderr=None,
    )

    # Give server time to start and display banner
    print("⏳ Waiting for server to start...")
    time.sleep(4)

    # Check if server started successfully
    if server_process.poll() is not None:
        print("❌ MCP Server failed to start")
        return 1

    print()
    print(f"✅ MCP Server running (PID: {server_process.pid})")
    print("   URL: http://127.0.0.1:8000/sse")
    print()

    # Now launch the inspector
    print("🔍 Launching MCP Inspector...")
    print("   Inspector UI: http://localhost:6274")
    print()
    print("Press Ctrl+C to stop both server and inspector")
    print()

    try:
        # Launch inspector - it will connect to the SSE server
        inspector_process = subprocess.run(
            [
                "npx",
                "@modelcontextprotocol/inspector",
                "http://127.0.0.1:8000/sse",
            ],
            check=False,
        )

        return inspector_process.returncode

    except KeyboardInterrupt:
        print("\n\n⏹️  Stopping Inspector and Server...")
        return 0

    finally:
        # Clean up server process
        if server_process.poll() is None:
            print("🛑 Stopping MCP Server...")
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print("⚠️  Server didn't stop gracefully, forcing...")
                server_process.kill()
        print("✅ Shutdown complete")


if __name__ == "__main__":
    sys.exit(main())
