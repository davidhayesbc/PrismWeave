# PrismWeave - Requirements & Design Document

## Project Overview
A comprehensive document management and content creation system that:
1. Captures web pages as markdown via browser button
2. Syncs files to VS Code via Git
3. Tags and summarizes documents using LLM
4. Enables AI-powered content creation (blog posts, articles)
5. Provides intelligent document search
6. Maintains sync across multiple machines

## Requirements Gathering (In Progress)

### Questions & Answers
- [x] **Question 1**: Browser Integration & Platform Preferences
  - **Browsers**: Edge and Chrome (primary)
  - **Format**: Cleaned-up markdown focused on readability
  - **Images**: Flexible - inline or references both acceptable
- [x] **Question 2**: Document Storage & Organization
  - **Primary Goal**: Get documents into VS Code efficiently
  - **Organization**: By topic/subject matter
  - **File Naming**: Automatic, clear labeling preferred
  - **Metadata**: Capture automatically when possible
- [x] **Question 3**: Git Integration & Sync Strategy
  - **Git Platform**: GitHub
  - **Commit Strategy**: Optional auto-commit and push
  - **Workflow**: Extension → Git repo (direct save)
  - **Multi-device**: Each machine can capture + access repository
- [x] **Question 4**: AI Integration & Processing
  - **LLM Platform**: Local models (Ollama, LM Studio, or similar)
  - **Hardware Optimization**: AI HX 370 laptop with NPU acceleration
  - **Document Analysis**:
    - Automatic tagging and categorization
    - Content summarization
    - Topic detection for organization
  - **Search Capabilities**: 
    - Semantic search (meaning-based, not just keywords)
    - Vector embeddings for document similarity
  - **Content Generation**:
    - Automatic multi-document synthesis
    - Context-aware article/blog post creation
    - Reference tracking to source documents
  - **Processing Strategy**: 
    - Automatic analysis preferred
    - Manual trigger as fallback option
    - Batch processing for efficiency
- [x] **Question 5**: User Interface & Workflow
  - **Primary Interface**: VS Code
  - **VS Code Extension**: Beneficial for enhanced integration
  - **Content Creation**: GitHub Copilot + Ollama integration
  - **Workflow**: Capture → Process → Create within VS Code ecosystem

### User Requirements

#### Browser Integration
- **Target Browsers**: Edge and Chrome
- **Capture Method**: Browser extension (recommended over bookmarklet)
- **Output Format**: Clean, readable markdown
- **Image Handling**: Flexible approach - can be inline or file references
- **Content Processing**: Strip ads, navigation, focus on main content

#### Document Storage & Organization
- **Initial Storage**: Flexible - whatever is easiest technically
- **Primary Goal**: Efficient transfer to VS Code workspace
- **Organization Strategy**: Topic-based folder structure
- **File Naming**: Automatic with clear, descriptive names
- **Metadata Capture**: Automatic collection of:
  - Source URL
  - Capture timestamp
  - Page title
  - Domain/website
  - Potential topic detection

#### Git Integration & Sync
- **Platform**: GitHub
- **Repository Structure**: Direct save from extension to Git repository
- **Commit Options**: 
  - Manual commits (user control)
  - Auto-commit and push (optional setting)
- **Multi-device Support**: 
  - Each device can capture documents
  - Each device can have VS Code workspace with repository
  - Distributed capture and consumption model
- **Workflow**: Browser Extension → Git Repository ↔ VS Code Workspace(s)

#### User Interface & Workflow
- **Primary Interface**: VS Code as the main workspace
- **VS Code Extension Benefits**:
  - Custom document browser/explorer
  - AI processing commands in command palette
  - Integrated search interface
  - Document metadata display
  - Tag management and filtering
- **Content Creation Workflow**:
  - Use GitHub Copilot + Ollama for article generation
  - Leverage document context from captured files
  - Seamless integration with existing VS Code workflow
- **Document Management**: File-based with enhanced VS Code tooling

---

## Requirements Summary

### Core Features Validated ✅
1. **Browser Extension** (Chrome/Edge) for clean markdown capture
2. **Git-based Sync** across multiple devices via GitHub
3. **Local AI Processing** (Ollama + AI HX 370 optimization)
4. **VS Code Integration** as primary workspace
5. **Semantic Search** with vector embeddings
6. **Content Creation** using GitHub Copilot + Ollama
7. **Automatic Organization** by topic with AI assistance

### Key Technical Decisions
- **Local-first AI**: Privacy and cost benefits with NPU acceleration
- **Git-centric Sync**: Proven, reliable, developer-friendly
- **VS Code Primary**: Leverage existing workflow and tooling
- **Phased Development**: Incremental value delivery

### Success Criteria
- Capture web articles in <5 seconds
- Find relevant documents with semantic queries
- Generate draft articles from document collection  
- Seamless multi-device synchronization
- Efficient local AI processing

## Next Steps
See detailed implementation plan in: [`IMPLEMENTATION_PLAN.md`](./IMPLEMENTATION_PLAN.md)

**Ready to begin Phase 1**: Browser extension development

---
*Requirements completed: June 13, 2025*
*Implementation plan: See IMPLEMENTATION_PLAN.md*