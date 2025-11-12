# PrismWeave

A comprehensive document management and content creation system that captures web pages as markdown, syncs via Git, and uses local AI for processing and content generation.

## Components

### 🌐 Browser Extension

Chrome/Edge extension for capturing web pages directly from your browser.

**Features:**

- One-click web page capture
- Automatic markdown conversion
- GitHub integration
- Smart content extraction
- Support for articles, blogs, documentation

**Location:** `browser-extension/`

### 💻 Command Line Interface (NEW!)

CLI tool for batch capturing and automation.

**Features:**

- Headless browser capture
- Batch processing from URL files
- Automated GitHub commits
- Smart folder organization
- Perfect for automation and scripts

**Location:** `cli/`  
**Quick Start:** See [cli/QUICKSTART.md](cli/QUICKSTART.md)

### 🤖 AI Processing

Local AI integration with Ollama for content processing and generation.

**Features:**

- Local embeddings with sentence-transformers
- NPU acceleration (AI HX 370)
- Document analysis and categorization
- Content generation from captured sources
- **MCP Server:** Model Context Protocol integration for VS Code
- **Semantic Search:** ChromaDB vector database for intelligent document retrieval

**Location:** `ai-processing/`

#### MCP Server (NEW!)

The PrismWeave MCP server enables AI-powered document management directly in VS Code through the Model Context Protocol.

**Key Capabilities:**

- Semantic search across all captured documents
- AI-powered tag generation and categorization
- Create synthesized documents from multiple sources
- Automatic vector embeddings for similarity search
- Git integration for version control

**Quick Start:**

```bash
cd ai-processing
uv sync
# Configure VS Code (see ai-processing/prismweave_mcp/VS_CODE_INTEGRATION.md)
```

**Documentation:**

- [MCP Server README](ai-processing/prismweave_mcp/README.md) - Complete guide
- [VS Code Integration](ai-processing/prismweave_mcp/VS_CODE_INTEGRATION.md) - Setup instructions
- [Troubleshooting](ai-processing/prismweave_mcp/TROUBLESHOOTING.md) - Common issues

### 🔧 VS Code Extension

VS Code integration for document management and content creation.

**Location:** `vscode-extension/`

## Getting Started

### Browser Extension

1. Navigate to `browser-extension/`
2. Run `npm install`
3. Run `npm run build`
4. Load unpacked extension in Chrome/Edge from `browser-extension/dist/`

### CLI Tool

Quick setup:

```bash
cd cli
npm install
npm run build
npm link

# Configure
prismweave config --set githubToken=your_token
prismweave config --set githubRepo=owner/repo

# Capture a page
prismweave capture https://example.com
```

For detailed instructions, see [cli/README.md](cli/README.md) or [cli/QUICKSTART.md](cli/QUICKSTART.md)

### AI Processing

```bash
cd ai-processing
uv sync
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Use CLI tool
python cli.py --help

# Or start MCP server for VS Code integration
# See ai-processing/prismweave_mcp/VS_CODE_INTEGRATION.md
```

## Architecture

```
PrismWeave/
├── browser-extension/   # Chrome/Edge extension
├── cli/                 # Command-line tool
├── ai-processing/       # Local AI integration
│   ├── prismweave_mcp/ # MCP server for VS Code (NEW!)
│   ├── src/            # Core AI processing modules
│   └── cli/            # AI processing CLI
├── vscode-extension/    # VS Code extension
├── shared-styles/       # Shared UI styles
└── website/            # Project website
```

**Document Repository:**

```
PrismWeaveDocs/
├── documents/          # Captured web pages
├── generated/          # AI-synthesized content
├── images/             # Captured images
└── .prismweave/       # Vector database & metadata
```

## Shared Code

The CLI and browser extension share core functionality:

- **Markdown Conversion**: `MarkdownConverterCore` for consistent HTML-to-markdown conversion
- **File Management**: `FileManager` for GitHub operations and file organization
- **Type Definitions**: Shared interfaces and types

This ensures consistency across all capture methods while maintaining code reusability.

## Use Cases

### Browser Extension Use Cases

- Quick article capture while browsing
- Research and documentation gathering
- One-click save for later reading
- Building personal knowledge base

### CLI Use Cases

- Batch processing multiple URLs
- Automated capture scripts
- CI/CD integration
- Scheduled captures (cron jobs)
- Server-side documentation capture
- Team documentation workflows

## Development

### Build All Components

```bash
npm install  # Root dependencies
npm run build  # Builds all components
```

### Run Tests

```bash
# Browser extension tests
cd browser-extension
npm test

# AI processing tests
cd ai-processing
pytest
```

## Documentation

- **Browser Extension**: [browser-extension/README.md](browser-extension/README.md)
- **CLI Tool**: [cli/README.md](cli/README.md)
- **CLI Quick Start**: [cli/QUICKSTART.md](cli/QUICKSTART.md)
- **AI Processing**: [ai-processing/README.md](ai-processing/README.md)
- **MCP Server**: [ai-processing/prismweave_mcp/README.md](ai-processing/prismweave_mcp/README.md)
- **VS Code MCP Integration**: [ai-processing/prismweave_mcp/VS_CODE_INTEGRATION.md](ai-processing/prismweave_mcp/VS_CODE_INTEGRATION.md)
- **Implementation Plan**: [docs/IMPLEMENTATION_PLAN.md](docs/IMPLEMENTATION_PLAN.md)
- **Requirements**: [docs/REQUIREMENTS.md](docs/REQUIREMENTS.md)

## Contributing

Contributions are welcome! Please see individual component READMEs for specific contribution guidelines.

## License

MIT License - See LICENSE file for details

## Support

For issues, questions, or suggestions:

- GitHub Issues: https://github.com/davidhayesbc/PrismWeave/issues
- Documentation: See component-specific README files
