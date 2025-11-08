# Post-Migration Installation Guide

After migrating from LangChain to Haystack, follow these steps to set up your environment:

## 1. Clean Previous Installation (Optional but Recommended)

```bash
# Remove old virtual environment
rm -rf .venv venv

# Clear Python cache
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null
```

## 2. Install Dependencies

### Using UV (Recommended)

```bash
cd ai-processing

# Install UV if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv sync

# Activate the environment
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate  # Windows
```

### Using pip

```bash
cd ai-processing

# Create virtual environment
python -m venv .venv

# Activate environment
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate  # Windows

# Install dependencies
pip install -e .
```

## 3. Verify Installation

```bash
# Check Haystack installation
python -c "import haystack; print(f'Haystack version: {haystack.__version__}')"

# Check ChromaDB integration
python -c "from haystack_integrations.document_stores.chroma import ChromaDocumentStore; print('ChromaDB integration OK')"

# Verify Ollama embedders
python -c "from haystack.components.embedders import OllamaDocumentEmbedder; print('Ollama embedders OK')"
```

## 4. Test the Migration

```bash
# Run tests to verify everything works
pytest tests/ -v

# Run a simple test processing
python cli.py --help

# Test with a sample document (if you have one)
python cli.py process /path/to/test/document.md --verbose
```

## 5. Verify Ollama is Running

```bash
# Check Ollama status
curl http://localhost:11434/api/tags

# If not running, start Ollama
ollama serve

# Pull required embedding model
ollama pull nomic-embed-text:latest
```

## 6. Check Configuration

```bash
# Verify config.yaml has correct settings
cat config.yaml

# Should see:
# - ollama.host: http://localhost:11434
# - ollama.models.embedding: 'nomic-embed-text:latest'
# - vector.collection_name: 'documents'
```

## Troubleshooting

### Issue: Import errors for Haystack

**Solution:**

```bash
# Reinstall Haystack
pip uninstall haystack-ai
pip install haystack-ai>=2.0.0
```

### Issue: ChromaDB integration not found

**Solution:**

```bash
# Install ChromaDB Haystack integration
pip install chroma-haystack>=0.22.0
```

### Issue: Document converters missing

**Solution:**

```bash
# Haystack includes basic converters by default
# For additional converters, install:
pip install pypdf python-docx beautifulsoup4
```

### Issue: Tests failing

**Solution:**

```bash
# Clear test cache
rm -rf .pytest_cache

# Reinstall in development mode
pip install -e ".[dev]"

# Run tests again
pytest tests/ -v
```

## Expected Package Versions

After installation, you should have:

```
haystack-ai >= 2.0.0
chroma-haystack >= 0.22.0
chromadb >= 0.4.15
python-frontmatter >= 1.0.0
pypdf >= 3.0.0
python-docx >= 1.0.0
beautifulsoup4 >= 4.12.2
pyyaml >= 6.0.1
requests >= 2.28.0
click >= 8.1.8
rich >= 13.6.0
```

## Next Steps

1. **Process your documents**: Use the CLI to process your document collection
2. **Test search functionality**: Verify semantic search works correctly
3. **Monitor performance**: Compare with previous LangChain performance
4. **Explore Haystack features**: Consider implementing pipelines and agents

## Resources

- [Haystack Documentation](https://docs.haystack.deepset.ai/docs/intro)
- [Installation Guide](https://docs.haystack.deepset.ai/docs/installation)
- [ChromaDB Integration](https://docs.haystack.deepset.ai/docs/chromadocumentstore)
- [Ollama Embedders](https://docs.haystack.deepset.ai/docs/ollamadocumentembedder)

## Support

If you encounter issues:

1. Check the [MIGRATION_TO_HAYSTACK.md](./MIGRATION_TO_HAYSTACK.md) document
2. Review [Haystack Troubleshooting](https://docs.haystack.deepset.ai/docs/faq)
3. Consult the [Haystack Discord](https://discord.com/invite/VBpFzsgRVF)

---

**Installation complete!** You're ready to use PrismWeave with Haystack. 🚀
