# PrismWeave MCP Server - VS Code Integration Guide

**Complete guide for integrating PrismWeave MCP server with Visual Studio Code**

---

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)

---

## Overview

The PrismWeave MCP server integrates with VS Code through the Model Context Protocol, providing AI assistants with:

- **Semantic search** across all PrismWeave documents
- **Document retrieval** for context and reference
- **Content generation** with AI-powered tagging and embeddings
- **Version control** through integrated git operations

### Architecture

```
VS Code with GitHub Copilot/Claude
         ↓
   MCP Extension
         ↓
  MCP Protocol (stdio)
         ↓
PrismWeave MCP Server
         ↓
Documents + AI Processing
```

---

## Prerequisites

### Required Software

1. **Visual Studio Code** (version 1.85+)

   ```bash
   code --version
   ```

2. **Python 3.10+** with PrismWeave environment

   ```bash
   cd /home/dhayes/Source/PrismWeave/ai-processing
   source .venv/bin/activate
   python --version
   ```

3. **Ollama** running locally

   ```bash
   curl http://localhost:11434/api/tags
   ```

4. **PrismWeave MCP Server** installed
   ```bash
   python -c "from prismweave_mcp import server; print('OK')"
   ```

### Required VS Code Extensions

- **GitHub Copilot** or **Claude for VS Code** (for MCP support)
- Install from VS Code Extensions marketplace

---

## Installation

### Step 1: Install VS Code MCP Extension

Currently, MCP support is available through:

**Option A: GitHub Copilot** (recommended)

```
1. Open VS Code
2. Go to Extensions (Ctrl+Shift+X)
3. Search for "GitHub Copilot"
4. Click Install
```

**Option B: Claude for VS Code**

```
1. Open VS Code
2. Go to Extensions (Ctrl+Shift+X)
3. Search for "Claude"
4. Click Install
```

---

### Step 2: Configure MCP Server

Create VS Code settings file for MCP configuration:

```bash
# Create .vscode directory if it doesn't exist
mkdir -p /home/dhayes/Source/PrismWeave/.vscode

# Copy MCP settings template
cp /home/dhayes/Source/PrismWeave/ai-processing/prismweave_mcp/.vscode/mcp-settings.json.template \
   /home/dhayes/Source/PrismWeave/.vscode/mcp-settings.json
```

---

### Step 3: Update VS Code Settings

Add MCP server configuration to VS Code settings:

**File**: `/home/dhayes/Source/PrismWeave/.vscode/settings.json`

```json
{
  "mcp.servers": {
    "prismweave": {
      "command": "python",
      "args": ["-m", "prismweave_mcp.server"],
      "cwd": "/home/dhayes/Source/PrismWeave/ai-processing",
      "env": {
        "PYTHONPATH": "/home/dhayes/Source/PrismWeave/ai-processing",
        "PRISMWEAVE_CONFIG": "/home/dhayes/Source/PrismWeave/ai-processing/config.yaml"
      }
    }
  }
}
```

**Or use absolute path to Python**:

```json
{
  "mcp.servers": {
    "prismweave": {
      "command": "/home/dhayes/Source/PrismWeave/ai-processing/.venv/bin/python",
      "args": ["-m", "prismweave_mcp.server"],
      "cwd": "/home/dhayes/Source/PrismWeave/ai-processing"
    }
  }
}
```

---

### Step 4: Reload VS Code

```
1. Open Command Palette (Ctrl+Shift+P)
2. Type "Developer: Reload Window"
3. Press Enter
```

---

### Step 5: Verify Connection

Check MCP server status:

```
1. Open Command Palette (Ctrl+Shift+P)
2. Type "MCP: Show Servers"
3. Verify "prismweave" is listed and connected
```

---

## Configuration

### MCP Server Settings

All configuration is in `ai-processing/config.yaml`:

```yaml
# Ollama Configuration
ollama:
  host: http://localhost:11434
  timeout: 60
  models:
    large: 'llama3.1:8b'
    medium: 'phi3:mini'
    embedding: 'nomic-embed-text'

# MCP Paths
mcp:
  paths:
    documents_root: '../../PrismWeaveDocs'
    generated_folder: 'generated'
    images_folder: 'images'

  # Search Settings
  search:
    max_results: 20
    similarity_threshold: 0.6

  # Creation Settings
  creation:
    auto_process: true # Auto-generate tags/embeddings
    auto_commit: false # Auto-commit to git

  # Git Settings
  git:
    auto_push: false
    commit_message_template: 'Add {title}'
```

### VS Code-Specific Settings

**File**: `.vscode/settings.json`

```json
{
  "mcp.servers": {
    "prismweave": {
      "command": "/home/dhayes/Source/PrismWeave/ai-processing/.venv/bin/python",
      "args": ["-m", "prismweave_mcp.server"],
      "cwd": "/home/dhayes/Source/PrismWeave/ai-processing",

      // Optional: Enable detailed logging
      "env": {
        "PRISMWEAVE_LOG_LEVEL": "DEBUG"
      }
    }
  },

  // Optional: Auto-restart server on file changes
  "mcp.autoRestart": true,

  // Optional: Show server output
  "mcp.showServerOutput": true
}
```

---

## Usage

### Basic Workflow

#### 1. Search Documents

Use AI assistant to search documents:

**Prompt**:

```
Search PrismWeave documents for "machine learning fundamentals"
```

**Behind the scenes**:

```json
{
  "tool": "search_documents",
  "parameters": {
    "query": "machine learning fundamentals",
    "max_results": 20
  }
}
```

**Result**:

- AI assistant receives search results
- Can reference found documents in response
- Provides relevant context from your knowledge base

---

#### 2. Retrieve Documents

**Prompt**:

```
Get the full content of document "2025-01-15-ml-basics.md"
```

**Behind the scenes**:

```json
{
  "tool": "get_document",
  "parameters": {
    "document_path": "documents/2025-01-15-ml-basics.md",
    "include_metadata": true
  }
}
```

**Result**:

- Full document content retrieved
- AI can quote, summarize, or analyze
- Metadata available for context

---

#### 3. Create Synthesized Content

**Prompt**:

```
Create a new document summarizing the top 3 articles about neural networks
```

**Behind the scenes**:

```
1. search_documents(query="neural networks")
2. get_document() for top 3 results
3. AI generates synthesis
4. create_document() with synthesized content
5. Optional: generate_tags(), generate_embeddings()
```

**Result**:

- New document created in `generated/` folder
- Automatically tagged and embedded
- Ready for search and retrieval

---

#### 4. Version Control

**Prompt**:

```
Commit the new article with message "Add neural networks summary"
```

**Behind the scenes**:

```json
{
  "tool": "commit_to_git",
  "parameters": {
    "message": "Add neural networks summary",
    "paths": ["generated/2025-01-15-neural-networks-summary.md"],
    "push": false
  }
}
```

**Result**:

- Changes committed to git
- Optionally pushed to remote
- Version history maintained

---

### Advanced Workflows

#### Batch Processing

**Prompt**:

```
Find all documents about "databases" and generate embeddings for any that don't have them
```

**Workflow**:

```
1. search_documents(query="databases")
2. For each result:
   a. get_document_metadata()
   b. Check if embeddings exist
   c. If not: generate_embeddings()
3. commit_to_git() with summary
```

---

#### Content Updates

**Prompt**:

```
Update the document "intro-to-ai.md" with new information about GPT-4, then regenerate its tags and embeddings
```

**Workflow**:

```
1. get_document(path="generated/intro-to-ai.md")
2. AI modifies content
3. update_document() with new content
4. generate_tags()
5. generate_embeddings()
6. commit_to_git()
```

---

#### Research Synthesis

**Prompt**:

```
Create a comprehensive article on "transformer architecture" by synthesizing information from all my captured articles on the topic
```

**Workflow**:

```
1. search_documents(query="transformer architecture")
2. get_document() for all relevant results
3. AI synthesizes content
4. create_document() with synthesis
5. Auto-processing (tags + embeddings)
6. commit_to_git()
```

---

## Examples

### Example 1: Simple Search

**User**: "Search my documents for articles about Python async programming"

**AI Assistant Uses**:

```json
{
  "tool": "search_documents",
  "parameters": {
    "query": "Python async programming",
    "max_results": 10,
    "filters": {
      "tags": ["python"]
    }
  }
}
```

**AI Response**:

```
I found 8 documents about Python async programming:

1. "Understanding Python Asyncio" (2025-01-10)
   - Comprehensive guide to asyncio fundamentals
   - Tags: python, async, concurrency

2. "Async Patterns in Python" (2025-01-12)
   - Best practices for async/await
   - Tags: python, async, patterns

[... rest of results ...]

Would you like me to retrieve the full content of any of these?
```

---

### Example 2: Content Creation

**User**: "Create a blog post synthesizing my top 3 articles on machine learning"

**AI Assistant Process**:

**Step 1 - Search**:

```json
{
  "tool": "search_documents",
  "parameters": {
    "query": "machine learning",
    "max_results": 3
  }
}
```

**Step 2 - Retrieve**:

```json
{
  "tool": "get_document",
  "parameters": {
    "document_id": "doc_123"
  }
}
```

(Repeated for top 3 results)

**Step 3 - Create**:

```json
{
  "tool": "create_document",
  "parameters": {
    "title": "Machine Learning Fundamentals: A Synthesis",
    "content": "[AI-generated synthesis of 3 articles]",
    "tags": ["machine-learning", "synthesis", "ai"],
    "auto_process": true,
    "auto_commit": false
  }
}
```

**AI Response**:

```
I've created a new blog post synthesizing your top 3 machine learning articles:

Title: "Machine Learning Fundamentals: A Synthesis"
Path: generated/2025-01-15-machine-learning-fundamentals-synthesis.md

The post covers:
- Core concepts from all three articles
- Key insights and connections
- Practical applications

Tags have been auto-generated and embeddings created for future search.

Would you like me to commit this to git?
```

---

### Example 3: Filtered Search

**User**: "Show me all generated documents about AI from the last month"

**AI Assistant Uses**:

```json
{
  "tool": "search_documents",
  "parameters": {
    "query": "AI",
    "max_results": 50,
    "filters": {
      "is_generated": true,
      "date_range": {
        "start": "2024-12-15T00:00:00Z",
        "end": "2025-01-15T00:00:00Z"
      },
      "tags": ["ai"]
    }
  }
}
```

---

### Example 4: Update Workflow

**User**: "Update my article on neural networks with the latest GPT-4 information, then regenerate its embeddings"

**AI Assistant Process**:

**Step 1 - Find Document**:

```json
{
  "tool": "search_documents",
  "parameters": {
    "query": "neural networks",
    "filters": { "is_generated": true }
  }
}
```

**Step 2 - Get Content**:

```json
{
  "tool": "get_document",
  "parameters": {
    "document_path": "generated/2024-11-01-neural-networks-intro.md"
  }
}
```

**Step 3 - Update**:

```json
{
  "tool": "update_document",
  "parameters": {
    "document_path": "generated/2024-11-01-neural-networks-intro.md",
    "content": "[Updated content with GPT-4 info]",
    "regenerate_embeddings": true
  }
}
```

**Step 4 - Commit**:

```json
{
  "tool": "commit_to_git",
  "parameters": {
    "message": "Update neural networks article with GPT-4 information",
    "paths": ["generated/2024-11-01-neural-networks-intro.md"]
  }
}
```

---

## Troubleshooting

### Server Not Connecting

**Symptom**: VS Code shows "MCP server prismweave disconnected"

**Checks**:

```bash
# 1. Verify Python path
/home/dhayes/Source/PrismWeave/ai-processing/.venv/bin/python --version

# 2. Test server manually
cd /home/dhayes/Source/PrismWeave/ai-processing
.venv/bin/python -m prismweave_mcp.server

# 3. Check VS Code MCP logs
# View > Output > Select "MCP" from dropdown
```

**Solutions**:

1. Check VS Code `settings.json` paths are absolute
2. Ensure virtual environment is activated
3. Verify `prismweave_mcp` module is installed

---

### Tools Not Available

**Symptom**: AI assistant says "I don't have access to search_documents tool"

**Solutions**:

1. **Restart MCP Server**:

   ```
   Command Palette > MCP: Restart Server > prismweave
   ```

2. **Check Server Status**:

   ```
   Command Palette > MCP: Show Servers
   ```

3. **View Server Logs**:

   ```
   View > Output > MCP > prismweave
   ```

4. **Verify Tool Registration**:
   ```bash
   # Test tools are available
   python -c "
   from prismweave_mcp import server
   print([tool for tool in dir(server) if not tool.startswith('_')])
   "
   ```

---

### Slow Performance

**Symptom**: Tools take >5 seconds to respond

**Solutions**:

1. **Check Ollama**:

   ```bash
   curl http://localhost:11434/api/tags
   ```

2. **Monitor Resource Usage**:

   ```bash
   top -p $(pgrep python | grep prismweave)
   ```

3. **Optimize Config**:
   ```yaml
   mcp:
     search:
       max_results: 10 # Reduce from 20
     rate_limiting:
       enabled: true
       requests_per_minute: 30
   ```

---

### Permission Errors

**Symptom**: "Cannot create document: permission denied"

**Solution**:

```bash
# Check permissions
ls -la ../../PrismWeaveDocs/generated/

# Fix permissions
chmod -R u+rw ../../PrismWeaveDocs/generated/

# Create directory if missing
mkdir -p ../../PrismWeaveDocs/generated
```

---

## Best Practices

### 1. Search Before Creating

Always search for existing content before creating new documents:

```
"Search for existing articles on [topic] before we create a new one"
```

### 2. Use Specific Queries

Be specific in search queries for better results:

**Good**: "Python async patterns for web scraping"  
**Bad**: "Python"

### 3. Enable Auto-Processing

For generated documents, enable auto-processing:

```yaml
mcp:
  creation:
    auto_process: true # Auto-generate tags and embeddings
```

### 4. Regular Commits

Commit changes regularly:

```
"After creating these 3 articles, commit them all with message 'Add AI synthesis articles'"
```

### 5. Review Generated Content

Always review AI-generated content before committing:

```
"Show me the generated article before committing"
```

---

## Advanced Configuration

### Multiple Environments

Create environment-specific configs:

```bash
# Development
cp config.yaml config.dev.yaml

# Production
cp config.yaml config.prod.yaml
```

Update VS Code settings:

```json
{
  "mcp.servers": {
    "prismweave-dev": {
      "command": "python",
      "args": ["-m", "prismweave_mcp.server"],
      "env": {
        "PRISMWEAVE_CONFIG": "config.dev.yaml"
      }
    },
    "prismweave-prod": {
      "command": "python",
      "args": ["-m", "prismweave_mcp.server"],
      "env": {
        "PRISMWEAVE_CONFIG": "config.prod.yaml"
      }
    }
  }
}
```

---

### Custom Keybindings

Add keyboard shortcuts for common MCP operations:

**File**: `.vscode/keybindings.json`

```json
[
  {
    "key": "ctrl+shift+m s",
    "command": "mcp.searchDocuments",
    "when": "editorTextFocus"
  },
  {
    "key": "ctrl+shift+m c",
    "command": "mcp.createDocument",
    "when": "editorTextFocus"
  }
]
```

---

## FAQ

**Q: Can I use multiple MCP servers simultaneously?**  
**A**: Yes! Configure multiple servers in `settings.json`. Each server gets its own namespace.

**Q: Does this work with GitHub Copilot Chat?**  
**A**: Yes, if Copilot has MCP support enabled in your version.

**Q: Can I disable specific tools?**  
**A**: Not directly, but you can modify `server.py` to comment out unwanted `@mcp.tool()` decorators.

**Q: How do I update the MCP server?**  
**A**:

```bash
cd /home/dhayes/Source/PrismWeave
git pull
cd ai-processing
uv sync
# Restart VS Code
```

---

## Next Steps

1. **Explore Tools**: Try each tool with simple queries
2. **Create Workflows**: Build multi-step processes
3. **Customize Config**: Adjust settings for your needs
4. **Monitor Performance**: Check logs and optimize
5. **Backup Data**: Regular git commits and ChromaDB backups

---

## Resources

- **Main Documentation**: [README.md](./README.md)
- **Troubleshooting**: [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)
- **Implementation Status**: [IMPLEMENTATION_STATUS.md](./IMPLEMENTATION_STATUS.md)
- **MCP Protocol**: https://modelcontextprotocol.io

---

**Last Updated**: November 11, 2025  
**Version**: 1.0.0
