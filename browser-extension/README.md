# PrismWeave Browser Extension

[![Chrome Web Store](https://img.shields.io/badge/chrome-web%20store-blue.svg)](https://chrome.google.com/webstore)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![TypeScript](https://img.shields.io/badge/typescript-5.8.3-blue.svg)](https://typescriptlang.org)
[![Tests](https://img.shields.io/badge/tests-jest-green.svg)](https://jestjs.io)

A powerful browser extension for capturing web pages as clean markdown and
syncing them to your Git repository. Part of the PrismWeave document management
ecosystem.

## 🚀 Features

### Smart Content Extraction

- **Clean Markdown Conversion**: Extracts main content, removing ads and
  navigation
- **Semantic Content Detection**: Identifies article text, headers, and
  structure
- **Image Handling**: Captures and processes images with proper alt text
- **Metadata Extraction**: Automatic title, author, and publication info capture
- **Multi-site Support**: Works across different website layouts and CMS systems

### Git Integration

- **Direct GitHub Sync**: Saves captured content directly to your GitHub
  repository
- **Automatic Commits**: Optional auto-commit with descriptive messages
- **Folder Organization**: Intelligent folder structure based on content type
- **Multi-device Sync**: Access your captured documents across all devices
- **Version Control**: Full Git history of all captured content

### Advanced Processing

- **Frontmatter Generation**: YAML metadata headers for document management
- **Link Preservation**: Maintains important links and references
- **Code Block Formatting**: Preserves syntax highlighting and structure
- **Table Conversion**: Converts HTML tables to markdown format
- **Custom Rules**: Configurable extraction rules per site

### User Experience

- **One-Click Capture**: Single button to capture any web page
- **Context Menu Integration**: Right-click on links to capture without
  navigation
- **Background Link Capture**: Capture content from links in background tabs
- **Progress Indicators**: Visual feedback during processing
- **Smart Notifications**: Status updates with clickable commit links
- **Error Handling**: Graceful handling of network and processing errors
- **Keyboard Shortcuts**: Quick access via keyboard combinations (Alt+S)
- **Multi-Capture Methods**: Browser action, context menu, and keyboard
  shortcuts

## 📋 Requirements

### Browser Support

- **Chrome**: Version 88+ (Manifest V3 support)
- **Edge**: Version 88+ (Chromium-based)
- **Firefox**: Version 109+ (Manifest V3 support)

### Prerequisites

- **GitHub Account**: For document synchronization
- **Git Repository**: Dedicated repository for captured documents
- **GitHub Personal Access Token**: For API access (classic token with repo
  scope)

### Optional Integration

- **VS Code**: Enhanced document management with PrismWeave VS Code extension
- **AI Processing**: Local AI analysis with PrismWeave AI processing pipeline

## 🛠️ Installation

### From Chrome Web Store (Recommended)

1. Visit the [Chrome Web Store](https://chrome.google.com/webstore) (link
   pending)
2. Search for "PrismWeave"
3. Click "Add to Chrome"
4. Follow the setup instructions

### Manual Installation (Development)

1. **Clone the repository**:

   ```bash
   git clone https://github.com/davidhayesbc/PrismWeave.git
   cd PrismWeave/browser-extension
   ```

2. **Install dependencies**:

   ```bash
   npm install
   ```

3. **Build the extension**:

   ```bash
   npm run build
   ```

4. **Load in Chrome**:
   - Open `chrome://extensions/`
   - Enable "Developer mode"
   - Click "Load unpacked"
   - Select the `dist` folder

## ⚙️ Setup & Configuration

### 1. GitHub Repository Setup

Create a dedicated repository for your captured documents:

```bash
# Create new repository
git clone https://github.com/yourusername/prismweave-docs.git
cd prismweave-docs

# Create initial structure
mkdir -p documents/{tech,news,research,reference}
mkdir -p images
echo "# PrismWeave Documents" > README.md
git add .
git commit -m "Initial document repository setup"
git push
```

### 2. GitHub Token Creation

1. Go to GitHub → Settings → Developer settings → Personal access tokens
2. Click "Generate new token (classic)"
3. Select scopes: `repo` (full repository access)
4. Copy the generated token (keep it secure!)

### 3. Extension Configuration

1. Click the PrismWeave icon in your browser
2. Click "Options" to open settings
3. Configure the following:

**GitHub Settings**:

- **Repository**: `yourusername/prismweave-docs`
- **Access Token**: Paste your GitHub token
- **Branch**: `main` (or preferred branch)
- **Auto-commit**: Enable for automatic commits

**Capture Settings**:

- **Folder Structure**: Choose organization method
- **Image Handling**: Inline or file references
- **Metadata**: Configure automatic frontmatter generation

## 🎯 Usage

### Capture Methods

#### 1. Browser Action (Main Method)

1. **Navigate** to any web page with interesting content
2. **Click** the PrismWeave extension icon
3. **Wait** for processing (progress indicator shows status)
4. **Review** the captured content in popup
5. **Save** to your Git repository

#### 2. Context Menu (Right-Click)

**Link Capture** (NEW):

1. **Right-click on any link** you want to capture
2. Select **"Capture this link with PrismWeave"** from context menu
3. Extension opens link in background tab, extracts content, and closes tab
4. No need to navigate away from current page

**Page Capture**:

1. **Right-click anywhere on the page** you want to capture
2. Select **"Capture this page with PrismWeave"** from context menu
3. Content is extracted from the current page

#### 3. Keyboard Shortcuts

- **Alt+S**: Quick capture current page
- **Ctrl+Shift+O** (Windows/Linux) or **Cmd+Shift+O** (Mac): Open options

### Context Menu Features

The context menu integration provides seamless content capture:

- **Smart Background Processing**: Links are opened in background tabs
- **Automatic Cleanup**: Background tabs are closed after extraction
- **Real-time Notifications**: Progress updates and results
- **No Page Navigation**: Capture links without leaving current page
- **Batch Processing**: Capture multiple links quickly

### Advanced Features

#### Custom Extraction Rules

Configure per-site extraction rules:

```json
{
  "rules": {
    "medium.com": {
      "selectors": ["article", ".post-content"],
      "exclude": [".follow-button", ".clap-button"]
    },
    "dev.to": {
      "selectors": ["#article-body"],
      "include_images": true
    }
  }
}
```

#### Batch Processing

Process multiple tabs at once:

1. Open multiple articles in tabs
2. Right-click on any tab
3. Select "Capture All Tabs with PrismWeave"

#### Metadata Customization

Control frontmatter generation:

```yaml
---
title: 'Article Title'
url: 'https://example.com/article'
author: 'Author Name'
captured_at: '2025-07-09T12:00:00Z'
tags: ['technology', 'ai', 'machine-learning']
category: 'tech'
reading_time: '5 min'
---
```

## 🏗️ Architecture

### Extension Structure

```
browser-extension/
├── src/
│   ├── background/        # Service worker (Manifest V3)
│   │   └── service-worker.ts
│   ├── content/           # Content scripts
│   │   └── content-script.ts
│   ├── popup/             # Extension popup UI
│   │   ├── popup.html
│   │   ├── popup.ts
│   │   └── popup.css
│   ├── options/           # Settings page
│   │   ├── options.html
│   │   ├── options.ts
│   │   └── options.css
│   ├── utils/             # Shared utilities
│   │   ├── github-client.ts
│   │   ├── markdown-converter.ts
│   │   ├── settings-manager.ts
│   │   └── content-extractor.ts
│   └── types/             # TypeScript definitions
│       └── index.ts
├── dist/                  # Built extension files
├── icons/                 # Extension icons
├── scripts/               # Build scripts
└── tests/                 # Test files
```

### Content Processing Flow

1. **Content Script Injection**: Analyzes page structure
2. **Content Extraction**: Identifies main content areas
3. **Markdown Conversion**: Converts HTML to clean markdown
4. **Metadata Generation**: Extracts title, author, date, etc.
5. **GitHub Integration**: Commits to repository
6. **User Feedback**: Shows success/error status

### Security Model

- **Content Security Policy**: Strict CSP for security
- **Permissions**: Minimal required permissions
- **Token Storage**: Secure storage of GitHub tokens
- **HTTPS Only**: All external communications use HTTPS

## 🧪 Development

### Build System

```bash
# Development build with watch mode
npm run dev

# Production build
npm run build:prod

# Run tests
npm run test

# Run tests with coverage
npm run test:coverage

# Lint code
npm run lint

# Format code
npm run format
```

### Testing

```bash
# Run all tests
npm test

# Watch mode during development
npm run test:watch

# Coverage report
npm run test:coverage

# CI mode (no watch)
npm run test:ci
```

### Test Structure

```
src/__tests__/
├── unit/                  # Unit tests
│   ├── content-extractor.test.ts
│   ├── markdown-converter.test.ts
│   └── github-client.test.ts
├── integration/           # Integration tests
│   ├── capture-flow.test.ts
│   └── github-sync.test.ts
└── fixtures/              # Test data
    ├── sample-pages/
    └── expected-outputs/
```

### Development Tools

```bash
# Setup development tools
npm run dev-tools:setup

# Test specific URL
npm run dev-tools:test

# Test URL conversion
npm run dev-tools:url "https://example.com"

# Compare extraction results
npm run dev-tools:compare
```

## 📊 Performance

### Capture Performance

- **Simple Articles**: ~2-3 seconds end-to-end
- **Complex Pages**: ~5-7 seconds with images
- **Batch Processing**: ~30-60 seconds per page
- **Memory Usage**: ~50MB peak during processing

### Optimization Features

- **Lazy Loading**: Content processed only when needed
- **Caching**: Frequently used resources cached
- **Compression**: Markdown content compressed for storage
- **Debouncing**: Prevents duplicate captures

### Browser Resource Usage

- **Background Memory**: ~10-20MB when idle
- **Content Script**: ~5-10MB per active tab
- **Storage**: ~1-5MB for settings and cache

## 🔧 Configuration Options

### GitHub Integration

```json
{
  "github": {
    "token": "your-github-token",
    "repository": "username/repo-name",
    "branch": "main",
    "auto_commit": true,
    "commit_message_template": "Add captured article: {{title}}",
    "folder_structure": {
      "tech": ["technology", "programming", "software"],
      "news": ["news", "current-events"],
      "research": ["research", "academic", "study"],
      "reference": ["documentation", "tutorial", "guide"]
    }
  }
}
```

### Content Extraction

```json
{
  "extraction": {
    "include_images": true,
    "include_links": true,
    "clean_html": true,
    "custom_selectors": {
      "article": ["article", "main", ".content"],
      "title": ["h1", ".title", ".headline"],
      "author": [".author", ".byline", "[rel=author]"]
    },
    "exclude_selectors": [
      ".advertisement",
      ".sidebar",
      ".navigation",
      ".comments"
    ]
  }
}
```

### Output Formatting

```json
{
  "output": {
    "include_frontmatter": true,
    "markdown_flavor": "github",
    "image_handling": "reference",
    "code_block_language": "auto",
    "table_conversion": true,
    "link_preservation": true
  }
}
```

## 🔌 API Integration

### Message Passing

The extension uses Chrome's message passing for component communication:

```typescript
// Send message to service worker
chrome.runtime.sendMessage({
  type: 'CAPTURE_PAGE',
  data: { url: window.location.href },
});

// Listen for responses
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'CAPTURE_COMPLETE') {
    // Handle completion
    sendResponse({ success: true });
  }
});
```

### GitHub API

Direct integration with GitHub's REST API:

```typescript
// Create or update file
const response = await fetch(
  `https://api.github.com/repos/${owner}/${repo}/contents/${path}`,
  {
    method: 'PUT',
    headers: {
      Authorization: `token ${githubToken}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      message: 'Add captured article',
      content: btoa(markdownContent),
      sha: existingFileSha, // For updates
    }),
  }
);
```

## 🆘 Troubleshooting

### Common Issues

**1. GitHub Authentication Failed**

```
Error: GitHub token is invalid or expired
```

- Check token permissions (needs `repo` scope)
- Regenerate token if expired
- Verify repository name format (`username/repo-name`)

**2. Content Extraction Failed**

```
Error: No main content found on page
```

- Try different extraction selectors
- Check if page uses JavaScript rendering
- Verify page has substantial text content

**3. Permission Denied**

```
Error: Cannot access page content
```

- Extension needs `activeTab` permission
- Some pages (chrome://, file://) are restricted
- Check if page is fully loaded

**4. Repository Not Found**

```
Error: Repository does not exist or access denied
```

- Verify repository exists and is accessible
- Check token has access to private repos (if applicable)
- Ensure correct repository name format

### Debug Mode

Enable debug logging in options:

1. Open extension options
2. Go to "Advanced" tab
3. Enable "Debug Mode"
4. Check browser console for detailed logs

### Reset Settings

If extension behavior is inconsistent:

1. Open extension options
2. Go to "Advanced" tab
3. Click "Reset to Defaults"
4. Reconfigure settings

## 🔗 Integration

### VS Code Extension

The browser extension integrates seamlessly with the PrismWeave VS Code
extension:

- **Automatic Sync**: Captured documents appear in VS Code workspace
- **AI Processing**: Triggers automatic analysis and tagging
- **Search Integration**: Documents become searchable in VS Code
- **Content Creation**: Use captured content for article generation

### AI Processing Pipeline

Captured documents can be processed by the AI pipeline:

- **Automatic Analysis**: Summarization, tagging, categorization
- **Semantic Search**: Vector embeddings for intelligent search
- **Content Generation**: RAG-based article creation
- **Batch Processing**: Efficient processing of multiple documents

## 📚 Examples

### Basic Capture Script

```typescript
// Capture current page
async function captureCurrentPage() {
  const extractor = new ContentExtractor();
  const converter = new MarkdownConverter();

  // Extract content
  const content = await extractor.extractMainContent();
  const metadata = await extractor.extractMetadata();

  // Convert to markdown
  const markdown = converter.convert(content.html);

  // Add frontmatter
  const frontmatter = generateFrontmatter(metadata);
  const document = `${frontmatter}\n\n${markdown}`;

  // Save to GitHub
  const github = new GitHubClient();
  await github.saveDocument(document, metadata.title);
}
```

### Custom Extraction Rules

```typescript
// Define custom rules for specific sites
const extractionRules = {
  'medium.com': {
    article: 'article',
    title: 'h1',
    author: '[rel="author"]',
    exclude: ['.follow-button', '.response-count'],
  },
  'dev.to': {
    article: '#article-body',
    title: '.crayons-article__header h1',
    author: '.crayons-article__subheader a',
    exclude: ['.reaction-button'],
  },
};
```

### Batch Processing

```typescript
// Process multiple tabs
async function captureAllTabs() {
  const tabs = await chrome.tabs.query({ url: ['http://*/*', 'https://*/*'] });

  for (const tab of tabs) {
    if (tab.id) {
      try {
        await captureTab(tab.id);
        console.log(`Captured: ${tab.title}`);
      } catch (error) {
        console.error(`Failed to capture ${tab.title}:`, error);
      }
    }
  }
}
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE)
file for details.

## 🤝 Contributing

Contributions are welcome! Please see our
[Contributing Guidelines](../CONTRIBUTING.md) for details.

### Development Workflow

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

### Code Style

- Use TypeScript for all code
- Follow ESLint configuration
- Use Prettier for formatting
- Add JSDoc comments for public APIs
- Include unit tests for new features

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/davidhayesbc/PrismWeave/issues)
- **Feature Requests**:
  [GitHub Discussions](https://github.com/davidhayesbc/PrismWeave/discussions)
- **Documentation**:
  [Project Wiki](https://github.com/davidhayesbc/PrismWeave/wiki)
- **Chrome Web Store**: [Extension Page](https://chrome.google.com/webstore)
  (pending)

## 🚧 Roadmap

### Version 1.1

- [ ] Firefox support (Manifest V3)
- [ ] Safari extension
- [ ] Improved content extraction for complex sites
- [ ] Better error handling and user feedback

### Version 1.2

- [ ] Offline processing capabilities
- [ ] Custom extraction rule editor
- [ ] Bulk export/import functionality
- [ ] Integration with popular read-later services

### Version 2.0

- [ ] Local AI processing integration
- [ ] Advanced content analysis
- [ ] Multi-language support
- [ ] Team collaboration features

---

_Transform your web reading into a powerful knowledge base with PrismWeave_ 🚀
