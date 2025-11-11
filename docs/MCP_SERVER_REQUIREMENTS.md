# MCP Server for PrismWeaveDocs - Requirements Gathering

**Date**: November 11, 2025  
**Project**: PrismWeave MCP Server  
**Purpose**: Enable LLM agents to access and interact with captured documents

---

## Overview

Building a Model Context Protocol (MCP) server to provide LLM agents with access to the PrismWeaveDocs document repository. This will enable AI assistants to search, read, and potentially manage captured web content.

---

## Questions & Answers

### 1. Core Access Patterns ✅

**Question**: What are the primary ways you want LLM agents to interact with your documents?

**Options to consider**:

- Search & Retrieval (by content, tags, metadata)
- Read Operations (full content, summaries, metadata)
- Write Operations (create, update, delete)
- Semantic Search (vector-based similarity)
- Collections/Filtering (date ranges, categories)

**Answer**:

- **Primary Use Case**: Query PrismWeaveDocs using natural language prompts
- **Document Synthesis**: Create new documents combining RAG (from PrismWeaveDocs) + Web search
- **Search Strategy**: Prefer embeddings database (ChromaDB) for retrieval
- **Capabilities Needed**:
  - ✅ Semantic search via vector embeddings
  - ✅ Full document retrieval
  - ✅ Document creation (AI-synthesized content)
  - ✅ RAG-based query answering
  - ✅ Web search integration for synthesis

---

### 2. RAG & Document Synthesis Architecture

**Question**: How should the MCP server integrate with your existing AI processing module?

**Sub-questions**:

**A) MCP Server Architecture**:

- Option 1: Thin wrapper delegating to existing `ai-processing` module (reuse ChromaDB, Ollama)
- Option 2: Standalone service with its own embedding/search logic
- Option 3: Extend existing `ai-processing` CLI to expose MCP endpoints

**B) Web Search Integration**:

- Use existing search API (Brave, SerpAPI, Tavily)?
- Scrape websites directly (like browser extension)?
- Combine vector search + web search?

**C) Document Synthesis Workflow**:

- Auto-save synthesized documents to PrismWeaveDocs?
- Apply AI processing pipeline (tagging, categorization)?
- Version control for AI-generated content?

**Answer**: ✅

- **Architecture**: Thin wrapper around existing ChromaDB embeddings database
- **Web Search**: Delegated to LLM agent (not in MCP server) - LLM uses other tools for web search
- **Generated Content**:

### 3. MCP Tools & Capabilities Design

**Question**: What specific MCP tools should the server expose?

**Proposed Tools**:

**Search & Retrieval**:

- `search_documents` - Semantic search using embeddings (returns doc IDs + snippets)
- `get_document` - Retrieve full document content by ID/path
- `list_documents` - Browse documents with filters (date, tags, category)
- `get_document_metadata` - Get just the frontmatter/metadata

**Document Creation**:

- `create_document` - Save new AI-generated content to `generated/` folder
- `update_document` - Modify existing documents (optional - may be risky)

**Post-Processing Options**:

- Auto-trigger on document creation:
  - Git commit
  - Embedding generation
  - AI tagging/categorization
- OR expose as separate tools for LLM control?

**Query Interface**:

- High-level `query` tool (search + retrieval combined)?
- OR atomic tools the LLM orchestrates?

**Answer**: ✅

- **All proposed tools approved**:
  - ✅ `search_documents` - Semantic search
  - ✅ `get_document` - Full content retrieval
  - ✅ `list_documents` - Browse with filters
  - ✅ `get_document_metadata` - Frontmatter only
  - ✅ `create_document` - Save to `generated/` folder
  - ✅ `update_document` - **Only for generated documents** (not captured)
- **Post-Processing Strategy**: Separate atomic tools
  - `generate_embeddings` - Create vectors for new document

### 4. Technology Stack & Deployment

**Question**: Which language/framework and deployment model?

**A) Language Options**:

**Python**:

- ✅ Matches existing `ai-processing` module (easy integration)
- ✅ MCP Python SDK available
- ✅ Direct access to ChromaDB, Ollama client
- ❌ Another Python service to manage

**TypeScript/Node.js**:

- ✅ Matches browser/VS Code extensions
- ✅ MCP TypeScript SDK available
- ❌ Would need to call Python AI processing as subprocess/API
- ❌ More complex integration

**B) Deployment Model**:

- Stdio transport (launched by Claude Desktop/other MCP clients)?
- HTTP/SSE transport (runs as persistent service)?
- Both?

**C) Configuration**:

- Use same `config.yaml` as ai-processing module?
- Separate MCP-specific config?

**Answer**: ✅

- **Language**: Python (matches ai-processing module, direct ChromaDB/Ollama access)
- **Deployment**: Stdio transport (recommended for VS Code integration)
  - ✅ Launched on-demand by VS Code
  - ✅ Simpler resource management
  - ✅ No separate service process
  - ✅ Better for single-user, single-IDE use case
- **Configuration**: Reuse existing `config.yaml` from ai-processing module
  - Consistent configuration across PrismWeave components
  - Single source of truth for Ollama endpoints, vector DB paths, etc.: Atomic tools for maximum flexibility
  - LLM composes search → retrieve → process workflows
  - More control over retrieval strategy

---

### 3. Security & Access Control

**Question**: [To be asked]

**Answer**: [PENDING]

---

### 4. Performance & Scalability

**Question**: [To be asked]

**Answer**: [PENDING]

---

### 5. MCP Server Architecture

**Question**: [To be asked]

**Answer**: [PENDING]

---

## Initial Observations

### Current PrismWeave Architecture

- **Browser Extension**: Captures web pages as markdown
- **AI Processing Module**: Python-based with Ollama for analysis and ChromaDB for vectors
- **VS Code Extension**: Document management interface
- **Document Storage**: PrismWeaveDocs repository with markdown files + metadata

### Potential MCP Server Approaches

1. **Standalone Python Server**: Leverage existing AI processing infrastructure
2. **TypeScript/Node.js Server**: Align with browser/VS Code extensions
3. **Hybrid Approach**: Python backend with TypeScript MCP wrapper

### Technical Considerations

- MCP SDK availability (Python vs TypeScript)
- Integration with existing vector database (ChromaDB)
- Performance for semantic search operations
- Document indexing and caching strategies

---

## Next Steps

1. Complete requirements gathering (Q&A session)
2. Design MCP server architecture
3. Create implementation plan with milestones
4. Identify dependencies and prerequisites
5. Begin implementation

---

## References

- [MCP Specification](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [MCP TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk)
- PrismWeave AI Processing Module: `/ai-processing`
- Document Repository: `/PrismWeaveDocs`
