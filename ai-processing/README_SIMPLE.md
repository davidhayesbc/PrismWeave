# PrismWeave AI Processing - Simplified

[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-pytest-green.svg)](https://pytest.org)

A simplified document processing system that converts documents into embeddings for semantic search. Uses LangChain and local Ollama models for privacy-focused AI processing.

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
- **LangChain Integration**: Built on LangChain ecosystem for reliability
- **Frontmatter Support**: Preserves metadata from markdown files
- **Smart Chunking**: Optimized chunk sizes for web documents
- **Batch Processing**: Process entire directories efficiently

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

### Simple Command Line
```bash
# Process documents from PrismWeaveDocs
python main.py

# Process documents from custom directory
python main.py /path/to/your/documents
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

## ⚙️ Configuration

Edit `config.yaml`:

```yaml
# Ollama Server Configuration
ollama:
  host: http://localhost:11434
  timeout: 60
  models:
    embedding: "nomic-embed-text:latest"

# Document Processing Configuration
processing:
  chunk_size: 1000           # Smaller chunks for web documents
  chunk_overlap: 200         # Overlap between chunks

# Vector Database Configuration
vector:
  collection_name: "documents"
  persist_directory: "../../PrismWeaveDocs/.prismweave/chroma_db"
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
├── main.py                          # Command line entry point
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
- **Core**: LangChain, ChromaDB, Ollama embeddings
- **Documents**: python-frontmatter, pypdf, docx2txt
- **Utils**: PyYAML, requests

### Code Structure
- **`DocumentProcessor`**: Handles file loading and text splitting
- **`EmbeddingStore`**: Manages ChromaDB operations
- **`Config`**: Configuration management with validation
- **`process_documents()`**: Main processing function

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

## 📝 License

This project is licensed under the MIT License.

## 🤝 Integration

Part of the PrismWeave document management ecosystem:
- **Browser Extension**: Captures web content as markdown
- **VS Code Extension**: Manages document collections
- **AI Processing**: Converts documents to searchable embeddings (this module)

---

*Simplified for focused document processing and embedding generation.*
