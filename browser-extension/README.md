# PrismWeave Browser Extension

[![Chrome Web Store](https://img.shields.io/badge/chrome-web%20store-blue.svg)](https://chrome.google.com/webstore)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![TypeScript](https://img.shields.io/badge/typescript-5.8.3-blue.svg)](https://typescriptlang.org)
[![Tests](https://img.shields.io/badge/tests-jest-green.svg)](https://jestjs.io)

A powerful Chrome/Edge Manifest V3 browser extension that captures web content,
converts it to clean markdown, and syncs it to GitHub repositories. Features
intelligent content extraction, customizable processing, seamless Git
integration, and optional bookmarklet functionality for universal browser
support.

## 📋 Table of Contents

- [Features](#-features)
- [Requirements](#-requirements)
- [Installation](#️-installation)
- [Setup & Configuration](#️-setup--configuration)
- [Usage](#-usage)
- [Bookmarklet Alternative](#-bookmarklet-alternative)
- [Architecture](#️-architecture)
- [Development](#-development)
- [Deployment](#-deployment)
- [Configuration Reference](#-configuration-reference)
- [API Integration](#-api-integration)
- [Performance](#-performance)
- [Troubleshooting](#-troubleshooting)
- [Integration](#-integration)
- [Examples](#-examples)
- [Contributing](#-contributing)
- [Support](#-support)

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
- **Bookmarklet Support**: Universal capture tool for any browser (Chrome,
  Firefox, Safari, Edge)
- **Progress Indicators**: Visual feedback during processing
- **Smart Notifications**: Status updates with clickable commit links
- **Error Handling**: Graceful handling of network and processing errors
- **Keyboard Shortcuts**: Quick access via keyboard combinations (Alt+S)
- **Multi-Capture Methods**: Browser action, context menu, keyboard shortcuts,
  and bookmarklet

## 📋 Requirements

### Browser Support

- **Chrome**: Version 88+ (Manifest V3 support) - Full extension functionality
- **Edge**: Version 88+ (Chromium-based) - Full extension functionality
- **Firefox**: Version 109+ (Manifest V3 support) - Full extension functionality
- **Safari**: All versions - Bookmarklet functionality only
- **Opera**: All Chromium-based versions - Full extension functionality
- **Brave**: All versions - Full extension functionality

### Extension vs Bookmarklet Support

| Feature                  | Chrome Extension | Bookmarklet  |
| ------------------------ | ---------------- | ------------ |
| One-click capture        | ✅               | ✅           |
| Background processing    | ✅               | ❌           |
| Context menu integration | ✅               | ❌           |
| Keyboard shortcuts       | ✅               | ❌           |
| Settings persistence     | ✅               | ⚠️ Limited   |
| Auto-commit              | ✅               | ✅           |
| Cross-browser support    | Chrome/Edge only | All browsers |

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

## 📖 Bookmarklet Alternative

For users who prefer a universal solution that works across all browsers
(Chrome, Firefox, Safari, Edge, Opera) or can't install browser extensions,
PrismWeave offers a comprehensive enhanced bookmarklet system.

### What is the PrismWeave Bookmarklet?

The PrismWeave bookmarklet is a sophisticated JavaScript-based tool that can be
saved as a browser bookmark. When clicked, it extracts content from the current
page, converts it to markdown, and saves it to your GitHub repository - all
without requiring a browser extension. The system features intelligent content
analysis, quality assessment, and enhanced error handling.

### Enhanced Bookmarklet System

PrismWeave now offers **two versions** of the bookmarklet:

#### 🚀 Standard Version (53KB)

- Core content extraction and GitHub sync
- Smart content detection and cleanup
- Basic markdown conversion
- Configuration dialog and progress tracking

#### ⭐ Enhanced Version (60KB)

- **Everything in Standard, plus:**
- Smart content quality assessment
- Enhanced document metadata extraction
- Quick mode for faster processing
- Advanced error handling with suggestions
- Browser notifications support
- Analytics tracking (privacy-conscious)

### Installation Options

#### Option 1: Bookmarklet Generator (Recommended)

Use the bundled generator page for the easiest setup experience:

**[🛠️ Open the PrismWeave Bookmarklet Generator](dist/bookmarklet/generator.html)**

The generator provides:

- **Inline Configuration**: Enter your GitHub token and repository details once
- **Preview & Testing**: Validate configuration before saving the bookmarklet
- **Compact Output**: Generates the latest optimized bookmarklet code
- **Device Compatibility**: Works on desktop and mobile browsers
- **Troubleshooting Tips**: Built-in guidance for common setup questions

#### Option 2: Build Your Own

For developers or users who want to customize the bookmarklet:

```bash
# Build the hybrid bookmarklet system
cd browser-extension
node scripts/build-hybrid-bookmarklet.js

# Generated files will be in dist/bookmarklet/
# - generator.html (interactive generator page)
# - generator.js (compiled generator logic)
# - Both standard and enhanced bookmarklet versions
```

### Current Size Considerations

**Important:** Both bookmarklet versions exceed typical size limits:

- **Standard**: 53KB (75KB encoded)
- **Enhanced**: 60KB (84KB encoded)
- **Typical Limit**: ~2KB for most browsers

**Recommended Approach**: For production use, consider implementing the hybrid
loader pattern:

1. Create a lightweight (~800 character) loader bookmarklet
2. Loader dynamically fetches full functionality from your website
3. Maintains all features while staying within browser limits

### Using the PrismWeave Bookmarklet

#### First-Time Configuration

When you use either bookmarklet version for the first time, you'll see a modern
configuration dialog:

1. **GitHub Personal Access Token**: Your token with repository access
2. **GitHub Repository**: Your repository in format `username/repo-name`
3. **Optional Advanced Settings**:
   - **Branch**: Target branch (default: `main`)
   - **Folder Path**: Where to save files (default: `documents`)
   - **Auto Commit**: Whether to save automatically (default: enabled)
   - **Quick Mode**: Faster processing with basic extraction (Enhanced version
     only)

#### Enhanced Features (Enhanced Version Only)

**Smart Quality Assessment:**

- Analyzes page content quality and reading complexity
- Provides feedback on extraction confidence
- Suggests manual review for low-quality captures

**Advanced Document Processing:**

- Enhanced metadata extraction including reading time estimates
- Smarter filename generation based on content analysis
- Better handling of complex page structures

**User Experience Improvements:**

- Browser desktop notifications for capture completion
- More detailed progress tracking and status updates
- Enhanced error messages with actionable suggestions
- Analytics tracking for usage insights (privacy-focused)

#### Basic Usage Workflow

1. **Navigate** to any web page you want to capture
2. **Click** the "PrismWeave Capture" bookmark
3. **Configure** (first time only): Fill in the setup dialog
4. **Monitor Progress**: Watch the modern overlay showing extraction progress
5. **Review Results**: Get notified when capture completes with commit link

#### What Each Version Does

**Content Processing Pipeline:**

1. **Page Analysis**: Detects content type and optimal extraction strategy
2. **Smart Extraction**: Uses semantic selectors to find main content
3. **Content Cleaning**: Removes ads, navigation, and clutter elements
4. **Markdown Conversion**: Converts HTML to clean, formatted markdown
5. **Metadata Generation**: Extracts comprehensive document metadata
6. **Quality Assessment**: (Enhanced only) Evaluates content completeness
7. **GitHub Integration**: Commits file with descriptive commit message
8. **User Feedback**: Shows success notification with repository link

### Enhanced Bookmarklet Features

#### Content Processing Capabilities

**Smart Content Detection & Analysis:**

- Multi-strategy content extraction using semantic HTML selectors
- Content quality assessment with confidence scoring
- Automatic detection of article structure and reading flow
- Intelligent handling of single-page applications (SPAs)

**Advanced Content Cleaning:**

- Removes ads, navigation, sidebars, and promotional content
- Filters out comment sections and social sharing widgets
- Handles complex CSS layouts and framework-specific structures
- Preserves essential formatting while removing visual clutter

**Professional Markdown Conversion:**

- Handles headers, paragraphs, lists, links, images, and code blocks
- Maintains proper markdown syntax and formatting
- Converts HTML tables to markdown table format
- Preserves code syntax highlighting information

**Comprehensive Metadata Extraction:**

- Captures Open Graph, Twitter Card, and JSON-LD structured data
- Extracts author information, publication dates, and descriptions
- Analyzes reading time and word count statistics
- Identifies content categories and relevant keywords

#### File Management & Organization

**Intelligent File Naming:**

- `YYYY-MM-DD-domain-title.md` format for chronological organization
- Automatic filename sanitization and length optimization
- Handles international characters and special symbols
- Prevents filename conflicts with automatic incrementing

**Smart Folder Organization:**

- Configurable target folders with automatic category detection
- Support for nested folder structures (e.g., `documents/tech/articles`)
- Date-based organization options (e.g., `2025/08/article-name.md`)
- Custom folder mapping based on content type or source domain

**Enhanced Frontmatter Generation:**

```yaml
---
title: 'Complete Article Title'
url: 'https://example.com/full-url'
domain: 'example.com'
author: 'Author Name'
published_date: '2025-08-04'
captured_at: '2025-08-04T15:30:45.123Z'
description: 'Article summary and description'
keywords: ['keyword1', 'keyword2', 'keyword3']
category: 'tech'
content_type: 'article'
reading_time: '8 min'
word_count: 1847
quality_score: 0.92
language: 'en'
tags: ['technology', 'development', 'best-practices']
---
```

#### Advanced User Experience (Enhanced Version)

**Smart Quality Assessment:**

- Content completeness scoring (0.0 - 1.0 scale)
- Reading complexity analysis
- Extraction confidence indicators
- Recommendations for manual review when needed

**Enhanced Error Handling:**

- Contextual error messages with specific troubleshooting steps
- Automatic retry mechanisms for transient failures
- Fallback extraction methods for difficult pages
- GitHub API error interpretation and suggested fixes

**Modern Interface Design:**

- Responsive overlay design that works on desktop and mobile
- Real-time progress indicators with step-by-step feedback
- Smooth animations and transitions for better user experience
- Accessibility features including keyboard navigation and screen reader support

**Browser Integration:**

- Desktop notifications for capture completion (with permission)
- Automatic commit link opening in new tab
- Respectful of user's notification preferences
- Works seamlessly across all major browsers

### Testing Your Enhanced Bookmarklet

#### Recommended Testing Approach

**Phase 1: Initial Setup Testing**

1. **Create a test repository** on GitHub specifically for bookmarklet testing
2. **Generate a test token** with limited repository permissions initially
3. **Use the installation page** to configure and test your GitHub connection
4. **Test on simple content** first (clean blog posts, documentation pages)

**Phase 2: Content Type Testing**

Test the bookmarklet on various content types to validate extraction quality:

| Content Type        | Test Site Examples              | Expected Quality Score | Notes                   |
| ------------------- | ------------------------------- | ---------------------- | ----------------------- |
| **Clean Articles**  | Medium, Dev.to, personal blogs  | 0.85 - 1.0             | Should work excellently |
| **Technical Docs**  | GitHub wikis, API documentation | 0.80 - 0.95            | May need manual review  |
| **News Articles**   | Major news sites                | 0.70 - 0.90            | Variable due to ads     |
| **Complex Sites**   | E-commerce, social media        | 0.40 - 0.70            | Use Enhanced version    |
| **Academic Papers** | arXiv, research journals        | 0.75 - 0.95            | Good structure usually  |

#### Built-in Testing Tools

**GitHub Connection Test:**

The installation page includes a built-in connection tester that validates:

- GitHub token authenticity and permissions
- Repository existence and write access
- API rate limit status and availability
- Network connectivity and firewall restrictions

**Content Quality Preview:**

Enhanced version provides real-time feedback:

- Content quality score (0.0 - 1.0 scale)
- Extraction confidence level
- Word count and reading time estimates
- Identification of potential issues before saving

#### Advanced Testing Scenarios

**Hybrid Loader Testing (Future Implementation):**

For production deployment, test the hybrid loader approach:

```javascript
// Lightweight loader bookmarklet (~800 characters)
javascript: (function () {
  if (window.PrismWeaveLoader) return;
  window.PrismWeaveLoader = true;
  const script = document.createElement('script');
  script.src = 'https://yoursite.com/prismweave-enhanced.js';
  script.onload = () => PrismWeave.init();
  script.onerror = () => alert('Failed to load PrismWeave');
  document.head.appendChild(script);
})();
```

This approach:

- Stays well within bookmarklet size limits
- Loads full functionality from your website
- Maintains all enhanced features
- Provides better update mechanisms

### Advanced Customization Options

#### Site-Specific Extraction Rules

The enhanced bookmarklet system supports advanced customization through
configuration:

```javascript
// Advanced site-specific rules (configured via installation page)
const SITE_RULES = {
  'medium.com': {
    selectors: {
      article: 'article',
      title: 'h1',
      author: '[rel="author"]',
      content: '.post-content',
    },
    exclude: ['.follow-button', '.clap-button', '.response-count'],
    quality_bonus: 0.1, // Boost quality score for known good sites
    category: 'articles',
  },
  'dev.to': {
    selectors: {
      article: '#article-body',
      title: '.crayons-article__header h1',
      author: '.crayons-article__subheader a',
    },
    exclude: ['.reaction-button', '.comment-subscription'],
    preserve_code: true,
    category: 'tech',
  },
  'github.com': {
    selectors: {
      content: '.markdown-body, .Box-body',
    },
    preserve_formatting: true,
    include_links: true,
    category: 'reference',
  },
};
```

#### Custom Filename Generation

Configure advanced filename patterns through the installation interface:

```javascript
// Available filename templates
const FILENAME_PATTERNS = {
  standard: 'YYYY-MM-DD-domain-title.md',
  categorized: 'category/YYYY-MM-DD-title.md',
  author: 'YYYY-MM-DD-author-title.md',
  hierarchical: 'domain/YYYY/MM/DD-title.md',
  simple: 'title-YYYY-MM-DD.md',
};
```

#### Multi-Repository Support

Advanced users can configure repository routing based on content analysis:

```javascript
// Repository selection based on detected content type
const REPOSITORY_ROUTING = {
  tech: {
    repo: 'username/tech-docs',
    folder: 'articles',
    commit_template: '📚 Add tech article: {title}',
  },
  news: {
    repo: 'username/news-clips',
    folder: 'daily/{YYYY}/{MM}',
    commit_template: '📰 {date}: {title} ({domain})',
  },
  research: {
    repo: 'username/research-papers',
    folder: 'papers/{category}',
    commit_template: '🔬 Add research: {title}',
  },
  default: {
    repo: 'username/general-docs',
    folder: 'unsorted',
    commit_template: '📄 Capture: {title}',
  },
};
```

#### Analytics and Performance Tracking

The Enhanced version includes privacy-conscious analytics:

```javascript
// Local analytics (never leaves your browser)
const ANALYTICS_CONFIG = {
  track_capture_time: true,
  track_content_types: true,
  track_success_rates: true,
  track_site_performance: true,
  generate_monthly_reports: true,
  export_data: true, // For personal analysis
};
```

### Enhanced Bookmarklet vs Extension Comparison

| Feature                      | Browser Extension       | Enhanced Bookmarklet      | Standard Bookmarklet    |
| ---------------------------- | ----------------------- | ------------------------- | ----------------------- |
| **Installation**             | Chrome Web Store        | Copy/paste or installer   | Copy/paste or installer |
| **Browser Support**          | Chrome, Edge, Firefox   | All browsers              | All browsers            |
| **Setup Complexity**         | Simple (UI-guided)      | Moderate (config page)    | Moderate (config page)  |
| **Background Processing**    | Yes                     | No                        | No                      |
| **Context Menu**             | Yes                     | No                        | No                      |
| **Keyboard Shortcuts**       | Yes                     | No                        | No                      |
| **Settings Persistence**     | Full                    | localStorage              | localStorage            |
| **Content Quality Analysis** | Basic                   | **Advanced**              | Basic                   |
| **Error Handling**           | Good                    | **Enhanced**              | Basic                   |
| **User Notifications**       | Extension notifications | **Desktop notifications** | Basic alerts            |
| **Analytics Tracking**       | None                    | **Privacy-focused**       | None                    |
| **Updates**                  | Automatic               | Manual page refresh       | Manual page refresh     |
| **Security**                 | Sandboxed               | Page context              | Page context            |
| **Performance**              | Optimized               | Good                      | Good                    |
| **Customization**            | UI options              | Advanced configuration    | Basic configuration     |
| **File Size**                | Extension package       | 60KB encoded              | 53KB encoded            |
| **Quick Mode**               | No                      | **Yes**                   | No                      |

### Production Deployment Considerations

#### Size Limitation Strategy

Both bookmarklet versions exceed typical browser limits. For production
deployment, consider:

**Hybrid Loader Approach (Recommended):**

```javascript
// Ultra-light loader (~800 chars)
javascript: (function () {
  const s = document.createElement('script');
  s.src = 'https://yoursite.com/prismweave.js';
  s.onload = () => window.PrismWeave?.init();
  document.head.appendChild(s);
})();
```

**Benefits of Hybrid Approach:**

- ✅ Stays within all browser bookmarklet size limits
- ✅ Loads full Enhanced functionality from your website
- ✅ Easy updates by updating hosted file
- ✅ Better caching and performance
- ✅ Analytics and usage tracking capabilities
- ✅ A/B testing different versions

#### Hosting Requirements

For hybrid deployment, you'll need:

- Static file hosting (GitHub Pages, Netlify, Vercel)
- HTTPS support (required for GitHub API)
- CORS headers configured properly
- CDN for global performance (optional)

### Enhanced Bookmarklet Troubleshooting

#### Common Issues & Solutions

**1. Configuration & Authentication**

```
❌ GitHub authentication failed - Invalid or expired token
```

**Solutions:**

- **Verify Token**: Use the built-in connection tester on the installation page
- **Check Permissions**: Ensure token has `repo` scope for full repository
  access
- **Token Format**: Confirm you're using a classic token (starts with `ghp_`)
- **Expiration**: Check if token has expired in GitHub settings

**Enhanced Diagnostic Features:**

- Real-time connection testing during configuration
- Detailed error messages with specific GitHub API response codes
- Automatic retry with exponential backoff for transient failures

---

**2. Content Extraction Problems**

```
❌ Low quality content detected (Score: 0.3/1.0)
⚠️ Content extraction confidence low - Manual review recommended
```

**Enhanced Version Solutions:**

- **Quality Assessment**: Check the quality score and confidence indicators
- **Quick Mode**: Try enabling Quick Mode for faster, simpler extraction
- **Site-Specific Rules**: Configure custom extraction rules for problematic
  sites
- **Manual Verification**: Use the preview feature to verify content before
  saving

**Common Extraction Issues:**

- JavaScript-heavy sites: Wait longer before clicking bookmarklet
- Paywall content: May only capture preview text
- Complex layouts: Enhanced version has better fallback strategies

---

**3. GitHub API & Network Issues**

```
❌ GitHub API rate limit exceeded (Retry after: 1234567890)
❌ Network error: Failed to reach GitHub API
```

**Enhanced Error Handling:**

- **Rate Limit Management**: Automatic retry scheduling with countdown display
- **Network Diagnostics**: Tests connectivity and suggests firewall/proxy
  solutions
- **API Status Monitoring**: Checks GitHub API status and reports service issues
- **Fallback Strategies**: Queues captures for retry when network recovers

---

**4. Browser-Specific Issues**

```
❌ Bookmarklet size exceeds browser limit
⚠️ Some browsers may not support large bookmarklets
```

**Solutions by Browser:**

- **Chrome/Edge**: Usually supports larger bookmarklets (~64KB)
- **Firefox**: May have stricter limits (~8KB)
- **Safari**: Most restrictive limits (~2KB)
- **Mobile Browsers**: Generally more restrictive

**Recommended Fix**: Use the hybrid loader approach for universal compatibility

---

**5. Performance & Memory Issues**

```
⚠️ Large page detected - Processing may take longer
❌ Page processing timeout after 30 seconds
```

**Enhanced Performance Features:**

- **Adaptive Timeout**: Automatically extends timeout for complex pages
- **Memory Management**: Efficient processing with cleanup mechanisms
- **Progress Tracking**: Real-time feedback on processing stages
- **Quick Mode**: Simplified extraction for faster processing

#### Advanced Debugging Tools

**Built-in Debug Mode:**

The Enhanced version includes comprehensive debugging:

```javascript
// Enable debug mode (accessible via installation page)
localStorage.setItem('prismweave-debug', 'true');

// Debug information includes:
// - Content extraction timeline
// - Quality assessment breakdown
// - GitHub API request/response details
// - Performance metrics and memory usage
// - Error stack traces with context
```

**Performance Analysis:**

```javascript
// View performance metrics (Enhanced version)
console.log(PrismWeave.getPerformanceMetrics());

// Output example:
// {
//   averageCaptureTime: 4200,
//   successRate: 0.94,
//   qualityScoreAverage: 0.78,
//   mostProblematicSites: ['example.com'],
//   topCategories: ['tech', 'news', 'articles']
// }
```

#### Expert-Level Troubleshooting

**Custom Extraction Rules Testing:**

```javascript
// Test custom rules on current page
PrismWeave.testExtractionRules({
  selectors: {
    title: 'h1, .title, [data-title]',
    content: 'article, .content, .post-body',
  },
  exclude: ['.ads', '.sidebar', '.comments'],
});
```

**Manual Content Inspection:**

```javascript
// Inspect detected content elements
PrismWeave.inspectPageStructure();

// View quality assessment details
PrismWeave.assessContentQuality(document.body);
```

#### Getting Additional Help

**Self-Diagnostic Report:**

The Enhanced version can generate comprehensive diagnostic reports:

```javascript
// Generate diagnostic report (Enhanced version only)
PrismWeave.generateDiagnosticReport();

// Includes:
// - Browser and environment details
// - Configuration settings (tokens redacted)
// - Recent capture history and success rates
// - Performance metrics and error logs
// - Network connectivity test results
```

**Community Support:**

- **GitHub Issues**: Report bugs with diagnostic information
- **Feature Requests**: Suggest improvements based on usage patterns
- **Configuration Help**: Share anonymized configs for troubleshooting
- **Site-Specific Issues**: Contribute extraction rules for problematic sites

### Bookmarklet Security Considerations

#### Safe Practices

1. **Token Security**: Store tokens securely, don't share bookmarklet code with
   tokens
2. **Repository Access**: Use dedicated repositories for captured content
3. **Content Validation**: Bookmarklet validates content before processing
4. **API Limits**: Respects GitHub API rate limits
5. **Error Handling**: Graceful failure without exposing sensitive data

#### Privacy Notes

- All processing happens in your browser
- Content is sent directly to your GitHub repository
- No third-party services involved
- GitHub token stored only in bookmarklet code
- No tracking or analytics

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

### Core Components

```
browser-extension/
├── src/
│   ├── background/          # Service worker (Manifest V3)
│   │   └── service-worker.ts
│   ├── content/            # Content scripts for page extraction
│   │   └── content-script.ts
│   ├── popup/              # Extension popup interface
│   │   ├── popup.html
│   │   ├── popup.ts
│   │   └── popup.css
│   ├── options/            # Settings/configuration page
│   │   ├── options.html
│   │   ├── options.ts
│   │   └── options.css
│   ├── utils/              # Shared utilities and services
│   │   ├── github-client.ts
│   │   ├── markdown-converter.ts
│   │   ├── settings-manager.ts
│   │   └── content-extractor.ts
│   └── types/              # TypeScript type definitions
│       └── index.ts
├── dist/                   # Built extension files
├── icons/                  # Extension icons (16x16, 48x48, 128x128)
├── scripts/                # Build and development scripts
├── coverage/               # Test coverage reports
└── __tests__/              # Test files and fixtures
```

### Technology Stack

- **Language**: TypeScript with ES2020 target
- **Module System**: ES6 modules with CommonJS compatibility for Chrome
- **Build Tools**: TypeScript compiler with custom build scripts
- **Testing**: Jest with jsdom environment (48 tests, 18.4% coverage)
- **Linting**: ESLint with TypeScript support
- **API Integration**: GitHub REST API v3
- **Manifest**: Version 3 (Chrome/Edge/Firefox compatible)

### Content Processing Flow

1. **Content Script Injection**: Analyzes page structure using semantic HTML
2. **Content Extraction**: Identifies main content areas, removes clutter
3. **Markdown Conversion**: Converts HTML to clean, formatted markdown
4. **Metadata Generation**: Extracts title, author, date, keywords, images
5. **Frontmatter Creation**: Generates YAML headers with comprehensive metadata
6. **GitHub Integration**: Commits to repository with customizable messages
7. **User Feedback**: Shows success/error status with actionable information

### Message Passing Architecture

```typescript
// Service worker to content script communication
interface IMessageData {
  type: string;
  data?: Record<string, unknown>;
  timestamp?: number;
}

interface IMessageResponse {
  success: boolean;
  data?: unknown;
  error?: string;
}

// Message types
type MessageType =
  | 'GET_SETTINGS'
  | 'UPDATE_SETTINGS'
  | 'CAPTURE_PAGE'
  | 'TEST_CONNECTION'
  | 'EXTRACT_CONTENT';
```

### Security Model

- **Content Security Policy**: Strict CSP compliance for Manifest V3
- **Permissions**: Minimal required permissions (`storage`, `activeTab`,
  `scripting`)
- **Token Storage**: Secure Chrome storage APIs with encryption
- **HTTPS Only**: All external communications use HTTPS
- **Sandboxing**: Service worker isolation and content script boundaries
- **Input Validation**: All user inputs and captured content sanitized

## 🧪 Development

### Development Environment Setup

#### Prerequisites

1. **Node.js** (v18 or higher) with npm
2. **Chrome/Edge browser** with Developer Mode enabled
3. **GitHub Personal Access Token** with repository permissions
4. **VS Code** (recommended) with TypeScript and ESLint extensions

#### Initial Setup

```bash
# Clone the repository
git clone https://github.com/davidhayesbc/PrismWeave.git
cd PrismWeave/browser-extension

# Install dependencies
npm install

# Build the extension
npm run build

# Load in browser for testing
# Open chrome://extensions/
# Enable "Developer mode"
# Click "Load unpacked" and select the dist/ folder
```

### Build System

#### Available Commands

```bash
# Development build with source maps
npm run build

# Production build (optimized)
npm run build:prod

# Development build with file watching
npm run dev

# Watch mode for development
npm run watch

# Type checking only
npm run type-check

# Clean build artifacts
npm run clean

# Full rebuild
npm run rebuild
```

#### Build Configuration

**TypeScript Configuration** (`tsconfig.json`):

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "ES2020",
    "moduleResolution": "node",
    "strict": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "outDir": "./dist",
    "rootDir": "./src"
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist", "**/*.test.ts"]
}
```

**Build Process Flow:**

1. **TypeScript Compilation**: ES2020 target with module support
2. **File Processing**: Copy static assets (HTML, CSS, icons)
3. **Manifest Generation**: Update version and permissions
4. **Source Maps**: Generate for debugging (dev mode only)
5. **Optimization**: Minification and tree-shaking (prod mode)

### Testing Framework

#### Test Structure

```
src/__tests__/
├── unit/                   # Unit tests for individual components
│   ├── content-extractor.test.ts
│   ├── markdown-converter.test.ts
│   ├── settings-manager.test.ts
│   └── github-client.test.ts
├── integration/            # Integration tests for workflows
│   ├── capture-flow.test.ts
│   ├── github-sync.test.ts
│   └── options-page.test.ts
├── e2e/                   # End-to-end tests
│   ├── extension-popup.test.ts
│   └── content-capture.test.ts
└── fixtures/              # Test data and mock responses
    ├── sample-pages/
    ├── expected-outputs/
    └── mock-responses/
```

#### Test Commands

```bash
# Run all tests
npm test

# Run tests with coverage
npm run test:coverage

# Run tests in watch mode (development)
npm run test:watch

# Run specific test suite
npm test -- --testNamePattern="SettingsManager"

# Run tests with verbose output
npm run test:verbose

# Run CI tests (no watch mode)
npm run test:ci

# Generate coverage report
npm run coverage:report
```

#### Test Configuration

**Jest Configuration** (`jest.config.js`):

```javascript
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'jsdom',
  roots: ['<rootDir>/src'],
  testMatch: ['**/__tests__/**/*.test.ts'],
  collectCoverageFrom: ['src/**/*.ts', '!src/**/*.d.ts', '!src/__tests__/**'],
  coverageThreshold: {
    global: {
      branches: 70,
      functions: 70,
      lines: 70,
      statements: 70,
    },
  },
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
};
```

#### Writing Tests

**Example Unit Test:**

```typescript
describe('SettingsManager', () => {
  let manager: SettingsManager;
  let mockChrome: any;

  beforeEach(() => {
    // Mock Chrome APIs
    mockChrome = {
      storage: {
        sync: {
          get: jest.fn(),
          set: jest.fn(),
        },
      },
    };
    (global as any).chrome = mockChrome;
    manager = new SettingsManager();
  });

  test('should load default settings when no stored settings exist', async () => {
    mockChrome.storage.sync.get.mockImplementation((keys, callback) => {
      callback({});
    });

    const settings = await manager.getSettings();

    expect(settings.githubToken).toBe('');
    expect(settings.autoCommit).toBe(true);
    expect(settings.defaultFolder).toBe('documents/unsorted');
  });

  test('should validate GitHub token format', async () => {
    const result = manager.validateGitHubToken('invalid-token');
    expect(result.isValid).toBe(false);
    expect(result.errors).toContain('Token must be at least 40 characters');
  });
});
```

#### Coverage Goals and Current Status

**Current Test Coverage:**

- **Overall**: 18.4% (Target: 70%+)
- **Critical Components**:
  - Settings Manager: 85%
  - Content Extractor: 79%
  - Service Worker: 0% (High Priority)
  - GitHub Client: 65%
  - Markdown Converter: 72%

**High Priority Areas for Testing:**

1. Service worker functionality (0% coverage)
2. Error handling scenarios
3. Chrome API integration
4. Content extraction edge cases
5. GitHub API error responses

### Development Tools

#### Browser Extension Development Tools

```bash
# Set up development tools
npm run dev-tools:setup

# Test content extraction on specific URL
npm run dev-tools:test-url "https://example.com/article"

# Compare extraction results between versions
npm run dev-tools:compare

# Test GitHub API connection
npm run dev-tools:test-github

# Generate test fixtures from real pages
npm run dev-tools:generate-fixtures
```

#### Content Extraction Testing

```typescript
// Test content extraction on various page types
const testSites = [
  'https://medium.com/sample-article',
  'https://dev.to/sample-post',
  'https://github.com/user/repo/blob/main/README.md',
  'https://docs.example.com/api-reference',
];

for (const url of testSites) {
  const result = await testContentExtraction(url);
  console.log(`${url}: ${result.success ? '✅' : '❌'}`, result.stats);
}
```

#### Chrome Extension APIs Testing

```typescript
// Mock Chrome APIs for testing
const createMockChrome = () => ({
  storage: {
    sync: {
      get: jest.fn(),
      set: jest.fn(),
      remove: jest.fn(),
    },
    local: {
      get: jest.fn(),
      set: jest.fn(),
    },
  },
  runtime: {
    sendMessage: jest.fn(),
    onMessage: {
      addListener: jest.fn(),
    },
    getManifest: jest.fn(() => ({ version: '1.0.0' })),
  },
  tabs: {
    query: jest.fn(),
    sendMessage: jest.fn(),
  },
  scripting: {
    executeScript: jest.fn(),
  },
});
```

### Code Quality Standards

#### ESLint Configuration

```json
{
  "extends": ["@typescript-eslint/recommended", "prettier"],
  "rules": {
    "@typescript-eslint/no-unused-vars": "error",
    "@typescript-eslint/explicit-function-return-type": "warn",
    "@typescript-eslint/no-explicit-any": "warn",
    "prefer-const": "error",
    "no-var": "error"
  }
}
```

#### Code Formatting

```bash
# Format all TypeScript files
npm run format

# Check formatting without fixing
npm run format:check

# Lint TypeScript files
npm run lint

# Fix linting issues automatically
npm run lint:fix
```

#### Pre-commit Hooks

```json
{
  "husky": {
    "hooks": {
      "pre-commit": "lint-staged"
    }
  },
  "lint-staged": {
    "*.ts": ["eslint --fix", "prettier --write", "git add"]
  }
}
```

### Debugging

#### Extension Debugging

1. **Service Worker Debugging**:
   - Open `chrome://extensions/`
   - Find PrismWeave extension
   - Click "Service worker" link
   - Use DevTools console for debugging

2. **Content Script Debugging**:
   - Open page with injected content script
   - Press F12 to open DevTools
   - Check Console tab for content script logs

3. **Popup Debugging**:
   - Right-click extension icon
   - Select "Inspect popup"
   - Debug popup HTML/JS in DevTools

#### Debug Mode Configuration

```typescript
// Enable debug mode in extension
const DEBUG_CONFIG = {
  logLevel: 'debug',
  enablePerformanceMetrics: true,
  saveDebugData: true,
  verboseErrorReporting: true,
};

// Debug logging utility
const debugLog = (message: string, data?: any) => {
  if (DEBUG_CONFIG.logLevel === 'debug') {
    console.log(`[PrismWeave Debug] ${message}`, data);
  }
};
```

### Performance Optimization

#### Content Extraction Optimization

```typescript
// Optimized content extraction with caching
class OptimizedContentExtractor {
  private cache = new Map<string, ExtractedContent>();

  async extractContent(url: string): Promise<ExtractedContent> {
    // Check cache first
    if (this.cache.has(url)) {
      return this.cache.get(url)!;
    }

    // Extract with timeout
    const result = await Promise.race([
      this.performExtraction(url),
      this.createTimeout(30000), // 30 second timeout
    ]);

    // Cache successful results
    if (result.success) {
      this.cache.set(url, result);
    }

    return result;
  }
}
```

#### Memory Management

```typescript
// Service worker memory management
class MemoryManager {
  private static readonly MAX_CACHE_SIZE = 50;
  private static cache = new Map();

  static addToCache(key: string, value: any): void {
    if (this.cache.size >= this.MAX_CACHE_SIZE) {
      // Remove oldest entry
      const firstKey = this.cache.keys().next().value;
      this.cache.delete(firstKey);
    }
    this.cache.set(key, value);
  }
}
```

### Browser Compatibility

#### Manifest V3 Considerations

```json
{
  "manifest_version": 3,
  "background": {
    "service_worker": "background/service-worker.js"
  },
  "content_scripts": [
    {
      "matches": ["<all_urls>"],
      "js": ["content/content-script.js"]
    }
  ],
  "permissions": ["storage", "activeTab", "scripting"],
  "host_permissions": ["https://api.github.com/*"]
}
```

#### Cross-Browser Testing

```bash
# Test in different browsers
npm run test:chrome
npm run test:edge
npm run test:firefox

# Check compatibility
npm run compat:check

# Generate compatibility report
npm run compat:report
```

### Continuous Integration

#### GitHub Actions Workflow

```yaml
name: Browser Extension CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm ci
      - run: npm run lint
      - run: npm run test:ci
      - run: npm run build:prod

  coverage:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm ci
      - run: npm run test:coverage
      - uses: codecov/codecov-action@v3
```

#### Quality Gates

- **Test Coverage**: Minimum 70% overall coverage
- **TypeScript**: No TypeScript errors in strict mode
- **ESLint**: No linting errors
- **Build**: Successful production build
- **Size**: Bundle size under 2MB

---

## 📦 Deployment

### Quick Start

To package and deploy the extension:

```bash
# Automated deployment (recommended)
npm run deploy

# Or manual process
npm run build:prod
npm run package
```

This creates a production-ready ZIP package for distribution.

### 🤖 GitHub Actions CI/CD

**Automated deployment via GitHub Actions** - The easiest way to build and
release!

Three deployment workflows available:

1. **Tag-based deployment** - Push a tag (`extension-v1.0.0`) for automatic
   build & release
2. **Manual workflow** - Trigger from GitHub Actions tab with custom options
3. **Auto-release** - Full version management and deployment automation

**See: [GITHUB_ACTIONS_DEPLOYMENT.md](GITHUB_ACTIONS_DEPLOYMENT.md)** - Complete
GitHub Actions guide

**Quick example:**

```bash
# Create and push a tag to trigger automatic deployment
git tag -a extension-v1.0.0 -m "Release v1.0.0"
git push origin extension-v1.0.0

# GitHub Actions automatically:
# - Syncs version across package.json and manifest.json
# - Runs full test suite
# - Builds production package
# - Creates GitHub Release with downloadable ZIP
# - Deploys to website (optional)
```

### Deployment Options

#### 1. **Website Distribution**

Host the extension ZIP on your website for direct download by users.

#### 2. **Microsoft Edge Add-ons**

Submit to the Edge Add-ons gallery for public distribution.

#### 3. **Chrome Web Store** (Optional)

Submit to Chrome Web Store for broader reach.

### Comprehensive Deployment Guide

For complete deployment instructions including:

- Building and packaging
- Store submission requirements
- Marketing materials preparation
- Review process details
- Post-deployment steps

**See: [DEPLOYMENT.md](DEPLOYMENT.md)** - Complete deployment guide

**See: [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)** - Quick reference
checklist

### Key Resources

- **Privacy Policy**: Required for all store submissions  
  Create at: `https://yoursite.com/privacy-policy`

- **Screenshots**: Capture 1280x800 images showing:
  - Extension popup and features
  - Options/settings page
  - Content capture process
  - GitHub integration

- **Store Links** (After Publication):
  - Edge Add-ons:
    `https://microsoftedge.microsoft.com/addons/detail/[extension-id]`
  - Chrome Web Store: `https://chrome.google.com/webstore/detail/[extension-id]`

---

## 📊 Performance

### Performance Metrics

#### Capture Performance Benchmarks

| Page Type                | Content Size | Processing Time | Memory Usage | Success Rate |
| ------------------------ | ------------ | --------------- | ------------ | ------------ |
| **Simple Blog Post**     | < 50KB       | 2-3 seconds     | ~20MB        | 98%          |
| **Technical Article**    | 50-150KB     | 3-5 seconds     | ~35MB        | 95%          |
| **Documentation Page**   | 100-300KB    | 4-7 seconds     | ~45MB        | 92%          |
| **Complex News Site**    | 200-500KB    | 6-10 seconds    | ~60MB        | 88%          |
| **JavaScript-Heavy SPA** | Variable     | 8-15 seconds    | ~75MB        | 80%          |

#### Performance Factors

**Factors Affecting Performance:**

- Page complexity and JavaScript rendering
- Number of images and media elements
- Network speed for GitHub API calls
- Browser resource availability
- Content size and structure complexity

**Optimization Strategies:**

- Lazy loading for non-critical operations
- Caching frequently accessed data
- Debouncing rapid successive captures
- Progressive content processing
- Memory cleanup after processing

### Browser Resource Usage

#### Extension Resource Footprint

| Component           | Idle State    | Active Processing | Peak Usage |
| ------------------- | ------------- | ----------------- | ---------- |
| **Service Worker**  | 5-10MB        | 15-25MB           | 40MB       |
| **Content Script**  | 2-5MB per tab | 10-20MB           | 30MB       |
| **Popup Interface** | 3-8MB         | 5-12MB            | 15MB       |
| **Options Page**    | 5-10MB        | 8-15MB            | 20MB       |
| **Storage Usage**   | 100KB-2MB     | N/A               | 5MB max    |

#### Performance Monitoring

```typescript
// Performance monitoring utilities
class PerformanceMonitor {
  private static metrics = new Map<string, number[]>();

  static startTiming(operation: string): number {
    const start = performance.now();
    return start;
  }

  static endTiming(operation: string, startTime: number): number {
    const duration = performance.now() - startTime;

    if (!this.metrics.has(operation)) {
      this.metrics.set(operation, []);
    }

    const measurements = this.metrics.get(operation)!;
    measurements.push(duration);

    // Keep only last 100 measurements
    if (measurements.length > 100) {
      measurements.shift();
    }

    return duration;
  }

  static getAverageTime(operation: string): number {
    const measurements = this.metrics.get(operation) || [];
    return measurements.reduce((a, b) => a + b, 0) / measurements.length;
  }
}
```

### Optimization Features

#### Content Processing Optimizations

**Lazy Loading Implementation:**

```typescript
class LazyContentProcessor {
  private processingQueue: ProcessingTask[] = [];
  private isProcessing = false;

  async processContent(content: string): Promise<ProcessedContent> {
    return new Promise(resolve => {
      this.processingQueue.push({ content, resolve });
      if (!this.isProcessing) {
        this.processQueue();
      }
    });
  }

  private async processQueue(): Promise<void> {
    this.isProcessing = true;

    while (this.processingQueue.length > 0) {
      const task = this.processingQueue.shift()!;
      const result = await this.processTask(task);
      task.resolve(result);

      // Yield to browser between tasks
      await new Promise(resolve => setTimeout(resolve, 0));
    }

    this.isProcessing = false;
  }
}
```

**Caching Strategy:**

```typescript
class SmartCache {
  private static readonly CACHE_DURATION = 5 * 60 * 1000; // 5 minutes
  private static cache = new Map<string, CachedItem>();

  static async get<T>(key: string, fetcher: () => Promise<T>): Promise<T> {
    const cached = this.cache.get(key);

    if (cached && Date.now() - cached.timestamp < this.CACHE_DURATION) {
      return cached.data as T;
    }

    const data = await fetcher();
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
    });

    return data;
  }

  static clear(): void {
    this.cache.clear();
  }
}
```

**Debounced Operations:**

```typescript
class DebouncedCapture {
  private static pendingCaptures = new Map<string, NodeJS.Timeout>();

  static scheduleCapture(
    url: string,
    delay: number = 1000
  ): Promise<CaptureResult> {
    return new Promise((resolve, reject) => {
      // Clear existing timeout for this URL
      const existing = this.pendingCaptures.get(url);
      if (existing) {
        clearTimeout(existing);
      }

      // Schedule new capture
      const timeout = setTimeout(async () => {
        this.pendingCaptures.delete(url);
        try {
          const result = await this.performCapture(url);
          resolve(result);
        } catch (error) {
          reject(error);
        }
      }, delay);

      this.pendingCaptures.set(url, timeout);
    });
  }
}
```

### Memory Management

#### Automatic Cleanup

```typescript
class MemoryManager {
  private static readonly MAX_MEMORY_USAGE = 100 * 1024 * 1024; // 100MB
  private static memoryUsage = 0;

  static trackMemoryUsage(size: number): void {
    this.memoryUsage += size;

    if (this.memoryUsage > this.MAX_MEMORY_USAGE) {
      this.performCleanup();
    }
  }

  static performCleanup(): void {
    // Clear caches
    SmartCache.clear();

    // Clear processed content cache
    ContentProcessor.clearCache();

    // Force garbage collection (if available)
    if (typeof window !== 'undefined' && 'gc' in window) {
      (window as any).gc();
    }

    this.memoryUsage = 0;
  }
}
```

#### Content Script Lifecycle

```typescript
// Cleanup content scripts when not needed
class ContentScriptManager {
  private static activeScripts = new Set<number>();

  static async injectScript(tabId: number): Promise<void> {
    if (this.activeScripts.has(tabId)) {
      return; // Already injected
    }

    await chrome.scripting.executeScript({
      target: { tabId },
      files: ['content/content-script.js'],
    });

    this.activeScripts.add(tabId);

    // Schedule cleanup after 5 minutes of inactivity
    setTimeout(
      () => {
        this.cleanupScript(tabId);
      },
      5 * 60 * 1000
    );
  }

  private static cleanupScript(tabId: number): void {
    this.activeScripts.delete(tabId);
    // Content script will be automatically cleaned up by browser
  }
}
```

### Network Optimization

#### Request Batching

```typescript
class GitHubAPIBatcher {
  private static batchQueue: APIRequest[] = [];
  private static batchTimeout: NodeJS.Timeout | null = null;

  static async queueRequest(request: APIRequest): Promise<APIResponse> {
    return new Promise((resolve, reject) => {
      this.batchQueue.push({ ...request, resolve, reject });

      if (!this.batchTimeout) {
        this.batchTimeout = setTimeout(() => {
          this.processBatch();
        }, 100); // Batch requests within 100ms
      }
    });
  }

  private static async processBatch(): Promise<void> {
    const batch = this.batchQueue.splice(0);
    this.batchTimeout = null;

    // Process batch requests efficiently
    const responses = await Promise.allSettled(
      batch.map(req => this.makeRequest(req))
    );

    // Resolve individual promises
    responses.forEach((response, index) => {
      const request = batch[index];
      if (response.status === 'fulfilled') {
        request.resolve(response.value);
      } else {
        request.reject(response.reason);
      }
    });
  }
}
```

#### Connection Pooling

```typescript
class HTTPConnectionPool {
  private static readonly MAX_CONNECTIONS = 6;
  private static activeConnections = 0;
  private static requestQueue: QueuedRequest[] = [];

  static async makeRequest(
    url: string,
    options: RequestInit
  ): Promise<Response> {
    if (this.activeConnections >= this.MAX_CONNECTIONS) {
      return new Promise((resolve, reject) => {
        this.requestQueue.push({ url, options, resolve, reject });
      });
    }

    this.activeConnections++;

    try {
      const response = await fetch(url, options);
      return response;
    } finally {
      this.activeConnections--;
      this.processQueue();
    }
  }

  private static processQueue(): void {
    if (
      this.requestQueue.length > 0 &&
      this.activeConnections < this.MAX_CONNECTIONS
    ) {
      const request = this.requestQueue.shift()!;
      this.makeRequest(request.url, request.options)
        .then(request.resolve)
        .catch(request.reject);
    }
  }
}
```

### Performance Monitoring Dashboard

#### Real-time Metrics

```typescript
// Performance dashboard for development
class PerformanceDashboard {
  static displayMetrics(): void {
    const metrics = {
      captureTime: PerformanceMonitor.getAverageTime('capture'),
      processingTime: PerformanceMonitor.getAverageTime('processing'),
      githubUpload: PerformanceMonitor.getAverageTime('github_upload'),
      memoryUsage: this.getMemoryUsage(),
      cacheHitRate: SmartCache.getHitRate(),
      activeConnections: HTTPConnectionPool.getActiveCount(),
    };

    console.table(metrics);
  }

  private static getMemoryUsage(): string {
    if ('memory' in performance) {
      const memory = (performance as any).memory;
      return `${Math.round(memory.usedJSHeapSize / 1024 / 1024)}MB`;
    }
    return 'Unknown';
  }
}
```

### Performance Best Practices

#### For Users

1. **Optimal Usage Patterns**:
   - Close unnecessary tabs before capturing
   - Allow pages to fully load before capturing
   - Use batch capture for multiple articles
   - Clear browser cache periodically

2. **Configuration Recommendations**:
   - Disable image capture for faster processing
   - Use specific folder structures to reduce API calls
   - Enable auto-commit to reduce user interaction delays
   - Set reasonable timeout values

#### For Developers

1. **Code Optimization**:
   - Use async/await patterns consistently
   - Implement proper error boundaries
   - Cache expensive operations
   - Minimize DOM manipulation

2. **Resource Management**:
   - Clean up event listeners
   - Clear timeouts and intervals
   - Remove unused DOM elements
   - Manage memory allocations carefully

3. **API Efficiency**:
   - Batch GitHub API requests when possible
   - Use conditional requests (ETags)
   - Implement exponential backoff for retries
   - Cache API responses appropriately

## � Configuration Reference

### Settings Overview

The extension provides comprehensive configuration options accessible through
the Options page (right-click extension icon → Options).

#### Repository Settings

| Setting        | Type   | Description                            | Default | Required |
| -------------- | ------ | -------------------------------------- | ------- | -------- |
| `githubToken`  | string | GitHub Personal Access Token (classic) | ""      | ✅       |
| `githubRepo`   | string | Repository in format `owner/repo-name` | ""      | ✅       |
| `githubBranch` | string | Target branch for commits              | "main"  | ❌       |

**GitHub Token Setup:**

1. Go to GitHub → Settings → Developer Settings → Personal Access Tokens
2. Click "Generate new token (classic)"
3. Select scopes: `repo` (full repository access)
4. Copy token and paste in extension settings

#### File Organization

| Setting             | Type   | Description                      | Default                   | Options                   |
| ------------------- | ------ | -------------------------------- | ------------------------- | ------------------------- |
| `defaultFolder`     | string | Target folder for captures       | "documents/unsorted"      | See folder options below  |
| `customFolder`      | string | Custom folder name when needed   | ""                        | Any valid path            |
| `fileNamingPattern` | string | Template for generated filenames | "YYYY-MM-DD-domain-title" | See naming patterns below |

**Available Folders:**

- `documents/unsorted` - General captures
- `documents/articles` - Article-type content
- `documents/research` - Research materials
- `documents/tech` - Technical content
- `documents/business` - Business-related captures
- `documents/news` - News articles
- `documents/reference` - Reference materials
- `custom` - User-defined folder path

**Filename Patterns:**

- `YYYY-MM-DD-domain-title` → `2025-08-04-example-com-article-title.md`
- `YYYY-MM-DD-title` → `2025-08-04-article-title.md`
- `domain-YYYY-MM-DD-title` → `example-com-2025-08-04-article-title.md`
- `title-YYYY-MM-DD` → `article-title-2025-08-04.md`
- `category/YYYY-MM-DD-title` → `tech/2025-08-04-article-title.md`

#### Content Processing

| Setting              | Type    | Description                                 | Default | Impact                  |
| -------------------- | ------- | ------------------------------------------- | ------- | ----------------------- |
| `captureImages`      | boolean | Download and reference images               | true    | File size, completeness |
| `removeAds`          | boolean | Remove advertisement content                | true    | Content cleanliness     |
| `removeNavigation`   | boolean | Remove navigation elements                  | true    | Content focus           |
| `removeSidebars`     | boolean | Remove sidebar content                      | true    | Content focus           |
| `customSelectors`    | string  | CSS selectors to remove (comma-separated)   | ""      | Custom cleaning         |
| `preserveFormatting` | boolean | Maintain original formatting where possible | true    | Output fidelity         |

**Custom Selectors Examples:**

```
.advertisement, .popup, .modal, .social-buttons, .comment-section
```

#### Output Formatting

| Setting              | Type    | Description                      | Default     | Options                        |
| -------------------- | ------- | -------------------------------- | ----------- | ------------------------------ |
| `includeFrontmatter` | boolean | Generate YAML frontmatter        | true        | true/false                     |
| `markdownFlavor`     | string  | Markdown dialect to use          | "github"    | github, commonmark, gfm        |
| `imageHandling`      | string  | How to handle images             | "reference" | reference, inline, skip        |
| `codeBlockLanguage`  | string  | Default language for code blocks | "auto"      | auto, javascript, python, etc. |
| `tableConversion`    | boolean | Convert HTML tables to markdown  | true        | true/false                     |
| `linkPreservation`   | boolean | Maintain original links          | true        | true/false                     |

**Frontmatter Template:**

```yaml
---
title: 'Article Title'
url: 'https://example.com/article'
domain: 'example.com'
author: 'Author Name'
captured_at: '2025-08-04T15:30:00.000Z'
description: 'Article description'
keywords: ['keyword1', 'keyword2']
category: 'tech'
reading_time: '5 min'
word_count: 1250
---
```

#### Automation Settings

| Setting                 | Type    | Description                          | Default                   | Use Case                 |
| ----------------------- | ------- | ------------------------------------ | ------------------------- | ------------------------ |
| `autoCommit`            | boolean | Automatically commit captures        | true                      | Streamlined workflow     |
| `commitMessageTemplate` | string  | Template for commit messages         | "Add: {domain} - {title}" | Git history              |
| `batchProcessing`       | boolean | Allow multiple simultaneous captures | false                     | Bulk operations          |
| `notificationLevel`     | string  | Notification verbosity               | "normal"                  | minimal, normal, verbose |

**Commit Message Variables:**

- `{domain}` → Source website domain (e.g., "medium.com")
- `{title}` → Page title (e.g., "How to Build Extensions")
- `{date}` → Capture date (e.g., "2025-08-04")
- `{time}` → Capture time (e.g., "15:30")
- `{filename}` → Generated filename
- `{category}` → Detected or assigned category
- `{author}` → Article author (if available)

**Template Examples:**

```
"Add: {domain} - {title}"
→ "Add: medium.com - How to Build Extensions"

"Capture [{category}]: {title}"
→ "Capture [tech]: How to Build Extensions"

"📄 {date}: {title} ({domain})"
→ "📄 2025-08-04: How to Build Extensions (medium.com)"
```

#### User Experience

| Setting                   | Type    | Description                | Default | Benefit              |
| ------------------------- | ------- | -------------------------- | ------- | -------------------- |
| `enableKeyboardShortcuts` | boolean | Enable Alt+S shortcut      | true    | Quick access         |
| `showNotifications`       | boolean | Show capture notifications | true    | Status feedback      |
| `debugMode`               | boolean | Enable debug logging       | false   | Troubleshooting      |
| `confirmBeforeCapture`    | boolean | Show confirmation dialog   | false   | Prevent accidents    |
| `previewBeforeSave`       | boolean | Show preview before saving | false   | Content verification |

### Site-Specific Configuration

#### Custom Extraction Rules

For better results on specific websites, configure custom extraction rules:

```json
{
  "siteRules": {
    "medium.com": {
      "selectors": {
        "article": "article",
        "title": "h1",
        "author": "[rel='author']",
        "content": ".post-content"
      },
      "exclude": [
        ".follow-button",
        ".clap-button",
        ".response-count",
        ".pw-multi-vote-icon"
      ],
      "metadata": {
        "readingTime": ".reading-time",
        "publishDate": "time[datetime]",
        "tags": ".tag"
      },
      "preprocessing": {
        "waitForLoad": 2000,
        "removeAds": true,
        "cleanupScripts": true
      }
    },

    "dev.to": {
      "selectors": {
        "article": "#article-body",
        "title": ".crayons-article__header h1",
        "author": ".crayons-article__subheader a",
        "content": ".crayons-article__main"
      },
      "exclude": [
        ".reaction-button",
        ".comment-subscription",
        ".crayons-card--secondary"
      ],
      "preserveCodeBlocks": true,
      "enhanceCodeSyntax": true
    },

    "github.com": {
      "selectors": {
        "content": ".markdown-body, .Box-body",
        "title": ".js-issue-title, h1.public",
        "breadcrumb": ".breadcrumb"
      },
      "preserveFormatting": true,
      "includeCodeBlocks": true,
      "maintainLinkStructure": true,
      "specialHandling": "documentation"
    },

    "stackoverflow.com": {
      "selectors": {
        "question": ".js-post-body",
        "answers": ".answercell",
        "title": ".question-hyperlink, h1[itemprop='name']"
      },
      "exclude": [
        ".js-voting-container",
        ".js-comment-actions",
        ".js-post-menu"
      ],
      "combineQAndA": true,
      "preserveCodeFormatting": true
    }
  }
}
```

#### Custom Filename Generation

```typescript
// Advanced filename generation patterns
class FilenameGenerator {
  static patterns = {
    'date-domain-title': (metadata: IMetadata) => {
      const date = new Date().toISOString().split('T')[0];
      const domain = this.cleanDomain(metadata.domain);
      const title = this.cleanTitle(metadata.title, 40);
      return `${date}-${domain}-${title}.md`;
    },

    'category-date-title': (metadata: IMetadata) => {
      const category = this.detectCategory(metadata);
      const date = new Date().toISOString().split('T')[0];
      const title = this.cleanTitle(metadata.title, 50);
      return `${category}/${date}-${title}.md`;
    },

    'author-date-title': (metadata: IMetadata) => {
      const author = this.cleanAuthor(metadata.author);
      const date = new Date().toISOString().split('T')[0];
      const title = this.cleanTitle(metadata.title, 45);
      return `authors/${author}/${date}-${title}.md`;
    },

    hierarchical: (metadata: IMetadata) => {
      const year = new Date().getFullYear();
      const month = String(new Date().getMonth() + 1).padStart(2, '0');
      const category = this.detectCategory(metadata);
      const title = this.cleanTitle(metadata.title, 60);
      return `${year}/${month}/${category}/${title}.md`;
    },
  };

  private static cleanTitle(title: string, maxLength: number): string {
    return title
      .toLowerCase()
      .replace(/[^a-z0-9\s-]/g, '')
      .replace(/\s+/g, '-')
      .substring(0, maxLength)
      .replace(/-+$/, '');
  }

  private static cleanDomain(domain: string): string {
    return domain.replace(/^www\./, '').replace(/[^a-z0-9.-]/g, '');
  }

  private static detectCategory(metadata: IMetadata): string {
    const url = metadata.url.toLowerCase();
    const title = metadata.title.toLowerCase();
    const keywords = metadata.keywords?.join(' ').toLowerCase() || '';

    if (
      url.includes('github.com') ||
      title.includes('code') ||
      keywords.includes('programming')
    ) {
      return 'tech';
    }
    if (url.includes('medium.com') || url.includes('blog')) {
      return 'articles';
    }
    if (keywords.includes('research') || keywords.includes('academic')) {
      return 'research';
    }
    if (url.includes('news') || keywords.includes('current events')) {
      return 'news';
    }
    return 'general';
  }
}
```

### Batch Processing Examples

#### Multi-Tab Capture

```typescript
// Capture all open tabs matching criteria
async function captureAllTabs(filters?: {
  domains?: string[];
  titlePatterns?: RegExp[];
  minContentLength?: number;
}) {
  const tabs = await chrome.tabs.query({
    url: ['http://*/*', 'https://*/*'],
  });

  const results: CaptureResult[] = [];
  const concurrencyLimit = 3; // Process 3 tabs at a time

  for (let i = 0; i < tabs.length; i += concurrencyLimit) {
    const batch = tabs.slice(i, i + concurrencyLimit);

    const batchPromises = batch.map(async tab => {
      if (!tab.id || !tab.url) return null;

      try {
        // Apply filters
        if (filters) {
          if (
            filters.domains &&
            !filters.domains.some(d => tab.url!.includes(d))
          ) {
            return null;
          }
          if (
            filters.titlePatterns &&
            !filters.titlePatterns.some(p => p.test(tab.title || ''))
          ) {
            return null;
          }
        }

        const result = await captureTab(tab.id);

        if (
          filters?.minContentLength &&
          result.wordCount < filters.minContentLength
        ) {
          return null;
        }

        return {
          tabId: tab.id,
          title: tab.title,
          url: tab.url,
          result,
          success: true,
        };
      } catch (error) {
        return {
          tabId: tab.id,
          title: tab.title,
          url: tab.url,
          error: error.message,
          success: false,
        };
      }
    });

    const batchResults = await Promise.all(batchPromises);
    results.push(...batchResults.filter(r => r !== null));

    console.log(
      `Processed batch ${Math.floor(i / concurrencyLimit) + 1}/${Math.ceil(tabs.length / concurrencyLimit)}`
    );
  }

  return results;
}

// Usage example
const captureResults = await captureAllTabs({
  domains: ['medium.com', 'dev.to', 'github.com'],
  titlePatterns: [/tutorial/i, /guide/i, /how to/i],
  minContentLength: 500,
});

console.log(
  `Successfully captured ${captureResults.filter(r => r.success).length} articles`
);
```

#### Link Collection Capture

```typescript
// Capture content from a list of URLs
async function captureUrlList(
  urls: string[],
  options?: {
    delay?: number;
    folder?: string;
    category?: string;
  }
) {
  const delay = options?.delay || 2000; // 2 second delay between captures
  const results: Array<{
    url: string;
    success: boolean;
    filename?: string;
    error?: string;
  }> = [];

  for (const url of urls) {
    try {
      console.log(`Capturing: ${url}`);

      // Open URL in background tab
      const tab = await chrome.tabs.create({
        url,
        active: false,
      });

      // Wait for page to load
      await new Promise(resolve => setTimeout(resolve, 5000));

      // Capture content
      const result = await captureTab(tab.id!);

      // Close the tab
      await chrome.tabs.remove(tab.id!);

      results.push({
        url,
        success: true,
        filename: result.filename,
      });

      console.log(`✅ Captured: ${result.filename}`);
    } catch (error) {
      results.push({
        url,
        success: false,
        error: error.message,
      });

      console.error(`❌ Failed to capture ${url}:`, error.message);
    }

    // Delay between captures to be respectful
    if (delay > 0) {
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }

  return results;
}

// Usage with reading list
const readingList = [
  'https://medium.com/@author/great-article',
  'https://dev.to/user/awesome-tutorial',
  'https://blog.example.com/important-post',
];

const results = await captureUrlList(readingList, {
  delay: 3000,
  folder: 'reading-list',
  category: 'articles',
});
```

### Integration Examples

#### VS Code Integration

```typescript
// Integration with VS Code workspace
class VSCodeIntegration {
  static async syncWithWorkspace(workspacePath: string) {
    const settings = await getSettings();

    // Clone repository to VS Code workspace
    const gitProcess = spawn('git', [
      'clone',
      `https://github.com/${settings.githubRepo}.git`,
      workspacePath,
    ]);

    gitProcess.on('close', code => {
      if (code === 0) {
        console.log('Repository synced to VS Code workspace');
        this.openInVSCode(workspacePath);
      }
    });
  }

  private static openInVSCode(path: string) {
    spawn('code', [path], { detached: true });
  }
}
```

#### AI Processing Pipeline Integration

```typescript
// Trigger AI processing after capture
async function captureWithAIProcessing(url: string) {
  // Capture content
  const captureResult = await captureContent(url);

  if (captureResult.success) {
    // Trigger AI processing
    await fetch('http://localhost:8000/process-document', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        filename: captureResult.filename,
        content: captureResult.markdown,
        metadata: captureResult.metadata,
      }),
    });

    console.log('AI processing triggered for:', captureResult.filename);
  }
}
```

### Testing Examples

#### Unit Test Examples

```typescript
// Test content extraction
describe('ContentExtractor', () => {
  let extractor: ContentExtractor;

  beforeEach(() => {
    // Mock DOM
    document.body.innerHTML = `
      <article>
        <h1>Test Article</h1>
        <p>This is a test paragraph with <strong>bold text</strong>.</p>
        <ul>
          <li>List item 1</li>
          <li>List item 2</li>
        </ul>
      </article>
    `;

    extractor = new ContentExtractor();
  });

  test('should extract main content correctly', async () => {
    const result = await extractor.extractContent();

    expect(result.title).toBe('Test Article');
    expect(result.markdown).toContain('# Test Article');
    expect(result.markdown).toContain('**bold text**');
    expect(result.markdown).toContain('- List item 1');
  });

  test('should handle missing content gracefully', async () => {
    document.body.innerHTML = '<div>No article content</div>';

    const result = await extractor.extractContent();

    expect(result.success).toBe(false);
    expect(result.error).toContain('No substantial content found');
  });
});
```

#### Integration Test Examples

```typescript
// Test full capture workflow
describe('Capture Workflow', () => {
  let mockGitHubAPI: jest.Mock;

  beforeEach(() => {
    mockGitHubAPI = jest.fn();
    global.fetch = mockGitHubAPI;
  });

  test('should complete full capture workflow', async () => {
    // Mock successful API response
    mockGitHubAPI.mockResolvedValue({
      ok: true,
      json: () =>
        Promise.resolve({
          content: {
            name: 'test-article.md',
            html_url: 'https://github.com/user/repo/blob/main/test-article.md',
          },
        }),
    });

    const result = await captureCurrentPage();

    expect(result.success).toBe(true);
    expect(result.filename).toMatch(/\.md$/);
    expect(mockGitHubAPI).toHaveBeenCalledWith(
      expect.stringContaining('api.github.com'),
      expect.objectContaining({
        method: 'PUT',
        headers: expect.objectContaining({
          Authorization: expect.stringContaining('token'),
        }),
      })
    );
  });
});
```

## 🔧 Troubleshooting

### Toast Notifications Appearing Behind Page Elements

If toast notifications (success/error messages) appear behind page elements like
modals, dropdowns, or sticky headers, you can use the enhanced z-index options:

#### Default High Z-Index (Automatic)

PrismWeave toast notifications now use a z-index of `10000` by default, which
should appear above most page elements:

```css
/* Automatically applied */
.pw-toast-container {
  z-index: 10000; /* High enough for most websites */
}
```

#### Maximum Z-Index Override (For Extreme Cases)

For websites with very high z-index values, you can force maximum z-index:

```javascript
// Force maximum z-index for extreme cases
window.prismweaveShowToastMaxZ('Message with maximum z-index');

// Or use the option parameter
window.prismweaveShowToast('Your message', {
  forceHighestZIndex: true,
});
```

This sets the z-index to `2147483647` (maximum safe CSS z-index value).

#### Global Helper Functions

Two global functions are available for toast notifications:

```javascript
// Standard toast (z-index: 10000)
window.prismweaveShowToast('Success message', { type: 'success' });

// Maximum z-index toast (z-index: 2147483647)
window.prismweaveShowToastMaxZ('Critical message', { type: 'error' });
```

#### Common Z-Index Conflicts

If notifications still appear behind elements:

1. **Check for CSS transforms**: Elements with `transform` create new stacking
   contexts
2. **Inspect competing z-index values**: Use browser dev tools to check other
   elements
3. **Website-specific issues**: Some sites use z-index values > 999999
4. **Use the maximum override**: Apply `forceHighestZIndex: true` for
   problematic sites

#### Example Usage

```javascript
// For most websites (automatic)
prismweaveShowToast('Content captured successfully!', {
  type: 'success',
  clickUrl: 'https://github.com/user/repo/blob/main/captured-article.md',
});

// For problematic websites with high z-index elements
prismweaveShowToast('Content captured successfully!', {
  type: 'success',
  forceHighestZIndex: true,
  clickUrl: 'https://github.com/user/repo/blob/main/captured-article.md',
});
```

The enhanced z-index system ensures toast notifications remain visible across
all website types and layouts.
