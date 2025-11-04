# Phase 3 CLI Quick Reference

**Quick reference for new CLI commands added in Phase 3**

---

## 🔍 Search Command

**Basic Usage:**
```bash
uv run python cli.py search "QUERY"
```

**Options:**
- `-m, --max INTEGER` - Max results (default: 10)
- `-t, --threshold FLOAT` - Similarity threshold (0.0-1.0)
- `-v, --verbose` - Show full content
- `--filter-type TEXT` - Filter by file type (md, txt, pdf)

**Examples:**
```bash
# Basic search
uv run python cli.py search "machine learning"

# More results
uv run python cli.py search "Python" --max 20

# Filter markdown only
uv run python cli.py search "API docs" --filter-type md

# Verbose output
uv run python cli.py search "tutorial" --verbose

# High relevance only
uv run python cli.py search "neural networks" --threshold 0.8
```

---

## 📊 Stats Command

**Basic Usage:**
```bash
uv run python cli.py stats
```

**Options:**
- `-d, --detailed` - Show detailed analytics

**Examples:**
```bash
# Quick overview
uv run python cli.py stats

# Full analytics with file types and tags
uv run python cli.py stats --detailed
```

**Shows:**
- Total chunks and files
- Average chunks per file
- File type distribution (detailed mode)
- Tag frequency (detailed mode)
- Content statistics (detailed mode)

---

## 💾 Export Command

**Basic Usage:**
```bash
uv run python cli.py export OUTPUT_FILE
```

**Options:**
- `-f, --format [json|csv]` - Export format (default: json)
- `--filter-type TEXT` - Filter by file type
- `--include-content` - Include full content (JSON only)
- `-m, --max INTEGER` - Max documents to export

**Examples:**
```bash
# Basic JSON export
uv run python cli.py export documents.json

# CSV export
uv run python cli.py export docs.csv --format csv

# Full content backup
uv run python cli.py export backup.json --include-content

# Export only markdown
uv run python cli.py export markdown.json --filter-type md

# Limited export
uv run python cli.py export sample.json --max 100

# Combined filters
uv run python cli.py export subset.json --filter-type md --max 50
```

---

## 📈 Progress Reporting

**Automatic for large batches (>5 files):**
- Shows current file
- Progress bar
- Time remaining
- Processing statistics

**Summary after completion:**
- Successful files
- Failed files
- Time elapsed
- Average time per file

---

## 🎨 Visual Enhancements

All commands use Rich library for:
- ✅ Color-coded output
- 📊 Formatted tables
- 📦 Organized panels
- ⏱️ Progress bars
- 🎯 Emoji indicators

---

## 🔄 Complete Workflow

```bash
# 1. Check stats
uv run python cli.py stats

# 2. Process with progress
uv run python cli.py process ../docs --incremental

# 3. Search content
uv run python cli.py search "topic" --max 10

# 4. Export results
uv run python cli.py export results.json --filter-type md

# 5. Verify
uv run python cli.py stats --detailed
```

---

## 💡 Pro Tips

### Search
- Use specific queries for better results
- Apply filters to narrow down results
- Adjust threshold for precision vs. recall
- Use verbose mode for detailed content

### Stats
- Use basic stats for quick checks
- Use detailed stats for deep analysis
- Run periodically to track collection growth
- Export stats to file for historical tracking

### Export
- Use JSON for full featured exports
- Use CSV for spreadsheet analysis
- Filter by type to focus exports
- Include content for backups
- Limit exports for quick samples

---

## 🆘 Quick Troubleshooting

**No search results?**
```bash
uv run python cli.py count  # Check collection
uv run python cli.py search "query" --threshold 0.0  # Lower threshold
```

**Export empty?**
```bash
uv run python cli.py list --max 10  # Verify documents
uv run python cli.py export test.json --max 5  # Try small export
```

**No progress bars?**
```bash
uv add rich  # Install Rich library
uv run python cli.py process ../many_docs  # Process >5 files
```

---

## 📚 Full Documentation

See [PHASE3_USAGE.md](./PHASE3_USAGE.md) for complete guide.

---

✅ Phase 3: Enhanced Features Complete!
