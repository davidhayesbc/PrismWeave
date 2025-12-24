# Multi-stage Dockerfile for PrismWeave AI Processing
# Supports both development and production builds

# Base stage with UV package manager
FROM python:3.11-slim as base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install UV package manager
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    if [ -x /root/.local/bin/uv ]; then cp /root/.local/bin/uv /usr/local/bin/uv; \
    elif [ -x /root/.cargo/bin/uv ]; then cp /root/.cargo/bin/uv /usr/local/bin/uv; \
    else echo "uv installation did not produce an executable" >&2; exit 1; fi
ENV PATH="/usr/local/bin:$PATH"

WORKDIR /app

# Copy dependency files
COPY ai-processing/pyproject.toml ai-processing/uv.lock* ai-processing/README.md ./

# Development stage
FROM base as development

# Copy source code (needed for installing the local project)
COPY ai-processing/src ./src
COPY ai-processing/prismweave_mcp ./prismweave_mcp
COPY ai-processing/cli.py ./cli.py
COPY ai-processing/config.yaml ./config.yaml

# Install all dependencies including dev (and install the local project)
RUN uv sync --all-extras

# Create workspace directories
RUN mkdir -p /workspace/documents /workspace/.prismweave/chroma_db

# Expose MCP server port
EXPOSE 8000

# Development command with hot-reload
# Serve both:
# - REST API (FastAPI) at /articles, /visualization/rebuild, /health
# - MCP over SSE at /sse (and /message)
CMD ["/app/.venv/bin/uvicorn", "src.unified_app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Production stage
FROM base as production

# Copy source code (needed for installing the local project)
COPY ai-processing/src ./src
COPY ai-processing/prismweave_mcp ./prismweave_mcp
COPY ai-processing/cli.py ./cli.py
COPY ai-processing/config.yaml ./config.yaml

# Install only production dependencies (and install the local project)
RUN uv sync --no-dev

# Create workspace directories
RUN mkdir -p /workspace/documents /workspace/.prismweave/chroma_db

# Create non-root user
RUN useradd -m -u 1000 prismweave && \
    chown -R prismweave:prismweave /app /workspace

USER prismweave

# Expose MCP server port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Production command
CMD ["/app/.venv/bin/uvicorn", "src.unified_app:app", "--host", "0.0.0.0", "--port", "8000"]
