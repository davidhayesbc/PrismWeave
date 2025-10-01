# PrismWeave CLI

Command-line tool for capturing web pages as markdown and syncing to Git repositories.

## Features

- 🌐 **Headless Browser Capture**: Uses Puppeteer to fetch and render web pages
- 📝 **Markdown Conversion**: Converts HTML content to clean markdown
- 🔄 **GitHub Integration**: Automatically commits captured content to GitHub
- 📦 **Batch Processing**: Process multiple URLs from a file
- 🎨 **Smart Organization**: Automatically categorizes content into folders
- 🔧 **Configurable**: Store settings for easy reuse

## Installation

### Prerequisites

- Node.js 18 or higher
- npm or yarn

### Install Dependencies

```bash
cd cli
npm install
```

### Build

```bash
npm run build
```

### Install Globally (Optional)

```bash
npm link
```

This makes the `prismweave` command available system-wide.

## Configuration

Before using the CLI, configure your GitHub credentials:

```bash
# Set GitHub personal access token
prismweave config --set githubToken=ghp_your_token_here

# Set GitHub repository (format: owner/repo)
prismweave config --set githubRepo=yourusername/your-repo

# Optional: Set default options
prismweave config --set defaultFolder=tech
prismweave config --set includeImages=true
prismweave config --set timeout=30000
```

### View Configuration

```bash
# List all configuration
prismweave config --list

# Get specific value
prismweave config --get githubToken
```

### Test Connection

Verify your GitHub credentials and repository access:

```bash
prismweave config --test
```

## Usage

### Capture a Single URL

```bash
prismweave capture https://example.com/article
```

### Capture Multiple URLs from a File

Create a file with URLs (one per line):

```text
# urls.txt
https://example.com/article1
https://example.com/article2
https://example.com/article3
```

Then capture all URLs:

```bash
prismweave capture --file urls.txt
```

### Advanced Options

```bash
# Capture with custom options
prismweave capture https://example.com \
  --token ghp_custom_token \
  --repo custom-owner/custom-repo \
  --timeout 60000 \
  --no-images \
  --no-links

# Dry run (preview without saving)
prismweave capture https://example.com --dry-run
```

## Command Reference

### `prismweave capture`

Capture one or more URLs and save to GitHub.

**Arguments:**
- `[url]` - URL to capture (optional if using --file)

**Options:**
- `-f, --file <path>` - File containing URLs (one per line)
- `-t, --token <token>` - GitHub personal access token
- `-r, --repo <repo>` - GitHub repository (owner/repo format)
- `--no-images` - Exclude images from capture
- `--no-links` - Convert links to plain text
- `--timeout <ms>` - Page load timeout in milliseconds (default: 30000)
- `--dry-run` - Preview without saving to GitHub

### `prismweave config`

Manage CLI configuration.

**Options:**
- `--set <key=value>` - Set a configuration value
- `--get <key>` - Get a configuration value
- `--list` - List all configuration
- `--test` - Test GitHub connection

## File Organization

The CLI automatically organizes captured content into folders based on content analysis:

- `tech/` - Programming, software development, technology articles
- `business/` - Business, marketing, finance content
- `tutorial/` - Tutorials, guides, how-to articles
- `news/` - News articles, blog posts
- `research/` - Research papers, academic content
- `design/` - Design, UI/UX content
- `tools/` - Software tools, utilities
- `reference/` - Documentation, reference materials
- `unsorted/` - Content that doesn't match other categories

## File Naming

Files are automatically named using the pattern:

```
YYYY-MM-DD-domain-title.md
```

For example:
```
2025-01-15-example-com-how-to-use-prismweave.md
```

## Markdown Format

Captured pages are converted to markdown with YAML frontmatter:

```markdown
---
title: "Article Title"
url: "https://example.com/article"
capture_date: "2025-01-15T10:30:00.000Z"
description: "Article description"
author: "Author Name"
tags:
  - "tag1"
  - "tag2"
word_count: 1234
reading_time: 7 min
source: "PrismWeave CLI"
---

# Article Title

Article content in markdown format...
```

## Sharing Code with Browser Extension

The CLI shares core functionality with the browser extension:

- **Markdown Conversion**: Uses `MarkdownConverterCore` for consistent conversion
- **File Management**: Uses `FileManager` for GitHub operations and file organization
- **Type Definitions**: Shares interfaces and types

Shared modules are located in:
- `cli/src/shared/markdown-converter-core.ts`
- `cli/src/shared/file-manager.ts`

## Examples

### Example 1: Capture Tech Articles

```bash
# Create a file with tech article URLs
cat > tech-articles.txt << EOF
https://dev.to/example-post
https://stackoverflow.com/questions/12345
https://github.blog/example-article
EOF

# Capture all articles
prismweave capture --file tech-articles.txt
```

### Example 2: Quick Single Capture

```bash
prismweave capture https://www.example.com/interesting-article
```

### Example 3: Dry Run Preview

```bash
# Preview what will be captured without saving
prismweave capture https://example.com --dry-run
```

### Example 4: Custom GitHub Repository

```bash
# Capture to a different repository
prismweave capture https://example.com \
  --token ghp_different_token \
  --repo different-user/different-repo
```

## Troubleshooting

### Browser Issues

If Puppeteer fails to launch:

```bash
# Install Chromium manually
npx puppeteer browsers install chrome
```

### GitHub Authentication

If GitHub authentication fails:

1. Verify your token has the correct permissions:
   - `repo` scope for private repositories
   - `public_repo` scope for public repositories

2. Test the connection:
   ```bash
   prismweave config --test
   ```

### Timeout Issues

For slow-loading pages, increase the timeout:

```bash
prismweave capture https://slow-site.com --timeout 60000
```

## Configuration File Location

The CLI stores configuration at:
- **Windows**: `C:\Users\<username>\.prismweave\config.json`
- **macOS/Linux**: `~/.prismweave/config.json`

## Development

### Build from Source

```bash
cd cli
npm install
npm run build
```

### Watch Mode

```bash
npm run dev
```

### Run Without Installing

```bash
npm start -- capture https://example.com
```

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please see the main PrismWeave repository for contribution guidelines.

## Related Projects

- **PrismWeave Browser Extension**: Chrome/Edge extension for capturing web pages
- **PrismWeave VS Code Extension**: VS Code integration for document management
- **PrismWeave AI Processing**: Local AI integration for content processing

## Support

For issues, questions, or suggestions, please visit:
https://github.com/yourusername/PrismWeave/issues
