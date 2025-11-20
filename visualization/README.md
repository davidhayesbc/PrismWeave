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

# Type check
npm run type-check
```

## Configuration

The API endpoint is configured in `vite.config.ts`:

- Development: proxies `/api` to `http://localhost:8000`
- Production: configure `VITE_API_BASE_URL` environment variable

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
