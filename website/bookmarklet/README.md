# PrismWeave Personal Bookmarklet Generator

This directory contains the personal bookmarklet generator for PrismWeave,
providing a simple way to create self-contained bookmarklets with embedded
GitHub credentials for seamless content capture.

## Architecture Overview

### Core Components

#### Personal Bookmarklet Generator

- **`generator.ts`** - Complete bookmarklet generator interface that creates
  personalized bookmarklets with embedded content extraction and GitHub
  integration
- **`generator.html`** - User-friendly interface for generating custom
  bookmarklets
- **`config.ts`** - Shared configuration constants and settings

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

#### Self-Contained Design

- **No External Dependencies**: Everything needed is embedded in the bookmarklet
- **Instant Execution**: No loading delays or network requests during operation
- **Privacy-Focused**: No external service calls or tracking
- **Reliable Operation**: No external failure points or CDN dependencies

#### Advanced User Experience

- **Custom Configuration**: Personalized settings embedded during generation
- **Progress Tracking**: Real-time feedback with detailed processing steps
- **Error Handling**: Contextual error messages with actionable troubleshooting
  steps
- **Smart Filename Generation**: Intelligent file naming based on content
  analysis

## Build System

The bookmarklet system provides a streamlined build process for the personal
bookmarklet generator:

### Personal Bookmarklet Generation

```bash
# Build the personal bookmarklet generator
npm run build:bookmarklet

# Development build with source maps
npm run build:bookmarklet --dev

# Clean up old files
npm run cleanup:bookmarklet
```

### Build Outputs

#### Personal Bookmarklet Files (dist/bookmarklet/)

- **`generator.html`** - Interactive bookmarklet generator interface
- **`generator.js`** - Compiled generator with embedded content extraction and
  GitHub integration
- **`README.md`** - Documentation

## Local Testing & Development

### Quick Start Testing

```bash
# Complete testing workflow (recommended)
npm run test:bookmarklet

# Or step by step:
npm run cleanup:bookmarklet          # Clean old files
npm run build:bookmarklet            # Build generator
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

- **🏠 Bookmarklet Generator**:
  `http://localhost:8080/bookmarklet/generator.html`
  - Interactive bookmarklet generator with GitHub settings
  - Personal bookmarklet creation with embedded configuration
  - Step-by-step installation instructions
  - Mobile-friendly interface

- **📊 Build Analytics**: `http://localhost:8080/build-analytics.json`
  - Build statistics and performance metrics
  - Size comparisons and optimization data

### Testing Workflow

1. **Start Local Server**: Run `npm run serve:web` from project root
2. **Open Generator Page**: Navigate to
   `http://localhost:8080/bookmarklet/generator.html`
3. **Generate Personal Bookmarklet**: Configure your GitHub settings and
   generate
4. **Install Bookmarklet**: Drag the generated button to your bookmarks bar
5. **Test on Web Pages**: Click the bookmark on various websites
6. **Configure GitHub**: Set up your GitHub token and repository on first use
7. **Verify Capture**: Check that content is properly extracted and committed

### Development Configuration

#### Modifying the Generator

To modify the personal bookmarklet generator, edit
`src/bookmarklet/generator.ts`:

```typescript
// Configuration for the generator interface
const config = {
  apiUrl: 'https://api.github.com',
  defaultBranch: 'main',
  maxContentSize: 1000000, // 1MB limit for content
  timeout: 30000, // 30 second timeout
};
```

#### Generator Development

The personal bookmarklet generator is built from:

- `generator.ts` - Complete generator interface with embedded content extraction
  and GitHub integration
- `config.ts` - Shared configuration constants

Changes to these files require rebuilding with `npm run build:bookmarklet`.

### File Organization

```
browser-extension/
├── src/bookmarklet/           # Source files
│   ├── generator.ts           # Complete bookmarklet generator with embedded functionality
│   ├── generator.html         # Generator interface template
│   ├── config.ts              # Shared configuration constants
│   └── README.md              # This documentation
├── scripts/                   # Build and utility scripts
│   ├── cleanup-bookmarklet.js # Cleanup utility
│   └── ...
└── dist/bookmarklet/          # Built files (auto-generated)
    ├── generator.html         # Interactive bookmarklet generator interface
    ├── generator.js           # Compiled generator with all functionality
    └── README.md              # Documentation
```

## Usage Guide

### 1. Generate Your Personal Bookmarklet

Use the bookmarklet generator interface:

- Open `dist/bookmarklet/generator.html` in your browser
- Enter your GitHub Personal Access Token
- Enter your repository name (owner/repo format)
- Click "Generate Personal Bookmarklet"
- Save the generated code as a browser bookmark

### 2. Using Your Bookmarklet

Once generated, using your personal bookmarklet is simple:

- Navigate to any web page you want to capture
- Click your personal bookmarklet from your browser bookmarks
- The content will be automatically extracted and saved to your GitHub
  repository
- Check your repository for the new markdown file

```typescript
// Example of what gets embedded in your personal bookmarklet
const config = {
  token: 'your_github_token_here',
  repository: 'your_username/your_repo',
  branch: 'main',
};
```

## Configuration

The personal bookmarklet generator creates self-contained bookmarklets with
embedded configuration:

```typescript
interface IPersonalBookmarkletConfig {
  // GitHub Integration (embedded at generation time)
  githubToken: string; // Your Personal Access Token
  githubRepo: string; // Repository name (owner/repo)
  githubBranch: string; // Target branch (default: 'main')
  folderPath: string; // Target folder (default: 'documents')

  // Content Processing (embedded defaults)
  includeImages: boolean; // Extract and reference images
  includeLinks: boolean; // Preserve links in markdown
  cleanHtml: boolean; // Remove unwanted elements

  // Runtime Behavior
  smartFilenames: boolean; // Generate intelligent filenames
  showPreview: boolean; // Show content preview (when possible)
  timeoutMs: number; // API timeout (default: 30000)
}
```

### Security Notes

- **Token Storage**: Your GitHub token is embedded in the bookmarklet
- **Repository Access**: Ensure your token has appropriate repository
  permissions
- **Safe Handling**: Treat generated bookmarklets as containing sensitive
  credentials

## Size Considerations

The personal bookmarklet approach generates compact, self-contained
bookmarklets:

- **Personal Bookmarklet**: ~8-12KB (varies with configuration)
- **Browser Limit**: Modern browsers support larger bookmarklets
- **No External Dependencies**: Complete functionality embedded

### Self-Contained Approach Benefits

The personal bookmarklet is designed for modern browsers:

1. **All-in-One**: Complete functionality without external runtime loading
2. **Reliable**: No dependency on external services or CDNs
3. **Private**: No tracking or analytics, works entirely within your browser
4. **Immediate**: No loading delays or network timeouts

### Generated Components

When you build the personal bookmarklet system:

- **`generator.html`** - Interactive bookmarklet generator interface
- **`generator.js`** - Complete compiled generator with embedded content
  extraction and GitHub integration

#### Personal Bookmarklet Architecture

```javascript
// Personal bookmarklet (self-contained)
javascript: (function () {
  // ... Complete personal bookmarklet with embedded GitHub API access
})();
```

The personal bookmarklet:

- ✅ Self-contained with no external dependencies
- ✅ Embeds GitHub Personal Access Token and repository configuration
- ✅ Direct GitHub API integration for immediate content upload
- ✅ Works offline once generated (no network dependencies for runtime)
- ✅ Privacy-focused with no external service tracking

#### Benefits of Personal Bookmarklet Approach

- **No External Dependencies**: Complete functionality embedded in bookmarklet
- **Instant Execution**: No loading delays or network requests for runtime
- **Privacy-Focused**: No tracking, analytics, or external service calls
- **Reliable Operation**: Works regardless of CDN availability or network issues
- **Simple Deployment**: Generate once, use anywhere
- **Full GitHub Integration**: Direct API access with proper authentication

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

### Personal Bookmarklet Troubleshooting

#### Generator Issues

```bash
# Rebuild the generator
npm run build:bookmarklet

# Check build output
ls dist/bookmarklet/
```

#### Bookmarklet Not Working

1. **Check Browser Console**: Look for JavaScript errors
2. **Verify Configuration**: Ensure GitHub token and repository are valid
3. **Test Permissions**: Check if your token has repository write access
4. **Clear Cache**: Try generating a fresh bookmarklet

#### GitHub Integration Issues

- **Token Errors**: Verify your GitHub Personal Access Token has repo
  permissions
- **Repository Access**: Ensure the repository exists and you have write access
- **Network Issues**: Check if GitHub API is accessible from your network
- **Rate Limits**: GitHub API has rate limits; wait and retry if needed

### Build System Troubleshooting

#### TypeScript Compilation Errors

```bash
# Check TypeScript configuration
npx tsc --project tsconfig.bookmarklet.json --noEmit

# Clean and rebuild
npm run clean
npm run build:bookmarklet
```

#### Generator Interface Issues

- Current generator includes complete embedded functionality
- Size typically 8-12KB for generated bookmarklets
- If issues occur, verify generator.ts builds correctly

### Personal Bookmarklet Usage

For optimal use of personal bookmarklets:

1. **Generate Fresh**: Create new bookmarklets when tokens change
2. **Test Configuration**: Verify GitHub access before generating
3. **Secure Storage**: Treat bookmarklets as containing sensitive credentials
4. **Regular Updates**: Regenerate periodically for security

### Features Overview

The personal bookmarklet includes:

- **Direct GitHub Integration**: No external services required
- **Complete Content Extraction**: Smart content detection and markdown
  conversion embedded
- **Error Handling**: Clear feedback for any issues encountered
- **Security Focus**: All operations happen locally in your browser

### Browser Compatibility

Tested and working on:

- ✅ Chrome (all versions)
- ✅ Firefox (all versions)
- ✅ Safari (all versions)
- ✅ Edge (all versions)
- ✅ Opera (all versions)
- ✅ Mobile browsers (with installation variations)

For additional support, see the main project documentation and GitHub issues.
