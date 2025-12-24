# PrismWeave Visualization Layer - Quick Start

## Launch the Application (Recommended)

Use Docker Compose from the repo root to start both the API and the visualization frontend:

```bash
docker-compose up -d --build
```

Then open:

- Frontend: **http://localhost:3001**
- API docs: **http://localhost:8000/docs**

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
   - If you’re using Docker Compose: `docker-compose up -d --build`
   - If you’re running manually: see below

## All Available Commands

**Important**: Run frontend commands from the `visualization` directory.

| Command              | Description                     |
| -------------------- | ------------------------------- |
| `npm run dev`        | Run the Vue frontend dev server |
| `npm run build`      | Build for production            |
| `npm run preview`    | Preview production build        |
| `npm run type-check` | TypeScript type checking        |

## Ports

- **Frontend**: http://localhost:3001
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs (Swagger UI)

## Stopping Services

If you used Docker Compose:

```bash
docker-compose down
```

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

# Kill process on port 3001 (Frontend)
lsof -ti:3001 | xargs kill -9
```

### Wrong Directory

Make sure you're in the `visualization` directory when running npm commands:

```bash
cd /path/to/PrismWeave/visualization
npm run dev
```

## More Information

See [visualization/DEV_GUIDE.md](visualization/DEV_GUIDE.md) for detailed documentation.
