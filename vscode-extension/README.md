# PrismWeave RAG Assistant - VS Code Extension

A VS Code extension that provides intelligent document querying and generation using local LLM models and ChromaDB RAG capabilities.

## Features

- **Multi-Model Support**: Supports ONNX, Phi-Silica, and custom LLM models
- **ChromaDB Integration**: Intelligent document retrieval from your document collection
- **Interactive Chat Interface**: GitHub Copilot-style sidebar for natural conversations
- **Document Generation**: Create new markdown articles with citations
- **Web Integration**: Query web sources alongside your documents (planned)
- **MCP Tools**: Extensible tool system using Model Context Protocol (planned)

## Installation

1. Clone this repository
2. Install dependencies: `npm install`
3. Compile the extension: `npm run compile`
4. Open in VS Code and press F5 to launch the extension development host

## Configuration

Configure the extension in your VS Code settings:

```json
{
  "prismweave.chromadb.host": "localhost",
  "prismweave.chromadb.port": 8000,
  "prismweave.chromadb.collection": "documents",
  "prismweave.model.provider": "onnx",
  "prismweave.model.name": "path/to/your/model",
  "prismweave.documents.articlesPath": "../PrismWeaveDocs/articles",
  "prismweave.web.enabled": true,
  "prismweave.mcp.enabled": false
}
```

## Prerequisites

- **ChromaDB Server**: Must be running and accessible at the configured host/port
- **Model Files**: ONNX or Phi-Silica models must be available at the specified paths
- **Node.js**: Version 16 or higher for development

## Usage

1. **Open the RAG Assistant**: Click the PrismWeave icon in the Activity Bar or use the command palette
2. **Ask Questions**: Type your questions in the chat interface
3. **Generate Documents**: Use the "Generate Document" command to create new articles
4. **Search Documents**: Use the "Search Documents" command for quick lookups

## Development

### Project Structure

```
src/
├── extension.ts              # Main extension entry point
├── models/                   # LLM model abstractions
│   ├── base-model.ts
│   ├── onnx-model.ts
│   ├── phi-silica-model.ts
│   └── model-manager.ts
├── rag/                      # RAG and ChromaDB integration
│   └── document-retriever.ts
├── ui/                       # UI components
│   └── sidebar-provider.ts
├── utils/                    # Utilities
│   ├── config.ts
│   └── logger.ts
└── types/                    # Type definitions
    ├── models.ts
    ├── rag.ts
    └── ui.ts
```

### Build Commands

- `npm run compile`: Compile TypeScript to JavaScript
- `npm run watch`: Watch for changes and recompile
- `npm run lint`: Run ESLint
- `npm run test`: Run tests (when available)

### Implementation Status

This is a shell project with the core architecture in place. Current implementation includes:

- ✅ Basic extension structure and configuration
- ✅ Model abstraction layer with placeholder implementations
- ✅ ChromaDB integration framework
- ✅ Interactive chat sidebar with VS Code theming
- ✅ Command registration and basic error handling
- ✅ TypeScript types and interfaces

### Next Steps

See the [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) for detailed development phases:

1. **Phase 1**: Project setup (✅ Complete)
2. **Phase 2**: LLM model integration (In Progress)
3. **Phase 3**: ChromaDB RAG integration
4. **Phase 4**: Enhanced UI components
5. **Phase 5**: MCP tools integration
6. **Phase 6**: Web querying capabilities
7. **Phase 7**: Document generation
8. **Phase 8**: Advanced features

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

This project is part of the PrismWeave ecosystem. See the main project for licensing information.

## Support

For issues and questions, please use the GitHub Issues system or refer to the main PrismWeave documentation.
