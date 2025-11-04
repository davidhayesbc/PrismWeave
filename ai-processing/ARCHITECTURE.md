# PrismWeave AI Processing - Architecture Documentation

**System Design and Component Interactions**

This document provides a comprehensive overview of the AI processing module's architecture, design decisions, and component interactions.

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Component Architecture](#component-architecture)
3. [Data Flow](#data-flow)
4. [LangChain Integration](#langchain-integration)
5. [Git Tracking Mechanism](#git-tracking-mechanism)
6. [Storage Architecture](#storage-architecture)
7. [Configuration System](#configuration-system)
8. [Error Handling Strategy](#error-handling-strategy)
9. [Testing Architecture](#testing-architecture)
10. [Performance Considerations](#performance-considerations)

---

## System Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      PrismWeave Ecosystem                    │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐      ┌──────────────┐      ┌───────────┐ │
│  │   Browser    │      │   VS Code    │      │  GitHub   │ │
│  │  Extension   │──────│  Extension   │──────│Repository │ │
│  └──────────────┘      └──────────────┘      └───────────┘ │
│         │                      │                     │       │
│         └──────────────────────┼─────────────────────┘       │
│                                │                             │
│                                ▼                             │
│                   ┌────────────────────────┐                │
│                   │   AI Processing Core   │                │
│                   │    (This Module)       │                │
│                   └────────────────────────┘                │
│                                │                             │
│                   ┌────────────┴────────────┐              │
│                   ▼                          ▼              │
│           ┌──────────────┐         ┌─────────────┐         │
│           │    Ollama    │         │  ChromaDB   │         │
│           │   (Local)    │         │  (Vector)   │         │
│           └──────────────┘         └─────────────┘         │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### Design Principles

1. **Local-First**: All AI processing happens locally via Ollama
2. **Privacy-Focused**: No external API calls, no data leaves the machine
3. **LangChain Native**: Built on LangChain ecosystem for reliability
4. **Git-Aware**: Intelligent incremental processing using git tracking
5. **Testable**: Comprehensive test coverage with clear boundaries
6. **Maintainable**: Simple, focused code with minimal dependencies

---

## Component Architecture

### Core Modules

```
src/core/
├── config.py              # Configuration management
├── document_processor.py  # Document loading and chunking
├── embedding_store.py     # Vector storage operations
└── git_tracker.py         # Git-based change tracking
```

### Module Responsibilities

#### config.py (150 LOC)

**Purpose**: Centralized configuration management

**Key Classes**:

- `Config`: Main configuration class with validation

**Responsibilities**:

- Load configuration from YAML files
- Provide default values
- Validate configuration settings
- Path resolution and normalization

**Public API**:

```python
class Config:
    # Properties
    ollama_host: str
    embedding_model: str
    chunk_size: int
    chunk_overlap: int
    chroma_db_path: Path
    collection_name: str

    # Methods
    @classmethod
    def from_file(cls, config_path: Path) -> Config
    def validate(self) -> List[str]
```

#### document_processor.py (200 LOC)

**Purpose**: Load and chunk documents using LangChain

**Key Classes**:

- `DocumentProcessor`: Main document processing engine

**Responsibilities**:

- Select appropriate LangChain loader for file type
- Extract frontmatter metadata from markdown
- Split documents into optimal chunks
- Preserve metadata through processing pipeline
- Track processed files via GitTracker

**Public API**:

```python
class DocumentProcessor:
    def __init__(self, config: Config, git_tracker: Optional[GitTracker] = None)
    def process_document(self, file_path: Path) -> List[Document]
    def get_loader_for_file(self, file_path: Path) -> Any
```

**Supported Formats**:

- Markdown (`.md`) - with frontmatter support
- PDF (`.pdf`) - via PyPDFLoader
- Word (`.docx`) - via Docx2txtLoader
- HTML (`.html`, `.htm`) - via BSHTMLLoader
- Text (`.txt`) - via TextLoader

#### embedding_store.py (250 LOC)

**Purpose**: Manage ChromaDB vector storage operations

**Key Classes**:

- `EmbeddingStore`: Vector database interface

**Responsibilities**:

- Initialize ChromaDB with Ollama embeddings
- Add documents with metadata preservation
- Search for similar documents
- Manage document lifecycle (add, remove, update)
- Provide collection statistics and verification
- Track document processing via GitTracker

**Public API**:

```python
class EmbeddingStore:
    def __init__(self, config: Config, git_tracker: Optional[GitTracker] = None)
    def add_document(self, file_path: Path, chunks: List[Document]) -> None
    def search_similar(self, query: str, k: int = 5) -> List[Document]
    def remove_file_documents(self, file_path: Path) -> None
    def get_file_document_count(self, file_path: Path) -> int
    def verify_embeddings(self) -> Dict[str, Any]
    def list_documents(self, max_documents: Optional[int] = 50) -> List[Dict]
    def get_document_count(self) -> int
    def get_unique_source_files(self) -> List[str]
    def clear_collection(self) -> None
```

#### git_tracker.py (200 LOC)

**Purpose**: Track document processing state using git commits

**Key Classes**:

- `GitTracker`: Git-based processing state manager

**Responsibilities**:

- Track which files have been processed
- Detect new or changed files since last processing
- Store processing state in `.prismweave` directory
- Provide processing summaries and statistics
- Reset processing state when needed

**Public API**:

```python
class GitTracker:
    def __init__(self, repo_path: Path)
    def is_file_processed(self, file_path: Path) -> bool
    def mark_file_processed(self, file_path: Path) -> None
    def get_unprocessed_files(self, file_extensions: Optional[Set[str]] = None) -> List[Path]
    def update_last_processed_commit(self) -> None
    def reset_processing_state(self) -> None
    def get_processing_summary(self) -> Dict[str, int]
```

---

## Data Flow

### Document Processing Pipeline

```
┌──────────────┐
│ Input File   │
│ (.md, .pdf,  │
│  .docx, etc) │
└──────┬───────┘
       │
       ▼
┌─────────────────────────────────────────────┐
│ Step 1: Document Loading (DocumentProcessor)│
│ - Select appropriate LangChain loader       │
│ - Load file content                         │
│ - Extract frontmatter (if markdown)         │
└──────┬──────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────┐
│ Step 2: Text Splitting (DocumentProcessor)  │
│ - RecursiveCharacterTextSplitter            │
│ - chunk_size: 1000 chars                    │
│ - chunk_overlap: 200 chars                  │
│ - Preserve metadata in each chunk           │
└──────┬──────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────┐
│ Step 3: Metadata Enrichment                 │
│ - Add source_file path                      │
│ - Add chunk_index and total_chunks          │
│ - Preserve frontmatter tags, title, etc.    │
│ - Clean metadata for ChromaDB compatibility │
└──────┬──────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────┐
│ Step 4: Embedding Generation (Ollama)       │
│ - Generate embeddings via OllamaEmbeddings  │
│ - Model: nomic-embed-text                   │
│ - Local processing via Ollama server        │
└──────┬──────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────┐
│ Step 5: Vector Storage (ChromaDB)           │
│ - Store embeddings in ChromaDB collection   │
│ - Preserve all metadata                     │
│ - Persist to disk                           │
└──────┬──────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────┐
│ Step 6: Git Tracking (Optional)             │
│ - Mark file as processed                    │
│ - Record git commit hash                    │
│ - Update processing state                   │
└─────────────────────────────────────────────┘
```

### Incremental Processing Flow

```
┌──────────────┐
│ Process      │
│ Request      │
└──────┬───────┘
       │
       ▼
┌─────────────────────────────────────────────┐
│ GitTracker: Check Processing State          │
│ - Get current git commit                    │
│ - Load last processed commit                │
│ - Compare commits                           │
└──────┬──────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────┐
│ GitTracker: Detect Changed Files            │
│ - Get git diff between commits              │
│ - Filter by supported extensions            │
│ - Check against processed file list         │
└──────┬──────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────┐
│ Process Only Unprocessed Files              │
│ - Skip already-processed files              │
│ - Process new or changed files              │
│ - Update existing embeddings if needed      │
└──────┬──────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────┐
│ Update Processing State                     │
│ - Mark newly processed files                │
│ - Update last processed commit              │
│ - Save state to .prismweave directory       │
└─────────────────────────────────────────────┘
```

---

## LangChain Integration

### Why LangChain?

**Benefits**:

1. **Mature Ecosystem**: Well-tested, production-ready components
2. **Consistent APIs**: Uniform interfaces across document loaders
3. **Active Development**: Regular updates and improvements
4. **Community Support**: Large user base and extensive documentation
5. **Integration Ready**: Easy to extend with additional capabilities

### LangChain Components Used

#### Document Loaders

```python
from langchain_community.document_loaders import (
    UnstructuredMarkdownLoader,  # Markdown with metadata
    PyPDFLoader,                  # PDF documents
    Docx2txtLoader,               # Word documents
    BSHTMLLoader,                 # HTML files
    TextLoader                    # Plain text
)

# Usage pattern
loader = UnstructuredMarkdownLoader(file_path)
documents = loader.load()  # Returns List[Document]
```

#### Text Splitting

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,        # Target chunk size
    chunk_overlap=200,      # Overlap for context
    length_function=len,    # Character-based splitting
    separators=["\n\n", "\n", " ", ""]  # Priority order
)

chunks = text_splitter.split_documents(documents)
```

**Why RecursiveCharacterTextSplitter?**

- Preserves document structure
- Respects natural boundaries (paragraphs, sentences)
- Configurable overlap for context
- Character-based for consistent sizing

#### Embeddings

```python
from langchain_ollama import OllamaEmbeddings

embeddings = OllamaEmbeddings(
    model="nomic-embed-text",
    base_url="http://localhost:11434"
)

# Generate embeddings for text
vectors = embeddings.embed_documents(["text1", "text2"])

# Generate embedding for query
query_vector = embeddings.embed_query("search query")
```

**Why nomic-embed-text?**

- Optimized for semantic search
- Good balance of speed and quality
- Runs efficiently on consumer hardware
- Supports long context windows

#### Vector Store

```python
from langchain_chroma import Chroma

vectorstore = Chroma(
    collection_name="documents",
    embedding_function=embeddings,
    persist_directory=".prismweave/chroma_db"
)

# Add documents
vectorstore.add_documents(chunks)

# Search
results = vectorstore.similarity_search(query, k=5)
```

### Document Object Structure

LangChain's `Document` class:

```python
class Document:
    page_content: str              # The actual text content
    metadata: Dict[str, Any]       # Associated metadata

# Example
Document(
    page_content="# React Hooks\n\nHooks are...",
    metadata={
        "source": "/path/to/file.md",
        "source_file": "/path/to/file.md",
        "title": "React Hooks Guide",
        "tags": ["react", "hooks", "frontend"],
        "chunk_index": 0,
        "total_chunks": 8
    }
)
```

---

## Git Tracking Mechanism

### State Storage

Processing state is stored in `.prismweave/processing_state.json`:

```json
{
  "last_processed_commit": "abc123def456...",
  "processed_files": {
    "documents/tech/react-hooks.md": {
      "commit": "abc123def456...",
      "processed_at": "2025-11-03T10:30:00",
      "chunk_count": 8
    },
    "documents/tech/vue-guide.md": {
      "commit": "abc123def456...",
      "processed_at": "2025-11-03T10:31:00",
      "chunk_count": 6
    }
  }
}
```

### Change Detection Algorithm

```python
def get_unprocessed_files(self) -> List[Path]:
    """
    1. Get current git commit hash
    2. Get last processed commit from state
    3. Run: git diff --name-only <last_commit>..<current_commit>
    4. Filter results by supported extensions
    5. Add any new files not in processed_files
    6. Return combined list of unprocessed files
    """
```

### Processing Workflow

```
┌─────────────────────────────────────────┐
│ User runs: python cli.py sync          │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│ GitTracker.get_unprocessed_files()      │
│ - Compares current vs last commit      │
│ - Returns list of changed files         │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│ Process each unprocessed file           │
│ - DocumentProcessor.process_document()  │
│ - EmbeddingStore.add_document()         │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│ GitTracker.mark_file_processed()        │
│ - Updates processed_files state         │
│ - Records current commit hash           │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│ GitTracker.update_last_processed_commit()│
│ - Saves state to disk                   │
│ - Updates last_processed_commit         │
└─────────────────────────────────────────┘
```

### Benefits of Git Integration

1. **Efficiency**: Only process changed files (90%+ time savings)
2. **Reliability**: Git commit hashes provide audit trail
3. **Simplicity**: Leverages existing git workflow
4. **Accuracy**: Detects exact file changes
5. **Rollback**: Can reprocess specific commits if needed

---

## Storage Architecture

### ChromaDB Collection Structure

```
Collection: "documents"
├── Embeddings (vectors)
├── Documents (text content)
├── Metadata (structured data)
└── IDs (unique identifiers)
```

### Metadata Schema

```python
{
    "source": str,              # Full file path (required by ChromaDB)
    "source_file": str,         # Normalized file path
    "title": str,               # Document title (from frontmatter or filename)
    "tags": List[str],          # Tags from frontmatter
    "chunk_index": int,         # Chunk position (0-based)
    "total_chunks": int,        # Total chunks for this file
    "category": str,            # Optional category
    "author": str,              # Optional author
    "date": str,                # Optional date
    # ... additional frontmatter fields
}
```

### Metadata Cleaning

ChromaDB requires metadata to be JSON-serializable. The `clean_metadata()` function:

```python
def clean_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    1. Convert non-JSON types to strings
    2. Remove None values
    3. Handle nested structures
    4. Preserve required fields
    """
```

### Storage Location

Default: `../../PrismWeaveDocs/.prismweave/chroma_db/`

Structure:

```
.prismweave/
├── chroma_db/               # ChromaDB collection data
│   ├── chroma.sqlite3       # SQLite database
│   └── [vector files]       # Binary vector data
└── processing_state.json    # Git tracking state
```

---

## Configuration System

### Configuration File Format

```yaml
# Ollama Server Configuration
ollama:
  host: http://localhost:11434
  timeout: 60
  models:
    embedding: 'nomic-embed-text'

# Document Processing Configuration
processing:
  chunk_size: 1000
  chunk_overlap: 200

# Vector Database Configuration
vector:
  collection_name: 'documents'
  persist_directory: '../../PrismWeaveDocs/.prismweave/chroma_db'
```

### Configuration Loading Priority

1. **Explicit Config**: `--config path/to/config.yaml`
2. **Default Config**: `./config.yaml` in ai-processing directory
3. **Defaults**: Hardcoded values in `Config` class

### Configuration Validation

```python
def validate(self) -> List[str]:
    """
    Validates:
    - Ollama host is accessible
    - Model name is specified
    - Chunk size is reasonable (100-10000)
    - Persist directory is writable
    - Collection name is valid
    """
```

---

## Error Handling Strategy

### Error Categories

1. **Configuration Errors**: Invalid config, missing models
2. **Document Errors**: File not found, unsupported format
3. **Processing Errors**: Chunking failures, metadata issues
4. **Storage Errors**: ChromaDB failures, disk space
5. **Git Errors**: Invalid repo, git not available

### Error Handling Pattern

```python
try:
    # Operation
    result = process_document(file_path)
except FileNotFoundError:
    # Specific error handling
    print(f"❌ File not found: {file_path}")
except Exception as e:
    # Generic error handling
    print(f"❌ Processing failed: {e}")
    if verbose:
        traceback.print_exc()
```

### User-Friendly Error Messages

- ✅ Clear emoji indicators (❌, ⚠️, ✅)
- ✅ Actionable suggestions for fixes
- ✅ Detailed logging in verbose mode
- ✅ Context-specific error messages

Example:

```
❌ Cannot connect to Ollama at http://localhost:11434

💡 Make sure Ollama is running:
   ollama serve
   ollama pull nomic-embed-text
```

---

## Testing Architecture

### Test Structure

```
tests/
├── conftest.py                    # Shared fixtures
├── test_core.py                   # Config & DocumentProcessor (8 tests)
├── test_embedding_store.py        # EmbeddingStore (17 tests)
├── test_git_tracker.py            # GitTracker (21 tests)
└── test_simple_integration.py     # End-to-end (5 tests)
```

### Test Categories

#### Unit Tests

- Test individual methods in isolation
- Mock external dependencies (Ollama, ChromaDB, git)
- Fast execution (<1s per test)

#### Integration Tests

- Test component interactions
- Use real file system operations
- May use mocked AI components

#### End-to-End Tests

- Test complete workflows
- Real file processing (using temp directories)
- Verify actual behavior

### Key Testing Patterns

#### Fixture Usage

```python
@pytest.fixture
def temp_repo(tmp_path):
    """Create temporary git repository for testing"""
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()
    # Initialize git
    subprocess.run(["git", "init"], cwd=repo_path)
    return repo_path
```

#### Mocking ChromaDB

```python
@pytest.fixture
def mock_chroma():
    """Mock ChromaDB collection"""
    with patch('chromadb.Client') as mock:
        collection = MagicMock()
        mock.return_value.get_or_create_collection.return_value = collection
        yield collection
```

#### Test Data

```python
@pytest.fixture
def sample_markdown_with_frontmatter(tmp_path):
    """Create sample markdown file"""
    file_path = tmp_path / "test.md"
    content = """---
title: Test Document
tags: [test, example]
---

# Content Here
"""
    file_path.write_text(content)
    return file_path
```

---

## Performance Considerations

### Bottlenecks

1. **Embedding Generation**: 2-5s per document (Ollama dependent)
2. **File I/O**: Minimal impact with SSD
3. **ChromaDB Operations**: <100ms per document
4. **Git Operations**: <50ms per query

### Optimization Strategies

#### 1. Batch Processing

Process multiple files in sequence to amortize startup costs.

#### 2. Incremental Updates

Use git tracking to avoid reprocessing unchanged files.

#### 3. Efficient Chunking

- chunk_size: 1000 (balance between context and granularity)
- chunk_overlap: 200 (ensures continuity)

#### 4. Local Storage

Store ChromaDB on SSD for fast vector operations.

#### 5. Ollama Optimization

- Keep Ollama running (avoid cold starts)
- Use appropriate hardware acceleration (NPU, GPU)
- Monitor resource usage

### Scalability Limits

- **Tested**: 100+ documents (works well)
- **Expected**: 1000+ documents (should work)
- **Limit**: ~10,000 documents before optimization needed

**Note**: ChromaDB is designed for millions of vectors, so scaling is mainly limited by embedding generation time.

---

## Extension Points

### Adding New Document Types

```python
# In document_processor.py
def get_loader_for_file(self, file_path: Path) -> Any:
    # Add new extension
    elif file_path.suffix == '.rst':
        from langchain_community.document_loaders import UnstructuredRSTLoader
        return UnstructuredRSTLoader(str(file_path))
```

### Custom Metadata Extraction

```python
# Override metadata extraction
def extract_custom_metadata(self, file_path: Path) -> Dict:
    # Custom logic here
    return metadata
```

### Alternative Embedding Models

```yaml
# In config.yaml
ollama:
  models:
    embedding: 'your-custom-model'
```

### Custom Search Filters

```python
# Add metadata filters to searches
results = vectorstore.similarity_search(
    query,
    k=5,
    filter={"tags": {"$contains": "python"}}
)
```

---

## Future Architecture Considerations

### Planned Enhancements

1. **FastAPI Server**: Optional REST API for remote access
2. **Real-time Processing**: File watcher for automatic updates
3. **Advanced Search**: Query expansion, semantic routing
4. **Multi-modal**: Image and diagram processing
5. **Distributed**: Support for multiple machines

### Architecture Evolution

```
Current: Simple, focused, local
    ↓
Next: Add REST API layer (optional)
    ↓
Future: Distributed processing, multi-modal support
```

---

## Conclusion

The PrismWeave AI Processing module is designed as a focused, maintainable, and extensible system for document processing and semantic search. The architecture prioritizes simplicity, testability, and local-first operation while providing a solid foundation for future enhancements.

**Key Architectural Decisions**:

- ✅ LangChain for reliability and consistency
- ✅ Git integration for intelligent incremental processing
- ✅ Local Ollama for privacy and cost efficiency
- ✅ ChromaDB for robust vector storage
- ✅ Comprehensive testing for confidence
- ✅ Clear separation of concerns for maintainability

---

**For more information**:

- [README.md](README.md) - User documentation
- [SIMPLIFICATION_PLAN.md](SIMPLIFICATION_PLAN.md) - Implementation history
- [examples/USAGE.md](examples/USAGE.md) - Practical examples
- [tests/](tests/) - Test suite
