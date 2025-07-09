# Copilot Instructions for PrismWeave AI Processing Module

<!-- Instructions for GitHub Copilot when working on PrismWeave AI processing components -->

## Module Overview

The **AI Processing Module** is the core intelligence engine of PrismWeave, providing local AI-powered document analysis, semantic search, and content generation capabilities. This module operates entirely offline using Ollama for privacy-focused AI processing.

## Technology Stack

### Package Management
- **UV Package Manager**: Primary dependency management (10-100x faster than pip)
- **pyproject.toml**: Modern Python project configuration
- **uv.lock**: Dependency lockfile for reproducible builds

### Core Dependencies
- **Ollama**: Local LLM inference server (`ollama>=0.1.7`)
- **ChromaDB**: Vector database for embeddings (`chromadb>=0.4.15`)
- **aiohttp**: Async HTTP client for Ollama communication (`aiohttp>=3.12.13`)
- **FastAPI**: Optional API server (`fastapi>=0.104.0`)
- **Rich**: CLI interface and progress indicators (`rich>=13.6.0`)
- **Click**: Command-line argument parsing (`click>=8.1.7`)

### AI/ML Libraries
- **sentence-transformers**: Text embeddings (`sentence-transformers>=2.2.2`)
- **transformers**: Hugging Face transformers (optional, in `performance` group)
- **torch**: PyTorch for local model execution (optional)

## Project Structure

```
ai-processing/
├── src/                    # Main source code
│   ├── models/            # AI model clients and wrappers
│   │   └── ollama_client.py  # Simplified Ollama client
│   ├── processors/        # Document analysis engines
│   │   └── langchain_document_processor.py
│   ├── search/           # Semantic search components
│   │   └── semantic_search.py
│   ├── rag/              # RAG (Retrieval Augmented Generation)
│   ├── utils/            # Configuration and utilities
│   └── api/              # Optional FastAPI server
├── cli/                  # Command-line interface
│   └── prismweave.py    # Main CLI entry point
├── tests/               # Test suite
├── config.yaml         # Configuration file
├── pyproject.toml      # Project metadata and dependencies
├── uv.lock             # UV lockfile
└── requirements.txt    # Legacy pip requirements
```

## Development Environment Setup

### Prerequisites
```bash
# Install UV (recommended)
curl -LsSf https://astral.sh/uv/install.sh | sh
# or: pip install uv

# Install Ollama
# Download from https://ollama.ai/
```

### UV-Based Setup (Recommended)
```bash
# Navigate to ai-processing directory
cd d:\source\PrismWeave\ai-processing

# Create virtual environment and install dependencies
uv sync

# Activate environment
uv shell

# Install development dependencies
uv sync --group dev

# Run CLI tool
uv run python cli/prismweave.py --help
```

### Traditional Setup (pip/venv)
```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Or install from pyproject.toml
pip install -e .
```

## Core Components

### 1. Ollama Client (`src/models/ollama_client.py`)

**Purpose**: Simplified async client for communicating with local Ollama server

**Key Features**:
- Async/await support with aiohttp
- Model management (list, pull, check existence)
- Text generation with streaming support
- Embedding generation
- Health checking and error handling
- Timeout and retry logic

**Usage Patterns**:
```python
# Always use async context manager
async with OllamaClient(host="http://localhost:11434") as client:
    # Check if model exists
    if not await client.model_exists("phi3:mini"):
        await client.pull_model("phi3:mini")
    
    # Generate text
    result = await client.generate(
        model="phi3:mini",
        prompt="Summarize this document...",
        system="You are a helpful document analyst."
    )
    
    # Generate embeddings
    embeddings = await client.embed(
        model="nomic-embed-text",
        input_text=["document content here"]
    )
```

**Error Handling**:
- Always wrap Ollama calls in try-catch
- Check model availability before use
- Handle timeout errors gracefully
- Use robust field handling for API responses

### 2. Document Processor (`src/processors/langchain_document_processor.py`)

**Purpose**: AI-powered document analysis and metadata generation

**Capabilities**:
- Content summarization
- Automatic tag generation
- Category classification
- Reading time estimation
- Language detection
- Readability scoring

**Usage Pattern**:
```python
processor = DocumentProcessor()
analysis, metadata = await processor.process_file(file_path)

# Access analysis results
print(f"Summary: {analysis.summary}")
print(f"Tags: {analysis.tags}")
print(f"Category: {analysis.category}")
print(f"Confidence: {analysis.confidence}")
```

### 3. Semantic Search (`src/search/semantic_search.py`)

**Purpose**: Vector-based document search and retrieval

**Features**:
- ChromaDB integration
- Embedding generation and storage
- Similarity search
- Document metadata management
- Batch processing support

**Usage Pattern**:
```python
search_engine = SemanticSearch(config.vector)
await search_engine.initialize()

# Add documents
await search_engine.add_document(
    document_id="doc_123",
    content="document content",
    metadata={"title": "Document Title", "category": "tech"}
)

# Search documents
results = await search_engine.search(
    query="machine learning concepts",
    max_results=10,
    similarity_threshold=0.7
)
```

### 4. CLI Interface (`cli/prismweave.py`)

**Purpose**: Rich command-line interface for AI processing operations

**Key Commands**:
- `health` - Check system health and model availability
- `process` - Analyze documents and generate metadata
- `search` - Semantic search across document collection
- `ask` - RAG-based question answering
- `models` - List/manage Ollama models
- `vector-*` - Vector database management

**CLI Design Principles**:
- Use Rich library for beautiful output
- Async operations with progress indicators
- Comprehensive error handling and reporting
- Modular command structure

## Configuration Management

### Configuration File (`config.yaml`)
```yaml
# Ollama server settings
ollama:
  host: http://localhost:11434
  timeout: 60
  models:
    large: "llama3.1:8b"      # Complex analysis
    medium: "phi3:mini"       # Standard processing
    small: "phi3:mini"        # Quick tasks
    embedding: "nomic-embed-text"  # Vector embeddings

# Processing settings
processing:
  max_concurrent: 1          # Prevent Ollama overload
  chunk_size: 3000
  chunk_overlap: 300
  summary_timeout: 180       # Increased timeouts
  tagging_timeout: 120
  categorization_timeout: 90

# Vector database
vector:
  collection_name: "documents"
  persist_directory: "../../PrismWeaveDocs/.prismweave/chroma_db"
  max_results: 20
  similarity_threshold: 0.6
```

### Configuration Loading
```python
from src.utils.config_simplified import get_config, Config

# Load configuration
config = get_config()

# Validate configuration
issues = config.validate()
if issues:
    for issue in issues:
        print(f"Config issue: {issue}")

# Access configuration values
ollama_host = config.ollama.host
embedding_model = config.get_model('embedding')
```

## Model Strategy

### Recommended Models
| Model | Size | Purpose | Use Case |
|-------|------|---------|----------|
| `phi3:mini` | ~2.3GB | Analysis, Tagging | Fast general-purpose processing |
| `nomic-embed-text` | ~274MB | Embeddings | Semantic search vectors |
| `llama3.1:8b` | ~4.6GB | Complex Analysis | High-quality summaries, RAG |
| `qwen2.5:7b` | ~4.4GB | Alternative | Advanced reasoning tasks |

### Model Selection Logic
```python
# Use smaller models for quick tasks
if task_type in ['tagging', 'classification']:
    model = config.get_model('small')  # phi3:mini
    
# Use larger models for complex analysis
elif task_type in ['summarization', 'rag']:
    model = config.get_model('large')  # llama3.1:8b
    
# Always use specialized embedding model
elif task_type == 'embedding':
    model = config.get_model('embedding')  # nomic-embed-text
```

## Error Handling Patterns

### Ollama Connection Errors
```python
async def safe_ollama_operation():
    try:
        async with OllamaClient() as client:
            if not await client.is_available():
                raise RuntimeError("Ollama server not available")
            
            # Perform operation
            result = await client.generate(...)
            return result
            
    except asyncio.TimeoutError:
        logger.error("Ollama operation timed out")
        raise
    except Exception as e:
        logger.error(f"Ollama operation failed: {e}")
        raise
```

### Model Management
```python
async def ensure_model_available(client: OllamaClient, model_name: str):
    """Ensure model is available, pull if necessary"""
    if not await client.model_exists(model_name):
        logger.info(f"Model {model_name} not found, pulling...")
        success = await client.pull_model(model_name)
        if not success:
            raise RuntimeError(f"Failed to pull model: {model_name}")
```

### Vector Database Errors
```python
try:
    search_engine = SemanticSearch(config.vector)
    await search_engine.initialize()
    # Perform operations
    
except Exception as e:
    logger.error(f"Vector database error: {e}")
    # Fallback to non-vector operations
```

## Testing Patterns

### Test Environment Setup
```python
# tests/conftest.py
import pytest
from src.utils.config_simplified import Config

@pytest.fixture
async def test_config():
    """Test configuration with mock values"""
    return Config(
        ollama={'host': 'http://localhost:11434'},
        vector={'collection_name': 'test_collection'}
    )

@pytest.fixture
async def mock_ollama_client():
    """Mock Ollama client for testing"""
    # Implementation
```

### Async Testing
```python
import pytest

@pytest.mark.asyncio
async def test_document_processing():
    """Test document processing pipeline"""
    processor = DocumentProcessor()
    
    # Test with sample document
    result = await processor.process_file(sample_file_path)
    
    assert result.analysis.summary
    assert len(result.analysis.tags) > 0
    assert result.analysis.confidence > 0.5
```

### UV Testing Commands
```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src

# Run specific test file
uv run pytest tests/test_processors.py -v

# Run only fast tests (exclude slow integration tests)
uv run pytest -m "not slow"
```

## Performance Optimization

### Ollama Optimization
- Use smaller models for simple tasks
- Implement proper connection pooling
- Set appropriate timeouts
- Monitor NPU utilization for AI HX 370

### Vector Database Optimization
- Batch document additions when possible
- Use appropriate chunk sizes (3000 chars recommended)
- Implement embedding caching
- Regular database cleanup

### Memory Management
```python
# Limit concurrent operations
async with asyncio.Semaphore(max_concurrent) as sem:
    async with sem:
        await process_document(doc)

# Clean up resources
async with OllamaClient() as client:
    # Operations here
    pass  # Client automatically closed
```

## Common Issues and Solutions

### GenerationResult API Compatibility
**Issue**: `GenerationResult.__init__() got an unexpected keyword argument 'done_reason'`

**Solution**: Use the `from_dict()` class method for robust field handling:
```python
# Correct approach
result = GenerationResult.from_dict(response_data)

# The from_dict method handles new fields gracefully
@classmethod
def from_dict(cls, data: Dict[str, Any]) -> 'GenerationResult':
    kwargs = {
        'response': data.get('response', ''),
        'model': data.get('model', ''),
        # ... handle all fields with defaults
    }
    return cls(**kwargs)
```

### Ollama Model Loading
**Issue**: Model not found errors

**Solution**: Always check and pull models:
```python
if not await client.model_exists(model_name):
    await client.pull_model(model_name)
```

### Vector Database Persistence
**Issue**: Embeddings not persisting between sessions

**Solution**: Use absolute paths and ensure directory creation:
```python
persist_dir = Path(config.vector.persist_directory).resolve()
persist_dir.mkdir(parents=True, exist_ok=True)
```

## Debugging and Logging

### Enable Debug Logging
```yaml
# config.yaml
log_level: "DEBUG"
```

### CLI Debugging
```bash
# Run with debug output
uv run python cli/prismweave.py --log-level DEBUG health

# Check vector database health
uv run python cli/prismweave.py vector-health

# Verify specific document
uv run python cli/prismweave.py vector-verify "document_id"
```

### Code Debugging
```python
import logging
logger = logging.getLogger(__name__)

# Add debug statements
logger.debug(f"Processing document: {file_path}")
logger.info(f"Generated {len(embeddings)} embeddings")
logger.warning(f"Model {model_name} not found, attempting to pull")
```

## Integration Points

### Browser Extension Integration
- Documents captured by browser extension are processed by this module
- Metadata flows back to browser extension for enhanced UI

### VS Code Extension Integration
- Processed documents available in VS Code sidebar
- Semantic search integration in VS Code command palette

### GitHub Repository Integration
- Processed documents stored in PrismWeaveDocs repository
- Vector database persisted alongside documents

## Development Workflow

### Adding New Features
1. Create feature branch
2. Update `pyproject.toml` if new dependencies needed
3. Run `uv sync` to install dependencies
4. Implement feature with proper async patterns
5. Add tests with `pytest`
6. Update configuration if needed
7. Test with CLI commands

### UV Package Management
```bash
# Add new dependency
uv add package-name

# Add development dependency
uv add --group dev package-name

# Update dependencies
uv sync --upgrade

# Remove dependency
uv remove package-name

# Show dependency tree
uv tree
```

### Code Quality
```bash
# Format code
uv run black src/ cli/ tests/

# Sort imports
uv run isort src/ cli/ tests/

# Type checking
uv run mypy src/

# Linting
uv run flake8 src/ cli/
```

## Best Practices

### Async Programming
- Always use `async with` for resource management
- Handle timeouts and cancellation properly
- Use semaphores to limit concurrency
- Prefer `asyncio.gather()` for parallel operations

### Error Handling
- Wrap external API calls in try-catch
- Provide meaningful error messages
- Log errors at appropriate levels
- Implement graceful degradation

### Configuration
- Use type hints for configuration classes
- Validate configuration on startup
- Provide sensible defaults
- Document all configuration options

### Testing
- Write async tests with proper fixtures
- Mock external dependencies (Ollama, ChromaDB)
- Test error conditions and edge cases
- Use appropriate test markers (`@pytest.mark.slow`)

### Documentation
- Document all public APIs
- Include usage examples
- Keep README.md updated
- Add inline comments for complex logic

## Future Enhancements

### Planned Features
- RAG (Retrieval Augmented Generation) improvements
- Multi-modal document processing (images, PDFs)
- Advanced query expansion and semantic routing
- Performance metrics and monitoring
- Distributed processing support

### Architecture Evolution
- Plugin system for custom processors
- Advanced caching strategies
- Model fine-tuning capabilities
- Integration with cloud AI services (optional)

---

**Remember**: This module prioritizes privacy and offline operation. All AI processing happens locally using Ollama, ensuring your documents never leave your machine.
