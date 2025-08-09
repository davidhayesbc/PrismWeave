# PrismWeave Usage Guide

## 🎯 Getting Started

Once PrismWeave is installed and configured, you're ready to start capturing web content. This guide covers all the ways you can use PrismWeave to build your knowledge repository.

## 📝 Basic Content Capture

### Method 1: Browser Extension
1. **Navigate** to any webpage you want to capture
2. **Click** the PrismWeave icon in your browser toolbar
3. **Review** the captured content in the preview
4. **Edit** metadata, tags, or content if needed
5. **Save** to commit to your GitHub repository

### Method 2: Bookmarklet
1. **Drag** the PrismWeave bookmarklet to your bookmarks bar
2. **Click** the bookmarklet on any webpage
3. **Use** the popup interface to capture and configure
4. **Save** directly to your repository

### Method 3: Context Menu
1. **Right-click** on any webpage
2. **Select** "Capture with PrismWeave" from context menu
3. **Choose** capture options (full page, selection, article only)
4. **Save** with automatic processing

## ⚙️ Capture Options

### Content Types
- **Full Page**: Captures entire webpage with all content
- **Article**: Extracts main article content using smart algorithms
- **Selection**: Captures only selected text/elements
- **Custom**: Use CSS selectors to target specific content

### Format Options
- **Markdown**: Clean, readable format for notes and documentation
- **HTML**: Preserves original formatting and styling
- **Text Only**: Plain text extraction for quotes and references
- **Mixed**: Markdown with embedded HTML where needed

### Metadata Enhancement
- **Auto-Generated**: Title, URL, date, word count, reading time
- **Custom Tags**: Add your own categorization tags
- **Author Info**: Extract author information when available
- **Publisher Data**: Capture source publication details

## 📁 Organization System

### Folder Structure
Configure how files are organized in your repository:

```
documents/
├── business/          # Business articles and resources
├── tech/             # Technical documentation
├── research/         # Research papers and studies
├── news/             # News articles and updates
├── reference/        # Reference materials
└── unsorted/         # Uncategorized items
```

### File Naming
Customize filename templates:
- `{date}-{domain}-{slug}.md` (default)
- `{category}/{date}-{title}.md`
- `{author}/{date}-{title}.md`
- Custom patterns with variables

### Automatic Categorization
- **Domain-based**: Automatically categorize by website
- **Content-based**: Use AI to suggest categories
- **Keyword-based**: Categorize by detected keywords
- **Manual**: Always prompt for category selection

## 🔍 Advanced Features

### Content Processing
- **Link Extraction**: Capture and organize all links
- **Image Handling**: Download and organize images
- **Code Block Detection**: Preserve syntax highlighting
- **Table Processing**: Convert HTML tables to markdown

### Bulk Operations
- **Multiple Tabs**: Capture all open tabs at once
- **Link Lists**: Process entire lists of URLs
- **RSS Feeds**: Monitor and auto-capture from feeds
- **Scheduled Capture**: Set up recurring captures

### Integration Features
- **VS Code Extension**: Browse and edit captured content
- **Git Integration**: Automatic commits with meaningful messages
- **Search**: Full-text search across all captured content
- **Export**: Generate websites, PDFs, or other formats

## 🎨 Customization

### Content Filtering
Set up rules to:
- Skip advertising and navigation content
- Focus on specific content types
- Filter by word count or reading time
- Exclude certain domains or sections

### Processing Rules
- **Markdown Rules**: Customize conversion options
- **Image Rules**: Set image download preferences
- **Link Rules**: Configure link handling (preserve, convert, remove)
- **Cleanup Rules**: Remove unwanted elements or formatting

### Templates
Create templates for different content types:
- **Article Template**: For blog posts and articles
- **Reference Template**: For documentation and references
- **Research Template**: For academic papers
- **Meeting Template**: For meeting notes and summaries

## 💡 Workflow Examples

### Research Workflow
1. **Discover** content via search or browsing
2. **Quick Capture** with bookmarklet for speed
3. **Batch Review** captured items later
4. **Tag and Organize** into research categories
5. **Cross-Reference** related documents

### Content Curation Workflow
1. **Monitor** RSS feeds and news sources
2. **Auto-Capture** interesting articles
3. **Daily Review** and categorization
4. **Weekly Synthesis** into summary documents
5. **Monthly Archive** of key insights

### Documentation Workflow
1. **Capture** technical documentation
2. **Add Notes** and personal insights
3. **Link Related** documents and resources
4. **Create Summaries** for quick reference
5. **Export Guides** for team sharing

## 🚀 Pro Tips

### Efficiency Shortcuts
- **Keyboard Shortcuts**: Set up custom hotkeys
- **Quick Tags**: Use frequent tags for faster categorization
- **Template Shortcuts**: Save common configurations
- **Batch Processing**: Group similar captures together

### Quality Control
- **Preview Mode**: Always review before saving
- **Edit Metadata**: Add context and improve discoverability
- **Link Validation**: Ensure links work and point to correct content
- **Regular Cleanup**: Archive or delete outdated content

### Collaboration
- **Shared Repositories**: Work with team members
- **Branch Strategy**: Use branches for different projects
- **Review Process**: Set up PR workflows for quality control
- **Documentation**: Keep README files updated

## 🔧 Troubleshooting Common Issues

### Content Not Capturing Properly
- **Try Different Methods**: Extension vs bookmarklet
- **Check Page Load**: Wait for dynamic content
- **Use Manual Selection**: For tricky layouts
- **Adjust Settings**: Modify content detection rules

### Large Files
- **Image Settings**: Disable image capture for text-only
- **Content Limits**: Set maximum word count limits
- **Chunking**: Break large content into sections
- **External Storage**: Use separate image repositories

### GitHub Issues
- **Rate Limits**: Space out captures to avoid limits
- **File Size**: GitHub has 100MB file size limits
- **Repository Size**: Monitor repository size growth
- **Token Permissions**: Ensure token has correct scopes

## 📊 Analytics & Insights

### Content Analytics
- **Capture Statistics**: Track capture frequency and sources
- **Content Types**: Analyze what types of content you capture most
- **Growth Metrics**: Monitor repository growth over time
- **Usage Patterns**: Identify peak capture times and sources

### Quality Metrics
- **Metadata Completeness**: Track how well content is tagged
- **Link Health**: Monitor for broken or outdated links
- **Content Freshness**: Identify outdated content for cleanup
- **Search Performance**: Analyze what content gets accessed most

## 🎯 Best Practices

### Content Strategy
1. **Define Purpose**: Know what you're collecting and why
2. **Set Boundaries**: Don't capture everything you see
3. **Regular Review**: Periodically clean up and organize
4. **Add Value**: Always add your own notes and context
5. **Share Insights**: Use captured content to create new value

### Technical Best Practices
1. **Regular Backups**: Keep local backups of your repository
2. **Monitor Limits**: Watch GitHub storage and API limits
3. **Update Regularly**: Keep extension updated for best performance
4. **Test Workflows**: Regularly verify your capture workflows
5. **Document Setup**: Keep notes on your configuration choices

---

**Ready to capture?** Start with simple webpage captures and gradually explore advanced features as you build your workflow!
