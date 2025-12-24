"""Unified API application for PrismWeave AI Processing.

This module exposes a single ASGI app that serves:

- The Visualization REST API (FastAPI) from ``src.api.app``
- The MCP server (FastMCP) over SSE/HTTP from ``prismweave_mcp.server``

Goal: allow running both APIs from the same container/port.
"""

from __future__ import annotations

from src.telemetry import configure_telemetry, instrument_fastapi

# Configure telemetry as early as possible (Aspire injects OTEL_* env vars).
configure_telemetry("ai-processing")

from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from prismweave_mcp.server import mcp
from src.api.app import app as rest_app

# Add FastAPI tracing (no-op when OTEL_EXPORTER_OTLP_ENDPOINT isn't set).
instrument_fastapi(rest_app)


def _build_mcp_http_app():
    # FastAPI middleware does not apply to mounted sub-apps; configure CORS here too.
    mcp_middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:6274", "http://127.0.0.1:6274", "*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    ]

    # Keep default MCP endpoints at the same paths the server uses when run standalone.
    # - SSE:     /sse
    # - Message: /message (configured inside FastMCP)
    return mcp.http_app(transport="sse", path="/sse", middleware=mcp_middleware)


# Mount MCP app at root *after* REST routes are defined.
# FastAPI routes (e.g. /health, /articles, /visualization/rebuild) take precedence.
rest_app.mount("/", _build_mcp_http_app())

# Export as the ASGI app for uvicorn.
app = rest_app
