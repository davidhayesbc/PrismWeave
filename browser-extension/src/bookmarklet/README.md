# PrismWeave Enhanced Bookmarklet System

This directory contains the enhanced bookmarklet implementation for PrismWeave,
providing universal browser support with sophisticated content extraction and
GitHub integration.

## Architecture Overview

### Core Components

#### Hybrid System (Production-Ready)

- **`hybrid-loader.ts`** - Ultra-lightweight loader (~1KB) that fits within
  browser limits
- **`enhanced-runtime-host.ts`** - Hosted script interface for CDN deployment
- **`build-hybrid-bookmarklet.js`** - Build system for hybrid bookmarklet
  generation

#### Enhanced Runtime

- **`enhanced-runtime-compatible.ts`** - Main runtime with enhanced features and
  existing interface compatibility
- **`github-api-client.ts`** - GitHub API integration for repository operations
- **`ui.ts`** - User interface components for configuration and progress display
- **`help.html`** - Help documentation embedded in the bookmarklet interface

### Enhanced Features

#### Smart Content Analysis

- **Quality Assessment**: 0.0-1.0 scoring system for content extraction
  confidence
- **Content Type Detection**: Automatic identification of articles,
  documentation, news, etc.
- **Reading Time Estimation**: Calculates estimated reading time based on
  content analysis
- **Metadata Enhancement**: Comprehensive extraction of structured data and
  social meta tags

#### Advanced User Experience

- **Quick Mode**: Streamlined processing for repeat captures
- **Progress Tracking**: Real-time feedback with detailed processing steps
- **Error Handling**: Contextual error messages with actionable troubleshooting
  steps
- **Browser Notifications**: Desktop notifications for capture completion (with
  permission)

#### Performance Optimizations

- **Adaptive Processing**: Adjusts timeout and processing based on page
  complexity
- **Memory Management**: Efficient handling of large pages with cleanup
  mechanisms
- **Analytics Tracking**: Privacy-conscious local usage analytics for
  optimization

## Build System

The bookmarklet system supports multiple build modes:

### Hybrid System (Recommended for Production)

```bash
# Build the hybrid bookmarklet system
npm run build:bookmarklet:hybrid

# Production build with minification
npm run build:bookmarklet:hybrid:prod

# Clean up old files and check integrity
npm run cleanup:bookmarklet
```

### Hybrid System (Production)

```bash
# Build hybrid bookmarklet system
node scripts/build-hybrid-bookmarklet.js

# Development build with source maps
node scripts/build-hybrid-bookmarklet.js --dev
```

### Build Outputs

#### Hybrid System Files (dist/bookmarklet/)

- **`hybrid-loader.js`** - Ultra-light loader bookmarklet (~1KB)
- **`enhanced-runtime.js`** - Hosted runtime script (75KB)
- **`enhanced-v2.0.0.js`** - Versioned runtime script
- **`install-hybrid.html`** - Interactive installation page
- **`README-hybrid.md`** - Hybrid system documentation
- **`build-analytics.json`** - Build statistics and performance metrics

#### Legacy System Files (Deprecated)

- **`bookmarklet.js`** - Standard version (60KB)
- **`bookmarklet-enhanced.js`** - Enhanced version (60KB)
- **`install.html`** - Full-featured installation page
- **`install-simple.html`** - Simplified installation page
- **`*-encoded.txt`** - URL-encoded bookmarklet strings
- **`size-report.json`** - Size analysis and recommendations

## Local Testing & Development

### Quick Start Testing

```bash
# Complete testing workflow (recommended)
npm run test:bookmarklet

# Or step by step:
npm run cleanup:bookmarklet          # Clean old files
npm run build:bookmarklet:hybrid     # Build hybrid system
node scripts/serve-local.js          # Start local server
```

### Local Testing Server

The local testing server provides a complete development environment:

```bash
# Start server on default port (8080)
node scripts/serve-local.js

# Custom port and host
node scripts/serve-local.js --port 3000 --host 0.0.0.0

# Skip automatic rebuild
node scripts/serve-local.js --no-rebuild
```

#### Available Endpoints

When the server is running on `http://localhost:8080`:

- **🏠 Installation Page**: `http://localhost:8080/install-hybrid.html`

  - Interactive bookmarklet installation
  - Size comparison and benefits
  - Step-by-step instructions
  - Mobile-friendly interface

- **⚡ Loader Script**: `http://localhost:8080/hybrid-loader.js`

  - Raw bookmarklet JavaScript for manual copying
  - ~1KB ultra-lightweight loader

- **🚀 Runtime Script**: `http://localhost:8080/enhanced-runtime.js`

  - Full 75KB runtime that gets loaded dynamically
  - Contains all enhanced bookmarklet functionality

- **📊 Build Analytics**: `http://localhost:8080/build-analytics.json`
  - Build statistics and performance metrics
  - Size comparisons and optimization data

### Testing Workflow

1. **Start Local Server**: Run `node scripts/serve-local.js`
2. **Open Installation Page**: Navigate to
   `http://localhost:8080/install-hybrid.html`
3. **Install Bookmarklet**: Drag the button to your bookmarks bar
4. **Test on Web Pages**: Click the bookmark on various websites
5. **Configure GitHub**: Set up your GitHub token and repository on first use
6. **Verify Capture**: Check that content is properly extracted and committed

### Development Configuration

#### Modifying the Loader

To modify the ultra-light loader, edit `src/bookmarklet/hybrid-loader.ts`:

```typescript
// The loader configuration is in build-hybrid-bookmarklet.js
const config = {
  cdnBaseUrl: 'http://localhost:8080', // For local testing
  fallbackUrl: 'http://localhost:8080/enhanced-runtime.js',
  version: '2.0.0',
  timeout: 10000,
};
```

#### Runtime Development

The hosted runtime is automatically built from:

- `enhanced-runtime-compatible.ts` - Core functionality
- `github-api-client.ts` - GitHub integration
- `ui.ts` - User interface components

Changes to these files require rebuilding with
`npm run build:bookmarklet:hybrid`.

### File Organization

```
browser-extension/
├── src/bookmarklet/           # Source files
│   ├── hybrid-loader.ts       # Ultra-light loader source
│   ├── enhanced-runtime-host.ts # Host interface
│   ├── enhanced-runtime-compatible.ts # Core runtime
│   └── ...
├── scripts/                   # Build and utility scripts
│   ├── build-hybrid-bookmarklet.js # Main build script
│   ├── serve-local.js         # Local testing server
│   ├── cleanup-bookmarklet.js # Cleanup utility
│   └── ...
└── dist/bookmarklet/          # Built files (auto-generated)
    ├── hybrid-loader.js       # Ready-to-use bookmarklet
    ├── enhanced-runtime.js    # Hosted runtime script
    ├── install-hybrid.html    # Installation page
    └── ...
```

## Installation Options

### 1. Interactive Installation Page

Use the generated `install.html` for the best user experience:

- Version selection (Standard vs Enhanced)
- GitHub connection testing
- Configuration validation
- Size impact analysis
- Troubleshooting guidance

### 2. Direct Integration

For developers integrating the bookmarklet:

```typescript
import { executeEnhancedBookmarklet } from './enhanced-runtime-compatible';

// Execute with default configuration
executeEnhancedBookmarklet();

// Execute with custom config
executeEnhancedBookmarklet({
  quickMode: true,
  notifications: false,
  analytics: false,
});
```

## Configuration Interface

The enhanced system uses a comprehensive configuration interface:

```typescript
interface IEnhancedBookmarkletConfig {
  // GitHub Integration
  githubToken: string;
  githubRepo: string;
  githubBranch: string;
  folderPath: string;
  autoCommit: boolean;

  // Content Processing
  includeImages: boolean;
  includeLinks: boolean;
  cleanHtml: boolean;

  // Enhanced Features
  quickMode: boolean; // Skip config if already set
  smartFilenames: boolean; // Generate intelligent filenames
  notifications: boolean; // Desktop notifications
  analytics: boolean; // Usage analytics
  showPreview: boolean; // Content preview before save
}
```

## Size Considerations

Both bookmarklet versions exceed typical browser limits:

- **Standard Version**: 60KB (85K encoded)
- **Enhanced Version**: 60KB (84K encoded)
- **Browser Limit**: ~2KB typical

### Production Deployment Strategy

For production use, the hybrid loader pattern is implemented:

#### Hybrid Loader System

The system consists of two components:

1. **Ultra-Light Loader** (~750 characters) - Fits within browser limits
2. **Hosted Runtime** (60KB) - Full functionality served from CDN/GitHub

Build and deploy using:

```bash
# Build the hybrid system
npm run build:bookmarklet:hybrid

# For production deployment
npm run build:bookmarklet:hybrid:prod
```

#### Generated Components

- **`hybrid-loader.ts`** - Ultra-lightweight loader source
- **`enhanced-runtime-host.ts`** - Hosted script interface
- **`ultra-light-loader.js`** - Minified loader (~750 chars)
- **`enhanced-runtime-hosted.js`** - Hosted runtime script
- **`install-hybrid.html`** - Installation page for hybrid system

#### Deployment Architecture

```javascript
// Ultra-lightweight loader (bookmarklet)
javascript: (function () {
  // ... ~750 character loader with fallback strategy
})();
```

The loader:

- ✅ Stays within all browser bookmarklet size limits (~750 chars)
- ✅ Automatically tries CDN first, then GitHub Raw fallback
- ✅ Shows loading progress and error feedback
- ✅ Handles network failures gracefully
- ✅ Caches runtime for performance

#### Benefits of Hybrid Approach

- **Size Compliance**: Loader fits within browser limits (750 chars vs 2KB
  limit)
- **Full Functionality**: Loads complete 60KB runtime dynamically
- **Easy Updates**: Update hosted script without changing bookmarklet
- **Performance**: CDN caching with GitHub fallback
- **Analytics**: Track usage and performance metrics
- **Version Management**: Serve different versions based on user preferences

## Development Guidelines

### Code Quality Standards

- **TypeScript**: Strict typing with comprehensive interfaces
- **Error Handling**: Graceful degradation with user-friendly messages
- **Performance**: Memory-conscious with cleanup mechanisms
- **Compatibility**: Works across all major browsers
- **Security**: Safe handling of user credentials and content

### Testing Recommendations

1. **Cross-Browser Testing**: Chrome, Firefox, Safari, Edge
2. **Content Variety**: Articles, documentation, news, complex layouts
3. **Network Conditions**: Slow connections, API timeouts, rate limits
4. **Configuration Edge Cases**: Invalid tokens, missing repos, permissions

### Contributing

When contributing to the bookmarklet system:

1. **Maintain Compatibility**: Preserve existing interface contracts
2. **Test Thoroughly**: Validate across different content types and browsers
3. **Document Changes**: Update configuration interfaces and user documentation
4. **Consider Size Impact**: Monitor bundle size and optimize where possible
5. **User Experience**: Prioritize clear feedback and error handling

## Support and Troubleshooting

### Local Testing Troubleshooting

#### Server Won't Start

```bash
# Check if port is in use
netstat -ano | findstr :8080

# Use different port
node scripts/serve-local.js --port 3000

# Check build integrity
npm run cleanup:bookmarklet --check-only
```

#### Bookmarklet Not Working

1. **Check Browser Console**: Look for JavaScript errors
2. **Verify Server**: Ensure `http://localhost:8080/enhanced-runtime.js` loads
3. **Clear Cache**: Hard refresh (Ctrl+F5) the installation page
4. **Rebuild**: Run `npm run build:bookmarklet:hybrid` and restart server

#### GitHub Integration Issues

- **Token Errors**: Verify your GitHub Personal Access Token has repo
  permissions
- **Repository Access**: Ensure the repository exists and you have write access
- **Network Issues**: Check if GitHub API is accessible from your network

### Build System Troubleshooting

#### TypeScript Compilation Errors

```bash
# Check TypeScript configuration
npx tsc --project tsconfig.bookmarklet.json --noEmit

# Clean and rebuild
npm run clean
npm run build:bookmarklet:hybrid
```

#### Size Optimization

- Current loader size: ~1014 characters (target: <1000)
- Runtime size: ~75KB (acceptable for hosted script)
- If loader exceeds 2KB, check for compression opportunities in
  `build-hybrid-bookmarklet.js`

### Production Deployment

For production deployment of the hybrid system:

1. **Upload Runtime**: Deploy `enhanced-runtime.js` to your CDN
2. **Update URLs**: Modify `cdnBaseUrl` in the build script
3. **Test Fallback**: Ensure GitHub Raw URL works as backup
4. **Monitor Performance**: Track loading times and success rates

### Enhanced Features Testing

The enhanced bookmarklet includes diagnostic capabilities:

- **Connection Testing**: Real-time GitHub API validation
- **Content Analysis**: Quality assessment with feedback
- **Performance Metrics**: Processing time and success rate tracking
- **Error Reporting**: Detailed error contexts with suggested solutions

### Browser Compatibility

Tested and working on:

- ✅ Chrome (all versions)
- ✅ Firefox (all versions)
- ✅ Safari (all versions)
- ✅ Edge (all versions)
- ✅ Opera (all versions)
- ✅ Mobile browsers (with installation variations)

For additional support, see the main project documentation and GitHub issues.
