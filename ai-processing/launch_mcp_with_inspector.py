#!/usr/bin/env python3
"""
Launch both MCP Server and Inspector together.

This script starts the MCP server in the background and then launches
the MCP Inspector, which will connect to the server for testing.
"""

import os
import subprocess
import sys
import time
from pathlib import Path


def main():
    """Launch MCP server and inspector together."""

    # Change to ai-processing directory if needed
    ai_processing = Path(__file__).parent
    os.chdir(ai_processing)

    print("🚀 Launching PrismWeave MCP Server + Inspector")
    print("=" * 50)
    print()

    # Start the MCP server in background (SSE transport for health checks)
    print("📡 Starting MCP Server (SSE transport)...")
    server_process = subprocess.Popen(
        [sys.executable, "-m", "prismweave_mcp.server", "--transport", "sse"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Give server a moment to start
    time.sleep(2)

    # Check if server started successfully
    if server_process.poll() is not None:
        print("❌ MCP Server failed to start")
        stdout, stderr = server_process.communicate()
        print("STDOUT:", stdout.decode())
        print("STDERR:", stderr.decode())
        return 1

    print(f"✅ MCP Server started (PID: {server_process.pid})")
    print()

    # Now launch the inspector (stdio transport for inspector connection)
    print("🔍 Launching MCP Inspector...")
    print()
    print("Inspector will open at: http://localhost:6274")
    print("Press Ctrl+C to stop both server and inspector")
    print()

    try:
        # Launch inspector - it will start its own stdio server instance
        inspector_process = subprocess.run(
            [
                "npx",
                "@modelcontextprotocol/inspector",
                sys.executable,
                "-m",
                "prismweave_mcp.server",
                "--transport",
                "stdio",
            ],
            check=False,
        )

        return inspector_process.returncode

    except KeyboardInterrupt:
        print("\n\n⏹️  Stopping MCP Server and Inspector...")
        return 0

    finally:
        # Clean up server process
        if server_process.poll() is None:
            print("🛑 Stopping MCP Server...")
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_process.kill()
        print("✅ Shutdown complete")


if __name__ == "__main__":
    sys.exit(main())
