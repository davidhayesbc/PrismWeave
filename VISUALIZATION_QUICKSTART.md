# PrismWeave Visualization Layer - Quick Start

## Launch the Application

From the `visualization` directory:

```bash
cd visualization
npm start
```

This single command launches:

- ✅ **API Backend** (FastAPI on port 8000)
- ✅ **Vue Frontend** (Vite on port 5173)

Then open your browser to: **http://localhost:5173**

## First Time Setup

1. **Install Python dependencies** (from `ai-processing`):

   ```bash
   cd ai-processing
   uv sync
   ```

2. **Install Node.js dependencies** (from `visualization`):

   ```bash
   cd visualization
   npm install
   ```

3. **Build the visualization index** (one-time):

   ```bash
   cd ai-processing
   source .venv/bin/activate
   prismweave-cli visualize build-index
   ```

4. **Start the application**:
   ```bash
   cd visualization
   npm start
   ```

## All Available Commands

| Command                | Description                                |
| ---------------------- | ------------------------------------------ |
| `npm start`            | Launch both API and frontend (recommended) |
| `npm run dev:all`      | Same as `npm start`                        |
| `npm run dev:api`      | Run only the API backend                   |
| `npm run dev:frontend` | Run only the Vue frontend                  |
| `npm run build`        | Build for production                       |
| `npm run preview`      | Preview production build                   |
| `npm run type-check`   | TypeScript type checking                   |

## Ports

- **Frontend**: http://localhost:5173
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs (Swagger UI)

## Stopping Services

Press `Ctrl+C` in the terminal to stop both services.

## More Information

See [visualization/DEV_GUIDE.md](visualization/DEV_GUIDE.md) for detailed documentation.
