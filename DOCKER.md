# PrismWeave Docker Documentation

Note: For local dev, the recommended orchestration path is now the Aspire AppHost (see the repo README). Docker Compose remains a supported alternative and is useful for containerizing the full stack.

## Architecture Overview

PrismWeave uses a multi-container Docker architecture:

```
┌─────────────────────────────────────────────────────┐
│                    Host Machine                      │
│                                                       │
│  ┌──────────────┐  ┌──────────────┐                │
│  │   Website    │  │Visualization │                │
│  │  :3002(dev)  │  │  :3001(dev)  │                │
│  │  :80(prod)   │  │  :8080(prod) │                │
│  └──────┬───────┘  └──────┬───────┘                │
│         │                  │                         │
│         └────────┬─────────┘                         │
│                  │                                    │
│         ┌────────▼──────────┐                        │
│         │  AI Processing    │                        │
│         │  MCP Server :8000 │                        │
│         └────────┬──────────┘                        │
│                  │                                    │
│         ┌────────▼──────────┐                        │
│         │  Ollama (opt)     │                        │
│         │     :11434        │                        │
│         └───────────────────┘                        │
│                                                       │
│  Volumes:                                            │
│  - PrismWeaveDocs (bind mount)                      │
│  - ChromaDB (named volume)                          │
│  - Ollama models (named volume)                     │
└─────────────────────────────────────────────────────┘
```

## Quick Start

### Development Mode

```bash
# Copy environment template
cp .env.example .env

# Edit .env to configure paths
nano .env

# Start all services (without Ollama)
npm run docker:dev

# Or start with Ollama container
npm run docker:dev:ollama

# Start in detached mode
npm run docker:dev:detached
```

### Production Mode

```bash
# Build and start production containers
npm run docker:prod

# With Ollama
npm run docker:prod:ollama
```

### Using Direct Docker Compose (alternative)

```bash
# Development
docker-compose up

# With Ollama
docker-compose --profile with-ollama up

# Production
docker-compose -f docker-compose.prod.yml up -d
```

## Service Details

### AI Processing Container

**Ports:**

- `8000` - MCP Server (HTTP/SSE endpoint)
- `8000` - Unified API server (MCP SSE + Visualization REST)

**Volumes:**

- `../PrismWeaveDocs:/workspace/documents` - Document storage (bind mount)
- `chroma-data:/workspace/.prismweave/chroma_db` - Vector database

**Environment Variables:**

- `OLLAMA_HOST` - Ollama server URL
- `LOG_LEVEL` - Logging verbosity
- `DOCUMENTS_PATH` - Path to documents
- `CHROMA_PERSIST_DIR` - ChromaDB storage path

**Health Check:**

```bash
curl http://localhost:8000/health
```

### Ollama Container (Optional)

**When to use:**

- You don't have Ollama running on your host
- You want isolated model management
- You need GPU access in containers

**When NOT to use:**

- You already have Ollama on host with models downloaded
- You want to share models across projects

**GPU Support:**
Requires nvidia-docker runtime:

```bash
# Install nvidia-container-toolkit
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker
```

### Website Container

**Development:**

- Port: `3002` (configurable via `WEBSITE_PORT`)
- Hot-reload enabled

**Production:**

- Port: `80`
- Nginx serving static files

### Visualization Container

**Development:**

- Port: `3001`
- Hot-reload enabled

**Production:**

- Port: `8080`
- Nginx serving static files

## Common Commands (npm scripts)

All Docker commands are available as npm scripts for cross-platform compatibility:

```bash
# Start development environment
npm run docker:dev

# Start development with live rebuild
npm run docker:dev:build

# Start with Ollama container
npm run docker:dev:ollama

# Start production
npm run docker:prod

# Stop all containers
npm run docker:down

# View logs
npm run docker:logs          # All services
npm run docker:logs:ai       # AI processing only
npm run docker:logs:web      # Website only
npm run docker:logs:viz      # Visualization only

# Build containers
npm run docker:build         # Build all
npm run docker:build:nocache # Rebuild from scratch

# Cleanup
npm run docker:clean         # Remove containers, volumes, images

# Testing
npm run docker:test          # Run tests in containers

# Shell access
npm run docker:shell:ai      # Access AI container
npm run docker:shell:web     # Access website container

# Utilities
npm run docker:pull-models   # Pull Ollama models
npm run docker:health        # Check container health
```

### Direct Docker Commands (if needed)

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f ai-processing

# Last 100 lines
docker-compose logs --tail=100 ai-processing
```

### Execute Commands in Container

```bash
# Access AI processing container shell
docker-compose exec ai-processing bash

# Run tests
docker-compose exec ai-processing uv run pytest

# Check Ollama models
docker-compose exec ollama ollama list

# Pull a model
docker-compose exec ollama ollama pull phi3:mini
```

### Manage Data

```bash
# Backup ChromaDB
docker run --rm -v prismweave_chroma-data:/data -v $(pwd):/backup \
  alpine tar czf /backup/chroma-backup.tar.gz -C /data .

# Restore ChromaDB
docker run --rm -v prismweave_chroma-data:/data -v $(pwd):/backup \
  alpine tar xzf /backup/chroma-backup.tar.gz -C /data

# List volumes
docker volume ls | grep prismweave

# Inspect volume
docker volume inspect prismweave_chroma-data
```

### Cleanup

```bash
# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Remove all PrismWeave containers and images
docker-compose down --rmi all

# Full cleanup (including volumes)
docker-compose down -v --rmi all
```

## Configuration

### Environment Variables

Create `.env` file in project root:

```bash
# Document storage path (relative to docker-compose.yml)
PRISMWEAVE_DOCS_PATH=../PrismWeaveDocs

# Use host's Ollama
OLLAMA_HOST=http://host.docker.internal:11434

# Or use container's Ollama
OLLAMA_HOST=http://ollama:11434

# Logging
LOG_LEVEL=INFO
```

### Using Host Ollama

To use Ollama running on your host machine:

1. Update `.env`:

   ```bash
   OLLAMA_HOST=http://host.docker.internal:11434
   ```

2. Start without Ollama container:
   ```bash
   docker-compose up
   ```

### Custom Document Path

To use a different document repository:

```bash
# In .env
PRISMWEAVE_DOCS_PATH=/path/to/your/documents

# Or via environment variable
PRISMWEAVE_DOCS_PATH=/custom/path docker-compose up
```

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs ai-processing

# Rebuild container
docker-compose build --no-cache ai-processing
docker-compose up ai-processing
```

### Ollama Connection Issues

```bash
# Test from container
docker-compose exec ai-processing curl http://ollama:11434/api/tags

# Test host Ollama
docker-compose exec ai-processing curl http://host.docker.internal:11434/api/tags
```

### Volume Permission Issues

```bash
# Check volume permissions
docker-compose exec ai-processing ls -la /workspace

# Fix permissions (if needed)
docker-compose exec -u root ai-processing chown -R prismweave:prismweave /workspace
```

### Port Conflicts

If ports are already in use:

```yaml
# Edit docker-compose.yml to change port mappings
ports:
  - '8002:8000' # Use 8002 instead of 8000
```

### ChromaDB Not Persisting

```bash
# Verify volume exists
docker volume inspect prismweave_chroma-data

# Check mount inside container
docker-compose exec ai-processing df -h /workspace/.prismweave/chroma_db
```

## Development Workflow

### Hot-Reload Development

```bash
# Start in dev mode with source mounts
docker-compose up

# Edit files on host - changes reflect immediately
# - Python files in ai-processing/src
# - HTML/JS in website or visualization
```

### Testing in Containers

```bash
# Run Python tests
docker-compose exec ai-processing uv run pytest -v

# Run with coverage
docker-compose exec ai-processing uv run pytest --cov=src

# Run specific test
docker-compose exec ai-processing uv run pytest tests/test_specific.py
```

### Updating Dependencies

```bash
# Python dependencies
docker-compose exec ai-processing uv sync --upgrade

# Rebuild container
docker-compose build ai-processing
docker-compose up -d ai-processing
```

## Production Deployment

### Build Production Images

```bash
# Build all production images
docker-compose -f docker-compose.prod.yml build

# Tag for registry
docker tag prismweave-ai-prod myregistry.com/prismweave-ai:latest

# Push to registry
docker push myregistry.com/prismweave-ai:latest
```

### Production Best Practices

1. **Use .env file for secrets** (never commit)
2. **Mount documents as read-only** if not editing
3. **Set resource limits** in docker-compose
4. **Enable automatic restarts**: `restart: always`
5. **Use health checks** for monitoring
6. **Regular backups** of ChromaDB volume
7. **Monitor container logs** with logging driver

### Resource Limits (Production)

Add to docker-compose.prod.yml:

```yaml
services:
  ai-processing:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

## Integration with MCP Clients

### Configure Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "prismweave": {
      "url": "http://localhost:8000/sse",
      "transport": "sse"
    }
  }
}
```

### Testing MCP Endpoint

```bash
# Test SSE connection
curl -N http://localhost:8000/sse

# Test health
curl http://localhost:8000/health

# List MCP tools
curl http://localhost:8000/tools
```

## Security Considerations

1. **Network Isolation**: Services communicate via internal network
2. **Non-root User**: Production containers run as `prismweave` user
3. **Read-only Mounts**: Prefer read-only mounts where feasible; the default dev compose mounts source as read/write for hot reload
4. **Secret Management**: Use Docker secrets or env files (not committed)
5. **Container Updates**: Regularly update base images

## Next Steps

- [ ] Configure `.env` with your paths
- [ ] Pull required Ollama models
- [ ] Start containers and verify health
- [ ] Test MCP server connection
- [ ] Add documents to PrismWeaveDocs
- [ ] Access visualization at http://localhost:3001
