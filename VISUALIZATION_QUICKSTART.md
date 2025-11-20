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

**Important**: Run these commands from the `visualization` directory!

| Command                | Description                                |
| ---------------------- | ------------------------------------------ |
| `npm run dev:all`      | Launch both API and frontend (recommended) |
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

## Troubleshooting

### 404 Errors from API

If you see 404 errors in the browser console or API logs:

**Symptom**: `GET /articles HTTP/1.1" 404 Not Found`

**Cause**: The visualization index hasn't been built yet.

**Solution**: Build the index using one of these methods:

```bash
# Method 1: Via API (with services running)
curl -X POST http://localhost:8000/visualization/rebuild

# Method 2: Via CLI
cd ai-processing
source .venv/bin/activate
python cli.py visualize build-index --verbose
```

### YAML Parsing Errors

If index building fails with YAML scanner errors:

**Error**: `found a tab character that violates indentation`

**Cause**: One or more markdown files have invalid YAML frontmatter (tab characters or syntax errors)

**Solution**:

1. Check the error message for the file path
2. Open the problematic markdown file
3. Fix the YAML frontmatter (use spaces, not tabs)
4. Ensure proper YAML syntax (quote special characters)
5. Retry building the index

### Port Already in Use

If you see `Address already in use` errors:

```bash
# Kill process on port 8000 (API)
lsof -ti:8000 | xargs kill -9

# Kill process on port 5173 (Frontend)
lsof -ti:5173 | xargs kill -9
```

### Wrong Directory

Make sure you're in the `visualization` directory when running npm commands:

```bash
cd /path/to/PrismWeave/visualization
npm run dev:all
```

## More Information

See [visualization/DEV_GUIDE.md](visualization/DEV_GUIDE.md) for detailed documentation.
