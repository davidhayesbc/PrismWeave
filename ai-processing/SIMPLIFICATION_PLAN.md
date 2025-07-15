# PrismWeave AI-Processing Simplification Plan

## Current State Analysis

The ai-processing module currently contains:
- Complex CLI with multiple commands and features
- Multiple processing strategies and fallback paths
- RAG (Retrieval Augmented Generation) server
- Multiple model interfaces and abstractions
- Extensive configuration management
- Performance monitoring and health checks
- Complex vector search with multiple backends
- API server with OpenAI compatibility
- Extensive testing infrastructure
- Docker configurations
- Integration scripts

## Simplification Objectives

**Primary Goal**: Reduce to ONLY document processing and embedding storage using LangChain

**Keep Only**:
1. Document processing (markdown files → embeddings)
2. Embedding generation and storage via LangChain
3. Basic verification that embeddings are stored correctly
4. Minimal configuration
5. Essential dependencies

**Remove Completely**:
1. CLI interface (complex command structure)
2. API server and RAG endpoints
3. Multiple model fallbacks and strategies
4. Docker configurations
5. Performance monitoring
6. Health checks and diagnostics
7. Complex search functionality
8. OpenAI compatibility layer
9. Integration scripts
10. Web interfaces (Streamlit, Gradio)
11. Graph analysis and relationships
12. Content categorization and tagging
13. Document summarization
14. Non-LangChain code paths

## Step-by-Step Implementation Plan

### Phase 1: Remove Unnecessary Folders and Files
- [ ] Remove `cli/` folder entirely
- [ ] Remove `docker/` folder entirely  
- [ ] Remove `scripts/` folder entirely
- [ ] Remove `integrations/` folder entirely
- [ ] Remove `src/api/` folder entirely
- [ ] Remove `src/rag/` folder entirely
- [ ] Remove `src/models/` folder (replace with LangChain models)
- [ ] Remove complex test files (keep only basic embedding tests)

### Phase 2: Simplify Dependencies
- [ ] Remove from pyproject.toml:
  - FastAPI, uvicorn (API server)
  - Click, rich (CLI tools)
  - NetworkX, scikit-learn (graph analysis)
  - Streamlit, gradio (web interfaces)
  - FAISS, custom search libraries
  - Performance monitoring tools
  - Ollama client dependencies
- [ ] Keep only LangChain dependencies:
  - `langchain`
  - `langchain-community`
  - `langchain-chroma` (for vector store)
  - `chromadb`
  - Basic text processing: `python-frontmatter`, `markdown`

### Phase 3: Create Simplified Core Module
- [ ] Create new `src/core/` module with:
  - `document_processor.py` - LangChain-only document processing
  - `embedding_store.py` - LangChain ChromaDB integration
  - `config.py` - Minimal configuration
  - `__init__.py` - Simple public API

### Phase 4: Implement LangChain-Only Processing
- [ ] `document_processor.py`:
  - Load markdown files with frontmatter
  - Split text using LangChain text splitters
  - Generate embeddings using LangChain embeddings models
  - No fallbacks, no multiple strategies
- [ ] `embedding_store.py`:
  - Use LangChain's ChromaDB integration exclusively
  - Simple add/retrieve/verify operations
  - No complex search or ranking

### Phase 5: Create Simple Entry Point
- [ ] Create `main.py` in root:
  - Single function to process a directory of markdown files
  - Generate embeddings and store in ChromaDB
  - Verify embeddings are stored correctly
  - Basic error handling only

### Phase 6: Minimal Configuration
- [ ] Simplify `config.yaml`:
  - Remove all Ollama configuration
  - Remove API configuration
  - Remove processing timeouts and complexity
  - Keep only: embedding model name, ChromaDB path, chunk size

### Phase 7: Essential Testing
- [ ] Create `test_core.py`:
  - Test document loading and processing
  - Test embedding generation and storage
  - Test verification functionality
  - Remove all other test files

### Phase 8: Update Documentation
- [ ] Rewrite `README.md`:
  - Remove all CLI documentation
  - Remove API documentation
  - Focus only on: "Process documents → Generate embeddings → Store in ChromaDB"
  - Simple usage example

## Final Structure

```
ai-processing/
├── src/
│   └── core/
│       ├── __init__.py
│       ├── document_processor.py
│       ├── embedding_store.py
│       └── config.py
├── tests/
│   └── test_core.py
├── main.py
├── config.yaml
├── pyproject.toml
└── README.md
```

## Dependencies (Final)

```toml
dependencies = [
    "langchain>=0.1.0",
    "langchain-community>=0.0.25",
    "langchain-chroma>=0.1.0",
    "chromadb>=0.4.15",
    "python-frontmatter>=1.0.0",
    "markdown>=3.5.1",
    "pyyaml>=6.0.1",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
]
```

## Usage (Final)

```python
from src.core import process_documents

# Process all markdown files in a directory
process_documents(
    input_dir="../../PrismWeaveDocs/documents",
    embeddings_dir="../../PrismWeaveDocs/.prismweave/chroma_db"
)
```

## Verification Plan

After simplification, verify:
1. [ ] Can load markdown files with frontmatter
2. [ ] Can generate embeddings using LangChain
3. [ ] Can store embeddings in ChromaDB via LangChain
4. [ ] Can verify embeddings are stored correctly
5. [ ] Total code is under 500 lines
6. [ ] No external dependencies beyond LangChain ecosystem

## Risk Assessment

**Low Risk**: 
- Document processing and embedding generation are core LangChain features
- ChromaDB integration is well-established in LangChain

**Medium Risk**:
- May need to adjust chunk sizes for optimal embedding quality
- May need to tune embedding model selection

**High Risk**:
- None identified - this is a significant simplification with well-supported components

## Success Criteria

1. **Simplicity**: Total codebase under 500 lines
2. **Focus**: Only document processing and embedding storage
3. **LangChain Only**: No custom implementations, use LangChain patterns
4. **Reliability**: All embeddings stored correctly and verifiable
5. **Maintainability**: Simple structure easy to understand and modify

## Timeline

- Phase 1-2: Remove files and dependencies (1 hour)
- Phase 3-4: Implement core functionality (2 hours)  
- Phase 5-6: Entry point and configuration (30 minutes)
- Phase 7-8: Testing and documentation (1 hour)
- **Total**: ~4.5 hours of focused work

## Questions for Clarification

1. Should we keep any specific embedding model, or use LangChain defaults?
2. Do you want to preserve any existing ChromaDB data, or start fresh?
3. Should the entry point be a Python script or just importable functions?
4. Any specific chunk size requirements for the documents?
