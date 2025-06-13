# AI Processing Pipeline - Copilot Instructions

## Component Overview
Local AI processing system using Ollama for document analysis, tagging, and content generation.

## Technology Focus
- **Ollama**: Local LLM integration and model management
- **Python**: AI processing pipeline and data handling
- **Vector Databases**: Embeddings storage and semantic search
- **NPU Acceleration**: Optimization for AI HX 370 hardware

## Key Development Patterns

### Ollama Integration
- Use official Ollama Python client for API communication
- Implement model lifecycle management (download, load, unload)
- Handle model selection based on task requirements
- Optimize prompts for different model capabilities
- Implement proper error handling and fallbacks

### Document Processing Pipeline
- Chunk documents efficiently for embedding generation
- Extract meaningful metadata from content
- Generate summaries preserving key information
- Create tags based on content analysis
- Implement quality scoring for document importance

### Vector Search Implementation
- Use sentence-transformers for local embeddings
- Implement efficient similarity search algorithms
- Store vectors in SQLite with extensions or Chroma
- Handle incremental updates to vector database
- Optimize query performance for large collections

### Batch Processing System
- Implement async processing queue for scalability
- Provide progress tracking and status updates
- Handle processing failures gracefully
- Support cancellation and retry mechanisms
- Optimize batch sizes for hardware capabilities

## File Organization
```
ai-processing/
├── src/
│   ├── models/           # Ollama model management
│   ├── processors/       # Document processing
│   ├── embeddings/       # Vector generation
│   ├── search/          # Semantic search
│   └── queue/           # Batch processing
├── config/              # Model and processing config
├── tests/              # Test suites
└── requirements.txt    # Python dependencies
```

## NPU Optimization Guidelines
- Use ONNX Runtime with NPU provider when available
- Implement CPU fallback for unsupported operations
- Profile memory usage and optimize batch sizes
- Cache model outputs to reduce computation
- Monitor NPU utilization and temperature

## AI Best Practices
- Validate AI outputs for quality and accuracy
- Implement deterministic processing where possible
- Use appropriate model sizes for tasks
- Handle multilingual content appropriately
- Maintain audit logs for AI decisions

## Performance Considerations
- Lazy load models to reduce startup time
- Use streaming for large document processing
- Implement efficient caching strategies
- Monitor resource usage and throttle when needed
- Optimize prompt engineering for speed and accuracy
