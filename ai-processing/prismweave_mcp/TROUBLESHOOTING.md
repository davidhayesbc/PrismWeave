# PrismWeave MCP Server - Troubleshooting Guide

**Common issues, solutions, and debugging tips for the PrismWeave MCP server**

---

## Table of Contents

- [Installation Issues](#installation-issues)
- [Server Startup Problems](#server-startup-problems)
- [Connection Issues](#connection-issues)
- [Search and Retrieval Issues](#search-and-retrieval-issues)
- [Document Creation Issues](#document-creation-issues)
- [AI Processing Issues](#ai-processing-issues)
- [Git Integration Issues](#git-integration-issues)
- [Performance Issues](#performance-issues)
- [Debugging Tips](#debugging-tips)
- [FAQ](#faq)

---

## Installation Issues

### Problem: `uv: command not found`

**Symptoms**: Cannot install dependencies with UV package manager

**Solution**:

```bash
# Install UV package manager
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or use pip
pip install uv

# Verify installation
uv --version
```

---

### Problem: `ModuleNotFoundError: No module named 'prismweave_mcp'`

**Symptoms**: Cannot import prismweave_mcp module

**Solution**:

```bash
# Ensure you're in the correct directory
cd /home/dhayes/Source/PrismWeave/ai-processing

# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Install/reinstall dependencies
uv sync

# Verify installation
python -c "from prismweave_mcp import server; print('OK')"
```

---

### Problem: Python Version Mismatch

**Symptoms**: `requires-python = ">=3.10"` error

**Solution**:

```bash
# Check current Python version
python --version

# If < 3.10, install newer Python
# Ubuntu/Debian:
sudo apt install python3.12

# macOS (with Homebrew):
brew install python@3.12

# Create venv with specific Python version
python3.12 -m venv .venv
source .venv/bin/activate
uv sync
```

---

## Server Startup Problems

### Problem: Server Won't Start

**Symptoms**:

- No error message when running server
- FastMCP import fails
- Server starts but doesn't respond

**Diagnosis**:

```bash
# Check if server module loads
python -c "from prismweave_mcp import server"

# Check FastMCP installation
python -c "import fastmcp; print(fastmcp.__version__)"

# Verbose startup for error details
python -m prismweave_mcp.server --verbose
```

**Solutions**:

1. **Missing dependencies**:

   ```bash
   uv sync
   ```

2. **Import errors**:

   ```bash
   # Check for namespace collisions
   python -c "import sys; print([p for p in sys.path if 'mcp' in p])"

   # Ensure prismweave_mcp directory exists (not mcp)
   ls -la prismweave_mcp/
   ```

3. **Configuration errors**:
   ```bash
   # Validate config file
   python -c "from prismweave_mcp.utils.config_manager import load_config; config = load_config(); print('Config OK')"
   ```

---

### Problem: `Config validation failed`

**Symptoms**: Server exits with config validation errors

**Solution**:

```bash
# Check config.yaml syntax
python -c "import yaml; yaml.safe_load(open('config.yaml'))"

# Verify required sections exist
grep -E "^(ollama|mcp|vector):" config.yaml

# Use default config template
cp config.yaml.example config.yaml  # If available

# Or create minimal config
cat > config.yaml << 'EOF'
ollama:
  host: http://localhost:11434
  models:
    embedding: nomic-embed-text

mcp:
  paths:
    documents_root: ../../PrismWeaveDocs

vector:
  collection_name: documents
  persist_directory: ../../PrismWeaveDocs/.prismweave/chroma_db
EOF
```

---

## Connection Issues

### Problem: `Cannot connect to Ollama`

**Symptoms**:

- `ConnectionError: Cannot reach http://localhost:11434`
- AI processing fails
- Embedding generation times out

**Diagnosis**:

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Check Ollama service status
systemctl status ollama  # Linux with systemd
ps aux | grep ollama     # General Linux/Mac
```

**Solutions**:

1. **Start Ollama**:

   ```bash
   # Start Ollama server
   ollama serve

   # Or as background service
   nohup ollama serve > /tmp/ollama.log 2>&1 &
   ```

2. **Check Ollama models**:

   ```bash
   # List installed models
   ollama list

   # Pull required models if missing
   ollama pull nomic-embed-text
   ollama pull phi3:mini
   ollama pull llama3.1:8b
   ```

3. **Verify Ollama connectivity**:

   ```bash
   # Test API endpoint
   curl http://localhost:11434/api/tags | jq

   # Test embedding generation
   curl http://localhost:11434/api/embeddings -d '{
     "model": "nomic-embed-text",
     "prompt": "test"
   }' | jq
   ```

---

### Problem: `ChromaDB connection failed`

**Symptoms**:

- `Collection 'documents' not found`
- Search returns no results
- Embedding storage fails

**Diagnosis**:

```bash
# Check if ChromaDB directory exists
ls -la ../../PrismWeaveDocs/.prismweave/chroma_db/

# Test ChromaDB connection
python -c "
import chromadb
client = chromadb.PersistentClient(path='../../PrismWeaveDocs/.prismweave/chroma_db')
print(client.list_collections())
"
```

**Solutions**:

1. **Initialize ChromaDB**:

   ```bash
   # Create database directory
   mkdir -p ../../PrismWeaveDocs/.prismweave/chroma_db

   # Initialize with Python
   python << 'EOF'
   import chromadb
   from chromadb.config import Settings

   client = chromadb.PersistentClient(
       path="../../PrismWeaveDocs/.prismweave/chroma_db"
   )

   # Create collection
   collection = client.get_or_create_collection(
       name="documents",
       metadata={"description": "PrismWeave document embeddings"}
   )
   print(f"Collection created: {collection.name}")
   EOF
   ```

2. **Reset ChromaDB** (if corrupted):

   ```bash
   # Backup existing database
   mv ../../PrismWeaveDocs/.prismweave/chroma_db ../../PrismWeaveDocs/.prismweave/chroma_db.backup

   # Reinitialize
   python cli/prismweave.py vector-init
   ```

---

## Search and Retrieval Issues

### Problem: Search Returns No Results

**Symptoms**:

- `search_documents` returns `total: 0`
- Known documents not found
- All queries return empty results

**Diagnosis**:

```bash
# Check if documents exist
ls -la ../../PrismWeaveDocs/documents/

# Check ChromaDB collection count
python -c "
import chromadb
client = chromadb.PersistentClient(path='../../PrismWeaveDocs/.prismweave/chroma_db')
collection = client.get_collection('documents')
print(f'Documents in ChromaDB: {collection.count()}')
"

# Test search directly
python -c "
from prismweave_mcp.managers.search_manager import SearchManager
from prismweave_mcp.utils.config_manager import load_config
import asyncio

async def test():
    config = load_config()
    mgr = SearchManager(config)
    await mgr.initialize()
    results = await mgr.search_documents(query='test', max_results=10)
    print(f'Found: {len(results)} results')

asyncio.run(test())
"
```

**Solutions**:

1. **Generate embeddings for documents**:

   ```bash
   # Process all documents
   python cli/prismweave.py process --all

   # Or specific document
   python cli/prismweave.py process documents/2025-01-15-example.md
   ```

2. **Lower similarity threshold**:

   ```yaml
   # In config.yaml
   mcp:
     search:
       similarity_threshold: 0.3 # Lower from 0.6
   ```

3. **Check embedding model**:

   ```bash
   # Verify embedding model is available
   ollama list | grep nomic-embed-text

   # Pull if missing
   ollama pull nomic-embed-text
   ```

---

### Problem: `Document not found` Error

**Symptoms**:

- `get_document` fails with document_id
- `FileNotFoundError` for valid paths

**Diagnosis**:

```bash
# List all document IDs
python -c "
from prismweave_mcp.managers.document_manager import DocumentManager
from prismweave_mcp.utils.config_manager import load_config
import asyncio

async def test():
    config = load_config()
    mgr = DocumentManager(config)
    docs = await mgr.list_documents(limit=10)
    for doc in docs:
        print(f'{doc[\"document_id\"]}: {doc[\"path\"]}')

asyncio.run(test())
"

# Check file permissions
ls -la ../../PrismWeaveDocs/documents/
```

**Solutions**:

1. **Use correct path format**:

   ```json
   {
     "document_path": "documents/2025-01-15-example.md"
     // NOT: /home/dhayes/Source/PrismWeaveDocs/documents/...
     // NOT: 2025-01-15-example.md
   }
   ```

2. **Verify file exists**:
   ```bash
   # From PrismWeaveDocs root
   cd ../../PrismWeaveDocs
   find . -name "*.md" -type f
   ```

---

## Document Creation Issues

### Problem: `Cannot create document in non-generated folder`

**Symptoms**:

- `create_document` fails with permission error
- Error: "Documents can only be created in generated/ folder"

**Solution**:

```bash
# Ensure generated/ folder exists
mkdir -p ../../PrismWeaveDocs/generated

# Verify permissions
ls -la ../../PrismWeaveDocs/generated

# Create document (will be placed in generated/ automatically)
# No need to specify path - it's auto-generated
```

---

### Problem: `Filename conflict` Error

**Symptoms**:

- Document creation fails
- Error: "File already exists"

**Diagnosis**:

```bash
# Check existing files
ls -la ../../PrismWeaveDocs/generated/

# Check for slug conflicts
ls ../../PrismWeaveDocs/generated/ | grep "$(echo 'My Title' | tr '[:upper:]' '[:lower:]' | tr ' ' '-')"
```

**Solutions**:

1. **Use different title**:

   ```json
   {
     "title": "My Article - Version 2", // Avoid duplicate slugs
     "content": "..."
   }
   ```

2. **Update existing document instead**:
   ```json
   {
     "document_path": "generated/2025-01-15-my-article.md",
     "content": "Updated content..."
   }
   ```

---

## AI Processing Issues

### Problem: `Tag generation failed`

**Symptoms**:

- `generate_tags` times out
- Returns generic tags
- Ollama errors in logs

**Diagnosis**:

```bash
# Test Ollama directly
curl http://localhost:11434/api/generate -d '{
  "model": "phi3:mini",
  "prompt": "Generate 5 relevant tags for: Machine learning article",
  "stream": false
}'

# Check Ollama logs
journalctl -u ollama -f  # If using systemd
tail -f /tmp/ollama.log  # If running manually
```

**Solutions**:

1. **Increase timeout**:

   ```yaml
   # In config.yaml
   ollama:
     timeout: 120 # Increase from 60

   processing:
     tagging_timeout: 180
   ```

2. **Use smaller model**:

   ```yaml
   # In config.yaml
   ollama:
     models:
       medium: 'phi3:mini' # Faster than llama3.1:8b
   ```

3. **Check model availability**:
   ```bash
   ollama pull phi3:mini
   ```

---

### Problem: `Embedding generation timeout`

**Symptoms**:

- `generate_embeddings` hangs
- Long processing times
- High memory usage

**Diagnosis**:

```bash
# Monitor Ollama resource usage
top -p $(pgrep ollama)

# Test embedding generation speed
time curl http://localhost:11434/api/embeddings -d '{
  "model": "nomic-embed-text",
  "prompt": "Test content for embedding"
}'
```

**Solutions**:

1. **Process in smaller chunks**:

   ```yaml
   # In config.yaml
   processing:
     chunk_size: 1500 # Reduce from 3000
     max_concurrent: 1 # Process one at a time
   ```

2. **Check NPU/GPU acceleration**:

   ```bash
   # For AI HX 370 NPU
   ollama run nomic-embed-text --verbose

   # Check if NPU is detected
   dmesg | grep -i npu
   ```

3. **Increase timeout**:
   ```yaml
   ollama:
     timeout: 180 # For large documents
   ```

---

## Git Integration Issues

### Problem: `Git commit failed`

**Symptoms**:

- `commit_to_git` returns error
- Permission denied
- Git not initialized

**Diagnosis**:

```bash
# Check git repository status
cd ../../PrismWeaveDocs
git status

# Check git configuration
git config user.name
git config user.email

# Check for uncommitted changes
git diff --stat
```

**Solutions**:

1. **Initialize git if needed**:

   ```bash
   cd ../../PrismWeaveDocs
   git init
   git remote add origin <your-repo-url>
   ```

2. **Configure git user**:

   ```bash
   git config user.name "Your Name"
   git config user.email "your.email@example.com"
   ```

3. **Check permissions**:
   ```bash
   ls -la .git/
   chmod -R u+rw .git/
   ```

---

### Problem: `Push failed - authentication required`

**Symptoms**:

- Commit succeeds but push fails
- Authentication errors

**Solutions**:

1. **Setup SSH keys**:

   ```bash
   ssh-keygen -t ed25519 -C "your.email@example.com"
   cat ~/.ssh/id_ed25519.pub  # Add to GitHub

   # Test SSH connection
   ssh -T git@github.com
   ```

2. **Use HTTPS with token**:

   ```bash
   # Configure credential helper
   git config credential.helper store

   # Or use GitHub CLI
   gh auth login
   ```

3. **Disable auto-push**:
   ```yaml
   # In config.yaml
   mcp:
     git:
       auto_push: false # Manual push only
   ```

---

## Performance Issues

### Problem: Slow Search Performance

**Symptoms**:

- Search takes >2 seconds
- High CPU usage during search
- Memory consumption increases

**Diagnosis**:

```bash
# Profile search performance
python -c "
import time
from prismweave_mcp.managers.search_manager import SearchManager
from prismweave_mcp.utils.config_manager import load_config
import asyncio

async def test():
    config = load_config()
    mgr = SearchManager(config)
    await mgr.initialize()

    start = time.time()
    results = await mgr.search_documents(query='test', max_results=20)
    elapsed = time.time() - start

    print(f'Search time: {elapsed:.2f}s')
    print(f'Results: {len(results)}')

asyncio.run(test())
"
```

**Solutions**:

1. **Optimize ChromaDB settings**:

   ```yaml
   vector:
     max_results: 10 # Reduce from 20
     similarity_threshold: 0.7 # Increase from 0.6 (fewer results)
   ```

2. **Add caching** (future enhancement):

   ```python
   # In search_manager.py
   from functools import lru_cache

   @lru_cache(maxsize=100)
   async def search_documents_cached(query, max_results):
       # Implementation
   ```

3. **Monitor ChromaDB size**:

   ```bash
   du -sh ../../PrismWeaveDocs/.prismweave/chroma_db/

   # Consider cleaning up old embeddings
   python cli/prismweave.py vector-cleanup
   ```

---

### Problem: High Memory Usage

**Symptoms**:

- Server process uses >2GB RAM
- Out of memory errors
- System becomes slow

**Solutions**:

1. **Limit concurrent operations**:

   ```yaml
   processing:
     max_concurrent: 1 # Process one document at a time
   ```

2. **Monitor memory usage**:

   ```bash
   # Check Python process memory
   ps aux | grep python | grep prismweave_mcp

   # Use memory profiler
   pip install memory-profiler
   python -m memory_profiler prismweave_mcp/server.py
   ```

3. **Restart server periodically**:
   ```bash
   # Add to cron or systemd timer
   */6 * * * * systemctl restart prismweave-mcp
   ```

---

## Debugging Tips

### Enable Verbose Logging

```python
# In server.py or tool files
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.debug("Detailed debug message")
```

### Test Individual Components

```bash
# Test document manager
python -c "
from prismweave_mcp.managers.document_manager import DocumentManager
from prismweave_mcp.utils.config_manager import load_config
import asyncio

async def test():
    config = load_config()
    mgr = DocumentManager(config)
    docs = await mgr.list_documents(limit=5)
    print(docs)

asyncio.run(test())
"

# Test search manager
python -c "
from prismweave_mcp.managers.search_manager import SearchManager
from prismweave_mcp.utils.config_manager import load_config
import asyncio

async def test():
    config = load_config()
    mgr = SearchManager(config)
    await mgr.initialize()
    results = await mgr.search_documents('test', max_results=5)
    print(f'Found {len(results)} results')

asyncio.run(test())
"
```

### Check MCP Protocol Communication

```bash
# Test MCP server with FastMCP dev client
fastmcp dev prismweave_mcp.server

# Or use MCP Inspector
npx @modelcontextprotocol/inspector python -m prismweave_mcp.server
```

### Trace Function Calls

```python
# Add to functions for tracing
import functools
import time

def trace(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.time()
        print(f"Calling {func.__name__}")
        result = await func(*args, **kwargs)
        elapsed = time.time() - start
        print(f"{func.__name__} took {elapsed:.2f}s")
        return result
    return wrapper

# Usage
@trace
async def search_documents(...):
    # Implementation
```

---

## FAQ

### Q: Can I use a different embedding model?

**A**: Yes, configure in `config.yaml`:

```yaml
ollama:
  models:
    embedding: 'your-model-name'
```

Ensure model is pulled: `ollama pull your-model-name`

---

### Q: How do I backup my ChromaDB data?

**A**: Simply copy the database directory:

```bash
cp -r ../../PrismWeaveDocs/.prismweave/chroma_db ../../PrismWeaveDocs/.prismweave/chroma_db.backup.$(date +%Y%m%d)
```

---

### Q: Can I run the MCP server on a different machine?

**A**: Yes, but you'll need to configure network access:

1. Update Ollama host in config.yaml
2. Ensure ChromaDB is accessible (consider network share or sync)
3. Ensure git repository is accessible

---

### Q: How do I reset everything?

**A**: Complete reset procedure:

```bash
# 1. Backup important data
cp -r ../../PrismWeaveDocs ../../PrismWeaveDocs.backup

# 2. Remove virtual environment
rm -rf .venv

# 3. Recreate environment
python3.12 -m venv .venv
source .venv/bin/activate
uv sync

# 4. Reset ChromaDB
rm -rf ../../PrismWeaveDocs/.prismweave/chroma_db
python cli/prismweave.py vector-init

# 5. Test server
python -m prismweave_mcp.server
```

---

### Q: Error logs are too verbose, how do I reduce them?

**A**: Configure logging level:

```yaml
# In config.yaml
log_level: 'WARNING' # Or 'ERROR', 'INFO'
```

Or set environment variable:

```bash
export PRISMWEAVE_LOG_LEVEL=WARNING
```

---

### Q: Can I use the MCP server without VS Code?

**A**: Yes! The MCP server can be used with:

- Any MCP-compatible client
- Direct Python API calls
- FastMCP development client
- HTTP API (future enhancement)

---

## Getting Help

If you're still experiencing issues:

1. **Check Implementation Status**: [IMPLEMENTATION_STATUS.md](./IMPLEMENTATION_STATUS.md)
2. **Review Documentation**: [README.md](./README.md)
3. **Search Issues**: [GitHub Issues](https://github.com/davidhayesbc/PrismWeave/issues)
4. **Create New Issue**: Include:
   - Error messages (full stack trace)
   - Configuration (sanitized)
   - Steps to reproduce
   - System information (OS, Python version, etc.)

---

**Last Updated**: November 11, 2025  
**Version**: 1.0.0
