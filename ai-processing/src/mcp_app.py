"""Standalone MCP ASGI application for PrismWeave.

This module exists so the MCP server can be run as a *separate* Aspire resource
(process) and show up independently in the Aspire dashboard.

It exposes FastMCP over SSE on:
- /sse

It also includes the MCP health endpoint (provided by the MCP server):
- /health
"""

from __future__ import annotations

from src.telemetry import configure_telemetry

# Configure telemetry as early as possible (Aspire injects OTEL_* env vars).
configure_telemetry("mcp-server")

from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from prismweave_mcp.server import mcp


def _build_mcp_http_app():
    # Configure CORS for MCP Inspector and local dev.
    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:6274", "http://127.0.0.1:6274", "*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    ]

    return mcp.http_app(transport="sse", path="/sse", middleware=middleware)


# Export as the ASGI app for uvicorn.
app = _build_mcp_http_app()
