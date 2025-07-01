# PrismWeave Dev Tools

Simple CLI tool to capture web pages as HTML and Markdown using the exact same
code from the PrismWeave browser extension.

## Setup

```bash
cd dev-tools
npm install
```

## Usage

```bash
# Capture any URL and save as HTML + Markdown + JSON metadata
npm run capture "https://example.com/article"

# The tool will save three files in ./test-outputs/:
# - [url-slug]-[timestamp].html (original HTML)
# - [url-slug]-[timestamp].md (converted markdown with frontmatter)
# - [url-slug]-[timestamp].json (metadata and stats)
```

## Features

- **Uses Browser Extension Code**: No duplication - directly imports and uses
  the existing `ContentExtractor` and `MarkdownConverter` from `../src/utils/`
- **Complete Capture**: Saves HTML, Markdown, and JSON metadata for each URL
- **Frontmatter Generation**: Creates YAML frontmatter with title, author, tags,
  etc.
- **Image & Link Extraction**: Catalogs all images and links found on the page
- **Statistics**: Word count, reading time, and conversion metrics

## Example Output

```
🔄 Fetching: https://example.com/article
✅ Fetched 45,234 characters
🔄 Extracting content...
🔄 Converting to markdown...
✅ Extraction complete
📝 Word count: 1,234
⏱️  Reading time: 5 min
💾 Saved HTML: ./test-outputs/example-com-article-2024-07-01T10-30-45.html
💾 Saved Markdown: ./test-outputs/example-com-article-2024-07-01T10-30-45.md
💾 Saved metadata: ./test-outputs/example-com-article-2024-07-01T10-30-45.json

🎉 Capture completed successfully!
📁 Files saved in: ./test-outputs
```

## Files Generated

### Markdown (.md)

Complete markdown with YAML frontmatter:

```yaml
---
title: 'Article Title'
url: 'https://example.com/article'
captured: '2024-07-01T10:30:45.123Z'
author: 'Author Name'
word_count: 1234
reading_time: 5
tags: ['tech', 'tutorial']
---
# Article Title

Article content converted to clean markdown...
```

### HTML (.html)

Original HTML source for reference and debugging.

### Metadata (.json)

Complete metadata including:

```json
{
  "url": "https://example.com/article",
  "timestamp": "2024-07-01T10:30:45.123Z",
  "title": "Article Title",
  "author": "Author Name",
  "wordCount": 1234,
  "readingTime": 5,
  "tags": ["tech", "tutorial"],
  "extractedImages": [...],
  "extractedLinks": [...]
}
```

## Testing Different Content Types

```bash
# Technical documentation
npm run capture "https://docs.microsoft.com/en-us/typescript/"

# Blog posts
npm run capture "https://medium.com/@author/article-title"

# GitHub repositories
npm run capture "https://github.com/microsoft/vscode/blob/main/README.md"

# News articles
npm run capture "https://example-news.com/breaking-news"
```

## How It Works

1. **Fetches** the URL using `node-fetch`
2. **Sets up** JSDOM environment to simulate a browser
3. **Uses** the exact same `ContentExtractor` and `MarkdownConverter` classes
   from the browser extension
4. **Extracts** content, images, links, and metadata
5. **Converts** to clean markdown with proper formatting
6. **Saves** all three formats (HTML, Markdown, JSON) for comparison and
   analysis

## No Code Duplication

This tool directly imports and uses:

- `ContentExtractor` from `../src/utils/content-extractor.js`
- `MarkdownConverter` from `../src/utils/markdown-converter.js`

Any improvements made to the browser extension code automatically work in this
dev tool.
