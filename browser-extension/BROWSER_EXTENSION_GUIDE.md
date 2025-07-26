# PrismWeave Browser Extension - Comprehensive Guide

## Overview

PrismWeave is a Chrome/Edge Manifest V3 browser extension that captures web
content, converts it to markdown, and syncs it to GitHub repositories. The
extension provides intelligent content extraction, customizable processing, and
seamless Git integration.

## Table of Contents

- [Architecture](#architecture)
- [Installation & Setup](#installation--setup)
- [Core Features](#core-features)
- [Configuration](#configuration)
- [Development](#development)
- [Testing](#testing)
- [API Reference](#api-reference)
- [Troubleshooting](#troubleshooting)

## Architecture

### Core Components

```
browser-extension/
├── src/
│   ├── background/          # Service worker (Manifest V3)
│   ├── content/            # Content scripts for page extraction
│   ├── popup/              # Extension popup interface
│   ├── options/            # Settings/configuration page
│   ├── utils/              # Shared utilities and services
│   └── types/              # TypeScript type definitions
├── icons/                  # Extension icons
├── coverage/               # Test coverage reports
└── dist/                   # Built extension files
```

### Technology Stack

- **Language**: TypeScript with ES2020 target
- **Module System**: CommonJS for Chrome extension compatibility
- **Build Tools**: TypeScript compiler with custom build scripts
- **Testing**: Jest with jsdom environment
- **Linting**: ESLint with TypeScript support
- **API Integration**: GitHub REST API v3

## Installation & Setup

### Prerequisites

1. **Node.js** (v18 or higher)
2. **npm** or **yarn**
3. **GitHub Personal Access Token** with repository permissions
4. **Chrome/Edge browser** with Developer Mode enabled

### Development Setup

1. **Clone and Install Dependencies**

   ```bash
   cd browser-extension
   npm install
   ```

2. **Build the Extension**

   ```bash
   npm run build
   ```

3. **Load in Browser**
   - Open Chrome/Edge
   - Navigate to `chrome://extensions/`
   - Enable "Developer mode"
   - Click "Load unpacked"
   - Select the `dist/` folder

### Configuration

1. **GitHub Setup**

   - Create a Personal Access Token at GitHub Settings > Developer Settings
   - Grant `repo` permissions for your target repository
   - Ensure repository exists and is accessible

2. **Extension Configuration**
   - Right-click extension icon → Options
   - Enter GitHub token and repository (format: `username/repo-name`)
   - Configure capture settings as needed
   - Test connection to verify setup

## Core Features

### 1. Content Capture

**Intelligent Content Extraction**

- Automatic detection of main content areas using semantic HTML
- Removal of advertisements, navigation, and clutter
- Support for custom CSS selectors
- Image URL extraction and processing

**Supported Content Types**

- Articles and blog posts
- Documentation pages
- News articles
- Research papers
- General web content

### 2. Markdown Conversion

**Clean Markdown Output**

- Proper heading hierarchy preservation
- Link and image handling
- Code block formatting
- Table conversion
- List formatting (ordered/unordered)

**Content Processing Options**

- Remove ads and promotional content
- Strip navigation elements
- Apply custom element removal rules
- Preserve formatting where appropriate

### 3. GitHub Integration

**Automated Repository Management**

- Direct commits to specified repository
- Configurable folder structure
- Flexible file naming patterns
- Automatic frontmatter generation

**Commit Features**

- Customizable commit message templates
- Optional auto-commit functionality
- Branch support (defaults to main)
- Conflict handling

### 4. User Interface

**Popup Interface**

- Quick capture functionality
- Status display and progress indicators
- Recent captures list
- One-click settings access

**Options Page**

- Comprehensive configuration management
- GitHub connection testing
- Settings import/export
- Real-time validation

## Configuration

### Settings Reference

#### Repository Settings

| Setting       | Type   | Description                       | Default |
| ------------- | ------ | --------------------------------- | ------- |
| `githubToken` | string | GitHub Personal Access Token      | ""      |
| `githubRepo`  | string | Repository in format `owner/repo` | ""      |

#### File Organization

| Setting             | Type   | Description                      | Default                   |
| ------------------- | ------ | -------------------------------- | ------------------------- |
| `defaultFolder`     | string | Target folder for captures       | "unsorted"                |
| `customFolder`      | string | Custom folder name when needed   | ""                        |
| `fileNamingPattern` | string | Template for generated filenames | "YYYY-MM-DD-domain-title" |

**Available Naming Patterns:**

- `YYYY-MM-DD-domain-title` → `2025-01-15-example-com-article-title.md`
- `YYYY-MM-DD-title` → `2025-01-15-article-title.md`
- `domain-YYYY-MM-DD-title` → `example-com-2025-01-15-article-title.md`
- `title-YYYY-MM-DD` → `article-title-2025-01-15.md`

#### Content Processing

| Setting            | Type    | Description                               | Default |
| ------------------ | ------- | ----------------------------------------- | ------- |
| `captureImages`    | boolean | Download and save images                  | true    |
| `removeAds`        | boolean | Remove advertisement content              | true    |
| `removeNavigation` | boolean | Remove navigation elements                | true    |
| `customSelectors`  | string  | CSS selectors to remove (comma-separated) | ""      |

#### Automation

| Setting                 | Type    | Description                   | Default                   |
| ----------------------- | ------- | ----------------------------- | ------------------------- |
| `autoCommit`            | boolean | Automatically commit captures | true                      |
| `commitMessageTemplate` | string  | Template for commit messages  | "Add: {domain} - {title}" |

**Template Variables:**

- `{domain}` → Source website domain
- `{title}` → Page title
- `{date}` → Capture date
- `{filename}` → Generated filename

#### User Experience

| Setting                   | Type    | Description                  | Default |
| ------------------------- | ------- | ---------------------------- | ------- |
| `enableKeyboardShortcuts` | boolean | Enable Ctrl+Shift+S shortcut | true    |
| `showNotifications`       | boolean | Show capture notifications   | true    |
| `debugMode`               | boolean | Enable debug logging         | false   |

### Folder Structure Options

**Predefined Folders:**

- `unsorted` - General captures
- `documents` - Document-type content
- `articles` - Article captures
- `research` - Research materials
- `notes` - Quick notes and snippets
- `tech` - Technical content
- `business` - Business-related captures
- `custom` - User-defined folder name

## Development

### Project Structure

```typescript
// Core interfaces
interface ISettings {
  githubToken: string;
  githubRepo: string;
  defaultFolder: string;
  // ... other settings
}

interface IMessageData {
  type: string;
  data?: Record<string, unknown>;
  timestamp?: number;
}
```

### Key Components

#### Service Worker (`background/service-worker.ts`)

```typescript
// Modern ES6 module approach
import { SettingsManager } from '../utils/settings-manager.js';
import { GitOperations } from '../utils/git-operations.js';

// Message handling
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  handleMessage(message, sender)
    .then(result => sendResponse({ success: true, data: result }))
    .catch(error => sendResponse({ success: false, error: error.message }));
  return true; // Keep message channel open
});
```

#### Content Script (`content/content-script.ts`)

```typescript
// Self-contained content extraction
class ContentExtractor {
  async extractContent(): Promise<IExtractedContent> {
    const mainContent = this.detectMainContent();
    const cleanedContent = this.cleanContent(mainContent);
    return this.convertToMarkdown(cleanedContent);
  }
}
```

#### Settings Management

```typescript
class SettingsManager {
  async getSettings(): Promise<ISettings> {
    // Chrome storage integration with validation
  }

  async updateSettings(updates: Partial<ISettings>): Promise<void> {
    // Type-safe settings updates with validation
  }
}
```

### Build Process

**TypeScript Configuration**

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "CommonJS", // Chrome extension compatibility
    "strict": true,
    "esModuleInterop": true
  }
}
```

**Build Commands**

```bash
# Development build
npm run build

# Production build
npm run build:prod

# Watch mode for development
npm run watch

# Type checking
npm run type-check
```

### Chrome Extension Compatibility

**Manifest V3 Requirements:**

- Service workers instead of background pages
- Declarative permissions model
- Content Security Policy compliance
- Modern JavaScript/TypeScript support

**Module System:**

- ES6 imports in source code
- CommonJS output for Chrome compatibility
- Self-contained service workers
- Proper module resolution

## Testing

### Test Suite Overview

```bash
# Run all tests
npm run test

# Run with coverage
npm run test:coverage

# Run specific test suites
npm run test -- --testNamePattern="SettingsManager"

# Run tests in watch mode
npm run test:watch
```

### Test Structure

```
src/__tests__/
├── background/           # Service worker tests
├── content/             # Content script tests
├── options/             # Options page tests
├── popup/               # Popup interface tests
└── utils/               # Utility function tests
```

### Writing Tests

```typescript
// Example test structure
describe('SettingsManager', () => {
  let manager: SettingsManager;

  beforeEach(() => {
    // Mock Chrome APIs
    global.chrome = createMockChrome();
    manager = new SettingsManager();
  });

  test('should load default settings', async () => {
    const settings = await manager.getSettings();
    expect(settings.githubToken).toBe('');
    expect(settings.autoCommit).toBe(true);
  });
});
```

### Coverage Goals

- **Overall Coverage**: 70%+
- **Critical Paths**: Service worker, content extraction
- **Settings Management**: 100%
- **Error Handling**: Comprehensive coverage

## API Reference

### Chrome Extension APIs Used

#### Storage API

```typescript
// Settings persistence
chrome.storage.sync.get(keys, callback);
chrome.storage.sync.set(data, callback);
```

#### Runtime API

```typescript
// Message passing
chrome.runtime.sendMessage(message, callback);
chrome.runtime.onMessage.addListener(callback);
```

#### Tabs API

```typescript
// Content script injection
chrome.tabs.sendMessage(tabId, message, callback);
chrome.scripting.executeScript(details);
```

### Internal APIs

#### Settings API

```typescript
interface SettingsAPI {
  getSettings(): Promise<ISettings>;
  updateSettings(updates: Partial<ISettings>): Promise<void>;
  resetSettings(): Promise<void>;
  validateSettings(settings: Partial<ISettings>): ValidationResult;
}
```

#### Content Extraction API

```typescript
interface ContentExtractionAPI {
  extractContent(options?: ExtractionOptions): Promise<IExtractedContent>;
  cleanContent(element: Element, options: CleaningOptions): Element;
  convertToMarkdown(html: string): string;
}
```

#### Git Operations API

```typescript
interface GitOperationsAPI {
  commitFile(params: CommitParams): Promise<CommitResult>;
  testConnection(): Promise<ConnectionResult>;
  createRepository(): Promise<RepositoryResult>;
}
```

### Message Types

```typescript
// Service worker messages
type MessageType =
  | 'GET_SETTINGS'
  | 'UPDATE_SETTINGS'
  | 'RESET_SETTINGS'
  | 'TEST_CONNECTION'
  | 'CAPTURE_PAGE'
  | 'GET_STATUS';

// Content script messages
type ContentMessageType =
  | 'EXTRACT_CONTENT'
  | 'GET_PAGE_INFO'
  | 'UPDATE_CONFIG'
  | 'PING';
```

## Troubleshooting

### Common Issues

#### 1. Extension Not Loading

**Symptoms**: Extension doesn't appear in browser **Solutions**:

- Check manifest.json syntax
- Verify all required files are in dist/
- Check browser console for errors
- Ensure Developer Mode is enabled

#### 2. GitHub Connection Errors

**Symptoms**: "Connection test failed" or commit errors **Solutions**:

- Verify GitHub token is valid and not expired
- Check repository name format (`owner/repo`)
- Ensure token has `repo` permissions
- Test repository access manually

#### 3. Content Extraction Issues

**Symptoms**: Poor quality markdown or missing content **Solutions**:

- Check custom selectors configuration
- Review removal settings (ads, navigation)
- Test on different websites
- Enable debug mode for detailed logs

#### 4. Build Errors

**Symptoms**: TypeScript compilation failures **Solutions**:

- Check TypeScript version compatibility
- Verify import paths use `.js` extensions
- Ensure all dependencies are installed
- Check tsconfig.json configuration

### Debug Mode

Enable debug mode in extension options for:

- Detailed console logging
- Content extraction diagnostics
- GitHub API request/response logging
- Performance metrics

### Performance Optimization

**Memory Management**:

- Content scripts are injected dynamically
- Service worker handles cleanup automatically
- Settings are cached appropriately

**Network Efficiency**:

- GitHub API calls are optimized
- Content extraction is performed locally
- Image processing is optional

### Browser Compatibility

**Supported Browsers**:

- Chrome 88+ (Manifest V3 support)
- Edge 88+ (Chromium-based)
- Brave (Chromium-based)

**Known Limitations**:

- Firefox requires Manifest V2 (separate build needed)
- Safari requires different architecture
- Mobile browsers not supported

## Security Considerations

### Data Privacy

- All processing happens locally in browser
- GitHub token stored securely in Chrome storage
- No data sent to third-party servers
- Content extraction respects page privacy

### Permissions

- `storage` - Settings persistence
- `activeTab` - Current page access only
- `scripting` - Content script injection
- Host permissions for target sites

### Content Security Policy

- No inline scripts in extension pages
- All resources loaded from extension
- GitHub API accessed via HTTPS only
- Sanitized content processing

## Contributing

### Code Style

- TypeScript with strict mode
- ESLint configuration enforced
- Prettier formatting
- Comprehensive JSDoc comments

### Submission Process

1. Fork repository
2. Create feature branch
3. Write tests for new functionality
4. Ensure all tests pass
5. Submit pull request with description

### Development Environment

- VS Code recommended
- Chrome Developer Tools for debugging
- GitHub Desktop or Git CLI
- Node.js LTS version

---

## Support

For issues, questions, or contributions:

1. Check existing GitHub issues
2. Review troubleshooting section
3. Create detailed issue report
4. Include browser/OS information
5. Provide reproduction steps

**Version**: 1.0.0  
**Last Updated**: January 2025  
**Compatibility**: Chrome 88+, Edge 88+
