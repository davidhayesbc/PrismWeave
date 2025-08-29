# PrismWeave Local Bookmarklet Development

Local development environment for creating and testing PrismWeave bookmarklets
without deployment.

## Quick Start

1. **Start the development server:**

   ```powershell
   # From the PrismWeave directory or browser-extension directory
   .\dev-tools\start-local-dev.ps1
   ```

2. **Open your browser** to the generator (should open automatically at
   http://localhost:8080)

3. **Generate and test** your bookmarklets locally!

## What's Included

### 🌟 Local Bookmarklet Generator (`local-bookmarklet-generator.html`)

A complete, standalone HTML application with three tabs:

#### Generator Tab

- **Real-time validation** of GitHub tokens and repositories
- **Compact bookmarklets** (~1000 characters) with embedded settings
- **Local storage** of preferences (excluding sensitive tokens)
- **Multiple output options**: copy to clipboard, download HTML page, test
  directly

#### Test Page Tab

- **Sample article content** with various HTML elements (headers, paragraphs,
  lists, code blocks)
- **Structured test data** to verify bookmarklet extraction quality
- **Built-in testing** without needing external websites

#### Debug Tools Tab

- **Page analysis**: Shows what content would be extracted from current page
- **Markdown preview**: See the exact markdown output before saving
- **GitHub API testing**: Validate your token and repository access
- **Error debugging**: Detailed output for troubleshooting issues

### 🚀 Development Server (`start-local-dev.ps1`)

PowerShell script that:

- **Starts local HTTP server** using Python (handles port conflicts
  automatically)
- **Opens browser** to generator automatically
- **Provides helpful information** and troubleshooting guidance
- **Creates index page** for easy navigation

## Development Workflow

### 1. Configure GitHub Settings

- Enter your GitHub Personal Access Token
- Specify your target repository (format: `owner/repo`)
- Choose folder structure and naming preferences
- Settings persist between sessions (except token for security)

### 2. Generate Bookmarklet

- Click "Generate Bookmarklet" to create your personalized tool
- Review the generated code in the expandable code display
- Drag the bookmarklet link to your browser's bookmarks bar

### 3. Test Functionality

- **Quick test**: Click "Test on This Page" button
- **Comprehensive test**: Switch to Test Page tab and test against sample
  content
- **Debug**: Use Debug Tools tab to analyze extraction behavior

### 4. Deploy to Real Use

- Use your verified bookmarklet on any website
- Content automatically saves to your GitHub repository
- Monitor GitHub repository for successful captures

## GitHub Token Setup

1. Go to
   [GitHub Settings > Personal Access Tokens](https://github.com/settings/tokens)
2. Create a new **Fine-grained personal access token** or **Classic token**
3. Required permissions:
   - **Contents**: Read and Write (to create/update files)
   - **Metadata**: Read (to access repository information)
4. Copy the token and paste it into the generator

## Features

### 🔒 Security Features

- **No token storage**: GitHub tokens never saved locally for security
- **Private bookmarklets**: Generated bookmarklets contain your token, keep them
  private
- **Local processing**: All generation happens in your browser, no external
  services

### 📊 Testing & Debugging

- **Built-in test content**: No need to find external test pages
- **Page analysis**: See exactly what content will be extracted
- **Markdown preview**: Verify output format before saving
- **API validation**: Test GitHub connectivity and permissions

### ⚙️ Customization Options

- **Folder structure**: Choose where files are saved in your repository
- **File naming**: Multiple patterns (title+date, date+title, domain+title+date)
- **Commit messages**: Customizable templates with {title} placeholder
- **Content extraction**: Automatic selection of best content area

## Requirements

- **Python** (any recent version) for local HTTP server
- **Modern web browser** with JavaScript enabled
- **GitHub Personal Access Token** with Contents write permissions
- **Target GitHub repository** where content will be saved

## Troubleshooting

### 🔌 Port Issues

If port 8080 is busy, the script automatically tries 8081, 8082, etc.

### 🐍 Python Not Found

Ensure Python is installed and in your PATH:

```powershell
python --version
# or
python3 --version
# or
py --version
```

### 📚 Bookmarklet Not Working

1. Check Debug Tools tab for detailed error messages
2. Verify GitHub token has correct permissions
3. Ensure repository exists and is accessible
4. Test with built-in test page first before external sites

### 🔗 GitHub API Errors

- **401 Unauthorized**: Token invalid or expired
- **403 Forbidden**: Token lacks "Contents" write permissions
- **404 Not Found**: Repository doesn't exist or token lacks access
- **422 Unprocessable Entity**: File already exists with different content

## Advanced Usage

### Custom Content Selectors

The bookmarklet tries these selectors in order:

1. `article` - Semantic article content
2. `main` - Main content area
3. `.content` - Common content class
4. `body` - Fallback to entire page

### Generated Markdown Format

```yaml
---
title: 'Page Title'
url: 'https://example.com/page'
captured: '2025-08-23T10:30:45.123Z'
---
# Page Title

Content extracted and converted to markdown...
```

### File Naming Examples

- **Title + Date**: `my-article-title-2025-08-23.md`
- **Date + Title**: `2025-08-23-my-article-title.md`
- **Domain + Title + Date**: `example-com-my-article-title-2025-08-23.md`

## Development Tips

### Modifying the Generator

1. Edit `local-bookmarklet-generator.html` directly
2. Refresh browser to see changes
3. No build process required - it's a standalone file

### Testing Different Scenarios

- Use Debug Tools to analyze different page structures
- Test with the sample content first
- Verify GitHub API connectivity before testing extraction
- Check browser console for detailed error information

### Performance Considerations

- Bookmarklets are limited to ~2000 characters (ours are ~1000)
- GitHub API has rate limits (typically 5000 requests/hour)
- Large files may hit GitHub's file size limits

## Integration with Main Project

This local development environment generates the same compact bookmarklets as
the main TypeScript generator in `src/bookmarklet/generator.ts`. The logic is
kept in sync to ensure consistency between development and production
environments.

Changes made here can be easily ported back to the main TypeScript codebase for
inclusion in the browser extension build.
