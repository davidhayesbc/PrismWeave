# PrismWeave Visualization Frontend

Vue 3 + TypeScript frontend for PrismWeave document visualization.

## Features

- 2D similarity map of articles with semantic layout
- Interactive node visualization (hover, click, pan, zoom)
- Article reader and editor
- Filters by topic, age, and text search
- Integration with VS Code for editing

## Development

```bash
# Install dependencies
npm install

# Start dev server (with hot reload)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Type check (separate from build)
npm run type-check
```

## Configuration

The frontend calls the backend through the API service in `src/services/api.ts`.
By default it uses a base path of `/api`.

**Development**

- Vite proxies `/api/*` to the backend (default: `http://localhost:8000`).
- You can override the proxy target with `API_URL`.

**Production (Docker Compose)**

- Nginx proxies `/api/*` to the `ai-processing` service.
- No special `VITE_API_BASE_URL` is needed; keeping it as `/api` is recommended.

If you deploy the frontend outside of the Compose network, set `VITE_API_BASE_URL` at build time to point at your backend.

Ports (defaults):

- Frontend dev server: `http://localhost:3001`
- Backend API: `http://localhost:8000` (Swagger docs at `/docs`)

## Architecture

- **Vue Router** for navigation
- **Pinia** for state management
- **D3.js** for visualization
- **Marked** for markdown rendering
- **Axios** for API communication

## Structure

```
src/
├── components/       # Reusable Vue components
├── views/           # Page components (MapView, ArticleView)
├── stores/          # Pinia stores
├── router/          # Vue Router configuration
├── services/        # API service layer
├── types/           # TypeScript type definitions
└── styles/          # Global styles
```
