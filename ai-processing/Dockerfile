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
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock* ./

# Development stage
FROM base as development

# Install all dependencies including dev
RUN uv sync --all-extras

# Copy source code
COPY . .

# Create workspace directories
RUN mkdir -p /workspace/documents /workspace/.prismweave/chroma_db

# Expose MCP server port
EXPOSE 8000
EXPOSE 8001

# Development command with hot-reload
CMD ["uv", "run", "python", "-m", "prismweave_mcp.server", "--transport", "sse", "--host", "0.0.0.0", "--port", "8000"]

# Production stage
FROM base as production

# Install only production dependencies
RUN uv sync --no-dev

# Copy source code
COPY src ./src
COPY prismweave_mcp ./prismweave_mcp
COPY cli ./cli
COPY config.yaml ./

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
CMD ["uv", "run", "python", "-m", "prismweave_mcp.server", "--transport", "sse", "--host", "0.0.0.0", "--port", "8000"]
