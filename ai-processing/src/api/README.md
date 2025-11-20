# PrismWeave Visualization API

HTTP API for PrismWeave document visualization and management.

## Overview

This FastAPI-based API provides endpoints for:
- Listing articles with metadata and visualization coordinates
- Reading full article content
- Updating article metadata and content
- Deleting articles
- Rebuilding the visualization index

## Running the API

### Development Mode

```bash
# From the ai-processing directory
python -m uvicorn src.api.app:app --reload --host 0.0.0.0 --port 8000
```

Or using the entry point:

```bash
prismweave-api
```

### Production Mode

```bash
uvicorn src.api.app:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Endpoints

### Root
- `GET /` - API information and available endpoints

### Articles
- `GET /articles` - List all articles with metadata and coordinates
- `GET /articles/{id}` - Get detailed article information with full content
- `PUT /articles/{id}` - Update article metadata and/or content
- `DELETE /articles/{id}` - Delete an article

### Visualization
- `POST /visualization/rebuild` - Rebuild the visualization index

## Interactive Documentation

Once the API is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Configuration

The API uses the standard PrismWeave configuration from `config.yaml`:
- `mcp.paths.documents_root` - Location of markdown documents
- Other settings for ChromaDB, Ollama, etc.

## CORS

CORS is enabled for all origins in development. For production, update the `allow_origins` setting in `src/api/app.py`.

## Notes

- The API requires that `visualize build-index` has been run at least once to create the metadata index
- Article updates write to disk immediately but do NOT automatically recompute embeddings/layout
- After editing articles, run `POST /visualization/rebuild` to update the visualization
