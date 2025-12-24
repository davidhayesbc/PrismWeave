# PrismWeave Visualization Development Guide

## Quick Start

### Prerequisites

Before running the visualization layer, ensure you have:

1. **Python environment set up** (from `ai-processing` directory):

   ```bash
   cd ai-processing
   # Create and activate virtual environment if not already done
   uv sync
   ```

2. **Node.js dependencies installed** (from `visualization` directory):
   ```bash
   cd visualization
   npm install
   ```

## Recommended: Docker Compose (Dev)

The easiest way to run the visualization + API together is via the repo-level Docker Compose.

```bash
cd ..
docker-compose up -d --build
```

Then open:

- Frontend: `http://localhost:3001`
- API: `http://localhost:8000/docs`

In Docker dev mode, the frontend dev server still proxies `/api/*` to the backend via the `API_URL` environment value.

## Manual: Run Services Separately (No Docker)

### 1) Backend API (ai-processing)

From the repo root:

```bash
cd ai-processing
uv sync
uv run python -m uvicorn src.api.app:app --reload --host 0.0.0.0 --port 8000
```

### 2) Frontend (visualization)

In another terminal:

```bash
cd visualization
npm install
npm run dev
```

Open `http://localhost:3001`.

The Vite dev server proxies `/api/*` to `http://localhost:8000` by default (config in `vite.config.ts`).

## Available Commands

### Frontend dev server

```bash
npm run dev
```

Runs the Vite dev server on port 3001.

### Other Commands

#### Build for Production

```bash
npm run build
```

Builds the Vue app for production.

#### Preview Production Build

```bash
npm run preview
```

Serves the production build locally for testing.

#### Type Check

```bash
npm run type-check
```

Runs TypeScript type checking without emitting files.

Note: If `vue-tsc` errors in your environment, keep `npm run build` working and run type-checking in CI or with a compatible Node version.

## Architecture

### API Backend

- **Framework**: FastAPI with Uvicorn
- **Port**: 8000
- **Code**: `../ai-processing/src/api/`
- **Features**:
  - RESTful endpoints for document management
  - Metadata indexing and search
  - Visualization data generation

### Frontend

- **Framework**: Vue 3 + TypeScript + Vite
- **Port**: 3001
- **Proxy**: API requests to `/api/*` are proxied to `http://localhost:8000/*`
- **Features**:
  - Interactive document visualization with D3.js
  - Document browsing and search
  - Markdown rendering

## API Endpoints

When running, the API provides:

- `GET /` - API information
- `GET /articles` - List all articles with metadata and coordinates
- `GET /articles/{id}` - Get detailed article information
- `PUT /articles/{id}` - Update article metadata/content
- `DELETE /articles/{id}` - Delete an article
- `POST /visualization/rebuild` - Rebuild visualization index

API documentation available at: `http://localhost:8000/docs`

## Troubleshooting

### 404 Errors - Index Not Found

**Symptom**: API returns `404 Not Found` with message: `Article index not found. Run 'visualize build-index' first.`

**Cause**: The visualization index hasn't been created yet.

**Solution**: Build the index using either method:

**Method 1: Via API (Recommended)**

```bash
# With services running
curl -X POST http://localhost:8000/visualization/rebuild
```

**Method 2: Via CLI**

```bash
cd ../ai-processing
source .venv/bin/activate
python cli.py visualize build-index --verbose
```

### YAML Parsing Errors

**Symptom**: Index building fails with `ScannerError: found a tab character that violates indentation`

**Cause**: Markdown files have invalid YAML frontmatter (tabs or syntax errors)

**Solution**:

1. Check the error for the problematic file
2. Open the file and fix the YAML frontmatter:
   - Replace tabs with spaces
   - Quote special characters in values
   - Ensure proper YAML list/dict syntax
3. Retry the index build

Example of correct frontmatter:

```yaml
---
title: 'My Article Title'
topic: technology
tags:
  - python
  - api
date: 2024-11-19
---
```

### Port Already in Use

If you see port conflicts:

```bash
# Kill process on port 8000 (API)
lsof -ti:8000 | xargs kill -9

# Kill process on port 3001 (Frontend)
lsof -ti:3001 | xargs kill -9
```

### Python Virtual Environment Not Found

Ensure the Python virtual environment exists:

```bash
cd ../ai-processing
uv sync
```

### API Connection Failed

1. Verify the API is running on port 8000
2. Check that `documents_root` is configured in `../ai-processing/config.yaml`
3. Ensure the visualization index exists (run `prismweave-cli visualize build-index` if needed)

### Hot Reload Issues

- **Backend**: Uses `uvicorn --reload` - changes to Python files are detected automatically
- **Frontend**: Uses Vite HMR - changes to Vue/TS files update instantly

If hot reload stops working, restart the services (Docker Compose or `npm run dev`).

## Development Workflow

1. **Start services**: via Docker Compose, or run backend + frontend manually
2. **Make changes**:
   - Backend: Edit files in `../ai-processing/src/api/`
   - Frontend: Edit files in `./src/`
3. **See changes**: Browser auto-refreshes (frontend) or API reloads (backend)
4. **Test endpoints**: Visit `http://localhost:8000/docs` for API testing
5. **Type check**: Run `npm run type-check` before committing

## Project Structure

```
visualization/
├── src/
│   ├── components/       # Vue components
│   ├── services/         # API service layer
│   ├── stores/           # Pinia state management
│   ├── views/            # Page components
│   ├── App.vue          # Root component
│   └── main.ts          # Entry point
├── public/              # Static assets
├── package.json         # Dependencies and scripts
├── vite.config.ts       # Vite configuration
└── DEV_GUIDE.md        # This file
```

## Notes

- The API runs with `--reload` flag for automatic reloading during development
- Frontend proxies `/api/*` requests to the backend automatically
- Both services need to be running for the full application to work
