# Copilot Instructions for PrismWeave Project

<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

## Project Overview
PrismWeave is a comprehensive document management and content creation system that captures web pages as markdown, syncs via Git, and uses local AI for processing and content generation.

## Core Architecture
- **Browser Extension**: Chrome/Edge Manifest V3 for web page capture
- **AI Processing**: Local Ollama integration with NPU acceleration (AI HX 370)
- **Storage**: Git-based repository with markdown files and vector database
- **Interface**: VS Code extension for document management and content creation
- **Sync**: Multi-device GitHub synchronization

## Development Guidelines

### Code Quality Standards
- Use TypeScript for all JavaScript/Node.js code
- Follow functional programming patterns where appropriate
- Implement comprehensive error handling and logging
- Write unit tests for core functionality
- Use async/await for asynchronous operations

### Browser Extension Development
- Target Manifest V3 for Chrome/Edge compatibility
- Implement content scripts for clean HTML extraction
- Use background service workers for Git operations
- Follow Chrome extension security best practices
- Optimize for performance and minimal memory usage
- **CRITICAL**: Service workers must be self-contained, no ES6 modules or importScripts
- Implement all functionality directly in service worker files
- Use inline type definitions and classes for Chrome extension compatibility
- Avoid external dependencies in service workers to prevent loading issues

### AI Integration Best Practices
- Use local models (Ollama) for privacy and cost efficiency
- Implement proper model lifecycle management
- Optimize for AI HX 370 NPU acceleration
- Handle AI processing failures gracefully
- Implement batch processing for efficiency

### VS Code Extension Development
- Follow VS Code extension API best practices
- Use TreeDataProvider for document explorer
- Implement proper webview security
- Integrate with VS Code's built-in Git functionality
- Support VS Code themes and accessibility

### Git Integration
- Implement atomic commits for document changes
- Use meaningful commit messages with document metadata
- Handle merge conflicts intelligently
- Support both manual and automatic push strategies
- Maintain clean repository structure

### File Management
- Use YAML frontmatter for document metadata
- Implement consistent file naming conventions
- Organize documents by topic/category automatically
- Handle image assets efficiently
- Support markdown standards (CommonMark)

### Security Considerations
- Secure GitHub token storage and handling
- Sanitize all user inputs and captured content
- Implement proper CORS handling in extensions
- Use secure communication between components
- Follow principle of least privilege

## Project Structure
```
PrismWeave/
├── .github/                # GitHub configuration
│   ├── instructions/       # Specialized Copilot instructions
│   └── copilot-instructions.md
├── .vscode/               # VS Code workspace settings
├── browser-extension/     # Chrome/Edge extension
│   ├── src/
│   │   ├── __tests__/     # Jest test files
│   │   ├── background/    # Service worker
│   │   ├── content/       # Content scripts
│   │   ├── options/       # Extension options page
│   │   ├── popup/         # Extension popup
│   │   └── utils/         # Shared utilities
│   ├── icons/             # Extension icons
│   ├── scripts/           # Build scripts
│   ├── coverage/          # Test coverage reports
│   └── dist/              # Built extension files
├── ai-processing/         # Local AI integration (Ollama)
├── vscode-extension/      # VS Code extension for document management
└── docs/                  # Project documentation
    ├── IMPLEMENTATION_PLAN.md
    ├── REQUIREMENTS.md
    └── PHASE1_COMPLETE.md
```

## Repository Structure (Target for captured content)
```
prismweave-repo/
├── documents/              # Captured markdown files
├── images/                 # Captured images  
├── .prismweave/           # System metadata and vector DB
├── generated/             # AI-created content
└── .github/               # GitHub configuration
```

## Technology Stack
- **Frontend**: TypeScript, Chrome Extension APIs, VS Code Extension API
- **Backend**: Python for AI processing, Node.js for utilities
- **AI**: Ollama, sentence-transformers, local embeddings
- **Database**: SQLite with vector extensions
- **Version Control**: Git with GitHub API integration

## Naming Conventions
- Use camelCase for JavaScript/TypeScript variables and functions
- Use PascalCase for classes and interfaces
- Use kebab-case for file names and CSS classes
- Use SCREAMING_SNAKE_CASE for constants
- Prefix interfaces with 'I' (e.g., IDocument, ICapture)

## Testing Strategy
- Unit tests for core business logic
- Integration tests for AI processing pipeline
- End-to-end tests for browser extension workflow
- Performance tests for large document collections
- Cross-browser compatibility testing

## Performance Optimization
- Lazy load document content in VS Code extension
- Implement efficient vector search algorithms
- Use streaming for large file operations
- Optimize AI model loading and caching
- Minimize memory usage in browser extension

## Content Creation Guidelines
When generating articles or blog posts:
- Reference source documents with proper citations
- Maintain factual accuracy from source material
- Use clear, engaging writing style
- Include relevant tags and metadata
- Generate proper markdown formatting

## AI Processing Guidelines
- Chunk documents appropriately for embedding generation
- Use appropriate model sizes for different tasks
- Implement progress tracking for long operations
- Cache AI results to avoid reprocessing
- Handle multilingual content appropriately

## Specialized Instructions
- **Testing**: Use `.github/instructions/copilot-instructions-testing.md` for Jest test creation
- **Browser Extension**: Use `browser-extension/copilot-instructions.md` for extension-specific code
- **AI Processing**: Use `ai-processing/copilot-instructions.md` for AI/ML related code
- **VS Code Extension**: Use `vscode-extension/copilot-instructions.md` for VS Code API code

## Common Issues and Solutions

### Browser Extension Module Compatibility
**Problem**: `Uncaught SyntaxError: Unexpected token 'export'` in service worker
**Solution**: 
1. Use ES2020 modules in TypeScript for clean development
2. Post-build conversion removes ES6 exports for service worker compatibility
3. Use global assignments for service worker importScripts
4. Maintain dual compatibility for different extension contexts

**Correct Pattern**:
```typescript
// Service worker - NO ES6 imports/exports after build
interface IMessageData { type: string; }

// Utility files - ES6 in source, converted for service worker
class MyUtil { }
export { MyUtil };  // Removed in service worker build
// Global assignments remain
if (typeof self !== 'undefined') {
  self.MyUtil = MyUtil;
}
```
