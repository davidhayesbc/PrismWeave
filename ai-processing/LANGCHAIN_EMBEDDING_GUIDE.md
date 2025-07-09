# LangChain Embedding Enhancements for PrismWeave

## How LangChain Improves the Embedding Process

LangChain provides significant improvements to document processing and embedding generation that go well beyond basic text chunking and vector storage.

## Key Embedding Enhancements

### 1. **Intelligent Text Splitting**

**Current PrismWeave Approach**:
```python
# Basic character-based splitting
def simple_chunk(text: str, chunk_size: int = 1000) -> List[str]:
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
```

**LangChain Enhanced Splitting**:
```python
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
    PythonCodeTextSplitter,
    MarkdownTextSplitter,
    TokenTextSplitter
)

# Code-aware splitting that preserves function boundaries
python_splitter = PythonCodeTextSplitter(
    chunk_size=1500,
    chunk_overlap=200,
    length_function=len
)

# Markdown-aware splitting that preserves headers and structure
markdown_splitter = MarkdownTextSplitter(
    chunk_size=1000,
    chunk_overlap=100,
    headers_to_split_on=[
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
    ]
)

# Semantic boundary splitting
recursive_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separators=["\n\n", "\n", " ", ""]  # Tries to split on paragraphs first
)
```

### 2. **Document Structure Preservation**

**Enhanced Metadata Extraction**:
```python
# LangChain preserves rich document context
class EnhancedDocument:
    content: str
    metadata: Dict[str, Any] = {
        "source": "file_path",
        "title": "extracted_title",
        "section": "current_section",
        "subsection": "current_subsection",
        "code_language": "python",
        "doc_type": "api_reference",
        "parent_chunk_id": "chunk_123",
        "hierarchy_level": 2,
        "word_count": 250,
        "estimated_reading_time": 60,
        "last_modified": "2025-01-11T10:30:00Z"
    }
```

### 3. **Hierarchical Chunking Strategies**

**Parent-Child Document Relationships**:
```python
# Create parent documents (larger context)
parent_docs = create_parent_documents(document, chunk_size=4000)

# Create child documents (focused content) 
child_docs = create_child_documents(parent_docs, chunk_size=1000)

# Store both with relationships
vector_store.add_documents(
    child_docs,  # Used for similarity search
    parent_mapping=parent_docs  # Retrieved for full context
)
```

### 4. **Multi-Model Embedding Strategies**

**Different Models for Different Content Types**:
```python
from langchain.embeddings import (
    OllamaEmbeddings,
    OpenAIEmbeddings,
    HuggingFaceEmbeddings
)

class MultiModelEmbedder:
    def __init__(self):
        self.code_embedder = HuggingFaceEmbeddings(
            model_name="microsoft/codebert-base"
        )
        self.text_embedder = OllamaEmbeddings(
            model="nomic-embed-text"
        )
        self.math_embedder = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
    
    def embed_document(self, doc) -> List[float]:
        if doc.metadata.get("doc_type") == "code":
            return self.code_embedder.embed_query(doc.content)
        elif doc.metadata.get("contains_math"):
            return self.math_embedder.embed_query(doc.content)
        else:
            return self.text_embedder.embed_query(doc.content)
```

### 5. **Incremental Embedding Updates**

**Smart Re-embedding**:
```python
class IncrementalEmbedder:
    def should_re_embed(self, document_hash: str, last_modified: datetime) -> bool:
        # Check if document changed since last embedding
        stored_hash = self.get_stored_hash(document_hash)
        return stored_hash != document_hash
    
    def update_embeddings(self, documents: List[Document]):
        for doc in documents:
            if self.should_re_embed(doc.metadata["hash"], doc.metadata["last_modified"]):
                # Only re-embed changed documents
                embedding = self.embedder.embed_query(doc.content)
                self.vector_store.update_document(doc.id, embedding)
```

### 6. **Embedding Quality Assessment**

**Automatic Quality Validation**:
```python
class EmbeddingQualityAssessor:
    def assess_chunk_quality(self, chunk: str) -> float:
        """Assess if a chunk will produce good embeddings"""
        # Check for minimum content
        if len(chunk.strip()) < 50:
            return 0.1
        
        # Check for code vs text balance
        code_ratio = self.calculate_code_ratio(chunk)
        if code_ratio > 0.8:  # Mostly code
            return 0.9
        elif code_ratio < 0.1:  # Mostly text
            return 0.8
        else:  # Mixed content
            return 0.95
    
    def filter_low_quality_chunks(self, chunks: List[str]) -> List[str]:
        return [chunk for chunk in chunks 
                if self.assess_chunk_quality(chunk) > 0.5]
```

## Benefits for Your PrismWeave Use Cases

### 1. **Better Code Documentation Embedding**

```python
# Current approach might break code examples
chunk = """
def authenticate_user(username, password):
    # This function handles user authentication
    if not username or not password:
        return False
    
    # Verify credentials against database
    user = database.get_user(username)
    if user and verify_password(password, user.password_hash):
        return create_session(user)
    return False

# Usage example:
if authenticate_user("john", "secret123"):
    print("Login successful")
"""

# LangChain preserves function boundaries and context
python_splitter = PythonCodeTextSplitter(chunk_size=1500)
chunks = python_splitter.split_text(chunk)
# Result: Complete functions with their docstrings and examples
```

### 2. **Markdown Structure Preservation**

```python
# Your technical documentation with headers
markdown_content = """
# Authentication System

## Overview
The authentication system provides secure user login...

## Implementation
### Database Setup
First, create the user table...

### API Endpoints
The following endpoints are available...

#### POST /auth/login
Authenticates a user and returns a session token...
"""

# LangChain preserves the hierarchy
markdown_splitter = MarkdownTextSplitter(
    headers_to_split_on=[("#", "Header 1"), ("##", "Header 2"), ("###", "Header 3")]
)
chunks = markdown_splitter.split_text(markdown_content)
# Each chunk knows its place in the document hierarchy
```

### 3. **Enhanced Retrieval Through Better Embeddings**

**Contextual Similarity**:
```python
# With better chunking and metadata, queries like:
"How do I handle user authentication errors?"

# Can find more relevant results:
- Function definitions with error handling
- Documentation sections about error cases  
- Code examples showing proper error responses
- Related security considerations
```

## Integration with Your Current System

### Updated Document Processing Pipeline

```python
# Enhanced document processor for PrismWeave
class LangChainDocumentProcessor:
    def __init__(self):
        self.splitters = {
            ".py": PythonCodeTextSplitter(chunk_size=1500, chunk_overlap=200),
            ".md": MarkdownTextSplitter(chunk_size=1000, chunk_overlap=100),
            ".js": RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=150),
            ".default": RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        }
        
    async def process_document(self, file_path: str) -> List[Document]:
        """Process document with appropriate splitter"""
        content = await self.load_file(file_path)
        file_extension = Path(file_path).suffix
        
        splitter = self.splitters.get(file_extension, self.splitters[".default"])
        chunks = splitter.split_text(content)
        
        documents = []
        for i, chunk in enumerate(chunks):
            metadata = {
                "source": file_path,
                "chunk_index": i,
                "total_chunks": len(chunks),
                "file_type": file_extension,
                "chunk_size": len(chunk),
                "processing_date": datetime.now().isoformat()
            }
            documents.append(Document(content=chunk, metadata=metadata))
        
        return documents
```

### Configuration for Enhanced Embedding

```yaml
# config.yaml
embedding:
  use_langchain_splitters: true
  splitter_configs:
    python:
      type: "PythonCodeTextSplitter"
      chunk_size: 1500
      chunk_overlap: 200
    markdown:
      type: "MarkdownTextSplitter" 
      chunk_size: 1000
      chunk_overlap: 100
      headers_to_split: ["#", "##", "###"]
    default:
      type: "RecursiveCharacterTextSplitter"
      chunk_size: 1000
      chunk_overlap: 200
      separators: ["\n\n", "\n", " ", ""]
  
  quality_threshold: 0.5
  enable_hierarchical_chunking: true
  preserve_metadata: true
```

## Performance Impact

### Embedding Quality Improvements

| Aspect | Standard Chunking | LangChain Enhanced |
|--------|------------------|-------------------|
| **Code Preservation** | Often breaks functions | Preserves function boundaries |
| **Context Retention** | Limited metadata | Rich hierarchical context |
| **Retrieval Accuracy** | Good | Excellent |
| **Processing Time** | Fast | Slightly slower (better quality) |
| **Storage Efficiency** | Good | Better (avoids redundant chunks) |

### Practical Benefits

1. **Better Code Searches**: Find complete function implementations, not fragments
2. **Contextual Documentation**: Understand which section a piece of info comes from
3. **Smarter Updates**: Only re-embed changed documents
4. **Quality Control**: Automatically filter out low-quality chunks

## Getting Started with Enhanced Embedding

```bash
# Install additional LangChain components
uv pip install langchain-text-splitters

# Update your document processing
python cli/prismweave.py process /path/to/docs \
  --use-langchain-splitters \
  --enable-hierarchical-chunking \
  --rebuild-embeddings
```

The enhanced embedding process particularly helps with:
- **Code documentation** (preserves function boundaries)
- **Technical guides** (maintains section structure) 
- **API documentation** (keeps related info together)
- **Mixed content** (handles code + text appropriately)

This results in much more accurate and contextual RAG responses when you ask questions about your codebase and documentation.
