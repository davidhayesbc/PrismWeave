# PrismWeave Browser Extension

Browser extension for capturing web pages as clean markdown and syncing to your Git repository.

## Features

- **One-Click Capture**: Save any web page as clean, readable markdown
- **Smart Content Extraction**: Automatically removes ads, navigation, and clutter
- **Git Integration**: Direct sync to your GitHub repository
- **Cross-Browser**: Works with Chrome and Edge (Manifest V3)
- **Customizable**: Configure capture settings and output formats

## Installation

### Development Setup

1. **Clone and Install Dependencies**:
   ```bash
   cd browser-extension
   npm install
   ```

2. **Build the Extension**:
   ```bash
   npm run build
   ```

3. **Load in Browser**:
   - Open Chrome/Edge and go to `chrome://extensions/`
   - Enable "Developer mode"
   - Click "Load unpacked" and select the `dist` folder

### Troubleshooting

If you encounter a `SyntaxError: Unexpected token 'export'` error, see [MODULE_COMPATIBILITY_FIX.md](./MODULE_COMPATIBILITY_FIX.md) for the solution.

## Development Guidelines

- **Module System**: Uses CommonJS compilation for service worker compatibility
- **No ES6 Imports**: Service workers use `importScripts()` instead
- **Dual Exports**: Utility files support both CommonJS and global patterns

### Production Install
*(Will be available on Chrome Web Store after development)*

## Usage

### Quick Capture
1. **Click the Extension Icon** in your browser toolbar
2. **Click "Capture This Page"** to save the current page
3. **Files are saved** to your configured repository path

### Keyboard Shortcut
- Press `Ctrl+Shift+S` to quickly capture the current page

### Settings Configuration
1. **Click the Extension Icon** and select "Settings"
2. **Configure Repository**: Set your local Git repository path
3. **GitHub Integration**: Add your GitHub token and repository
4. **Customize Capture**: Choose file naming, processing options

## Configuration

### Repository Setup
The extension needs a local Git repository to save captured documents:

```
your-prismweave-repo/
├── documents/           # Captured markdown files
│   ├── tech/
│   ├── business/
│   ├── research/
│   └── unsorted/       # Default folder
├── images/             # Downloaded images
└── .git/              # Git repository
```

### GitHub Integration
1. Create a [GitHub Personal Access Token](https://github.com/settings/tokens)
2. Give it `repo` permissions
3. Add the token in extension settings
4. Specify your repository (format: `username/repo-name`)

## File Output Format

Captured pages are saved as markdown files with YAML frontmatter:

```markdown
---
title: "Article Title"
source_url: "https://example.com/article"
domain: "example.com"
captured_date: "2025-06-13T10:30:00Z"
tags: []
summary: ""
---

# Article Content

The main article content converted to clean markdown...
```

## Content Processing

The extension intelligently processes web pages:

### Removes Unwanted Content
- Navigation menus and headers
- Advertisements and promotional content
- Sidebars and widgets
- Comments and social media buttons
- Cookie notices and popups

### Preserves Important Content
- Main article text and structure
- Headings and formatting
- Images and captions
- Important links
- Code blocks and quotes

## Settings Options

### Capture Settings
- **Default Folder**: Where new captures are saved
- **File Naming**: Pattern for generated filenames
- **Auto-Commit**: Automatically commit captures to Git
- **Auto-Push**: Automatically push to GitHub
- **Image Handling**: Download images locally or reference URLs

### Content Processing
- **Remove Ads**: Strip advertising content
- **Remove Navigation**: Remove menu and navigation elements
- **Preserve Links**: Keep all links in markdown
- **Custom Selectors**: Additional CSS selectors to remove

### Advanced Options
- **Commit Messages**: Template for Git commit messages
- **Keyboard Shortcuts**: Enable/disable shortcuts
- **Notifications**: Browser notification preferences

## Development

### Project Structure
```
browser-extension/
├── src/
│   ├── background/        # Background service worker
│   ├── content/          # Content scripts
│   ├── popup/            # Extension popup UI
│   ├── options/          # Settings page
│   └── utils/            # Shared utilities
├── scripts/              # Build scripts
├── dist/                 # Built extension
├── manifest.json         # Extension manifest
└── package.json          # Dependencies and scripts
```

### Build Commands
- `npm run dev` - Development build
- `npm run build` - Production build
- `npm run lint` - Code linting
- `npm run test` - Run tests
- `npm run zip` - Package for distribution

### Architecture

#### Background Service Worker
- Handles extension lifecycle
- Manages Git operations
- Processes captured content
- Stores user settings

#### Content Script
- Extracts page content
- Removes unwanted elements
- Provides visual feedback
- Handles keyboard shortcuts

#### Popup Interface
- Quick capture controls
- Status indicators
- Settings access
- Repository management

## Troubleshooting

### Common Issues

**Extension Won't Load**
- Check that all files are in the `dist` folder
- Verify manifest.json is valid
- Check browser console for errors

**Capture Fails**
- Ensure the page is fully loaded
- Check if the site blocks content scripts
- Verify repository path is accessible

**Git Operations Fail**
- Check repository path exists
- Verify GitHub token has correct permissions
- Ensure Git is installed and configured

**Images Not Saving**
- Check image capture is enabled in settings
- Verify sufficient disk space
- Check for CORS restrictions on images

### Debug Mode
Enable extension developer mode to see detailed logs:
1. Go to `chrome://extensions/`
2. Click "Inspect views: background page"
3. Check Console tab for logs

## Roadmap

### Phase 1 (Current)
- [x] Basic page capture
- [x] Markdown conversion
- [x] Settings interface
- [x] File management
- [ ] Git integration
- [ ] Image handling

### Phase 2 (Planned)
- [ ] AI content processing
- [ ] Advanced filtering rules
- [ ] Batch capture
- [ ] Site-specific configurations

### Phase 3 (Future)
- [ ] Team collaboration features
- [ ] Cloud sync options
- [ ] Mobile companion app
- [ ] Advanced export formats

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

- **Issues**: GitHub Issues
- **Documentation**: README and inline comments
- **Community**: GitHub Discussions
