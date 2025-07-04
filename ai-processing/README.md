# PrismWeave AI Processing Pipeline (Phase 2)

> **✨ New**: Using [UV](https://astral.sh/uv/) for faster, more reliable Python package management!  
> 📖 **Quick Start**: See [UV_QUICKSTART.md](UV_QUICKSTART.md) for setup with UV (recommended)

## Overview

The AI Processing Pipeline is the core intelligence engine of PrismWeave, providing semantic search, document analysis, and AI-powered insights using local Ollama models. This phase transforms your captured documents into a searchable, intelligent knowledge base.

## 🎯 Key Features

- **Local AI Processing**: Uses Ollama for privacy-focused, offline AI capabilities
- **Multi-Model Strategy**: Optimized model selection for different tasks
- **Semantic Search**: Vector-based document similarity and retrieval
- **Document Analysis**: Automated summarization, tagging, and categorization
- **NPU Acceleration**: Optimized for AI HX 370 NPU hardware
- **Batch Processing**: Efficient processing of large document collections
- **Rich CLI**: Beautiful command-line interface with progress indicators

## 🏗️ Architecture

```
ai-processing/
├── src/
│   ├── models/          # AI model integrations
│   ├── processors/      # Document analysis engines
│   ├── search/         # Semantic search components
│   └── utils/          # Configuration and utilities
├── cli/                # Command-line interface
├── tests/             # Test suite
└── logs/              # Processing logs
```

## 🚀 Quick Start

> **New**: We now use [UV](https://astral.sh/uv/) for package management - it's 10-100x faster than pip! 
> See **[UV_QUICKSTART.md](UV_QUICKSTART.md)** for the complete UV setup guide.

```bash
# One-command setup
cd d:\source\PrismWeave\ai-processing && python setup.py

# Or with UV directly
uv sync && uv shell && uv run python cli/prismweave.py process
```

### Traditional Setup (pip/venv)

<details>
<summary>Click here for traditional setup instructions</summary>

#### 1. Prerequisites

- **Python 3.9+**: Required for async support and modern typing
- **Ollama**: Install from [ollama.ai](https://ollama.ai/)
- **Git**: For repository integration
- **8GB+ RAM**: Recommended for AI model processing

#### 2. Automated Setup

Run the automated setup script:

```powershell
cd d:\source\PrismWeave\ai-processing
python setup.py
```

This will:
- Create a Python virtual environment
- Install all dependencies
- Check Ollama installation
- Download recommended AI models
- Create necessary directories
- Test the installation

#### 3. Manual Setup (Alternative)

If you prefer manual setup:

```powershell
# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Ollama (if not already installed)
# Download from https://ollama.ai/

# Pull recommended models
ollama pull phi3:mini
ollama pull nomic-embed-text
```

### 4. Configuration

Edit `config.yaml` to customize settings:

```yaml
ollama:
  base_url: "http://localhost:11434"
  models:
    analysis: "phi3:mini"          # Fast model for analysis
    summarization: "phi3:mini"     # Summarization model
    embedding: "nomic-embed-text"  # Embedding model
```

</details>

## 📊 Usage

### Process Documents

Process your existing document collection:

```bash
# UV (Recommended)
uv run python cli/prismweave.py process

# Or if environment is activated
python cli/prismweave.py process

# With specific options  
uv run python cli/prismweave.py process --batch-size 10 --force-reprocess
```

### Search Documents

Perform semantic search across your documents:

```bash
# Basic search
uv run python cli/prismweave.py search "machine learning concepts"

# Advanced search with filters
uv run python cli/prismweave.py search "typescript patterns" --limit 10 --min-score 0.7

# Search with context
uv run python cli/prismweave.py search "database optimization" --show-context
```

### System Status

Check the health of your AI processing system:

```bash
uv run python cli/prismweave.py status
```

This shows:
- Ollama server status
- Available models
- Document collection statistics
- Processing performance metrics
- Storage usage

### Configuration Management

View and update configuration:

```powershell
# Show current configuration
python cli/prismweave.py config show

# Set configuration values
python cli/prismweave.py config set ollama.models.analysis "llama3.2:3b"

# Reset to defaults
python cli/prismweave.py config reset
```

## 🎛️ Configuration Options

### Ollama Settings

```yaml
ollama:
  base_url: "http://localhost:11434"
  timeout: 60
  models:
    analysis: "phi3:mini"
    summarization: "phi3:mini" 
    embedding: "nomic-embed-text"
    fallback: "phi3:mini"
```

### Processing Settings

```yaml
processing:
  batch_size: 5
  max_workers: 3
  chunk_size: 1000
  overlap: 200
  enable_summaries: true
  enable_tags: true
  enable_categories: true
```

### Search Settings

```yaml
search:
  vector_db: "chroma"  # or "inmemory"
  embedding_model: "nomic-embed-text"
  similarity_threshold: 0.6
  max_results: 20
  enable_hybrid: true
```

## 🧠 AI Models

### Recommended Models

| Model | Size | Purpose | Use Case |
|-------|------|---------|----------|
| `phi3:mini` | ~2.3GB | Analysis, Tagging | Fast general-purpose processing |
| `nomic-embed-text` | ~274MB | Embeddings | Semantic search vectors |
| `llama3.2:3b` | ~2GB | Summarization | High-quality summaries |
| `qwen2.5:7b` | ~4.4GB | Analysis | Advanced reasoning (optional) |

### Model Strategy

- **Small Models (< 3GB)**: For tagging, classification, quick analysis
- **Medium Models (3-7GB)**: For summarization, content generation
- **Embedding Models**: Specialized for vector generation
- **NPU Optimization**: Models optimized for AI HX 370 acceleration

### Installing Additional Models

```powershell
# List available models
ollama list

# Pull a specific model
ollama pull llama3.2:3b

# Remove unused models
ollama rm old-model-name
```

## 📁 Document Processing

### Input Formats

The system processes markdown files with YAML frontmatter:

```markdown
---
title: "Document Title"
url: "https://source-url.com"
tags: ["tag1", "tag2"]
capture_date: "2025-01-15"
---

# Document Content

Your markdown content here...
```

### Processing Pipeline

1. **Frontmatter Extraction**: Parses YAML metadata
2. **Content Analysis**: AI-powered content understanding
3. **Summarization**: Generates concise summaries
4. **Tagging**: Automatic tag generation and enhancement
5. **Categorization**: Document classification
6. **Embedding Generation**: Vector representations for search
7. **Storage**: Saves to vector database

### Output Structure

```
.prismweave/
├── chroma_db/          # Vector database
├── summaries/          # Generated summaries
├── metadata/           # Enhanced metadata
└── embeddings/         # Vector embeddings
```

## 🔍 Search Capabilities

### Semantic Search

- **Vector Similarity**: Uses embedding models for semantic understanding
- **Hybrid Search**: Combines semantic and keyword matching
- **Context Awareness**: Understands document relationships
- **Relevance Scoring**: Ranked results with confidence scores

### Search Types

1. **Semantic**: `"concepts related to machine learning"`
2. **Keyword**: `"exact phrase matching"`
3. **Hybrid**: Combines both approaches
4. **Filtered**: By tags, dates, categories

### Advanced Features

- **Multi-document Context**: Search across related documents
- **Temporal Search**: Find documents by time periods
- **Tag-based Filtering**: Narrow results by categories
- **Similarity Clustering**: Group related documents

## 🔧 Development

### Project Structure

```python
# Core components
from src.models.ollama_client import OllamaClient
from src.processors.document_processor import DocumentProcessor
from src.search.semantic_search import SemanticSearch
from src.utils.config import get_config

# Example usage
config = get_config()
client = OllamaClient(config.ollama)
processor = DocumentProcessor(client, config.processing)
```

### Adding Custom Processors

```python
from src.processors.base_processor import BaseProcessor

class CustomProcessor(BaseProcessor):
    async def process_document(self, document_path: Path) -> ProcessingResult:
        # Your custom processing logic
        pass
```

### Testing

```powershell
# Run all tests
python -m pytest tests/

# Run specific test categories
python -m pytest tests/test_processors.py -v

# Run with coverage
python -m pytest --cov=src tests/
```

## 📊 Performance

### Benchmarks

Based on the AI HX 370 NPU:

- **Document Processing**: ~50 documents/minute
- **Search Queries**: <500ms response time
- **Embedding Generation**: ~2 seconds/document
- **Memory Usage**: ~4GB for 1000 documents

### Optimization Tips

1. **Batch Processing**: Process documents in batches of 5-10
2. **Model Selection**: Use smaller models for simple tasks
3. **Caching**: Enable result caching for repeated operations
4. **NPU Utilization**: Ensure NPU drivers are installed

## 🐛 Troubleshooting

### Common Issues

**Ollama Connection Errors**
```
❌ Error: Failed to connect to Ollama server
```
- Ensure Ollama is running: `ollama serve`
- Check firewall settings
- Verify `base_url` in config.yaml

**GenerationResult `done_reason` Error (FIXED in v1.1)**
```
❌ Error: GenerationResult.__init__() got an unexpected keyword argument 'done_reason'
```
- **Fixed**: Updated `GenerationResult` class to handle new Ollama API fields
- The class now gracefully handles `done_reason` and other new fields from newer Ollama versions
- Uses `GenerationResult.from_dict()` method for robust field handling

**Memory Issues**
```
❌ Error: Out of memory during processing
```
- Reduce `batch_size` in configuration
- Use smaller AI models
- Increase system virtual memory

**Slow Processing**
```
⚠️ Warning: Processing is slower than expected
```
- Check NPU driver installation
- Reduce model size
- Optimize batch processing settings

**Import Errors**
```
❌ Error: No module named 'ollama'
```
- Activate virtual environment: `venv\Scripts\activate`
- Reinstall requirements: `pip install -r requirements.txt`
- Or use UV: `uv sync`

### Debug Mode

Enable debug logging in `config.yaml`:

```yaml
logging:
  level: DEBUG
  file: logs/prismweave.log
  console: true
```

### Getting Help

1. Check logs in `logs/prismweave.log`
2. Run `python cli/prismweave.py status` for system diagnostics
3. Verify Ollama models: `ollama list`
4. Test configuration: `python cli/prismweave.py config show`

## 🚀 What's Next?

After Phase 2 is working:

- **Phase 3**: VS Code extension with AI-powered document management
- **Phase 4**: Advanced content generation and research tools
- **Phase 5**: Real-time document watching and smart recommendations

## 📞 Support

For issues specific to the PrismWeave AI processing pipeline:

1. Check the troubleshooting section above
2. Review logs in `logs/prismweave.log`
3. Verify your configuration with `config show`
4. Test with a small document subset first

---

**Happy AI-powered document processing! 🤖📚**
