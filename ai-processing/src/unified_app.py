"""Unified REST API application for PrismWeave AI Processing.

This module exposes the Visualization REST API (FastAPI) from ``src.api.app``.

The MCP server is intentionally *not* hosted here anymore.
Run MCP as a separate ASGI app (``src.mcp_app:app``) so it appears as its own
Aspire resource/process in the dashboard.
"""

from __future__ import annotations

from src.telemetry import configure_telemetry, instrument_fastapi

# Configure telemetry as early as possible (Aspire injects OTEL_* env vars).
configure_telemetry("ai-processing")


from src.api.app import app as rest_app

# Add FastAPI tracing (no-op when OTEL_EXPORTER_OTLP_ENDPOINT isn't set).
instrument_fastapi(rest_app)
# Export as the ASGI app for uvicorn.
app = rest_app
