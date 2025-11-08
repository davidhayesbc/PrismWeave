# PrismWeave AI Processing - Simplified

[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-pytest-green.svg)](https://pytest.org)

A simplified document processing system that converts documents into embeddings for semantic search. Uses Haystack and local Ollama models for privacy-focused AI processing.

## 🎯 What This Does

**Simple Purpose**: Take documents → Generate embeddings → Store in ChromaDB

### Supported Document Types

- **Markdown** (`.md`) with frontmatter support
- **PDF** (`.pdf`) files
- **Word Documents** (`.docx`)
- **HTML** (`.html`, `.htm`) files
- **Text** (`.txt`) files

### Key Features

- **Local Processing**: Uses Ollama for privacy (no cloud APIs)
- **Haystack Integration**: Built on Haystack framework for reliability and modularity
- **Git-Based Incremental Processing**: Only process new or changed files (90%+ time savings)
- **Semantic Search**: Find documents by meaning, not just keywords (Phase 3)
- **Collection Analytics**: Detailed statistics and insights (Phase 3)
- **Document Export**: Export to JSON/CSV for backup and analysis (Phase 3)
- **Rich Progress Bars**: Beautiful terminal UI with real-time feedback (Phase 3)
- **Frontmatter Support**: Preserves metadata from markdown files
- **Smart Chunking**: Optimized chunk sizes for web documents
- **Batch Processing**: Process entire directories efficiently
- **Comprehensive Testing**: 63 passing tests with >80% coverage

## 🛠️ Installation

### 1. Prerequisites

```bash
# Install Ollama
# Download from: https://ollama.com

# Pull the embedding model
ollama pull nomic-embed-text:latest
```

### 2. Install Dependencies

```bash
cd ai-processing
uv sync

# Activate virtual environment
.venv\Scripts\activate  # Windows
# or
source .venv/bin/activate  # Linux/Mac
```

## 🚀 Usage

### Command Line Interface

````bash
# Process a single file
python cli.py process document.md

# Process a directory (recursive)
python cli.py process /path/to/documents

# Incremental processing (only new/changed files - RECOMMENDED)
python cli.py process /path/to/documents --incremental

# Git-based sync (auto-detect repository and process changes)
python cli.py sync

# Sync specific repository
python cli.py sync /path/to/docs

# Force reprocess everything
python cli.py process /path/to/documents --force

# Process with verbose output
python cli.py process document.md --verbose

# Process and verify embeddings
python cli.py process /path/to/documents --verify

# Clear existing embeddings before processing
python cli.py process /path/to/documents --clear

# Use custom config file
python cli.py process document.md --config custom-config.yaml

# List documents in the collection (max 50 by default)
python cli.py list

# List first 10 documents
python cli.py list --max 10

# List unique source files only
python cli.py list --source-files

# Show detailed document information
python cli.py list --max 5 --verbose

# Get total document count
python cli.py count

# Search documents (Phase 3 NEW!)
python cli.py search "machine learning" --max 10

# Search with filters
python cli.py search "API documentation" --filter-type md --verbose

# Show collection statistics (Phase 3 NEW!)
python cli.py stats

# Show detailed analytics
python cli.py stats --detailed

# Export documents (Phase 3 NEW!)
python cli.py export documents.json

# Export to CSV
python cli.py export docs.csv --format csv

# Export with filters
python cli.py export markdown_only.json --filter-type md --max 100
```

### Examples

```bash
# Git-based incremental sync (RECOMMENDED for regular use)
python cli.py sync ~/PrismWeaveDocs

# Process only changed files in a directory
python cli.py process ~/PrismWeaveDocs/documents --incremental

# Search for specific topics
python cli.py search "neural networks" --max 15 --verbose

# Get detailed collection statistics
python cli.py stats --detailed

# Export all markdown documents
python cli.py export backup.json --filter-type md --include-content

# Process PrismWeaveDocs tech folder with verification
python cli.py process "d:\source\PrismWeaveDocs\documents\tech" --verify

# Process single document with verbose output
python cli.py process "d:\source\PrismWeaveDocs\documents\tech\example.md" --verbose

# Force reprocess all files (after config changes)
python cli.py sync ~/PrismWeaveDocs --force

# Enumerate first 20 documents with details
python cli.py list --max 20 --verbose
````

### Examples

```bash
# Process PrismWeaveDocs tech folder with verification
python cli.py process "d:\source\PrismWeaveDocs\documents\tech" --verify

# Process single document with verbose output
python cli.py process "d:\source\PrismWeaveDocs\documents\tech\example.md" --verbose

# Enumerate first 20 documents with details
python cli.py list --max 20 --verbose
```

### Python API

```python
from src.core import process_documents

# Process all documents in a directory
process_documents(
    input_dir="../../PrismWeaveDocs/documents",
    embeddings_dir="../../PrismWeaveDocs/.prismweave/chroma_db"
)
```

### Advanced Usage

```python
from src.core import DocumentProcessor, EmbeddingStore, load_config

# Load configuration
config = load_config()

# Initialize components
processor = DocumentProcessor(config)
store = EmbeddingStore(config)

# Process a single document
from pathlib import Path
chunks = processor.process_document(Path("document.md"))
store.add_document(Path("document.md"), chunks)

# Verify embeddings
result = store.verify_embeddings()
print(f"Stored {result['document_count']} documents")

# Search similar content
results = store.search_similar("machine learning", k=5)
for doc in results:
    print(f"Found: {doc.metadata['title']}")
```

## 🎯 Phase 3: Enhanced Features (NEW!)

### Semantic Search

Find documents based on meaning, not just keywords:

```bash
# Basic search
python cli.py search "machine learning algorithms"

# Filter by file type
python cli.py search "API documentation" --filter-type md

# Get more results with verbose output
python cli.py search "Python tutorial" --max 20 --verbose

# Control relevance with similarity threshold
python cli.py search "neural networks" --threshold 0.8
```

### Collection Statistics

Analyze your document collection:

```bash
# Quick overview
python cli.py stats

# Detailed analytics with file types and tag frequency
python cli.py stats --detailed
```

Shows:

- Total chunks and source files
- Average chunks per file
- File type distribution
- Tag frequency analysis
- Content size statistics

### Document Export

Export your collection for backup or analysis:

```bash
# Export to JSON
python cli.py export documents.json

# Export to CSV
python cli.py export docs.csv --format csv

# Export with full content (JSON only)
python cli.py export backup.json --include-content

# Export filtered documents
python cli.py export markdown_docs.json --filter-type md --max 100
```

### Progress Reporting

Automatic rich progress bars for batch operations (>5 files):

- Real-time progress visualization
- Current file indicator
- Time elapsed and ETA
- Processing statistics summary

**See [Phase 3 Usage Guide](examples/PHASE3_USAGE.md) for detailed examples and best practices.**

## ⚙️ Configuration

Edit `config.yaml`:

```yaml
# Ollama Server Configuration
ollama:
  host: http://localhost:11434
  timeout: 60
  models:
    embedding: 'nomic-embed-text:latest'

# Document Processing Configuration
processing:
  chunk_size: 1000 # Smaller chunks for web documents
  chunk_overlap: 200 # Overlap between chunks

# Vector Database Configuration
vector:
  collection_name: 'documents'
  persist_directory: '../../PrismWeaveDocs/.prismweave/chroma_db'
```

## 📁 Project Structure

```
ai-processing/
├── src/
│   └── core/
│       ├── __init__.py              # Public API
│       ├── document_processor.py    # Document loading and chunking
│       ├── embedding_store.py       # ChromaDB integration
│       └── config.py                # Configuration management
├── tests/
│   └── test_core.py                 # Essential tests
├── cli.py                           # Unified CLI tool
├── config.yaml                      # Configuration file
├── pyproject.toml                   # Dependencies
└── README.md                        # This file
```

## 📊 What Gets Processed

### Input Documents

- Loads documents from specified directory (recursive)
- Preserves frontmatter metadata from markdown files
- Handles various document formats via LangChain loaders

### Processing Steps

1. **Load Document**: Read file with appropriate loader
2. **Extract Metadata**: Parse frontmatter and file info
3. **Split Text**: Create chunks for optimal embedding
4. **Generate Embeddings**: Use Ollama local model
5. **Store in ChromaDB**: Save with metadata for retrieval

### Output

- Embeddings stored in ChromaDB collection
- Metadata preserved for each document chunk
- Verification reports for stored data

## 🔧 Development

### Run Tests

```bash
pytest tests/
```

### Dependencies

- **Core**: Haystack, ChromaDB, Ollama embeddings
- **Documents**: python-frontmatter, pypdf, python-docx

## ❓ Troubleshooting

### Ollama Connection Issues

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama if needed
ollama serve

# Pull embedding model if missing
ollama pull nomic-embed-text:latest
```

### Memory Issues

- Reduce `chunk_size` in config for lower memory usage
- Process smaller directories at a time
- Restart Ollama to clear memory: `ollama serve`

### ChromaDB Issues

```python
# Clear existing embeddings
from src.core import EmbeddingStore, load_config
store = EmbeddingStore(load_config())
store.clear_collection()
```

Or via CLI:

```bash
python cli.py process /path/to/docs --clear --force
```

## 🤝 Integration

Part of the PrismWeave document management ecosystem:

- **Browser Extension**: Captures web content as markdown
- **VS Code Extension**: Manages document collections
- **AI Processing**: Converts documents to searchable embeddings (this module)

## 📚 Documentation

- **[README.md](README.md)**: User documentation (this file)
- **[ARCHITECTURE.md](ARCHITECTURE.md)**: System architecture and design
- **[SIMPLIFICATION_PLAN.md](SIMPLIFICATION_PLAN.md)**: Implementation history and decisions
- **[examples/USAGE.md](examples/USAGE.md)**: Practical usage examples and workflows
- **[examples/PHASE3_USAGE.md](examples/PHASE3_USAGE.md)**: Phase 3 enhanced features guide (NEW!)
- **[examples/QUICK_REFERENCE.md](examples/QUICK_REFERENCE.md)**: CLI quick reference card (NEW!)
- **[NEXT_STEPS.md](NEXT_STEPS.md)**: Development roadmap and future plans

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/test_embedding_store.py -v

# Quick smoke test
pytest tests/test_core.py -v
```

**Test Coverage**: 51 passing tests across 5 test suites

- Config: 3 tests
- DocumentProcessor: 5 tests
- EmbeddingStore: 17 tests
- GitTracker: 21 tests
- Integration: 5 tests

---

_Simplified for focused document processing and embedding generation. Built with ❤️ for privacy-focused, local-first AI processing._
python cli.py sync /path/to/docs --force

# Or manually remove processing state

rm -rf /path/to/docs/.prismweave/processing_state.json

````

## 💡 Performance Tips

### Use Incremental Processing

For best performance with large document collections:

```bash
# Initial processing (full scan)
python cli.py sync ~/Documents

# Subsequent updates (only changed files) - 90%+ faster!
python cli.py sync ~/Documents
````

### Optimize Configuration

Edit `config.yaml` for your use case:

```yaml
processing:
  chunk_size: 1000 # Smaller = more chunks, better granularity
  chunk_overlap: 200 # Higher = more context, slower processing
```

### Monitor Processing

Use verbose mode to understand bottlenecks:

```bash
python cli.py process document.md --verbose
```

### Batch Processing Strategy

For large collections:

1. Process in sections first time
2. Use `--incremental` for updates
3. Schedule regular syncs with cron/schedulerestart Ollama to clear memory: `ollama serve`

### ChromaDB Issues

```python
# Clear existing embeddings
from src.core import EmbeddingStore, load_config
store = EmbeddingStore(load_config())
store.clear_collection()
```

## 📝 License

This project is licensed under the MIT License.

## 🤝 Integration

Part of the PrismWeave document management ecosystem:

- **Browser Extension**: Captures web content as markdown
- **VS Code Extension**: Manages document collections
- **AI Processing**: Converts documents to searchable embeddings (this module)

---

_Simplified for focused document processing and embedding generation._
