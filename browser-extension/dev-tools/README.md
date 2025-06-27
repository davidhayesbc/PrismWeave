# PrismWeave Markdown Converter Development Tools

Development tools for testing PrismWeave markdown conversion using the exact
same core logic as the browser extension. This toolkit allows you to rapidly
test URL conversion and debug markdown output.

## 🚀 Quick Start

### Setup

```bash
cd dev-tools
npm install
```

### Test URL Conversion

```bash
# Test a URL and save HTML + Markdown for comparison
npm run test-url "https://example.com/article"

# The tool will save three files in ./test-outputs/:
# - [url-slug]-[timestamp].html (original HTML)
# - [url-slug]-[timestamp].md (converted markdown with frontmatter)
# - [url-slug]-[timestamp].json (metadata and stats)
```

## 📁 Core Files

- `url-test-cli.ts` - Main CLI tool for testing URL conversions
- `markdown-converter-node.ts` - Node.js wrapper for browser extension core
- `package.json` - Dependencies and scripts
- `tsconfig.json` - TypeScript configuration
- `test-outputs/` - Generated test results

### Compare Results

```bash
# Compare two conversion results
npm run compare result1.json result2.json

# Batch analyze all results
npm run compare --batch
```

## 📁 Project Structure

```
dev-tools/
├── package.json              # Dependencies and scripts
├── tsconfig.json            # TypeScript configuration
├── dev-cli.js              # Simple CLI for local file testing
├── test-url-conversion.ts   # Advanced URL testing tool
├── src/
│   ├── universal-markdown-converter.ts  # Refactored converter (Node.js + Browser compatible)
│   └── comparison-utility.ts            # Result analysis and comparison
└── test-outputs/            # Generated test results
    ├── *.html              # Original HTML
    ├── *.md               # Converted Markdown
    └── *.json            # Test metadata and stats
```

## 🛠️ Available Commands

### Core Testing

- `npm run test-url <url>` - Test URL conversion with full analysis
- `npm run dev test <file>` - Test local HTML file conversion
- `npm run compare <file1> <file2>` - Compare two conversion results

### Development Utilities

- `npm run build` - Compile TypeScript
- `npm run dev` - Interactive development mode

### Advanced URL Testing Options

```bash
# Basic URL test
npm run test-url "https://example.com"

# Save only markdown output
npm run test-url "https://example.com" --format=markdown

# Custom output directory
npm run test-url "https://example.com" --output=./my-tests

# Verbose mode with detailed logging
npm run test-url "https://example.com" --verbose

# Without frontmatter generation
npm run test-url "https://example.com" --no-frontmatter
```

## 🔧 Features

### Universal Markdown Converter

- **Environment Detection**: Automatically adapts to Node.js or Browser
  environment
- **Same Logic**: Uses identical conversion rules as the browser extension
- **Enhanced Rules**: All Turndown customizations from the original converter
- **Quality Metrics**: Built-in analysis of conversion quality

### URL Testing Tool

- **Automatic Fetching**: Downloads and processes any web page
- **Metadata Extraction**: Pulls title, author, description, dates
- **Image Detection**: Identifies and catalogs all images
- **Performance Metrics**: Tracks conversion time and statistics

### Comparison Utility

- **Side-by-Side Analysis**: Compare multiple conversion attempts
- **Quality Scoring**: Automated assessment of conversion quality
- **Diff Visualization**: Highlights differences between results
- **Batch Processing**: Analyze multiple files at once

### Quality Metrics

- **Markdown Validity**: Syntax correctness checking
- **Code Block Integrity**: Formatting and language detection quality
- **Link Integrity**: URL validation and structure
- **Heading Structure**: Hierarchy and organization assessment
- **Content Preservation**: Estimates how much original content was retained
- **Readability Score**: Line length and formatting assessment

## 🎯 Development Workflow

### 1. Test Individual URLs

```bash
# Test conversion on real-world content
npm run test-url "https://docs.microsoft.com/en-us/typescript/"
npm run test-url "https://github.com/microsoft/vscode/blob/main/README.md"
npm run test-url "https://stackoverflow.com/questions/12345/some-question"
```

### 2. Analyze Results

```bash
# Check quality metrics
npm run compare --batch

# Compare specific results
npm run compare docs-microsoft-2024.json github-vscode-2024.json
```

### 3. Iterate on Conversion Logic

1. Edit `src/universal-markdown-converter.ts`
2. Run `npm run build`
3. Test with `npm run test-url <url>`
4. Compare results with previous versions

### 4. Apply Changes to Browser Extension

Once satisfied with results:

1. Copy improvements to `../src/utils/markdown-converter.ts`
2. Test in browser extension environment
3. Run browser extension tests

## 🔬 Testing Strategies

### Content Types to Test

- **Technical Documentation**: GitHub README files, API docs
- **Blog Posts**: Medium articles, personal blogs
- **News Articles**: News websites, journalism
- **Code Examples**: Stack Overflow, coding tutorials
- **Academic Papers**: Research publications, arxiv papers

### Quality Benchmarks

- **Markdown Validity**: Should be 100%
- **Code Block Integrity**: Target 90%+
- **Link Integrity**: Target 95%+
- **Content Preservation**: Target 80%+
- **Readability Score**: Target 85%+

### Example Test Workflow

```bash
# Test a variety of content types
npm run test-url "https://github.com/microsoft/TypeScript/blob/main/README.md"
npm run test-url "https://medium.com/@author/article-title"
npm run test-url "https://docs.python.org/3/tutorial/"
npm run test-url "https://stackoverflow.com/questions/tagged/javascript"

# Analyze batch results
npm run compare --batch

# Compare specific improvements
npm run test-url "https://github.com/microsoft/TypeScript/blob/main/README.md" --output=./version2
npm run compare ./test-outputs/github-typescript-v1.json ./version2/github-typescript-v2.json
```

## 🐛 Troubleshooting

### Common Issues

#### "TurndownService not found"

```bash
# Make sure dependencies are installed
npm install
```

#### "Cannot find module errors"

```bash
# Rebuild TypeScript
npm run build
```

#### "JSDOM errors"

```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Debug Mode

Enable verbose logging:

```bash
npm run test-url "https://example.com" --verbose
```

## 🔄 Integration with Browser Extension

The `UniversalMarkdownConverter` class is designed to use identical logic to the
browser extension's `MarkdownConverter`. Key shared features:

- **Same Turndown Rules**: Identical custom rules for code blocks, callouts,
  etc.
- **Same Preprocessing**: HTML cleaning and normalization
- **Same Postprocessing**: Markdown cleanup and formatting
- **Same Quality Checks**: Validation and metrics

### Applying Changes

1. Test changes in this environment first
2. Copy successful modifications to `../src/utils/markdown-converter.ts`
3. Ensure browser extension compatibility (no Node.js specific code)
4. Run browser extension tests

## 📊 Output Files

### Markdown Files (.md)

- Complete converted markdown with frontmatter
- Ready for Git repository storage
- Compatible with standard markdown processors

### HTML Files (.html)

- Original source HTML for reference
- Useful for debugging conversion issues

### Metadata Files (.json)

- Conversion statistics and timing
- Extracted metadata (title, author, etc.)
- Quality metrics and analysis
- Image asset information

## 🎨 Example Output

After running a test, you'll see:

```
🚀 PrismWeave URL Tester

🌐 Fetching URL: https://example.com
✓ Fetched 45,234 characters
🔄 Converting to markdown...
✓ Conversion completed in 156ms

💾 Results saved:
   HTML: test-outputs/example-com-2024-06-23T10-30-45.html
   Markdown: test-outputs/example-com-2024-06-23T10-30-45.md
   Metadata: test-outputs/example-com-2024-06-23T10-30-45.json

📊 Conversion Statistics:
   Words: 1,234
   Characters: 8,456
   Headings: 6
   Links: 23
   Images: 4
   Code blocks: 2
   Conversion time: 156ms

⭐ Quality Metrics:
   Markdown Validity: ✓
   Code Block Integrity: 95%
   Link Integrity: 98%
   Heading Structure: 90%
   Content Preservation: 87%
   Readability Score: 92%

✅ Test completed successfully!
```

## 🤝 Contributing

When making improvements:

1. Test with diverse content types
2. Maintain compatibility with browser extension
3. Document any new configuration options
4. Update quality metrics if needed
5. Add test cases for edge cases

---

**Happy Testing!** 🎉

This development environment should significantly speed up your iteration cycle
for improving the markdown conversion quality.
