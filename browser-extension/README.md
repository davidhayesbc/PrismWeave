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
PrismWeave offers a powerful bookmarklet alternative.

### What is the PrismWeave Bookmarklet?

The PrismWeave bookmarklet is a JavaScript-based tool that can be saved as a
browser bookmark. When clicked, it extracts content from the current page,
converts it to markdown, and saves it to your GitHub repository - all without
requiring a browser extension.

### Bookmarklet Setup

#### 1. Create the Bookmarklet

**Option A: Generate from Extension**

1. Install the PrismWeave browser extension (if available in your browser)
2. Open extension options
3. Navigate to "Bookmarklet" tab
4. Click "Generate Bookmarklet" - this creates a personalized bookmarklet with
   your GitHub settings
5. Drag the generated link to your bookmarks bar

**Option B: Manual Creation**

1. Copy the bookmarklet code below
2. Create a new bookmark in your browser
3. Set the name to "PrismWeave Capture"
4. Paste the code as the URL (starting with `javascript:`)

#### 2. Bookmarklet Code

````javascript
javascript: (function () {
  /* PrismWeave Content Capture Bookmarklet v1.0 */
  if (window.prismweaveBookmarklet) {
    return;
  }
  window.prismweaveBookmarklet = true;

  /* Configuration - Replace with your settings */
  const CONFIG = {
    githubToken: 'YOUR_GITHUB_TOKEN_HERE',
    githubRepo: 'YOUR_USERNAME/YOUR_REPO_NAME',
    githubBranch: 'main',
    defaultFolder: 'documents/unsorted',
    autoCommit: true,
  };

  /* Create UI */
  const overlay = document.createElement('div');
  overlay.style.cssText = `
    position: fixed; top: 20px; right: 20px; z-index: 999999;
    background: #2d3748; color: white; padding: 20px;
    border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    max-width: 350px; font-size: 14px;
  `;

  const status = document.createElement('div');
  status.innerHTML = '<strong>PrismWeave</strong><br/>Initializing...';
  overlay.appendChild(status);

  const progressBar = document.createElement('div');
  progressBar.style.cssText = `
    width: 100%; height: 4px; background: #4a5568;
    border-radius: 2px; margin: 10px 0; overflow: hidden;
  `;
  const progress = document.createElement('div');
  progress.style.cssText = `
    height: 100%; background: #4299e1; width: 0%;
    transition: width 0.3s ease;
  `;
  progressBar.appendChild(progress);
  overlay.appendChild(progressBar);

  const closeBtn = document.createElement('button');
  closeBtn.textContent = '×';
  closeBtn.style.cssText = `
    position: absolute; top: 5px; right: 10px;
    background: none; border: none; color: white;
    font-size: 20px; cursor: pointer; padding: 0;
    width: 20px; height: 20px; line-height: 1;
  `;
  closeBtn.onclick = () => {
    document.body.removeChild(overlay);
    window.prismweaveBookmarklet = false;
  };
  overlay.appendChild(closeBtn);

  document.body.appendChild(overlay);

  /* Content Extraction Functions */
  function updateProgress(percent, message) {
    progress.style.width = percent + '%';
    status.innerHTML = '<strong>PrismWeave</strong><br/>' + message;
  }

  function detectMainContent() {
    const selectors = [
      'article',
      'main',
      '[role="main"]',
      '.content',
      '.post',
      '.entry',
      '.article',
      '#content',
      '#main',
      '#post',
      '#entry',
    ];

    for (const selector of selectors) {
      const element = document.querySelector(selector);
      if (element && element.textContent.trim().length > 200) {
        return element;
      }
    }
    return document.body;
  }

  function cleanContent(element) {
    const clone = element.cloneNode(true);
    const removeSelectors = [
      'script',
      'style',
      'nav',
      'header',
      'footer',
      '.advertisement',
      '.ad',
      '.ads',
      '.popup',
      '.modal',
      '.social-share',
      '.comments',
      '.sidebar',
    ];

    removeSelectors.forEach(selector => {
      const elements = clone.querySelectorAll(selector);
      elements.forEach(el => el.remove());
    });

    return clone;
  }

  function htmlToMarkdown(html) {
    let markdown = html;

    /* Headers */
    markdown = markdown.replace(
      /<h([1-6])[^>]*>(.*?)<\/h[1-6]>/gi,
      (match, level, content) => {
        const headerLevel = '#'.repeat(parseInt(level));
        return `\n${headerLevel} ${content.replace(/<[^>]*>/g, '').trim()}\n`;
      }
    );

    /* Paragraphs */
    markdown = markdown.replace(/<p[^>]*>(.*?)<\/p>/gi, '\n$1\n');

    /* Bold/Strong */
    markdown = markdown.replace(
      /<(strong|b)[^>]*>(.*?)<\/(strong|b)>/gi,
      '**$2**'
    );

    /* Italic/Emphasis */
    markdown = markdown.replace(/<(em|i)[^>]*>(.*?)<\/(em|i)>/gi, '*$2*');

    /* Links */
    markdown = markdown.replace(
      /<a[^>]*href=["']([^"']*)["'][^>]*>(.*?)<\/a>/gi,
      '[$2]($1)'
    );

    /* Images */
    markdown = markdown.replace(
      /<img[^>]*src=["']([^"']*)["'][^>]*alt=["']([^"']*)["'][^>]*>/gi,
      '![$2]($1)'
    );
    markdown = markdown.replace(
      /<img[^>]*src=["']([^"']*)["'][^>]*>/gi,
      '![]($1)'
    );

    /* Lists */
    markdown = markdown.replace(/<ul[^>]*>(.*?)<\/ul>/gis, (match, content) => {
      const items = content.replace(/<li[^>]*>(.*?)<\/li>/gi, '- $1\n');
      return `\n${items}\n`;
    });

    /* Code blocks */
    markdown = markdown.replace(
      /<pre[^>]*><code[^>]*>(.*?)<\/code><\/pre>/gis,
      '\n```\n$1\n```\n'
    );
    markdown = markdown.replace(/<code[^>]*>(.*?)<\/code>/gi, '`$1`');

    /* Line breaks */
    markdown = markdown.replace(/<br[^>]*>/gi, '\n');

    /* Remove remaining HTML */
    markdown = markdown.replace(/<[^>]*>/g, '');

    /* Clean up whitespace */
    markdown = markdown.replace(/\n\s*\n\s*\n/g, '\n\n').trim();

    return markdown;
  }

  function generateFrontmatter(metadata) {
    const frontmatter = [
      '---',
      `title: '${metadata.title.replace(/'/g, "''")}'`,
      `url: '${metadata.url}'`,
      `domain: '${metadata.domain}'`,
      `captured_at: '${new Date().toISOString()}'`,
    ];

    if (metadata.author) {
      frontmatter.push(`author: '${metadata.author.replace(/'/g, "''")}'`);
    }

    if (metadata.description) {
      frontmatter.push(
        `description: '${metadata.description.replace(/'/g, "''")}'`
      );
    }

    if (metadata.keywords && metadata.keywords.length > 0) {
      frontmatter.push(
        `keywords: [${metadata.keywords.map(k => `'${k}'`).join(', ')}]`
      );
    }

    frontmatter.push('---', '');
    return frontmatter.join('\n');
  }

  function extractMetadata() {
    const getMetaContent = name => {
      const meta = document.querySelector(
        `meta[name="${name}"], meta[property="${name}"]`
      );
      return meta ? meta.getAttribute('content') : null;
    };

    const title =
      document.title ||
      getMetaContent('og:title') ||
      getMetaContent('twitter:title') ||
      'Untitled Page';

    const author =
      getMetaContent('author') ||
      getMetaContent('article:author') ||
      document.querySelector('[rel="author"]')?.textContent?.trim();

    const description =
      getMetaContent('description') ||
      getMetaContent('og:description') ||
      getMetaContent('twitter:description');

    const keywords =
      getMetaContent('keywords')
        ?.split(',')
        .map(k => k.trim()) || [];

    return {
      title,
      url: window.location.href,
      domain: window.location.hostname,
      author,
      description,
      keywords,
    };
  }

  async function saveToGitHub(content, filename) {
    const api = `https://api.github.com/repos/${CONFIG.githubRepo}/contents/${CONFIG.defaultFolder}/${filename}`;

    /* Check if file exists */
    let existingSha = null;
    try {
      const existing = await fetch(api, {
        headers: { Authorization: `token ${CONFIG.githubToken}` },
      });
      if (existing.ok) {
        const data = await existing.json();
        existingSha = data.sha;
      }
    } catch (e) {
      /* File doesn't exist, which is fine */
    }

    const commitData = {
      message: `Add captured article: ${filename}`,
      content: btoa(unescape(encodeURIComponent(content))),
      branch: CONFIG.githubBranch,
    };

    if (existingSha) {
      commitData.sha = existingSha;
    }

    const response = await fetch(api, {
      method: 'PUT',
      headers: {
        Authorization: `token ${CONFIG.githubToken}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(commitData),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(`GitHub API error: ${error.message}`);
    }

    return await response.json();
  }

  function generateFilename(title, domain) {
    const date = new Date().toISOString().split('T')[0];
    const cleanTitle = title
      .toLowerCase()
      .replace(/[^a-z0-9\s-]/g, '')
      .replace(/\s+/g, '-')
      .substring(0, 50);
    const cleanDomain = domain.replace(/[^a-z0-9.-]/g, '');
    return `${date}-${cleanDomain}-${cleanTitle}.md`;
  }

  /* Main Execution */
  async function captureContent() {
    try {
      updateProgress(10, 'Extracting page content...');

      const mainContent = detectMainContent();
      const cleanedContent = cleanContent(mainContent);

      updateProgress(30, 'Converting to markdown...');

      const markdown = htmlToMarkdown(cleanedContent.innerHTML);
      const metadata = extractMetadata();

      updateProgress(50, 'Generating frontmatter...');

      const frontmatter = generateFrontmatter(metadata);
      const document = frontmatter + '\n' + markdown;

      updateProgress(70, 'Saving to GitHub...');

      const filename = generateFilename(metadata.title, metadata.domain);
      const result = await saveToGitHub(document, filename);

      updateProgress(
        100,
        `✅ Saved successfully!<br/><small>File: ${filename}</small>`
      );

      /* Show success for 3 seconds, then close */
      setTimeout(() => {
        if (overlay.parentNode) {
          document.body.removeChild(overlay);
          window.prismweaveBookmarklet = false;
        }
      }, 3000);
    } catch (error) {
      updateProgress(
        0,
        `❌ Error: ${error.message}<br/><small>Check console for details</small>`
      );
      console.error('PrismWeave Bookmarklet Error:', error);
    }
  }

  /* Validate configuration */
  if (!CONFIG.githubToken || CONFIG.githubToken === 'YOUR_GITHUB_TOKEN_HERE') {
    updateProgress(
      0,
      '❌ Configuration required<br/><small>Please set your GitHub token in the bookmarklet code</small>'
    );
    return;
  }

  if (
    !CONFIG.githubRepo ||
    CONFIG.githubRepo === 'YOUR_USERNAME/YOUR_REPO_NAME'
  ) {
    updateProgress(
      0,
      '❌ Configuration required<br/><small>Please set your GitHub repository in the bookmarklet code</small>'
    );
    return;
  }

  /* Start capture */
  captureContent();
})();
````

#### 3. Customize Your Bookmarklet

Before using the bookmarklet, you must customize it with your GitHub settings:

1. **Replace `YOUR_GITHUB_TOKEN_HERE`** with your actual GitHub Personal Access
   Token
2. **Replace `YOUR_USERNAME/YOUR_REPO_NAME`** with your repository (e.g.,
   `johndoe/my-documents`)
3. **Adjust other settings** as needed:
   - `githubBranch`: Target branch (default: `main`)
   - `defaultFolder`: Where to save files (default: `documents/unsorted`)
   - `autoCommit`: Whether to commit automatically (default: `true`)

### Using the Bookmarklet

#### Basic Usage

1. **Navigate** to any web page you want to capture
2. **Click** the "PrismWeave Capture" bookmark in your bookmarks bar
3. **Wait** for the overlay to show progress
4. **Content is automatically extracted and saved** to your GitHub repository

#### Bookmarklet Interface

The bookmarklet displays a small overlay with:

- **Progress indicator**: Shows current step and completion percentage
- **Status messages**: Real-time feedback on processing
- **Close button**: Manual close option (auto-closes on success)
- **Error handling**: Clear error messages with troubleshooting hints

#### What the Bookmarklet Does

1. **Content Detection**: Automatically finds the main content area using
   semantic HTML
2. **Content Cleaning**: Removes ads, navigation, sidebars, and other clutter
3. **Markdown Conversion**: Converts HTML to clean, formatted markdown
4. **Metadata Extraction**: Pulls title, author, description, and keywords
5. **Frontmatter Generation**: Creates YAML frontmatter with metadata
6. **GitHub Integration**: Commits the file directly to your repository
7. **File Naming**: Generates descriptive filenames with date and source

### Bookmarklet Features

#### Content Processing

- **Smart Content Detection**: Uses multiple strategies to find main content
- **Ad/Clutter Removal**: Automatically removes common unwanted elements
- **Markdown Conversion**: Handles headers, paragraphs, lists, links, images,
  and code
- **Metadata Extraction**: Captures Open Graph, Twitter Card, and standard meta
  tags

#### File Management

- **Intelligent Filename Generation**: `YYYY-MM-DD-domain-title.md` format
- **Automatic Folder Organization**: Configurable target folders
- **Frontmatter Generation**: YAML headers with comprehensive metadata
- **Duplicate Handling**: Updates existing files if they already exist

#### Error Handling

- **Configuration Validation**: Checks for required settings before processing
- **Network Error Handling**: Graceful handling of GitHub API issues
- **Content Validation**: Ensures substantial content before processing
- **User Feedback**: Clear error messages and troubleshooting guidance

### Bookmarklet Testing

#### Test Setup

1. **Create a test repository** on GitHub for testing
2. **Use a test token** with limited permissions initially
3. **Test on simple pages** first (blog posts, articles)
4. **Verify output** in your repository

#### Test Procedure

```javascript
// Test the bookmarklet configuration
javascript: (function () {
  const CONFIG = {
    githubToken: 'YOUR_TOKEN',
    githubRepo: 'YOUR_REPO',
    githubBranch: 'main',
    defaultFolder: 'test-captures',
  };

  // Test GitHub API connection
  fetch(`https://api.github.com/repos/${CONFIG.githubRepo}`, {
    headers: { Authorization: `token ${CONFIG.githubToken}` },
  })
    .then(response => response.json())
    .then(data => {
      if (data.name) {
        alert(
          `✅ Configuration test passed!\nRepository: ${data.full_name}\nAccess: ${data.permissions ? 'Full' : 'Read-only'}`
        );
      } else {
        alert(`❌ Configuration test failed!\nError: ${data.message}`);
      }
    })
    .catch(error => {
      alert(`❌ Network error: ${error.message}`);
    });
})();
```

#### Common Test Scenarios

1. **Simple Blog Post**: Test on a clean blog post or article
2. **Complex Page**: Test on pages with lots of ads and navigation
3. **Documentation**: Test on technical documentation sites
4. **News Article**: Test on news websites with complex layouts
5. **Academic Paper**: Test on research papers or academic content

### Advanced Bookmarklet Customization

#### Custom Content Selectors

```javascript
// Add to bookmarklet configuration
const CUSTOM_SELECTORS = {
  'medium.com': {
    article: 'article',
    title: 'h1',
    exclude: ['.follow-button', '.clap-button'],
  },
  'dev.to': {
    article: '#article-body',
    title: '.crayons-article__header h1',
    exclude: ['.reaction-button'],
  },
};
```

#### Enhanced File Naming

```javascript
// Custom filename generation
function generateFilename(title, domain, metadata) {
  const date = new Date().toISOString().split('T')[0];
  const category = detectCategory(domain, title);
  const cleanTitle = title
    .toLowerCase()
    .replace(/[^a-z0-9\s-]/g, '')
    .replace(/\s+/g, '-')
    .substring(0, 40);

  return `${date}-${category}-${domain}-${cleanTitle}.md`;
}

function detectCategory(domain, title) {
  const techDomains = ['github.com', 'stackoverflow.com', 'dev.to'];
  const newsDomains = ['cnn.com', 'bbc.com', 'reuters.com'];

  if (techDomains.some(d => domain.includes(d))) return 'tech';
  if (newsDomains.some(d => domain.includes(d))) return 'news';
  return 'general';
}
```

#### Multi-Repository Support

```javascript
// Repository selection based on content type
const REPO_CONFIG = {
  tech: {
    repo: 'username/tech-docs',
    folder: 'articles',
  },
  news: {
    repo: 'username/news-clips',
    folder: 'daily',
  },
  default: {
    repo: 'username/general-docs',
    folder: 'unsorted',
  },
};
```

### Bookmarklet vs Extension Comparison

| Feature                   | Browser Extension     | Bookmarklet             |
| ------------------------- | --------------------- | ----------------------- |
| **Installation**          | Chrome Web Store      | Copy/paste code         |
| **Browser Support**       | Chrome, Edge, Firefox | All browsers            |
| **Setup Complexity**      | Simple (UI-guided)    | Moderate (code editing) |
| **Background Processing** | Yes                   | No                      |
| **Context Menu**          | Yes                   | No                      |
| **Keyboard Shortcuts**    | Yes                   | No                      |
| **Settings Persistence**  | Full                  | Limited                 |
| **Updates**               | Automatic             | Manual                  |
| **Security**              | Sandboxed             | Runs on page            |
| **Performance**           | Optimized             | Good                    |
| **Customization**         | UI options            | Code modification       |

### Bookmarklet Troubleshooting

#### Common Issues

**1. Configuration Errors**

```
❌ Configuration required - Please set your GitHub token
```

- Ensure you've replaced `YOUR_GITHUB_TOKEN_HERE` with your actual token
- Verify the token has `repo` permissions
- Check that the repository name is in `owner/repo` format

**2. GitHub API Errors**

```
❌ GitHub API error: Bad credentials
```

- Token may be expired or invalid
- Check token permissions include repository access
- Verify repository exists and is accessible

**3. Content Extraction Issues**

```
❌ No substantial content found
```

- Page may be primarily JavaScript-rendered
- Try waiting for page to fully load before clicking bookmarklet
- Some pages may have unusual content structures

**4. Network Errors**

```
❌ Network error: Failed to fetch
```

- Check internet connection
- GitHub API may be temporarily unavailable
- Corporate firewalls may block GitHub API access

#### Debug Mode

Add this debug version for troubleshooting:

```javascript
// Debug version - logs to console
javascript: (function () {
  console.log('PrismWeave Debug Mode');
  window.PRISMWEAVE_DEBUG = true;
  // ... rest of bookmarklet code with console.log statements
})();
```

#### Performance Optimization

For better performance on complex pages:

```javascript
// Optimized version for large pages
const CONFIG = {
  // ... your config
  maxContentLength: 50000, // Limit content size
  timeout: 30000, // 30 second timeout
  enableCache: true, // Cache common operations
};
```

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
      "exclude": [".follow-button", ".clap-button", ".response-count"],
      "include_images": true,
      "clean_html": true
    },
    "dev.to": {
      "selectors": {
        "article": "#article-body",
        "title": ".crayons-article__header h1",
        "author": ".crayons-article__subheader a"
      },
      "exclude": [".reaction-button", ".comment-subscription"],
      "preserve_code": true
    },
    "github.com": {
      "selectors": {
        "content": ".markdown-body, .Box-body"
      },
      "preserve_formatting": true,
      "include_links": true
    }
  }
}
```

#### Content Type Detection

The extension automatically detects content types and applies appropriate
processing:

| Content Type          | Detection Criteria               | Special Processing                 |
| --------------------- | -------------------------------- | ---------------------------------- |
| **Technical Article** | Code blocks, technical keywords  | Preserve syntax highlighting       |
| **News Article**      | News site domains, date patterns | Extract publication info           |
| **Blog Post**         | Blog platforms, author info      | Enhanced metadata extraction       |
| **Documentation**     | Doc sites, API references        | Preserve structure and links       |
| **Research Paper**    | Academic domains, citations      | Maintain formatting and references |

### Advanced Configuration

#### Performance Tuning

```json
{
  "performance": {
    "maxContentLength": 100000,
    "timeoutDuration": 30000,
    "maxConcurrentCaptures": 3,
    "enableCaching": true,
    "optimizeImages": true
  }
}
```

#### Network Configuration

```json
{
  "network": {
    "retryAttempts": 3,
    "retryDelay": 1000,
    "requestTimeout": 10000,
    "userAgent": "PrismWeave/1.0 (Browser Extension)"
  }
}
```

#### Error Handling

```json
{
  "errorHandling": {
    "logLevel": "info",
    "saveFailedCaptures": true,
    "fallbackToSimpleExtraction": true,
    "notifyOnErrors": true
  }
}
```

### Configuration Import/Export

#### Export Settings

```javascript
// Access via extension options page
const settings = await getSettings();
const configBlob = new Blob([JSON.stringify(settings, null, 2)], {
  type: 'application/json',
});
// Download as prismweave-config.json
```

#### Import Settings

```javascript
// Upload JSON file via options page
const fileInput = document.getElementById('config-file');
fileInput.addEventListener('change', async event => {
  const file = event.target.files[0];
  const config = JSON.parse(await file.text());
  await updateSettings(config);
});
```

#### Configuration Validation

The extension validates all settings before applying:

```javascript
interface ConfigValidation {
  isValid: boolean;
  errors: string[];
  warnings: string[];
}

// Validation rules
const validationRules = {
  githubToken: (token) => token.length >= 40,
  githubRepo: (repo) => /^[\w\-\.]+\/[\w\-\.]+$/.test(repo),
  fileNamingPattern: (pattern) => /^[YYYY\-MM\-DD\-\w\{\}]+$/.test(pattern)
};
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

### Common Issues and Solutions

#### 1. GitHub Authentication Problems

**Issue: GitHub Authentication Failed**

```
Error: GitHub token is invalid or expired
Status: 401 Unauthorized
```

**Solutions:**

- **Check Token Validity**: Ensure your GitHub Personal Access Token is active
  - Go to GitHub → Settings → Developer Settings → Personal Access Tokens
  - Verify the token hasn't expired
  - Check that it has `repo` scope permissions
- **Token Format**: Ensure you're using a classic token (starts with `ghp_`)
- **Repository Access**: Verify the token has access to your target repository
- **Copy/Paste Errors**: Re-copy the token to avoid invisible characters

**Test Your Token:**

```bash
curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/user
```

---

#### 2. Repository Access Issues

**Issue: Repository Not Found**

```
Error: Repository does not exist or access denied
Status: 404 Not Found
```

**Solutions:**

- **Repository Name Format**: Use exact format `username/repository-name`
- **Repository Visibility**: Ensure repository exists and is accessible
- **Private Repository Access**: Token needs full `repo` permissions for private
  repos
- **Organization Repositories**: May require additional permissions

**Verification Steps:**

1. Visit your repository on GitHub to confirm it exists
2. Check repository settings → Manage access
3. Verify your token has the correct scope

---

#### 3. Content Extraction Failures

**Issue: No Main Content Found**

```
Error: No main content found on page
Warning: Extracted content too short
```

**Solutions:**

- **Page Loading**: Ensure page is fully loaded before capturing
- **JavaScript Rendering**: Some sites require time for JavaScript to render
  content
- **Custom Selectors**: Configure site-specific extraction rules
- **Content Structure**: Page may have unusual HTML structure

**Debugging Steps:**

1. Enable debug mode in extension options
2. Check browser console for detailed logs
3. Try capturing after page fully loads
4. Test on different types of content

**Custom Selector Configuration:**

```json
{
  "customSelectors": {
    "yoursite.com": {
      "article": ".main-content, .post-body",
      "exclude": [".ads", ".sidebar", ".comments"]
    }
  }
}
```

---

#### 4. Permission and Access Errors

**Issue: Cannot Access Page Content**

```
Error: Cannot access page content
Status: Permission denied
```

**Solutions:**

- **Restricted Pages**: Extension cannot access `chrome://`, `file://`, or
  extension pages
- **ActiveTab Permission**: Ensure extension has necessary permissions
- **Page Load Timing**: Wait for page to fully load
- **HTTPS Requirements**: Some sites require secure connections

**Supported Page Types:**

- ✅ HTTP/HTTPS web pages
- ✅ Most public websites
- ❌ Chrome internal pages (`chrome://`)
- ❌ Local files (`file://`)
- ❌ Extension pages
- ❌ Chrome Web Store pages

---

#### 5. Network and Connectivity Issues

**Issue: Network Timeouts**

```
Error: Request timeout after 30 seconds
Error: Failed to fetch from GitHub API
```

**Solutions:**

- **Internet Connection**: Verify stable internet connection
- **GitHub API Status**: Check GitHub status page
- **Corporate Firewall**: May block GitHub API access
- **Rate Limiting**: GitHub API has rate limits

**Rate Limit Information:**

- Authenticated requests: 5,000 per hour
- Check remaining requests: `X-RateLimit-Remaining` header
- Reset time: `X-RateLimit-Reset` header

---

#### 6. File Size and Content Limits

**Issue: Content Too Large**

```
Error: File size exceeds GitHub limit
Warning: Content truncated
```

**Solutions:**

- **GitHub File Limit**: 100MB per file (recommended < 1MB)
- **Repository Size**: 1GB soft limit per repository
- **Large Content**: Consider splitting content or using external storage
- **Image Optimization**: Disable image capture for large pages

**Size Optimization:**

```json
{
  "processing": {
    "maxContentLength": 50000,
    "captureImages": false,
    "compressContent": true
  }
}
```

### Advanced Debugging

#### Debug Mode Configuration

**Enable Debug Mode:**

1. Right-click extension icon → Options
2. Navigate to "Advanced" tab
3. Enable "Debug Mode"
4. Enable "Verbose Logging"
5. Check browser console for detailed logs

**Debug Information Includes:**

- Content extraction steps
- GitHub API requests/responses
- Performance metrics
- Error stack traces
- Network request details

#### Console Debugging Commands

**Check Extension Status:**

```javascript
// In browser console (F12)
chrome.runtime.sendMessage({ type: 'GET_STATUS' }, console.log);
```

**Test GitHub Connection:**

```javascript
chrome.runtime.sendMessage({ type: 'TEST_CONNECTION' }, console.log);
```

**Get Current Settings:**

```javascript
chrome.runtime.sendMessage({ type: 'GET_SETTINGS' }, console.log);
```

**Extract Content from Current Page:**

```javascript
chrome.tabs.query({ active: true, currentWindow: true }, tabs => {
  chrome.tabs.sendMessage(tabs[0].id, { type: 'EXTRACT_CONTENT' }, console.log);
});
```

#### Log Analysis

**Understanding Log Levels:**

```
[DEBUG] - Detailed operation information
[INFO]  - General operation status
[WARN]  - Potential issues that don't prevent operation
[ERROR] - Failures that prevent operation
```

**Common Log Patterns:**

```
[INFO] Content extraction started for: https://example.com
[DEBUG] Found main content selector: article
[DEBUG] Cleaned content: 1250 words, 15 images
[INFO] Markdown conversion completed: 2.3s
[DEBUG] GitHub API request: PUT /repos/user/repo/contents/file.md
[INFO] File committed successfully: abc123def
```

### Performance Troubleshooting

#### Slow Capture Performance

**Symptoms:**

- Captures taking > 30 seconds
- Browser becoming unresponsive
- Memory usage warnings

**Solutions:**

1. **Reduce Image Processing**:

   ```json
   { "captureImages": false }
   ```

2. **Limit Content Size**:

   ```json
   { "maxContentLength": 25000 }
   ```

3. **Clear Cache**:

   ```javascript
   chrome.runtime.sendMessage({ type: 'CLEAR_CACHE' });
   ```

4. **Restart Extension**:
   - Disable and re-enable in `chrome://extensions/`

#### Memory Issues

**High Memory Usage:**

```
Warning: Extension using excessive memory
Error: Out of memory during processing
```

**Memory Optimization:**

1. Close unused tabs before capturing
2. Restart browser periodically
3. Reduce concurrent captures
4. Enable content compression

**Memory Monitoring:**

```javascript
// Check memory usage (in console)
if (performance.memory) {
  console.log(
    'Used:',
    Math.round(performance.memory.usedJSHeapSize / 1024 / 1024) + 'MB'
  );
  console.log(
    'Total:',
    Math.round(performance.memory.totalJSHeapSize / 1024 / 1024) + 'MB'
  );
}
```

### Site-Specific Issues

#### JavaScript-Heavy Sites

**Common Sites with Issues:**

- Single Page Applications (SPAs)
- Sites with lazy-loaded content
- Infinite scroll pages
- Dynamic content sites

**Solutions:**

1. **Wait for Content Loading**:

   - Wait 5-10 seconds after page load
   - Look for loading indicators to disappear

2. **Use Bookmarklet Alternative**:

   - Works better with JavaScript-rendered content
   - Can access final rendered state

3. **Custom Timing**:
   ```json
   {
     "extractionDelay": 5000,
     "waitForElements": [".content-loaded", ".article-body"]
   }
   ```

#### Content Management Systems

**WordPress Sites:**

```json
{
  "wordpress.com": {
    "selectors": [".post-content", ".entry-content"],
    "exclude": [".sharedaddy", ".related-posts"]
  }
}
```

**Medium Articles:**

```json
{
  "medium.com": {
    "selectors": ["article", ".postArticle-content"],
    "exclude": [".followButton", ".clapButton"]
  }
}
```

**Ghost Blogs:**

```json
{
  "ghost.org": {
    "selectors": [".post-content", ".gh-content"],
    "exclude": [".gh-subscribe", ".gh-comments"]
  }
}
```

### Error Recovery

#### Automatic Recovery Features

**Built-in Recovery:**

1. **Retry Logic**: Automatic retry for transient failures
2. **Fallback Extraction**: Alternative content extraction methods
3. **Partial Content**: Save what can be extracted
4. **Error Logging**: Detailed error information for debugging

**Manual Recovery Steps:**

1. **Reset Settings**: Restore default configuration
2. **Clear Storage**: Remove cached data
3. **Reinstall Extension**: Fresh installation
4. **Alternative Methods**: Use bookmarklet as backup

### Getting Help

#### Before Reporting Issues

**Information to Collect:**

1. **Extension Version**: Check in `chrome://extensions/`
2. **Browser Version**: Chrome/Edge version number
3. **Page URL**: URL where issue occurred (if shareable)
4. **Error Messages**: Exact error text
5. **Console Logs**: Browser console output
6. **Settings**: Current extension configuration

#### Diagnostic Data Export

**Export Debug Information:**

1. Enable debug mode
2. Reproduce the issue
3. Export logs from extension options
4. Include in issue report

**Log Export Format:**

```json
{
  "version": "1.0.0",
  "timestamp": "2025-08-04T15:30:00.000Z",
  "browser": "Chrome 126.0.6478.126",
  "settings": {...},
  "errors": [...],
  "performance": {...}
}
```

#### Support Channels

1. **GitHub Issues**: Bug reports and feature requests
2. **Documentation**: Check project wiki and guides
3. **Community**: GitHub Discussions for general questions
4. **Email**: Direct support for critical issues

#### Temporary Workarounds

**While Waiting for Fixes:**

1. **Use Bookmarklet**: Universal browser support
2. **Manual Capture**: Copy/paste content manually
3. **Alternative Tools**: Use other capture tools temporarily
4. **Simplified Settings**: Disable advanced features

### Self-Diagnosis Checklist

**Quick Troubleshooting Steps:**

- [ ] **Extension Enabled**: Check `chrome://extensions/`
- [ ] **Updated Version**: Ensure latest version installed
- [ ] **Valid GitHub Token**: Token not expired, correct permissions
- [ ] **Correct Repository**: Repository exists and accessible
- [ ] **Internet Connection**: Stable connection to GitHub
- [ ] **Page Fully Loaded**: Wait for page to complete loading
- [ ] **Supported Page Type**: Not a restricted page
- [ ] **Debug Mode**: Enable for detailed error information
- [ ] **Browser Console**: Check for error messages
- [ ] **Settings Valid**: All required settings configured

**If All Else Fails:**

1. Disable and re-enable the extension
2. Restart your browser
3. Clear browser cache and cookies
4. Try the bookmarklet alternative
5. Report the issue with detailed information

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

### Basic Usage Examples

#### Extension-Based Capture

```typescript
// Capture current page programmatically
async function captureCurrentPage() {
  const extractor = new ContentExtractor();
  const converter = new MarkdownConverter();
  const github = new GitHubClient();

  try {
    // Extract content from current page
    const content = await extractor.extractMainContent();
    const metadata = await extractor.extractMetadata();

    // Convert to clean markdown
    const markdown = converter.convert(content.html);

    // Generate frontmatter
    const frontmatter = generateFrontmatter(metadata);
    const document = `${frontmatter}\n\n${markdown}`;

    // Save to GitHub repository
    const result = await github.saveDocument(document, metadata.title);

    console.log('Successfully captured:', result.html_url);
  } catch (error) {
    console.error('Capture failed:', error.message);
  }
}
```

#### Bookmarklet Usage Patterns

**Basic Bookmarklet Capture:**

```javascript
// Simplified bookmarklet for quick captures
javascript: (function () {
  const CONFIG = {
    githubToken: 'ghp_your_token_here',
    githubRepo: 'username/my-documents',
    defaultFolder: 'articles',
  };

  // Quick status overlay
  const overlay = document.createElement('div');
  overlay.style.cssText =
    'position:fixed;top:20px;right:20px;z-index:999999;background:#333;color:white;padding:15px;border-radius:5px;';
  overlay.textContent = 'Capturing content...';
  document.body.appendChild(overlay);

  // Extract and save content
  const title = document.title;
  const content =
    document.querySelector('article, main, .content')?.innerHTML ||
    document.body.innerHTML;

  // Simple markdown conversion
  const markdown = content
    .replace(
      /<h([1-6])[^>]*>(.*?)<\/h[1-6]>/gi,
      (m, level, text) => '\n' + '#'.repeat(level) + ' ' + text + '\n'
    )
    .replace(/<p[^>]*>(.*?)<\/p>/gi, '\n$1\n')
    .replace(/<[^>]*>/g, '');

  // Save to GitHub
  const filename =
    new Date().toISOString().split('T')[0] +
    '-' +
    title.replace(/[^a-z0-9]/gi, '-').toLowerCase() +
    '.md';
  const frontmatter = `---\ntitle: '${title}'\nurl: '${location.href}'\ncaptured_at: '${new Date().toISOString()}'\n---\n\n`;

  fetch(
    `https://api.github.com/repos/${CONFIG.githubRepo}/contents/${CONFIG.defaultFolder}/${filename}`,
    {
      method: 'PUT',
      headers: {
        Authorization: `token ${CONFIG.githubToken}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: `Add captured article: ${title}`,
        content: btoa(unescape(encodeURIComponent(frontmatter + markdown))),
      }),
    }
  )
    .then(response => response.json())
    .then(data => {
      overlay.textContent = '✅ Captured successfully!';
      setTimeout(() => document.body.removeChild(overlay), 2000);
    })
    .catch(error => {
      overlay.textContent = '❌ Error: ' + error.message;
      console.error('Capture error:', error);
    });
})();
```

### Advanced Configuration Examples

#### Site-Specific Extraction Rules

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

### Customization Examples

#### Custom Markdown Converter

```typescript
// Extended markdown converter with custom rules
class CustomMarkdownConverter extends MarkdownConverter {
  protected convertCustomElements(html: string): string {
    // Convert custom callout boxes
    html = html.replace(
      /<div class="callout callout-(\w+)">(.*?)<\/div>/gis,
      (match, type, content) => {
        const emoji = this.getCalloutEmoji(type);
        return `\n> ${emoji} **${type.toUpperCase()}**\n> ${content.replace(/<[^>]*>/g, '').trim()}\n`;
      }
    );

    // Convert code snippets with language detection
    html = html.replace(
      /<pre><code class="language-(\w+)">(.*?)<\/code><\/pre>/gis,
      (match, lang, code) => {
        return `\n\`\`\`${lang}\n${this.decodeHtml(code)}\n\`\`\`\n`;
      }
    );

    return html;
  }

  private getCalloutEmoji(type: string): string {
    const emojis = {
      info: 'ℹ️',
      warning: '⚠️',
      error: '❌',
      success: '✅',
      tip: '💡',
    };
    return emojis[type] || '📝';
  }
}
```

These examples demonstrate the flexibility and power of the PrismWeave browser
extension, from basic content capture to advanced automation and integration
scenarios.

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
