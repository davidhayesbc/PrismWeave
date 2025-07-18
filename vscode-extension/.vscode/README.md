# VSCode Extension Development

## Launch Configuration

The extension can be launched and debugged using the following configuration:

1. Open the project in VS Code
2. Press F5 to launch the Extension Development Host
3. In the new window, the extension will be loaded and available

## Commands

- `prismweave.openChat`: Open the RAG chat interface
- `prismweave.generateDocument`: Generate a new document
- `prismweave.searchDocuments`: Search documents in ChromaDB
- `prismweave.refreshModels`: Refresh available models

## Development Notes

This is a shell project with the core architecture in place. Key files:

- `src/extension.ts`: Main extension entry point
- `src/ui/sidebar-provider.ts`: Chat interface implementation
- `src/models/model-manager.ts`: Model abstraction layer
- `src/rag/document-retriever.ts`: ChromaDB integration
- `IMPLEMENTATION_PLAN.md`: Detailed roadmap

The extension is ready for development and can be loaded into VS Code for testing.
