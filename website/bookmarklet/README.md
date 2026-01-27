# PrismWeave Personal Bookmarklet Generator

This directory contains the personal bookmarklet generator for PrismWeave,
providing a simple way to create lightweight loader bookmarklets with embedded
GitHub credentials for seamless content capture.

## Architecture Overview

### Core Components

#### Personal Bookmarklet Generator

- **`generator.ts`** - Bookmarklet generator interface that creates
  personalized loader bookmarklets with embedded GitHub integration
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

#### Lightweight Loader Design

- **Hosted Injectable**: Loads the PrismWeave injector script at runtime
- **Fast Setup**: Small bookmarklet size with minimal embedded logic
- **Privacy-Focused**: No analytics or tracking calls
- **Config Embedded**: GitHub settings are embedded at generation time

#### Advanced User Experience

- **Custom Configuration**: Personalized settings embedded during generation
- **Progress Tracking**: Real-time feedback with detailed processing steps
- **Error Handling**: Contextual error messages with actionable troubleshooting
  steps
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
- **`generator.js`** - Compiled generator with loader bookmarklet logic
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

1. **Start Development Server**: Run `npm run dev` from project root
2. **Open Generator Page**: Navigate to
   `http://localhost:4003/bookmarklet/generator.html`
3. **Generate Personal Bookmarklet**: Configure your GitHub settings and
   generate
4. **Install Bookmarklet**: Drag the generated button to your bookmarks bar
5. **Test on Web Pages**: Click the bookmark on various websites
6. **Configure GitHub**: Set up your GitHub token and repository on first use
7. **Verify Capture**: Check that content is properly extracted and committed

Note: `npm run dev` starts Aspire which serves the website at port 4003.

### Development Configuration

#### Modifying the Generator

To modify the personal bookmarklet generator, edit
`src/bookmarklet/generator.ts` and the shared defaults in
`src/bookmarklet/config.ts`.

#### Generator Development

The personal bookmarklet generator is built from:

- `generator.ts` - Generator UI and loader bookmarklet creation
- `config.ts` - Shared configuration constants

Changes to these files require rebuilding with `npm run build:bookmarklet`.

### File Organization

```
browser-extension/
├── src/bookmarklet/           # Source files
│   ├── generator.ts           # Bookmarklet generator UI and loader generation logic
│   ├── generator.html         # Generator interface template
│   ├── config.ts              # Shared configuration constants
│   └── README.md              # This documentation
├── scripts/                   # Build and utility scripts
│   ├── cleanup-bookmarklet.js # Cleanup utility
│   └── ...
└── dist/bookmarklet/          # Built files (auto-generated)
    ├── generator.html         # Interactive bookmarklet generator interface
    ├── generator.js           # Compiled generator with loader logic
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
  commitMessage: 'PrismWeave: Add {title}',
};
```

## Configuration

The personal bookmarklet generator creates loader-based bookmarklets with
embedded configuration:

```typescript
interface IPersonalBookmarkletConfig {
  // GitHub Integration (embedded at generation time)
  githubToken: string; // Your Personal Access Token
  githubRepo: string; // Repository name (owner/repo)
  commitMessageTemplate: string; // Commit template (default: PrismWeave: Add {title})

  // Content Processing (runtime defaults)
  includeImages: boolean; // Extract and reference images
  includeLinks: boolean; // Preserve links in markdown
  cleanHtml: boolean; // Remove unwanted elements
  generateFrontmatter: boolean; // Include YAML frontmatter
  includeMetadata: boolean; // Include extracted metadata
}
```

### Security Notes

- **Token Storage**: Your GitHub token is embedded in the bookmarklet
- **Repository Access**: Ensure your token has appropriate repository
  permissions
- **Safe Handling**: Treat generated bookmarklets as containing sensitive
  credentials

## Size Considerations

The personal bookmarklet approach generates compact, loader-based
bookmarklets:

- **Personal Bookmarklet**: Small loader (size varies with configuration)
- **Browser Limit**: Modern browsers support larger bookmarklets
- **Hosted Injectable**: Full extraction logic lives in the injectable script

### Loader Approach Benefits

The personal bookmarklet is designed for modern browsers:

1. **Lightweight**: Minimal embedded code
2. **Maintainable**: Updates ship via the injectable script
3. **Private**: No tracking or analytics
4. **Reliable**: Clear error handling when the injectable fails to load

### Generated Components

When you build the personal bookmarklet system:

- **`generator.html`** - Interactive bookmarklet generator interface
- **`generator.js`** - Complete compiled generator with embedded content
  extraction and GitHub integration

#### Personal Bookmarklet Architecture

```javascript
// Personal bookmarklet (loader)
javascript: (function () {
  // ... Loads the PrismWeave injectable script and runs extraction
})();
```

The personal bookmarklet:

- ✅ Lightweight loader with embedded GitHub configuration
- ✅ Loads the PrismWeave injectable extractor at runtime
- ✅ Direct GitHub API integration via the injected script
- ✅ Privacy-focused with no tracking or analytics calls

#### Benefits of Personal Bookmarklet Approach

- **Small Bookmarklet Size**: Minimal embedded code
- **Centralized Updates**: Update the injectable once, bookmarklet stays current
- **Privacy-Focused**: No tracking or analytics
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

- Current generator loads the injectable script for extraction
- Size typically small for generated bookmarklets
- If issues occur, verify generator.ts builds correctly

### Personal Bookmarklet Usage

For optimal use of personal bookmarklets:

1. **Generate Fresh**: Create new bookmarklets when tokens change
2. **Test Configuration**: Verify GitHub access before generating
3. **Secure Storage**: Treat bookmarklets as containing sensitive credentials
4. **Regular Updates**: Regenerate periodically for security

### Features Overview

The personal bookmarklet includes:

- **Direct GitHub Integration**: GitHub calls are handled by the injectable
- **Complete Content Extraction**: Smart extraction runs via the injectable
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
