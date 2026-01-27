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

### Aspire Orchestration + OpenTelemetry

This repo includes a file-based Aspire AppHost that can orchestrate the Python API/MCP server plus the dev UIs, and routes logs/traces/metrics via OpenTelemetry to the Aspire dashboard.

Files:

- [apphost.cs](apphost.cs)
- [apphost.run.json](apphost.run.json)

Prereqs:

- .NET SDK 10+
- Aspire CLI (`aspire`)

Run (from repo root):

```bash
npm run aspire:run
# or: aspire run
# or (no Aspire CLI): npm run aspire:run:dotnet
```

VS Code (recommended for dev):

- Open the Run & Debug panel and start **"Aspire: Run AppHost (dotnet run)"**.
- It will run `dotnet run apphost.cs` and auto-open the Aspire dashboard when it prints the dashboard URL.

Note:

- The default settings in `apphost.run.json` configure the dashboard to run over HTTP (to avoid dev-certs trust issues) and set `ASPIRE_ALLOW_UNSECURED_TRANSPORT=true`.

Verify:

- Open the dashboard URL printed by the CLI and confirm `ai-processing`, `visualization`, and `website` are healthy.
- Hit the `ai-processing` `/health` endpoint and confirm traces appear in the dashboard.
- Confirm `ai-processing` startup logs appear in the dashboard logs view.

MCP URL:

- In the dashboard, copy the `ai-processing` HTTP endpoint base URL and append `/sse`.
  - Example: `http://127.0.0.1:4001/sse`

Tip:

- Set `PRISMWEAVE_OTEL_CONSOLE_PASSTHROUGH=0` to suppress duplicated stdout when Node console logs are also exported to OpenTelemetry.

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

### Setup

1. **Clone repository and install dependencies:**

```bash
git clone https://github.com/davidhayesbc/PrismWeave.git
cd PrismWeave
npm install  # Installs all workspace dependencies
```

2. **Build all components:**

```bash
npm run build:browser-extension
npm run build:cli
npm run build:web
```

### Running Tests

```bash
# CLI tests (120 tests, fast)
npm run test:cli

# Browser extension tests (comprehensive, may take longer)
npm run test:browser-extension

# AI processing tests
cd ai-processing
uv sync
uv run pytest
```

### Development Workflow

**Working on a specific component:**

```bash
# Browser extension with auto-rebuild
cd browser-extension
npm run dev

# Website with live server
cd website
npm run dev

# Visualization with Vite dev server
cd visualization
npm run dev

# CLI in watch mode
cd cli
npm run build -- --watch
```

**TypeScript compilation:**

```bash
# Check all components
npx tsc --build

# Check specific component
cd cli && npx tsc --noEmit
```

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
