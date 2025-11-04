# Phase 3 Enhanced Features - Usage Guide

**Status**: Complete and Tested  
**Date**: November 3, 2025  
**Features**: Semantic Search, Statistics, Export, Progress Reporting

---

## Overview

Phase 3 introduces powerful new features to enhance your document management workflow:

1. **Semantic Search**: Find documents based on meaning, not just keywords
2. **Collection Statistics**: Analyze your document collection with detailed metrics
3. **Document Export**: Export your data to JSON or CSV for backup or analysis
4. **Progress Reporting**: Beautiful progress bars with Rich library integration

---

## 🔍 Semantic Search

### Basic Search

Search your entire document collection using natural language queries:

```bash
# Search for machine learning concepts
uv run python cli.py search "machine learning algorithms"

# Get more results
uv run python cli.py search "Python programming" --max 20
```

**Example Output:**

```
╭─ Result 1: neural_networks.md ─────────────────────────────────╮
│ 📁 File: neural_networks.md                                    │
│ 🔢 Chunk: 1/5                                                  │
│ 🏷️  Tags: ai, deep-learning, neural-networks                  │
│                                                                 │
│ 📝 Content:                                                    │
│ Neural networks are a fundamental concept in machine learning  │
│ that mimics the human brain's structure. They consist of       │
│ interconnected nodes (neurons) organized in layers...          │
╰─────────────────────────────────────────────────────────────────╯
```

### Advanced Search Options

#### Filter by File Type

Only search within specific file types:

```bash
# Search only markdown files
uv run python cli.py search "API documentation" --filter-type md

# Search only text files
uv run python cli.py search "meeting notes" --filter-type txt

# Search PDFs
uv run python cli.py search "research paper" --filter-type pdf
```

#### Verbose Output

Get full content instead of previews:

```bash
uv run python cli.py search "database design" --verbose
```

**Verbose Output Features:**

- Full content display (up to 500 characters)
- All metadata fields
- Chunk information
- Complete tag lists

#### Similarity Threshold

Control result relevance (0.0 to 1.0, higher = more similar):

```bash
# Only very relevant results
uv run python cli.py search "GraphQL APIs" --threshold 0.8

# More lenient matching
uv run python cli.py search "web development" --threshold 0.5
```

### Real-World Search Examples

#### Finding Technical Documentation

```bash
# Find all mentions of a specific API
uv run python cli.py search "authentication middleware" --filter-type md --max 15

# Search for error handling patterns
uv run python cli.py search "exception handling best practices" --verbose
```

#### Research and Learning

```bash
# Find learning resources
uv run python cli.py search "beginner tutorial" --max 10

# Find related concepts
uv run python cli.py search "microservices architecture patterns"
```

#### Project Documentation

```bash
# Find setup instructions
uv run python cli.py search "installation steps" --filter-type md

# Locate API endpoints
uv run python cli.py search "REST endpoints" --verbose
```

---

## 📊 Collection Statistics

### Basic Statistics

Get a quick overview of your collection:

```bash
uv run python cli.py stats
```

**Example Output:**

```
╭─────────── Collection Overview ───────────╮
│ Metric              │ Value              │
├─────────────────────┼────────────────────┤
│ 📄 Total Chunks     │ 1,247              │
│ 📁 Source Files     │ 156                │
│ 📈 Avg Chunks/File  │ 8.0                │
╰─────────────────────┴────────────────────╯

Collection: documents
Storage: /path/to/.prismweave/chroma_db
```

### Detailed Analytics

Get comprehensive insights into your collection:

```bash
uv run python cli.py stats --detailed
```

**Detailed Output Includes:**

1. **File Type Distribution**

   ```
   ╭────── File Type Distribution ──────╮
   │ Extension │ Count │ Percentage    │
   ├───────────┼───────┼───────────────┤
   │ .md       │ 523   │ 41.9%         │
   │ .txt      │ 412   │ 33.0%         │
   │ .pdf      │ 198   │ 15.9%         │
   │ .html     │ 114   │ 9.1%          │
   ╰───────────┴───────┴───────────────╯
   ```

2. **Content Statistics**
   - Total content size
   - Average chunk size
   - Content distribution

3. **Top Tags**
   ```
   ╭────────── Top 10 Tags ──────────╮
   │ Tag               │ Frequency   │
   ├───────────────────┼─────────────┤
   │ programming       │ 89          │
   │ documentation     │ 67          │
   │ tutorial          │ 45          │
   │ api               │ 38          │
   ╰───────────────────┴─────────────╯
   ```

### Use Cases for Statistics

#### Before Processing New Documents

```bash
# Check current state
uv run python cli.py stats

# Process new documents
uv run python cli.py process ../new_docs --incremental

# Verify changes
uv run python cli.py stats --detailed
```

#### Monitoring Collection Growth

```bash
# Weekly check
uv run python cli.py stats --detailed > stats_$(date +%Y%m%d).txt

# Compare statistics over time
```

#### Understanding Your Documentation

```bash
# What types of documents do you have?
uv run python cli.py stats --detailed

# What topics are most common?
# (Look at the tag frequency analysis)
```

---

## 💾 Document Export

### JSON Export (Default)

Export all documents with metadata:

```bash
# Basic JSON export
uv run python cli.py export documents.json

# With full content (instead of previews)
uv run python cli.py export full_backup.json --include-content
```

**JSON Structure:**

```json
{
  "export_date": "2025-11-03T16:45:30.123456",
  "total_documents": 150,
  "collection_name": "documents",
  "documents": [
    {
      "id": "doc1_chunk0_a1b2c3d4",
      "source_file": "/docs/example.md",
      "chunk_index": 0,
      "total_chunks": 5,
      "tags": "python, programming, tutorial",
      "content_length": 1024,
      "content_preview": "This is a tutorial about..."
    }
  ]
}
```

### CSV Export

Export to spreadsheet-friendly format:

```bash
# Export to CSV
uv run python cli.py export documents.csv --format csv
```

**CSV Columns:**

- id
- source_file
- chunk_index
- total_chunks
- tags
- content_length
- content_preview

### Filtered Exports

#### By File Type

```bash
# Export only markdown files
uv run python cli.py export markdown_docs.json --filter-type md

# Export only PDFs
uv run python cli.py export pdf_docs.csv --format csv --filter-type pdf
```

#### Limited Exports

```bash
# Export first 100 documents
uv run python cli.py export sample.json --max 100

# Export 50 markdown files with full content
uv run python cli.py export sample_full.json --filter-type md --max 50 --include-content
```

### Export Use Cases

#### Backup Your Collection

```bash
# Full backup with content
uv run python cli.py export backup_$(date +%Y%m%d).json --include-content

# Quick metadata backup
uv run python cli.py export metadata_backup.json
```

#### Data Analysis

```bash
# Export to CSV for Excel/Google Sheets analysis
uv run python cli.py export analysis.csv --format csv --max 1000

# Export specific file types for specialized analysis
uv run python cli.py export technical_docs.csv --format csv --filter-type md
```

#### Migration or Sharing

```bash
# Export subset for sharing
uv run python cli.py export share_docs.json --filter-type md --max 50

# Export with full content for migration
uv run python cli.py export migration.json --include-content
```

#### Quality Assurance

```bash
# Export and review document chunks
uv run python cli.py export qa_review.csv --format csv --max 100

# Check tag distribution
uv run python cli.py export tag_analysis.json
```

---

## 📈 Progress Reporting

### Automatic Progress Bars

When processing more than 5 files, the CLI automatically shows rich progress bars:

**Progress Bar Features:**

```
Processing documents...
⠋ Processing: document_45.md ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 45/100 45% 0:00:25
```

**Information Displayed:**

- Spinner animation
- Current file being processed
- Progress bar
- Files completed / total files
- Percentage complete
- Estimated time remaining

### Processing Summary

After completion, see detailed statistics:

```
╭─────────── Processing Summary ───────────╮
│ Metric              │ Value              │
├─────────────────────┼────────────────────┤
│ ✅ Successful       │ 98                 │
│ ❌ Failed           │ 2                  │
│ ⏱️  Time Elapsed    │ 125.3s             │
│ 📈 Avg Time/File    │ 1.25s              │
╰─────────────────────┴────────────────────╯
```

### Performance Tips

1. **Batch Processing**: Process directories instead of individual files
2. **Incremental Mode**: Use `--incremental` to only process changed files
3. **Parallel Processing**: Future enhancement (currently single-threaded)

---

## 🎨 Rich Formatting

All Phase 3 features use the Rich library for beautiful terminal output:

### Benefits

- **Colored Output**: Better visual hierarchy
- **Tables**: Organized data display
- **Panels**: Grouped information
- **Progress Bars**: Real-time feedback
- **Emoji Icons**: Quick visual cues

### Fallback Mode

If Rich is not available, commands fall back to simple text output:

```bash
# Install Rich (recommended)
uv add rich

# Or use pip
pip install rich>=13.6.0
```

---

## 📝 Complete Workflow Example

Here's a complete workflow using all Phase 3 features:

```bash
# 1. Check current collection state
uv run python cli.py stats --detailed

# 2. Process new documents with progress bars
uv run python cli.py process ../new_docs --incremental --verbose

# 3. Search for specific topics
uv run python cli.py search "API authentication" --max 10 --verbose

# 4. Export results for analysis
uv run python cli.py export api_docs.json --filter-type md --max 50

# 5. Review updated statistics
uv run python cli.py stats --detailed

# 6. Create backup
uv run python cli.py export backup_$(date +%Y%m%d).json --include-content
```

---

## 🐛 Troubleshooting

### Search Returns No Results

**Problem**: Search query returns empty results

**Solutions**:

```bash
# 1. Check collection has documents
uv run python cli.py count

# 2. Try broader search terms
uv run python cli.py search "general topic" --max 20

# 3. Remove filters
uv run python cli.py search "query" --threshold 0.0

# 4. Verify Ollama is running
curl http://localhost:11434/api/tags
```

### Export Fails

**Problem**: Export command fails or creates empty file

**Solutions**:

```bash
# 1. Check collection has documents
uv run python cli.py count

# 2. Try smaller export
uv run python cli.py export test.json --max 10

# 3. Check disk space and permissions
df -h
ls -la /path/to/output

# 4. Use absolute paths
uv run python cli.py export /tmp/export.json
```

### Progress Bar Not Showing

**Problem**: No progress bar during processing

**Cause**: Processing fewer than 6 files or Rich not installed

**Solutions**:

```bash
# Install Rich
uv add rich

# Verify installation
python -c "import rich; print(rich.__version__)"

# Process larger batch to see progress bars
uv run python cli.py process ../large_docs
```

### Stats Show Unexpected Results

**Problem**: Statistics don't match expectations

**Solutions**:

```bash
# 1. List documents to verify contents
uv run python cli.py list --max 50

# 2. Check unique source files
uv run python cli.py list --source-files

# 3. Verify ChromaDB collection
uv run python cli.py count

# 4. Clear and reprocess if needed
uv run python cli.py process ../docs --clear --force
```

---

## 🚀 Performance Tips

### Search Performance

- Use specific queries instead of broad terms
- Apply file type filters to reduce search space
- Adjust `--max` parameter based on needs
- Higher similarity thresholds return fewer, more relevant results

### Export Performance

- Use `--max` parameter for large collections
- CSV exports are faster than JSON with `--include-content`
- Filter by file type before exporting
- Export in batches for very large collections

### Statistics Performance

- Basic stats are fast (collection metadata only)
- Detailed stats require reading all documents
- Schedule detailed stats for off-peak times
- Cache results for frequently accessed statistics

---

## 📚 Additional Resources

- [CLI Reference](../README.md) - Complete command documentation
- [Architecture](../ARCHITECTURE.md) - System design and components
- [Testing Guide](../tests/README.md) - Running and writing tests
- [Integration Guide](../examples/USAGE.md) - Integration patterns

---

## 🎯 Next Steps

Now that you've mastered Phase 3 features, explore:

1. **Phase 4**: Integration with VS Code and browser extensions
2. **Advanced Workflows**: Automated processing pipelines
3. **Custom Analytics**: Building your own analysis tools
4. **API Integration**: Using the optional FastAPI server

---

**Questions or Issues?**

- Check [Troubleshooting Guide](../TROUBLESHOOTING.md)
- Review [GitHub Issues](https://github.com/davidhayesbc/PrismWeave/issues)
- See [Architecture Documentation](../ARCHITECTURE.md)

---

✅ **Phase 3 Complete**: All features implemented, tested, and documented!
