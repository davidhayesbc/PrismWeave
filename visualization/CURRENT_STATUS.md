# Current Status - PrismWeave Visualization

## ✅ What's Working

- **Frontend configured** - Vue app calls the API via `/api/*`
- **Services can run together** - Use Docker Compose (recommended) or run backend manually
- **Ports** - API on 8000, frontend on 3001
- **Dependencies installed** - All Python and Node.js dependencies are in place
- **API endpoints functional** - FastAPI server is responding correctly

## ⚠️ Current Issue: 404 Errors

### Problem

The frontend is getting 404 errors when calling `/articles` endpoint:

```
INFO: 127.0.0.1:47924 - "GET /articles HTTP/1.1" 404 Not Found
```

### Root Cause

The visualization index hasn't been built yet. The API is responding correctly with:

```json
{
  "detail": "Article index not found. Run 'visualize build-index' first."
}
```

### Solution

You need to build the visualization index. There are two methods:

#### Method 1: Via API (Recommended)

With the services running (which they are now):

```bash
curl -X POST http://localhost:8000/visualization/rebuild
```

#### Method 2: Via CLI

```bash
cd ai-processing
source .venv/bin/activate
python cli.py visualize build-index --verbose
```

### Known Sub-Issue

There's a YAML parsing error in one of your markdown files:

```
found a tab character that violates indentation
  in "<unicode string>", line 57, column 5
```

**You need to**:

1. Find the markdown file with the YAML error
2. Fix the YAML frontmatter (replace tabs with spaces, fix syntax)
3. Then run the index build command

## 🚀 How to Start Development

### Option A (Recommended): Docker Compose

From the repo root:

```bash
docker-compose up -d --build
```

Open:

- Frontend: `http://localhost:3001`
- API docs: `http://localhost:8000/docs`

### Option B: Run backend manually

```bash
cd ai-processing
uv sync
uv run python -m uvicorn src.api.app:app --reload --host 0.0.0.0 --port 8000
```

Then in another terminal:

```bash
cd visualization
npm install
npm run dev
```

## 📝 Next Steps

1. **Fix YAML errors** in markdown files (check documents in `/home/dhayes/Source/PrismWeaveDocs/documents/`)
2. **Build the index** using one of the methods above
3. **Refresh the browser** - The frontend should then load articles

## 📚 Documentation

- **Quick Reference**: `/home/dhayes/Source/PrismWeave/VISUALIZATION_QUICKSTART.md`
- **Full Guide**: `/home/dhayes/Source/PrismWeave/visualization/DEV_GUIDE.md`

## 🔧 Useful Commands

```bash
# Check what's running on ports
lsof -i:8000  # API
lsof -i:3001  # Frontend

# Kill if needed
lsof -ti:8000 | xargs kill -9
lsof -ti:3001 | xargs kill -9

# Test API directly
curl http://localhost:8000/
curl http://localhost:8000/articles

# Rebuild index via API
curl -X POST http://localhost:8000/visualization/rebuild

# View API docs
# Open http://localhost:8000/docs in browser
```

## Current Terminal Session

(If you used Docker Compose) stop with:

```bash
docker-compose down
```
