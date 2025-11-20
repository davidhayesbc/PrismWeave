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

## Available Commands

### Start Everything (Recommended)

To launch both the API backend and Vue frontend together:

```bash
cd visualization
npm start
```

Or equivalently:

```bash
npm run dev:all
```

This will start:

- **API Server** on `http://localhost:8000` (blue output)
- **Frontend Dev Server** on `http://localhost:5173` (green output)

Open your browser to `http://localhost:5173` to use the application.

### Individual Services

If you need to run services separately for debugging:

#### Backend API Only

```bash
npm run dev:api
```

Runs the FastAPI backend with hot-reload enabled on port 8000.

#### Frontend Only

```bash
npm run dev:frontend
```

Or simply:

```bash
npm run dev
```

Runs the Vite development server on port 5173.

### Other Commands

#### Build for Production

```bash
npm run build
```

Compiles TypeScript and builds the Vue app for production.

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
- **Port**: 5173
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

### Port Already in Use

If you see port conflicts:

```bash
# Kill process on port 8000 (API)
lsof -ti:8000 | xargs kill -9

# Kill process on port 5173 (Frontend)
lsof -ti:5173 | xargs kill -9
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

If hot reload stops working, restart the services with `npm start`.

## Development Workflow

1. **Start both services**: `npm start`
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

- The `concurrently` package allows running multiple npm scripts simultaneously with colored output
- The API runs with `--reload` flag for automatic reloading during development
- Frontend proxies `/api/*` requests to the backend automatically
- Both services need to be running for the full application to work
