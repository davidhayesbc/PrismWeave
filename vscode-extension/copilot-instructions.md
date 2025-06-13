# VS Code Extension Development - Copilot Instructions

## Component Overview
VS Code extension providing document management, search interface, and content creation tools.

## Technology Focus
- **VS Code Extension API**: TreeDataProvider, commands, webviews
- **TypeScript**: Type-safe extension development
- **Webview API**: Custom UI components for document management
- **Git Integration**: Leverage VS Code's built-in Git functionality

## Key Development Patterns

### Extension Architecture
- Use proper extension activation events
- Implement commands with meaningful IDs
- Create TreeDataProvider for document explorer
- Use webviews for complex UI components
- Follow VS Code extension guidelines and conventions

### Document Management
- Integrate with workspace folders and file watchers
- Provide custom TreeView for document organization
- Implement filtering and search capabilities
- Support drag-and-drop operations
- Handle file system changes reactively

### Search Interface
- Create custom webview for search results
- Implement semantic search with relevance scoring
- Provide search history and saved queries
- Support advanced filtering options
- Integrate with VS Code's search functionality

### Content Creation Tools
- Integrate with GitHub Copilot for enhanced assistance
- Create article generation commands and workflows
- Implement template system for different content types
- Provide real-time preview capabilities
- Support multi-document reference systems

## File Organization
```
vscode-extension/
├── package.json          # Extension manifest
├── src/
│   ├── extension.ts     # Main extension entry point
│   ├── providers/       # Tree data providers
│   ├── commands/        # Command implementations
│   ├── webviews/        # Custom UI components
│   └── utils/           # Shared utilities
├── media/               # Icons and assets
├── syntaxes/           # Language definitions
└── tests/              # Test suites
```

## VS Code API Best Practices
- Use proper disposal patterns for subscriptions
- Implement proper error handling and user feedback
- Follow VS Code theming and accessibility guidelines
- Use appropriate progress indicators for long operations
- Integrate with VS Code's configuration system

### TreeDataProvider Implementation
- Implement efficient data loading and caching
- Support refresh and incremental updates
- Provide proper icons and context menus
- Handle large document collections performantly
- Support sorting and filtering options

### Command Implementation
- Use meaningful command IDs and titles
- Implement proper parameter validation
- Provide user feedback for command execution
- Support undo/redo where appropriate
- Handle concurrent command execution

### Webview Security
- Use proper Content Security Policy
- Sanitize all user inputs and dynamic content
- Implement secure message passing
- Validate all webview communications
- Follow principle of least privilege

## Integration Guidelines
- Leverage existing VS Code Git functionality
- Integrate with workspace trust system
- Support multi-root workspaces
- Follow VS Code extension publishing guidelines
- Implement proper telemetry and error reporting
