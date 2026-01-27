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

**Location:** `ai-processing/`

#### MCP Server (NEW!)

The PrismWeave MCP server enables AI-powered document management directly in VS Code through the Model Context Protocol.

**Key Capabilities:**

**Quick Start:**

```bash
cd ai-processing
uv sync
# Configure VS Code (see ai-processing/prismweave_mcp/VS_CODE_INTEGRATION.md)
```

### MCP (Model Context Protocol)

MCP runs as a separate Aspire resource/process named `mcp-server`.

- MCP SSE endpoint: `{mcp-server base URL}/sse`

In Aspire, copy the `mcp-server` HTTP endpoint from the dashboard and append `/sse`.
Example (with fixed ports): `http://127.0.0.1:4005/sse`.
VS Code integration for document management and content creation.

**Location:** `vscode-extension/`

## Quick Start

### Development (Recommended)

Start all services with Aspire orchestration:

```bash
npm run dev
```

This starts:

- **Aspire Dashboard**: http://localhost:4000 (integrated logging, metrics, health checks)
- **Website**: http://localhost:4003
- **Visualization**: http://localhost:4002
- **MCP Server**: http://localhost:4005
- **MCP Inspector**: http://localhost:4009 (debugging interface)
- **Ollama**: http://localhost:11434 (local AI)

The Aspire dashboard provides a unified view of all services with integrated observability.

### Building Components

```bash
# Build all components
npm run build

# Build specific components
npm run build:browser-extension
npm run build:cli
npm run build:web

# Clean all build artifacts
npm run clean
```

### Testing

```bash
# Run all tests
npm test

# Test specific components
npm run test:cli
npm run test:browser-extension
npm run test:ai
```

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
uv sync  # Install dependencies with uv

# Use CLI tool
python cli.py --help

# Or run within Aspire (recommended)
npm run dev  # Starts all services including AI processing
```

For VS Code MCP integration, see [ai-processing/prismweave_mcp/VS_CODE_INTEGRATION.md](ai-processing/prismweave_mcp/VS_CODE_INTEGRATION.md)

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

## Workspace Architecture

PrismWeave uses **npm workspaces** for efficient monorepo management with shared dependencies and consistent tooling across all TypeScript components.

### TypeScript Configuration

- **Centralized Base Config**: [`tsconfig.base.json`](tsconfig.base.json) provides strict TypeScript settings shared across all components
- **Project References**: Enables incremental builds and better IDE performance
- **Strict Type Checking**: `strict`, `noUncheckedIndexedAccess`, `noImplicitOverride` enabled project-wide

### Build System

**Root-level commands** (from repository root):

```bash
# Build individual components
npm run build:browser-extension
npm run build:cli
npm run build:bookmarklet
npm run build:dev-tools

# Build web components (visualization + website)
npm run build:web
npm run build:web:fast

# Test components
npm run test:cli
npm run test:browser-extension
```

**Component-level builds** (if working within a component):

```bash
cd cli && npm run build
cd browser-extension && npm run build
cd visualization && npm run build
cd website && npm run build
```

### Benefits of Workspace Architecture

1. **Shared Dependencies**: Common tools (TypeScript, Jest, ESLint) hoisted to root
2. **Consistent Configuration**: Unified TypeScript and testing standards
3. **Better Type Safety**: Strict checking catches bugs at compile-time
4. **Incremental Builds**: TypeScript project references enable faster rebuilds
5. **Simplified Installation**: Single `npm install` at root configures everything

### Test Coverage

- **CLI**: 120/120 tests passing (4 test suites)
- **Browser Extension**: Comprehensive integration and unit tests
- **AI Processing**: Pytest-based test suite

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

### Prerequisites

- **Node.js** 16+ and npm 8+
- **.NET SDK** 10+ (for Aspire)
- **Aspire CLI** (`aspire`)
- **Python** 3.10+ with uv (for AI processing)
- **Ollama** (for local AI)

### Setup

1. **Clone and install dependencies:**

```bash
git clone https://github.com/davidhayesbc/PrismWeave.git
cd PrismWeave
npm install  # Installs all workspace dependencies
```

2. **Start development environment:**

```bash
npm run dev  # Starts Aspire with all services
```

Open the **Aspire Dashboard** at http://localhost:4000 to:

- View service health and logs
- Monitor metrics and traces
- Debug service interactions
- Access direct links to each service

### Component-Specific Development

If you need to work on a single component in isolation:

```bash
# Browser extension
cd browser-extension && npm run build

# CLI tool
cd cli && npm test

# AI processing
cd ai-processing && uv run pytest

# Website
cd website && npm run build

# Visualization
cd visualization && npm run dev
```

### Running Tests

```bash
# All tests
npm test

# Component tests
npm run test:cli              # CLI (120 tests)
npm run test:browser-extension  # Extension tests
npm run test:ai               # AI processing tests

# TypeScript type checking
npm run typecheck
```

### Code Quality

```bash
# Format all code
npm run format

# Check formatting
npm run format:check
```

### Production Deployment

```bash
# Build for production
npm run docker:prod:build

# Start production containers
npm run docker:prod

# View production logs
npm run docker:prod:logs

# Stop production containers
npm run docker:prod:down
```

Note: Production uses `docker-compose.prod.yml` (different from development Aspire setup).

## Documentation

- **Browser Extension**: [browser-extension/README.md](browser-extension/README.md)
- **CLI Tool**: [cli/README.md](cli/README.md)
- **CLI Quick Start**: [cli/QUICKSTART.md](cli/QUICKSTART.md)
- **AI Processing**: [ai-processing/README.md](ai-processing/README.md)
- **MCP Server**: [ai-processing/prismweave_mcp/README.md](ai-processing/prismweave_mcp/README.md)
- **VS Code MCP Integration**: [ai-processing/prismweave_mcp/VS_CODE_INTEGRATION.md](ai-processing/prismweave_mcp/VS_CODE_INTEGRATION.md)
- **Visualization Requirements**: [ai-processing/Requirements.md](ai-processing/Requirements.md)
- **Document Organization Refactor**: [REFACTORING_COMPLETE.md](REFACTORING_COMPLETE.md)
- **Solution Structure Index**: [docs/README.md](docs/README.md)

## Contributing

Contributions are welcome! Please see individual component READMEs for specific contribution guidelines.

## License

MIT License - See LICENSE file for details

## Support

For issues, questions, or suggestions:

- GitHub Issues: https://github.com/davidhayesbc/PrismWeave/issues
- Documentation: See component-specific README files
