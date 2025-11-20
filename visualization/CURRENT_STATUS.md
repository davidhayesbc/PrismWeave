# Current Status - PrismWeave Visualization

## ✅ What's Working

- **npm scripts configured** - Both API and frontend can be launched together
- **Services running** - Both API (port 8000) and frontend (port 5173) are operational
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

From the `visualization` directory:

```bash
npm run dev:all
```

This launches both services with colored output:

- **[API]** - Blue text - API server on port 8000
- **[Frontend]** - Green text - Frontend on port 5173

Stop with `Ctrl+C`.

## 📝 Next Steps

1. **Fix YAML errors** in markdown files (check documents in `/home/dhayes/Source/PrismWeaveDocs/documents/`)
2. **Build the index** using one of the methods above
3. **Refresh the browser** - The frontend should then load articles

## 📚 Documentation

- **Quick Reference**: `/home/dhayes/Source/PrismWeave/VISUALIZATION_QUICKSTART.md`
- **Full Guide**: `/home/dhayes/Source/PrismWeave/visualization/DEV_GUIDE.md`

Both documents have been updated with:

- Correct commands (`npm run dev:all` instead of `npm start`)
- Troubleshooting for 404 errors
- YAML parsing error solutions
- Index building procedures

## 🔧 Useful Commands

```bash
# Check what's running on ports
lsof -i:8000  # API
lsof -i:5173  # Frontend

# Kill if needed
lsof -ti:8000 | xargs kill -9
lsof -ti:5173 | xargs kill -9

# Test API directly
curl http://localhost:8000/
curl http://localhost:8000/articles

# Rebuild index via API
curl -X POST http://localhost:8000/visualization/rebuild

# View API docs
# Open http://localhost:8000/docs in browser
```

## Current Terminal Session

Services are currently running in background (terminal ID: a6ac0753-1b8a-478c-9b77-043c0e792f23).

You can stop them with:

```bash
pkill -f "concurrently"
```

Or press Ctrl+C if they're in foreground.
