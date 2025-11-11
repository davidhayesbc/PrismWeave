"""
Pydantic response schemas for MCP tools
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

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Machine Learning Basics",
                "tags": ["ml", "ai", "python"],
                "category": "tech",
                "word_count": 1500,
                "reading_time": 7,
            }
        }


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
    """Single search result"""

    document_id: str = Field(..., description="Document ID")
    path: str = Field(..., description="Relative path to document")
    title: str = Field(..., description="Document title")
    similarity_score: float = Field(..., ge=0.0, le=1.0, description="Similarity score")
    snippet: str = Field(..., description="Relevant content snippet")
    metadata: Optional[DocumentMetadata] = Field(default=None, description="Document metadata")
    content: Optional[str] = Field(default=None, description="Full content if requested")

    class Config:
        json_schema_extra = {
            "example": {
                "document_id": "doc_abc123",
                "path": "documents/2024-01-15-ml-article.md",
                "title": "Machine Learning Introduction",
                "similarity_score": 0.85,
                "snippet": "Machine learning is a subset of AI that...",
                "metadata": {"tags": ["ml", "ai"], "category": "tech"},
            }
        }


class SearchDocumentsResponse(BaseModel):
    """Response schema for document search"""

    success: bool = Field(..., description="Whether the search was successful")
    results: list[SearchResult] = Field(default_factory=list, description="Search results")
    total_found: int = Field(..., ge=0, description="Total number of results found")
    query: str = Field(..., description="Original search query")
    execution_time_ms: Optional[float] = Field(default=None, description="Search execution time in milliseconds")
    error: Optional[str] = Field(default=None, description="Error message if failed")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "results": [
                    {
                        "document_id": "doc_abc123",
                        "path": "documents/ml-intro.md",
                        "title": "ML Introduction",
                        "similarity_score": 0.85,
                        "snippet": "Machine learning basics...",
                    }
                ],
                "total_found": 1,
                "query": "machine learning",
                "execution_time_ms": 45.2,
            }
        }


class GetDocumentResponse(BaseModel):
    """Response schema for retrieving a document"""

    success: bool = Field(..., description="Whether the retrieval was successful")
    document: Optional[Document] = Field(default=None, description="Retrieved document")
    error: Optional[str] = Field(default=None, description="Error message if failed")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "document": {
                    "id": "doc_abc123",
                    "path": "generated/2024-01-15-article.md",
                    "content": "# Article\n\nContent...",
                    "metadata": {"title": "Article", "tags": ["tech"]},
                    "has_embeddings": True,
                },
            }
        }


class DocumentSummary(BaseModel):
    """Summary of a document (for listing)"""

    id: str = Field(..., description="Document ID")
    path: str = Field(..., description="Relative path")
    title: str = Field(..., description="Document title")
    size_bytes: int = Field(..., ge=0, description="File size in bytes")
    modified_at: Optional[datetime] = Field(default=None, description="Last modification timestamp")
    tags: list[str] = Field(default_factory=list, description="Document tags")
    category: Optional[str] = Field(default=None, description="Document category")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "doc_abc123",
                "path": "generated/2024-01-15-article.md",
                "title": "Article Title",
                "size_bytes": 5120,
                "tags": ["tech", "ai"],
                "category": "technology",
            }
        }


class ListDocumentsResponse(BaseModel):
    """Response schema for listing documents"""

    success: bool = Field(..., description="Whether the listing was successful")
    documents: list[DocumentSummary] = Field(default_factory=list, description="Document summaries")
    total_count: int = Field(..., ge=0, description="Total number of documents available")
    offset: int = Field(..., ge=0, description="Offset used for pagination")
    limit: int = Field(..., ge=1, description="Limit used for pagination")
    error: Optional[str] = Field(default=None, description="Error message if failed")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "documents": [
                    {
                        "id": "doc_abc123",
                        "path": "generated/2024-01-15-article.md",
                        "title": "Article",
                        "size_bytes": 5120,
                        "tags": ["tech"],
                    }
                ],
                "total_count": 1,
                "offset": 0,
                "limit": 100,
            }
        }


class CreateDocumentResponse(BaseModel):
    """Response schema for document creation"""

    success: bool = Field(..., description="Whether the creation was successful")
    document_id: Optional[str] = Field(default=None, description="ID of created document")
    path: Optional[str] = Field(default=None, description="Path to created document")
    embeddings_generated: bool = Field(False, description="Whether embeddings were generated")
    tags_generated: bool = Field(False, description="Whether tags were auto-generated")
    committed: bool = Field(False, description="Whether changes were committed to git")
    error: Optional[str] = Field(default=None, description="Error message if failed")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "document_id": "doc_abc123",
                "path": "generated/2024-01-15-new-article.md",
                "embeddings_generated": True,
                "tags_generated": True,
                "committed": False,
            }
        }


class UpdateDocumentResponse(BaseModel):
    """Response schema for document update"""

    success: bool = Field(..., description="Whether the update was successful")
    document_id: Optional[str] = Field(default=None, description="ID of updated document")
    path: Optional[str] = Field(default=None, description="Path to updated document")
    fields_updated: list[str] = Field(default_factory=list, description="Fields that were updated")
    embeddings_regenerated: bool = Field(False, description="Whether embeddings were regenerated")
    committed: bool = Field(False, description="Whether changes were committed to git")
    error: Optional[str] = Field(default=None, description="Error message if failed")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "document_id": "doc_abc123",
                "path": "generated/2024-01-15-article.md",
                "fields_updated": ["content", "tags"],
                "embeddings_regenerated": True,
                "committed": False,
            }
        }


class GenerateEmbeddingsResponse(BaseModel):
    """Response schema for embedding generation"""

    success: bool = Field(..., description="Whether embedding generation was successful")
    document_id: Optional[str] = Field(default=None, description="Document ID")
    path: Optional[str] = Field(default=None, description="Document path")
    embeddings_count: int = Field(0, ge=0, description="Number of embeddings generated")
    chunks_processed: int = Field(0, ge=0, description="Number of chunks processed")
    execution_time_ms: Optional[float] = Field(default=None, description="Processing time in milliseconds")
    error: Optional[str] = Field(default=None, description="Error message if failed")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "document_id": "doc_abc123",
                "path": "generated/2024-01-15-article.md",
                "embeddings_count": 15,
                "chunks_processed": 15,
                "execution_time_ms": 1250.5,
            }
        }


class GenerateTagsResponse(BaseModel):
    """Response schema for tag generation"""

    success: bool = Field(..., description="Whether tag generation was successful")
    document_id: Optional[str] = Field(default=None, description="Document ID")
    path: Optional[str] = Field(default=None, description="Document path")
    tags: list[str] = Field(default_factory=list, description="Generated tags")
    merged: bool = Field(False, description="Whether tags were merged with existing")
    execution_time_ms: Optional[float] = Field(default=None, description="Processing time in milliseconds")
    error: Optional[str] = Field(default=None, description="Error message if failed")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "document_id": "doc_abc123",
                "path": "generated/2024-01-15-article.md",
                "tags": ["ml", "ai", "python", "tutorial"],
                "merged": True,
                "execution_time_ms": 850.2,
            }
        }


class CommitToGitResponse(BaseModel):
    """Response schema for git commit operation"""

    success: bool = Field(..., description="Whether the commit was successful")
    commit_hash: Optional[str] = Field(default=None, description="Git commit hash")
    files_committed: int = Field(0, ge=0, description="Number of files committed")
    pushed: bool = Field(False, description="Whether changes were pushed to remote")
    branch: Optional[str] = Field(default=None, description="Branch committed to")
    error: Optional[str] = Field(default=None, description="Error message if failed")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "commit_hash": "abc123def456",
                "files_committed": 1,
                "pushed": False,
                "branch": "main",
            }
        }


class ErrorResponse(BaseModel):
    """Generic error response schema"""

    success: bool = Field(False, description="Always False for errors")
    error: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(default=None, description="Error code for programmatic handling")
    details: Optional[dict[str, Any]] = Field(default=None, description="Additional error details")

    class Config:
        json_schema_extra = {
            "example": {"success": False, "error": "Document not found", "error_code": "DOCUMENT_NOT_FOUND"}
        }
