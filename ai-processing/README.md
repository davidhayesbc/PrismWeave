# PrismWeave AI Processing Pipeline

[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-pytest-green.svg)](https://pytest.org)

A comprehensive AI processing pipeline for document management, analysis, and content generation using local LLMs and vector search. Part of the PrismWeave document management ecosystem.

## 🚀 Features

### Document Analysis & Processing
- **Automatic Summarization**: Generate concise document summaries
- **Smart Tagging**: AI-powered tag generation for organization
- **Content Categorization**: Automatic topic classification
- **Metadata Extraction**: Title, author, keywords, and more
- **Language Detection**: Multi-language document support
- **Readability Analysis**: Content accessibility scoring

### Vector Search & Embeddings
- **Semantic Search**: Meaning-based document retrieval
- **Vector Database**: ChromaDB integration for fast similarity search
- **Batch Processing**: Efficient embedding generation
- **Multi-model Support**: Various embedding models available
- **Similarity Scoring**: Relevance ranking and threshold filtering

### RAG (Retrieval Augmented Generation)
- **Context-Aware Responses**: Question answering with document context
- **Source Citations**: Traceable responses with document references
- **Flexible Synthesis**: Multiple response styles and formats
- **OpenAI-Compatible API**: Standard API endpoints for integration

### Local AI Integration
- **Ollama Integration**: Local LLM processing for privacy
- **NPU Optimization**: Hardware acceleration support (AI HX 370)
- **Model Management**: Automatic model downloading and switching
- **Batch Processing**: Efficient document processing workflows

## 📋 Requirements

### System Requirements
- **Python**: 3.9 or higher
- **Memory**: 8GB RAM minimum (16GB+ recommended for large models)
- **Storage**: 10GB+ free space for models and vector database
- **OS**: Windows 10/11, macOS 10.14+, or Linux

### AI Hardware (Optional)
- **NPU Support**: Intel AI HX 370 or compatible NPU for acceleration
- **GPU**: NVIDIA GPU with CUDA support (optional)

### Dependencies
- **Ollama**: Local LLM server (automatically managed)
- **ChromaDB**: Vector database for embeddings
- **Sentence Transformers**: Text embedding models
- **FastAPI**: API server for RAG endpoints

## 🛠️ Installation

### 1. Clone and Setup
```bash
git clone https://github.com/davidhayesbc/PrismWeave.git
cd PrismWeave/ai-processing
```

### 2. Install Dependencies
Using UV (recommended):
```bash
# Install UV package manager
pip install uv

# Install dependencies
uv sync

# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate  # Windows
```

Using pip:
```bash
pip install -e .

# Development dependencies
pip install -e .[dev]
```

### 3. Install Ollama
**Windows/Mac**:
Download from [ollama.com](https://ollama.com)

**Linux**:
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### 4. Pull Required Models
```bash
# Core models for PrismWeave
ollama pull llama3.1:8b        # Large model for complex tasks
ollama pull phi3:mini          # Fast model for quick processing  
ollama pull nomic-embed-text   # Embedding model for search
```

## 🚀 Quick Start

### 1. Check System Health
```bash
prismweave health
```

### 2. Process Documents
```bash
# Process a single document
prismweave process document.md

# Process directory recursively with vector database
prismweave process documents/ --recursive --add-to-vector

# Process and verify embeddings
prismweave process documents/ --recursive --add-to-vector --verify-embeddings
```

### 3. Search Documents
```bash
# Semantic search
prismweave search "machine learning techniques"

# Limit results and adjust threshold
prismweave search "AI applications" --limit 10 --threshold 0.8
```

### 4. Ask Questions (RAG)
```bash
# Question answering with document context
prismweave ask "What are the key benefits of local AI processing?"

# Use more context documents
prismweave ask "Explain the architecture" --context-docs 5
```

### 5. Vector Database Management
```bash
# Check vector database health
prismweave vector-health

# List documents in vector database
prismweave vector-list --limit 20 --verbose

# Verify specific document
prismweave vector-verify "documents/ai-guide.md"

# Export vector database info
prismweave vector-export --output embeddings_backup.json
```

## 📁 Project Structure

```
ai-processing/
├── cli/                    # Command-line interface
│   └── prismweave.py      # Main CLI application
├── src/                   # Core source code
│   ├── api/              # FastAPI server and endpoints
│   ├── models/           # AI model interfaces (Ollama)
│   ├── processors/       # Document processing logic
│   ├── rag/              # RAG implementation
│   ├── search/           # Vector search and embeddings
│   └── utils/            # Utilities and configuration
├── tests/                # Unit and integration tests
├── docker/               # Docker configurations
├── scripts/              # Automation scripts
├── config.yaml           # Configuration file
├── pyproject.toml        # Python project configuration
└── README.md             # This file
```

## ⚙️ Configuration

The system uses a YAML configuration file (`config.yaml`) for all settings:

```yaml
# Ollama Server Configuration
ollama:
  host: http://localhost:11434
  timeout: 60
  models:
    large: "llama3.1:8b"           # Complex analysis
    medium: "phi3:mini"            # Standard processing
    small: "phi3:mini"             # Quick tasks
    embedding: "nomic-embed-text"  # Vector embeddings

# Document Processing
processing:
  max_concurrent: 1
  chunk_size: 3000
  chunk_overlap: 300
  summary_timeout: 180
  max_tags: 10

# Vector Database
vector:
  collection_name: "documents"
  persist_directory: "../../PrismWeaveDocs/.prismweave/chroma_db"
  max_results: 20
  similarity_threshold: 0.3

# API Server
api:
  host: "127.0.0.1"
  port: 8000
  rag_enabled: true
  openai_compatible: true
```

### View Current Configuration
```bash
prismweave config-show
```

## 🔌 API Server

### Start RAG Server
```bash
# Start API server
python scripts/start_rag_server.py

# Or use the CLI
prismweave api-server
```

### API Endpoints
- `POST /v1/chat/completions` - OpenAI-compatible chat endpoint
- `POST /v1/embeddings` - Generate embeddings
- `GET /health` - Health check
- `GET /models` - List available models
- `POST /search` - Semantic document search

### Example API Usage
```python
import requests

# RAG question answering
response = requests.post("http://localhost:8000/v1/chat/completions", 
    json={
        "model": "llama3.1:8b",
        "messages": [{"role": "user", "content": "What is machine learning?"}],
        "rag_enabled": True
    }
)

# Document search
search_response = requests.post("http://localhost:8000/search",
    json={
        "query": "artificial intelligence",
        "limit": 5,
        "threshold": 0.7
    }
)
```

## 🧪 Testing

### Run Tests
```bash
# All tests
pytest

# With coverage
pytest --cov=src --cov-report=html

# Specific test categories
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m "not slow"    # Skip slow tests
```

### Test Structure
```
tests/
├── unit/              # Unit tests
├── integration/       # Integration tests
├── fixtures/          # Test data and fixtures
└── conftest.py        # Pytest configuration
```

## 📊 Performance & Monitoring

### Model Performance
- **Phi3 Mini**: ~1-2 seconds per document (tagging, categorization)
- **Llama3.1 8B**: ~5-10 seconds per document (summarization, analysis)
- **Embedding Generation**: ~0.5-1 second per document

### Memory Usage
- **Base Memory**: ~2GB for ChromaDB and embeddings
- **Phi3 Mini**: ~2GB additional when loaded
- **Llama3.1 8B**: ~8GB additional when loaded

### Optimization Tips
1. **Batch Processing**: Process multiple documents together
2. **Model Management**: Use smaller models for quick tasks
3. **Concurrent Processing**: Adjust `max_concurrent` based on hardware
4. **Vector Database**: Regular maintenance and optimization

## 🔧 Development

### Development Setup
```bash
# Install development dependencies
pip install -e .[dev]

# Install pre-commit hooks
pre-commit install

# Run linting
flake8 src/ cli/
black src/ cli/
isort src/ cli/

# Type checking
mypy src/ cli/
```

### Code Quality
- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking
- **pytest**: Testing

### Contributing
1. Fork the repository
2. Create a feature branch
3. Run tests and linting
4. Submit a pull request

## 📚 Usage Examples

### Document Processing Pipeline
```python
from src.processors.langchain_document_processor import LangChainDocumentProcessor
from src.search.semantic_search import SemanticSearch
from pathlib import Path

# Initialize processor
processor = LangChainDocumentProcessor()

# Process document
analysis, metadata = await processor.process_file(Path("document.md"))

# Add to vector database
search_engine = SemanticSearch()
await search_engine.add_document(
    document_id="doc1",
    content=document_content,
    metadata=metadata
)
```

### RAG Implementation
```python
from src.rag.rag_engine import RAGEngine
from src.models.ollama_client import OllamaClient

# Initialize RAG engine
rag = RAGEngine()

# Ask question with context
response = await rag.ask_question(
    question="What are the key benefits?",
    context_docs=5,
    model="llama3.1:8b"
)
```

### Custom Document Analysis
```python
from src.processors.document_analyzer import DocumentAnalyzer

analyzer = DocumentAnalyzer()

# Custom analysis
result = await analyzer.analyze_document(
    content="Your document content here",
    include_summary=True,
    include_tags=True,
    include_category=True
)
```

## 🆘 Troubleshooting

### Common Issues

**1. Ollama Connection Failed**
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama service
ollama serve
```

**2. Model Not Found**
```bash
# List available models
ollama list

# Pull missing model
ollama pull llama3.1:8b
```

**3. Vector Database Issues**
```bash
# Check vector database health
prismweave vector-health

# Verify specific document
prismweave vector-verify "document-id"
```

**4. Memory Issues**
- Reduce `max_concurrent` in config
- Use smaller models for batch processing
- Restart Ollama to clear memory

### Debug Mode
```bash
# Enable debug logging
prismweave --log-level DEBUG command

# Check system health
prismweave health
```

## 🔗 Integration

### VS Code Extension
The AI processing pipeline integrates with the PrismWeave VS Code extension:
- Document analysis triggers
- Search integration
- Content generation assistance

### Browser Extension
Processes documents captured by the browser extension:
- Automatic analysis of captured pages
- Tag generation for organization
- Content summarization

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please see our [Contributing Guidelines](../CONTRIBUTING.md) for details.

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/davidhayesbc/PrismWeave/issues)
- **Discussions**: [GitHub Discussions](https://github.com/davidhayesbc/PrismWeave/discussions)
- **Documentation**: [Project Wiki](https://github.com/davidhayesbc/PrismWeave/wiki)

## 🚧 Roadmap

### Upcoming Features
- [ ] Additional embedding models
- [ ] GPU acceleration support
- [ ] Multi-language processing
- [ ] Advanced analytics dashboard
- [ ] Plugin system for custom processors

### Performance Improvements
- [ ] Streaming processing for large documents
- [ ] Distributed processing support
- [ ] Advanced caching mechanisms
- [ ] Memory optimization for large collections

---

*Built with ❤️ for the PrismWeave document management ecosystem*
