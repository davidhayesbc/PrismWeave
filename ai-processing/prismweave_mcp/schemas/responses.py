"""
Pydantic response schemas for MCP tools

Note: Using class Config (Pydantic v1 style) - warnings suppressed in pytest.ini
"""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class DocumentMetadata(BaseModel):
    """Document metadata schema"""

    title: str = Field(..., description="Document title")
    tags: list[str] = Field(default_factory=list, description="Document tags")
    category: Optional[str] = Field(default=None, description="Document category")
    created_at: Optional[datetime] = Field(default=None, description="Creation timestamp")
    modified_at: Optional[datetime] = Field(default=None, description="Last modification timestamp")
    word_count: Optional[int] = Field(default=None, description="Word count")
    reading_time: Optional[int] = Field(default=None, description="Estimated reading time in minutes")
    source_url: Optional[str] = Field(default=None, description="Source URL if captured from web")
    author: Optional[str] = Field(default=None, description="Document author")
    additional: Optional[dict[str, Any]] = Field(default=None, description="Additional metadata fields")


class Document(BaseModel):
    """Complete document schema"""

    id: str = Field(..., description="Document ID")
    path: str = Field(..., description="Relative path to document")
    content: str = Field(..., description="Markdown content")
    metadata: DocumentMetadata = Field(..., description="Document metadata")
    has_embeddings: bool = Field(False, description="Whether embeddings exist for this document")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "doc_abc123",
                "path": "generated/2024-01-15-ml-basics.md",
                "content": "# Machine Learning\n\nContent here...",
                "metadata": {
                    "title": "Machine Learning Basics",
                    "tags": ["ml", "ai"],
                    "category": "tech",
                    "word_count": 1500,
                },
                "has_embeddings": True,
            }
        }


class SearchResult(BaseModel):
    """Single search result item.

    Note: tests expect a top-level "title" attribute as a convenient
    shortcut in addition to the richer nested ``metadata`` structure.
    """

    document_id: str = Field(..., description="Document ID")
    path: str = Field(..., description="Relative path to source document")
    score: float = Field(..., description="Similarity score (0-1)")
    excerpt: str = Field(..., description="Relevant excerpt from document")
    # Convenience field surfaced for callers/tests; kept in sync with
    # ``metadata.title`` by the search manager when available.
    title: Optional[str] = Field(default=None, description="Document title for this result")
    metadata: Optional[DocumentMetadata] = Field(default=None, description="Document metadata (optional)")

    class Config:
        json_schema_extra = {
            "example": {
                "document_id": "doc_abc123",
                "path": "documents/tech/ml-basics.md",
                "score": 0.92,
                "excerpt": "Machine learning is a subset of artificial intelligence...",
                "title": "ML Basics",
                "metadata": {
                    "title": "ML Basics",
                    "tags": ["ml", "ai"],
                },
            }
        }


class SearchDocumentsResponse(BaseModel):
    """Search results response"""

    query: str = Field(..., description="Original search query")
    results: list[SearchResult] = Field(..., description="Search results")
    total_results: int = Field(..., description="Total number of results found")

    class Config:
        json_schema_extra = {
            "example": {
                "query": "machine learning concepts",
                "results": [],
                "total_results": 5,
            }
        }


class ListDocumentsResponse(BaseModel):
    """List of documents response"""

    documents: list[Document] = Field(..., description="List of documents")
    total_count: int = Field(..., description="Total number of documents")
    category: Optional[str] = Field(default=None, description="Filter category if specified")

    class Config:
        json_schema_extra = {
            "example": {
                "documents": [],
                "total_count": 10,
                "category": "tech",
            }
        }


class ProcessingResponse(BaseModel):
    """Processing operation response"""

    success: bool = Field(..., description="Whether operation succeeded")
    message: str = Field(..., description="Status message")
    data: Optional[dict[str, Any]] = Field(default=None, description="Processing results")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Embeddings generated successfully",
                "data": {"embedding_count": 50},
            }
        }


class GenerateEmbeddingsResponse(BaseModel):
    """Embedding generation response"""

    document_id: str = Field(..., description="Document ID")
    embedding_count: int = Field(..., description="Number of embeddings generated")
    model: str = Field(..., description="Model used for embeddings")

    class Config:
        json_schema_extra = {
            "example": {
                "document_id": "doc_abc123",
                "embedding_count": 50,
                "model": "nomic-embed-text",
            }
        }


class GenerateTagsResponse(BaseModel):
    """Tag generation response"""

    document_id: str = Field(..., description="Document ID")
    tags: list[str] = Field(..., description="Generated tags")
    confidence: float = Field(..., description="Confidence score")

    class Config:
        json_schema_extra = {
            "example": {
                "document_id": "doc_abc123",
                "tags": ["machine-learning", "ai", "python"],
                "confidence": 0.85,
            }
        }


class CommitToGitResponse(BaseModel):
    """Git commit operation response"""

    success: bool = Field(..., description="Whether commit succeeded")
    commit_hash: Optional[str] = Field(default=None, description="Git commit hash")
    message: str = Field(..., description="Commit message or error")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "commit_hash": "abc123def456",
                "message": "Added new document: ml-basics.md",
            }
        }


class ErrorDetail(BaseModel):
    """Error detail information"""

    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    details: Optional[dict[str, Any]] = Field(default=None, description="Additional error details")

    class Config:
        json_schema_extra = {
            "example": {
                "code": "DOCUMENT_NOT_FOUND",
                "message": "Document doc_abc123 not found",
                "details": {"searched_paths": ["/path1", "/path2"]},
            }
        }


class ErrorResponse(BaseModel):
    """Standard error response"""

    error: str = Field(..., description="Error message")
    error_code: str = Field(..., description="Error code for programmatic handling")
    details: Optional[dict[str, Any]] = Field(default=None, description="Error details and context information")

    class Config:
        json_schema_extra = {
            "example": {
                "error": "Document not found",
                "error_code": "DOCUMENT_NOT_FOUND",
                "details": {"document_id": "doc_abc123"},
            }
        }


class DocumentSummary(BaseModel):
    """Summary information about a document"""

    id: str = Field(..., description="Document ID")
    title: str = Field(..., description="Document title")
    tags: list[str] = Field(default_factory=list, description="Document tags")
    category: Optional[str] = Field(default=None, description="Document category")
    word_count: Optional[int] = Field(default=None, description="Word count")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "doc_abc123",
                "title": "Machine Learning Basics",
                "tags": ["ml", "ai"],
                "category": "tech",
                "word_count": 1500,
            }
        }


class GetDocumentResponse(BaseModel):
    """Response for getting a document"""

    document: Document = Field(..., description="The retrieved document")

    class Config:
        json_schema_extra = {
            "example": {
                "document": {
                    "id": "doc_abc123",
                    "path": "generated/2024-01-15-ml-basics.md",
                    "content": "# Machine Learning\n\nContent...",
                    "metadata": {"title": "ML Basics", "tags": ["ml"]},
                    "has_embeddings": True,
                }
            }
        }


class CreateDocumentResponse(BaseModel):
    """Response for creating a document"""

    document_id: str = Field(..., description="ID of created document")
    path: str = Field(..., description="Path where document was created")

    class Config:
        json_schema_extra = {
            "example": {
                "document_id": "doc_abc123",
                "path": "generated/2024-01-15-ml-basics.md",
            }
        }


class UpdateDocumentResponse(BaseModel):
    """Response for updating a document"""

    document_id: str = Field(..., description="ID of updated document")
    updated_fields: list[str] = Field(..., description="List of fields that were updated")

    class Config:
        json_schema_extra = {
            "example": {
                "document_id": "doc_abc123",
                "updated_fields": ["title", "tags"],
            }
        }
