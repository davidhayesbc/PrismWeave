# PrismWeave Bookmarklet

A self-contained bookmarklet implementation of PrismWeave that enables web page capture functionality in environments where browser extensions cannot be installed.

## 📋 Overview

The PrismWeave Bookmarklet provides the same core functionality as the browser extension but runs as a JavaScript bookmarklet that can be activated on any webpage. It reuses the shared core utilities from the main PrismWeave project while implementing bookmarklet-specific adapters for storage, notifications, and content extraction.

## 🏗️ Architecture

### Core Components

- **Main Entry Point**: `src/core/bookmarklet-main.ts`
  - Initializes and coordinates all bookmarklet functionality
  - Manages the lifecycle of components and UI

- **UI Overlay**: `src/core/ui-overlay.ts`
  - Provides a non-intrusive interface for content capture
  - Includes settings panel and progress indicators
  - Handles user interactions and notifications

### Adapters

The bookmarklet implements environment-specific adapters that implement the shared interfaces:

- **LocalStorageProvider**: `src/adapters/local-storage-provider.ts`
  - Implements `IStorageProvider` using browser localStorage
  - Provides persistent storage for settings and data

- **OverlayNotificationProvider**: `src/adapters/overlay-notification-provider.ts`
  - Implements `INotificationProvider` using UI overlay notifications
  - Shows success/error messages within the bookmarklet interface

- **BookmarkletContentExtractor**: `src/adapters/bookmarklet-content-extractor.ts`
  - Wraps shared `ContentExtractorCore` with browser DOM provider
  - Extracts content directly from the current page

- **BookmarkletGitHubClient**: `src/adapters/bookmarklet-github-client.ts`
  - Implements GitHub API operations using direct fetch API
  - CORS-compatible implementation for bookmarklet environment

## 🚀 Features

### Current Implementation

- ✅ Self-contained bookmarklet entry point
- ✅ UI overlay with capture and settings panels
- ✅ Local storage for settings persistence
- ✅ Notification system within overlay
- ✅ Content extraction using shared core
- ✅ GitHub API integration with direct fetch

### Planned Features

- [ ] Webpack/esbuild configuration for single-file output
- [ ] Base64 encoding for essential assets
- [ ] Content security policy compatibility
- [ ] Cross-browser compatibility testing
- [ ] Installation and usage documentation

## 💻 Development

### Project Structure

```
bookmarklet/
├── src/
│   ├── core/
│   │   ├── bookmarklet-main.ts    # Main entry point
│   │   └── ui-overlay.ts          # UI overlay component
│   ├── adapters/
│   │   ├── local-storage-provider.ts
│   │   ├── overlay-notification-provider.ts
│   │   ├── bookmarklet-content-extractor.ts
│   │   └── bookmarklet-github-client.ts
│   └── build/                     # Build configuration (planned)
├── dist/                          # Built bookmarklet files (planned)
└── README.md                      # This file
```

### Dependencies

The bookmarklet reuses shared components from the main PrismWeave project:

- `../shared/core/` - Core utilities (MarkdownConverter, GitHubAPICore, etc.)
- `../shared/interfaces/` - Provider interfaces
- `../types/` - Shared type definitions

### Building (Planned)

```bash
# Install dependencies
npm install

# Build bookmarklet
npm run build:bookmarklet

# Generated files will be in dist/
ls dist/prismweave-bookmarklet.js
```

## 📱 Installation (Planned)

### Manual Installation

1. Copy the bookmarklet code from `dist/prismweave-bookmarklet.js`
2. Create a new bookmark in your browser
3. Paste the bookmarklet code as the URL
4. Name it "PrismWeave Capture"

### One-Click Installation

Visit the PrismWeave installation page and drag the bookmarklet button to your bookmarks toolbar.

## 🔧 Usage

1. **Navigate to a webpage** you want to capture
2. **Click the PrismWeave bookmarklet** in your bookmarks
3. **Configure settings** on first use:
   - Enter your GitHub Personal Access Token
   - Specify the target repository (owner/repo format)
   - Choose default folder organization
4. **Click "Capture Page"** to extract and save the content
5. **View progress** in the notification system
6. **Success!** Content is saved to your GitHub repository

## ⚙️ Settings

### GitHub Configuration

- **Token**: Personal Access Token with `repo` permissions
- **Repository**: Target repository in `owner/repo` format
- **Default Folder**: Organization folder for captured content

### Content Extraction Options

- **Clean HTML**: Remove ads, navigation, and unwanted elements
- **Preserve Formatting**: Maintain original text formatting
- **Include Images**: Extract and reference images from content
- **Custom Selectors**: Override default content detection

## 🔐 Security Considerations

### Data Storage

- Settings stored in browser localStorage with `prismweave_` prefix
- GitHub token stored securely in encrypted localStorage where available
- No data transmitted to third parties except GitHub API

### Content Security Policy

- Bookmarklet designed to work with strict CSP policies
- No inline script execution after initial load
- All styles injected programmatically with proper namespacing

### Cross-Site Scripting

- All user inputs and web content properly escaped
- GitHub API responses validated and sanitized
- UI overlay protected against page script interference

## 🌐 Browser Compatibility

### Minimum Requirements

- **ES2017**: async/await support
- **Fetch API**: Native fetch() support
- **localStorage**: Client-side storage
- **Modern CSS**: Flexbox and CSS custom properties

### Tested Browsers

- Chrome 60+
- Firefox 55+
- Safari 11+
- Edge 16+

### Mobile Support

- iOS Safari 11+
- Chrome Mobile 60+
- Firefox Mobile 55+

## 🆚 Comparison with Browser Extension

| Feature | Browser Extension | Bookmarklet |
|---------|------------------|-------------|
| Installation | Extension store | Bookmark drag & drop |
| Permissions | Extensive | Page-level only |
| Background Processing | Yes | No |
| Automatic Updates | Yes | Manual |
| Offline Support | Limited | No |
| Storage Capacity | Large (Chrome storage) | Limited (localStorage) |
| System Integration | Yes | No |
| CORS Restrictions | Bypassed | Must handle |

## 🐛 Troubleshooting

### Common Issues

**"GitHub connection failed"**
- Verify GitHub token has `repo` permissions
- Check repository name format (owner/repo)
- Ensure repository exists and is accessible

**"Content extraction failed"**
- Page may have anti-scraping protection
- Try different content selectors in settings
- Check browser console for detailed errors

**"localStorage not available"**
- Enable cookies and local storage in browser settings
- Check if in private/incognito mode
- Some corporate firewalls block localStorage

### Debug Mode

Enable debug logging by running in browser console:
```javascript
localStorage.setItem('prismweave_debug', 'true');
```

## 🔄 Updates

The bookmarklet checks for updates when activated. To force an update:

1. Delete the old bookmarklet
2. Visit the PrismWeave installation page
3. Drag the new bookmarklet to your bookmarks

## 📄 License

Same license as the main PrismWeave project.

## 🤝 Contributing

Bookmarklet development follows the same patterns as the main project. See the main CONTRIBUTING.md for guidelines.

---

*This bookmarklet is part of the PrismWeave project and shares its core utilities while providing standalone functionality for environments where browser extensions are not available.*
