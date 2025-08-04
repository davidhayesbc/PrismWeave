# PrismWeave Bookmarklet Documentation

## Overview

The PrismWeave bookmarklet allows users to capture web page content and convert
it to markdown without installing the browser extension. It provides a
standalone solution that works across all modern browsers.

## Installation

### Method 1: Drag and Drop

1. Visit the bookmarklet page in your extension options
2. Drag the "PrismWeave Capture" link to your bookmarks toolbar
3. Click the bookmark on any webpage to capture content

### Method 2: Manual Bookmark Creation

1. Create a new bookmark in your browser
2. Set the name to "PrismWeave Capture"
3. Copy the generated bookmarklet code as the URL
4. Save the bookmark to your toolbar

## Features

### Content Extraction

- **Smart Detection**: Automatically finds main content using semantic HTML
  analysis
- **Content Scoring**: Uses algorithms to identify the most relevant content
  sections
- **Clean Extraction**: Removes navigation, ads, and irrelevant elements
- **Fallback Strategies**: Multiple extraction methods for different page
  layouts

### Markdown Conversion

- **HTML to Markdown**: Converts extracted HTML to clean markdown format
- **Preserved Formatting**: Maintains headers, lists, links, and text formatting
- **Image Handling**: Processes and includes image references
- **Link Processing**: Preserves internal and external links

### GitHub Integration

- **Direct API**: Communicates directly with GitHub API without proxy servers
- **Repository Management**: Creates and manages files in specified repositories
- **Automatic Commits**: Generates meaningful commit messages with metadata
- **File Organization**: Supports custom folder structures and naming
  conventions

### User Interface

- **Overlay Interface**: Non-intrusive popup interface for configuration
- **Progress Indication**: Real-time feedback during capture process
- **Error Handling**: Clear error messages and recovery suggestions
- **Settings Persistence**: Stores configuration in browser local storage

## Configuration Options

### GitHub Settings

- **Personal Access Token**: Required for repository access
- **Repository**: Target repository in `owner/repo` format
- **Branch**: Target branch (default: main)
- **Folder Path**: Custom folder structure for organizing content

### Content Processing

- **Include Images**: Toggle image processing and inclusion
- **Include Links**: Toggle link preservation in markdown
- **Clean HTML**: Enable/disable HTML cleanup before conversion
- **Custom Selectors**: Override default content detection selectors

### UI Preferences

- **Theme**: Light, dark, or auto theme selection
- **Position**: Popup position on screen
- **Auto-close**: Automatic popup closing after successful capture
- **Progress Display**: Toggle progress indicator visibility

## Technical Implementation

### Build Process

The bookmarklet is built using a specialized build script that:

1. Compiles TypeScript to optimized JavaScript
2. Minifies code for maximum compression
3. URL-encodes the result for bookmark compatibility
4. Generates installation templates and documentation

### Size Optimization

- **Tree Shaking**: Removes unused code during build
- **Minification**: Aggressive code compression
- **Dependency Bundling**: Includes only necessary dependencies
- **Target Size**: Aims for <2000 characters for maximum browser compatibility

### Security Considerations

- **Local Storage**: GitHub tokens stored locally in browser
- **Direct API Calls**: No intermediary servers involved
- **Content Sanitization**: HTML content is cleaned before processing
- **Error Handling**: Secure error reporting without sensitive data exposure

## Browser Compatibility

### Supported Browsers

- **Chrome**: Version 88+
- **Firefox**: Version 85+
- **Safari**: Version 14+
- **Edge**: Version 88+

### Known Limitations

- **Content Security Policy**: Some websites may block bookmarklet execution
- **Large Content**: Very large pages may be truncated
- **Dynamic Content**: JavaScript-generated content may not be captured
- **Cross-Origin**: Some API calls may be restricted on certain domains

## Troubleshooting

### Common Issues

#### Bookmarklet Not Executing

- **Cause**: Content Security Policy restrictions
- **Solution**: Try refreshing the page and clicking again
- **Alternative**: Use the browser extension instead

#### GitHub API Errors

- **Cause**: Invalid or expired personal access token
- **Solution**: Generate a new token with repository permissions
- **Check**: Verify repository name format is `owner/repo`

#### Content Not Captured

- **Cause**: Unusual page structure or dynamic content
- **Solution**: Try manual content selection
- **Alternative**: Adjust content selectors in settings

#### Large File Issues

- **Cause**: GitHub API file size limits
- **Solution**: Enable content truncation or selective capture
- **Alternative**: Split large content into multiple files

### Error Messages

#### "Failed to extract content"

- The page structure couldn't be parsed
- Try adjusting extraction selectors
- Some pages may not be compatible

#### "GitHub API error: 401"

- Authentication failed
- Check personal access token validity
- Ensure token has repository write permissions

#### "Repository not found"

- Repository name is incorrect
- Check repository exists and is accessible
- Verify repository name format

#### "Content too large"

- Captured content exceeds GitHub limits
- Enable content truncation
- Consider selective content capture

## Development

### Building the Bookmarklet

```bash
# Build extension including bookmarklet
npm run build

# Build only bookmarklet components
npm run build:bookmarklet

# Build for production with maximum optimization
npm run build:bookmarklet:prod
```

### File Structure

```
dist/bookmarklet/
├── runtime.js              # Main bookmarklet code
├── bookmarklet.js          # URL-encoded bookmarklet
├── bookmarklet-readable.js # Human-readable version
├── template.html           # Installation page
└── templates/             # Template assets
    ├── bookmarklet-config.js
    ├── bookmarklet-template.html
    └── bookmarklet-template.css
```

### Customization

The bookmarklet can be customized by modifying:

- `src/bookmarklet/runtime.ts`: Main functionality
- `src/bookmarklet/ui.ts`: User interface components
- `src/bookmarklet/templates/`: Installation templates
- `scripts/build-bookmarklet.js`: Build configuration

## API Reference

### Bookmarklet Runtime

The bookmarklet exposes a global `PrismWeaveBookmarklet` object with the
following methods:

#### `capture(options?)`

Captures the current page content.

- `options.includeImages`: Include images in capture
- `options.includeLinks`: Preserve links in markdown
- `options.cleanHtml`: Clean HTML before conversion

#### `configure(settings)`

Updates bookmarklet configuration.

- `settings.githubToken`: GitHub personal access token
- `settings.githubRepo`: Target repository
- `settings.folderPath`: File organization path

#### `getStatus()`

Returns current bookmarklet status and configuration.

### Event Handlers

The bookmarklet emits events for integration:

- `capture:start`: Capture process begins
- `capture:progress`: Progress updates
- `capture:complete`: Capture finished successfully
- `capture:error`: Error occurred during capture

## Support

### Getting Help

- Check the troubleshooting section above
- Review error messages for specific guidance
- Verify GitHub token permissions and repository access
- Test with simple pages first

### Reporting Issues

When reporting issues, include:

- Browser version and type
- Website URL where issue occurred
- Complete error message
- Bookmarklet configuration (without sensitive tokens)

### Contributing

The PrismWeave project welcomes contributions:

- Submit bug reports and feature requests
- Contribute code improvements
- Help with documentation and translations
- Share usage feedback and suggestions
