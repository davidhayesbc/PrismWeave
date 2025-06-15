# Browser Extension Development - Copilot Instructions

## Component Overview

Browser extension for capturing web pages as clean markdown with automatic Git
sync.

## Technology Focus

- **Manifest V3**: Chrome/Edge extension APIs
- **Content Scripts**: DOM manipulation and content extraction
- **Background Service Workers**: File operations and Git integration
- **TypeScript**: Type-safe development

## Key Development Patterns

### Content Script Best Practices

- Use DOM traversal to identify main content areas
- Strip navigation, ads, and non-content elements
- Preserve semantic HTML structure during conversion
- Handle dynamic content loading with mutation observers
- Implement proper event listener cleanup

### Background Service Worker

- Keep service worker lightweight and stateless
- Use chrome.storage for persistent configuration
- Implement proper message passing between contexts
- Handle browser extension lifecycle events
- Manage Git operations without blocking UI

### Markdown Conversion

- Convert semantic HTML to clean markdown
- Preserve code blocks, lists, and formatting
- Handle images with proper alt text and references
- Generate YAML frontmatter with metadata
- Maintain readability over perfect fidelity

### Git Integration

- Use libgit2 or simple-git for repository operations
- Implement atomic commits for consistency
- Generate meaningful commit messages with metadata
- Handle authentication with stored tokens
- Provide conflict resolution strategies

## File Organization

```
browser-extension/
├── manifest.json           # Extension configuration
├── src/
│   ├── content/           # Content scripts
│   ├── background/        # Service worker
│   ├── popup/            # Extension popup UI
│   └── utils/            # Shared utilities
├── dist/                 # Build output
└── tests/               # Test suites
```

## Security Considerations

- Sanitize all captured content
- Use Content Security Policy properly
- Validate all external inputs
- Secure storage of GitHub tokens
- Implement proper CORS handling

## Performance Guidelines

- Minimize memory usage in content scripts
- Use efficient DOM queries and caching
- Implement background processing for heavy operations
- Optimize bundle size with tree shaking
- Lazy load non-critical functionality
