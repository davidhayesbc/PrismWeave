# PrismWeave AI Processing - Usage Examples

**Real-world scenarios and workflows for document processing**

This guide provides practical examples of using the PrismWeave AI Processing module in common scenarios.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Processing Tech Documentation](#processing-tech-documentation)
3. [Incremental Sync Workflows](#incremental-sync-workflows)
4. [Searching Documents](#searching-documents)
5. [Managing Collections](#managing-collections)
6. [Integration Patterns](#integration-patterns)
7. [Troubleshooting](#troubleshooting)

---

## Quick Start

### First Time Setup

```bash
# 1. Install Ollama
# Download from: https://ollama.com

# 2. Pull the embedding model
ollama pull nomic-embed-text

# 3. Start Ollama server
ollama serve

# 4. Install dependencies
cd ai-processing
uv sync
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows

# 5. Process your first document
python cli.py process README.md --verbose

# 6. Verify it worked
python cli.py list
```

**Expected Output:**

```
🔮 PrismWeave Document Processor
========================================
🔍 Checking Ollama availability...
✅ Ollama is running

📄 Processing single file: README.md
🔮 Processing: README.md
🤖 Using model: nomic-embed-text
💾 Storage: ../../PrismWeaveDocs/.prismweave/chroma_db

📄 Loading and processing document...
✅ Generated 3 chunks
🔗 Generating and storing embeddings...
✅ Processed README.md (3 chunks)

✅ Processing completed successfully!
```

---

## Processing Tech Documentation

### Scenario: You've Downloaded Technical Documentation

You have a folder of technical documentation (MDX/Markdown files) from various sources and want to make them searchable.

```bash
# Process the entire tech docs folder
python cli.py process ~/Documents/tech-docs --verify

# Example output:
# 📂 Processing directory: /home/user/Documents/tech-docs
# ✅ Successfully processed: 47 files
# 🔍 Verifying embeddings storage...
# ✅ Verification result: {'document_count': 47, 'chunk_count': 312}
```

### With Verbose Output

```bash
python cli.py process ~/Documents/tech-docs/react-hooks.md --verbose
```

**Expected Output:**

```
🔮 Processing: react-hooks.md
🤖 Using model: nomic-embed-text
💾 Storage: ../../PrismWeaveDocs/.prismweave/chroma_db

📄 Loading and processing document...
✅ Generated 8 chunks
🔗 Generating and storing embeddings...
🔍 Verifying embeddings storage...
✅ Verification result: {
    'collection_name': 'documents',
    'persist_directory': '../../PrismWeaveDocs/.prismweave/chroma_db',
    'document_count': 1,
    'chunk_count': 8
}

📊 Sample chunk metadata:
  Chunk 1:
    Content preview: # React Hooks\n\nHooks are functions that let you use state and other React features...
    Metadata keys: ['source', 'chunk_index', 'total_chunks', 'source_file', 'tags', 'title']
    Tags: ['react', 'hooks', 'frontend']

✅ Processed react-hooks.md (8 chunks)
```

### Processing Mixed Document Types

```bash
# Process a folder with PDFs, DOCX, and Markdown
python cli.py process ~/Documents/mixed-docs

# Supported formats are automatically detected:
# - .md (Markdown with frontmatter)
# - .pdf (PDF documents)
# - .docx (Word documents)
# - .html/.htm (HTML files)
# - .txt (Plain text)
```

---

## Incremental Sync Workflows

### Scenario: Working with a Git Repository of Documents

You have a git repository (like PrismWeaveDocs) that gets updated regularly. You want to only process new or changed files.

#### Initial Processing

```bash
# First time: process everything
python cli.py sync ~/PrismWeaveDocs --verbose
```

**Expected Output:**

```
🔮 PrismWeave Document Sync
========================================
📂 Repository: /home/user/PrismWeaveDocs
🔍 Checking Ollama availability...
✅ Ollama is running
🔄 Starting sync (mode: incremental)

📂 Incremental mode: Found 127 unprocessed files
✅ Successfully processed: 127 files

📊 Processing Summary:
   ✅ Successfully processed: 127 files
   🔄 Updated processing state

✅ Sync completed successfully!
```

#### Subsequent Updates (Only Changed Files)

```bash
# After making changes and committing
git pull origin main  # Get latest changes
python cli.py sync ~/PrismWeaveDocs
```

**Expected Output:**

```
🔮 PrismWeave Document Sync
========================================
📂 Repository: /home/user/PrismWeaveDocs
🔄 Starting sync (mode: incremental)

📂 Incremental mode: Found 3 unprocessed files
✅ Successfully processed: 3 files

📊 Processing Summary:
   ✅ Successfully processed: 3 files

✅ Sync completed successfully!
```

#### Force Re-processing Everything

```bash
# Sometimes you want to reprocess everything (config changes, etc.)
python cli.py sync ~/PrismWeaveDocs --force
```

**Expected Output:**

```
🔮 PrismWeave Document Sync
========================================
📂 Repository: /home/user/PrismWeaveDocs
🔄 Starting sync (mode: force)

📂 Processing in force mode: Found 127 files
✅ Successfully processed: 127 files

📊 Processing Summary:
   ✅ Successfully processed: 127 files
   🔄 Updated processing state

✅ Sync completed successfully!
```

---

## Searching Documents

### Using Python API for Semantic Search

```python
from pathlib import Path
from src.core.config import Config
from src.core.embedding_store import EmbeddingStore

# Initialize
config = Config.from_file(Path("config.yaml"))
store = EmbeddingStore(config)

# Search for relevant documents
results = store.search_similar(
    query="How do React hooks work?",
    k=5  # Return top 5 results
)

# Display results
for i, doc in enumerate(results, 1):
    print(f"\n{i}. {doc.metadata.get('title', 'Untitled')}")
    print(f"   Source: {doc.metadata.get('source_file')}")
    print(f"   Tags: {doc.metadata.get('tags', [])}")
    print(f"   Content preview: {doc.page_content[:200]}...")
    if 'chunk_index' in doc.metadata:
        chunk_info = f"{doc.metadata['chunk_index'] + 1}/{doc.metadata['total_chunks']}"
        print(f"   Chunk: {chunk_info}")
```

**Expected Output:**

````
1. React Hooks Guide
   Source: /home/user/docs/react-hooks.md
   Tags: ['react', 'hooks', 'frontend']
   Content preview: # React Hooks\n\nHooks are functions that let you use state and other React features without writing a class. They were introduced in React 16.8...
   Chunk: 1/8

2. useState Hook Documentation
   Source: /home/user/docs/react-hooks.md
   Tags: ['react', 'hooks', 'frontend']
   Content preview: ## useState Hook\n\nThe useState Hook lets you add state to functional components. Here's how it works:\n\n```jsx\nconst [count, setCount] = useState(0);\n```...
   Chunk: 3/8

3. Custom Hooks Pattern
   Source: /home/user/docs/advanced-react.md
   Tags: ['react', 'patterns', 'hooks']
   Content preview: ## Building Custom Hooks\n\nCustom Hooks are a mechanism to reuse stateful logic. They follow the naming convention of starting with "use"...
   Chunk: 12/15
````

---

## Managing Collections

### Listing Documents

#### Compact View (Default)

```bash
python cli.py list --max 10
```

**Expected Output:**

```
🔮 PrismWeave Document List
========================================
📄 Source files in collection (max: 10):

     1. react-hooks.md
        📄 Chunks: 8
        🏷️  Tags: react, hooks, frontend
        📏 Total content: 12,456 characters

     2. vue-composition-api.md
        📄 Chunks: 6
        🏷️  Tags: vue, composition, frontend
        📏 Total content: 9,234 characters

     3. python-best-practices.md
        📄 Chunks: 12
        🏷️  Tags: python, best-practices, backend
        📏 Total content: 18,901 characters

📊 Summary: 10 files shown
   (Total in collection: 127 files, 892 chunks)
```

#### Detailed View

```bash
python cli.py list --max 5 --verbose
```

**Expected Output:**

```
🔮 PrismWeave Document List
========================================
📄 Document chunks in collection (max: 5):

     1. Chunk ID: abc123...
        📁 File: react-hooks.md
        🔢 Chunk: 1/8
        📄 Length: 1547 characters
        🏷️  Tags: react, hooks, frontend
        📝 Preview: # React Hooks\n\nHooks are functions that let you...

     2. Chunk ID: def456...
        📁 File: react-hooks.md
        🔢 Chunk: 2/8
        📄 Length: 1823 characters
        🏷️  Tags: react, hooks, frontend
        📝 Preview: ## useState Hook\n\nThe useState Hook lets you add...

📊 Showing 5 chunks
   (Total in collection: 892 chunks)
```

#### Show Unique Source Files Only

```bash
python cli.py list --source-files --max 20
```

**Expected Output:**

```
🔮 PrismWeave Document List
========================================
📂 Unique source files in collection:
     1. react-hooks.md
     2. vue-composition-api.md
     3. python-best-practices.md
     4. docker-guide.md
     5. kubernetes-intro.md
    ...
    20. typescript-advanced.md

📊 Showing 20 of 127 unique source files
```

### Document Statistics

```bash
python cli.py count
```

**Expected Output:**

```
🔮 PrismWeave Document Count
========================================
📊 Collection Statistics:
   📄 Total document chunks: 892
   📁 Unique source files: 127
   📈 Average chunks per file: 7.0
   🗄️  Collection name: documents
   💾 Storage path: ../../PrismWeaveDocs/.prismweave/chroma_db
```

---

## Integration Patterns

### Browser Extension Integration

When the browser extension captures a web page:

```python
from pathlib import Path
from src.core import DocumentProcessor, EmbeddingStore, Config

def process_browser_capture(markdown_content: str, url: str, title: str):
    """Process markdown captured by browser extension"""

    # Save to temporary file (or use in-memory processing)
    temp_file = Path(f"/tmp/capture_{hash(url)}.md")

    # Add frontmatter for metadata
    content = f"""---
title: {title}
source_url: {url}
captured_at: {datetime.now().isoformat()}
tags: [web-capture]
---

{markdown_content}
"""
    temp_file.write_text(content)

    # Process the document
    config = Config()
    processor = DocumentProcessor(config)
    store = EmbeddingStore(config)

    chunks = processor.process_document(temp_file)
    store.add_document(temp_file, chunks)

    # Clean up
    temp_file.unlink()

    return {
        "success": True,
        "document_id": str(hash(url)),
        "chunk_count": len(chunks)
    }
```

### Scheduled Processing

```bash
#!/bin/bash
# scheduled-sync.sh - Run via cron for automatic updates

# Navigate to repository
cd ~/PrismWeaveDocs

# Pull latest changes
git pull origin main

# Process new/changed documents
cd ~/Source/PrismWeave/ai-processing
source .venv/bin/activate
python cli.py sync ~/PrismWeaveDocs

# Optional: Send notification
if [ $? -eq 0 ]; then
    echo "PrismWeave sync completed successfully" | notify-send "PrismWeave"
fi
```

**Cron Entry:**

```cron
# Run every 2 hours
0 */2 * * * /home/user/scripts/scheduled-sync.sh >> /var/log/prismweave-sync.log 2>&1
```

### VS Code Extension Query

```python
def search_documents_for_vscode(query: str, max_results: int = 10):
    """Search interface for VS Code extension"""

    config = Config()
    store = EmbeddingStore(config)

    results = store.search_similar(query, k=max_results)

    # Format for VS Code display
    formatted_results = []
    for doc in results:
        formatted_results.append({
            "title": doc.metadata.get("title", "Untitled"),
            "source": doc.metadata.get("source_file"),
            "preview": doc.page_content[:200],
            "tags": doc.metadata.get("tags", []),
            "chunk_info": f"{doc.metadata.get('chunk_index', 0) + 1}/{doc.metadata.get('total_chunks', 1)}"
        })

    return formatted_results
```

---

## Troubleshooting

### Ollama Not Running

**Symptom:**

```
❌ Cannot connect to Ollama at http://localhost:11434
```

**Solution:**

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama
ollama serve

# Pull the model if missing
ollama list
ollama pull nomic-embed-text
```

### Model Not Found

**Symptom:**

```
❌ Model nomic-embed-text not found
```

**Solution:**

```bash
# Pull the embedding model
ollama pull nomic-embed-text

# Verify it's available
ollama list
```

### Git Repository Not Detected

**Symptom:**

```
❌ No git repository found.
```

**Solution:**

```bash
# Initialize git in your documents folder if needed
cd ~/Documents
git init
git add .
git commit -m "Initial commit"

# Or specify the repository path explicitly
python cli.py sync /path/to/your/git-repo
```

### Memory Issues

**Symptom:**

```
❌ OutOfMemoryError during processing
```

**Solution:**

Edit `config.yaml`:

```yaml
processing:
  chunk_size: 500 # Reduce from 1000
  chunk_overlap: 100 # Reduce from 200
```

### ChromaDB Corruption

**Symptom:**

```
❌ ChromaDB error: Collection not found or corrupted
```

**Solution:**

```bash
# Clear the collection and reprocess
python cli.py process /path/to/docs --clear --force
```

### Permission Errors

**Symptom:**

```
❌ PermissionError: Cannot write to chroma_db directory
```

**Solution:**

```bash
# Check directory permissions
ls -la ~/.prismweave/

# Fix permissions
chmod -R 755 ~/.prismweave/

# Or change the storage location in config.yaml
vector:
  persist_directory: '/tmp/prismweave_db'  # Temporary location
```

---

## Best Practices

### 1. Regular Incremental Syncs

Set up automated syncs for document repositories:

```bash
# Daily sync via cron
0 9 * * * cd ~/Source/PrismWeave/ai-processing && python cli.py sync ~/PrismWeaveDocs
```

### 2. Use Verbose Mode for Debugging

When troubleshooting, always use `--verbose`:

```bash
python cli.py process document.md --verbose
```

### 3. Verify After Major Changes

After configuration changes or updates, verify the collection:

```bash
python cli.py process /path/to/docs --clear --verify
```

### 4. Monitor Collection Size

Regularly check collection statistics:

```bash
python cli.py count
python cli.py list --source-files | wc -l
```

### 5. Tag Documents Properly

Use frontmatter for better searchability:

```markdown
---
title: React Hooks Guide
tags: [react, hooks, frontend, javascript]
category: web-development
author: Your Name
---

# Content here...
```

### 6. Batch Process When Possible

Process multiple files at once instead of one by one:

```bash
# Good: Process entire directory
python cli.py process ~/Documents/tech-docs

# Less efficient: Process files individually
python cli.py process ~/Documents/tech-docs/file1.md
python cli.py process ~/Documents/tech-docs/file2.md
```

---

## Performance Tips

### Optimization Checklist

- ✅ Use incremental sync (`--incremental`) for large repositories
- ✅ Adjust chunk size based on document type (smaller for dense content)
- ✅ Process during off-hours for large batches
- ✅ Monitor Ollama performance (CPU/NPU usage)
- ✅ Keep ChromaDB directory on SSD for faster queries
- ✅ Regularly clean up old or unused collections

### Expected Performance

- **Small files** (1-5KB): ~2-3 seconds
- **Medium files** (10-50KB): ~5-10 seconds
- **Large files** (100KB+): ~15-30 seconds
- **Batch processing**: ~100 files in 10-15 minutes

_Times vary based on hardware and Ollama configuration_

---

## Getting Help

### Resources

- **Documentation**: `/home/user/Source/PrismWeave/ai-processing/README.md`
- **Architecture**: `/home/user/Source/PrismWeave/ai-processing/ARCHITECTURE.md`
- **Tests**: `/home/user/Source/PrismWeave/ai-processing/tests/`

### Common Questions

**Q: Can I use a different embedding model?**  
A: Yes! Edit `config.yaml` and change `ollama.models.embedding` to any Ollama model that supports embeddings.

**Q: How do I backup my collection?**  
A: Copy the entire ChromaDB directory specified in `config.yaml` (default: `.prismweave/chroma_db`)

**Q: Can I process documents without git tracking?**  
A: Yes! Simply omit the `--incremental` flag or use the standard `process` command instead of `sync`.

**Q: What happens if I interrupt processing?**  
A: Processing is atomic per-file. Already processed files are saved; interrupted files will need reprocessing.

---

**Happy Document Processing! 🚀**
