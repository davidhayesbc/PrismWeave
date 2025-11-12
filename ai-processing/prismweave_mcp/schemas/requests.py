"""
Pydantic request schemas for MCP tools

Note: Using class Config (Pydantic v1 style) - warnings suppressed in pytest.ini
"""

from typing import Any, Optional

from pydantic import BaseModel, Field


class SearchDocumentsRequest(BaseModel):
    """Search documents request"""

    query: str = Field(..., description="Search query text")
    max_results: int = Field(20, description="Maximum number of results to return")
    similarity_threshold: float = Field(0.6, description="Minimum similarity score (0-1)")

    class Config:
        json_schema_extra = {
            "example": {
                "query": "machine learning concepts",
                "max_results": 10,
                "similarity_threshold": 0.7,
            }
        }


class GetDocumentRequest(BaseModel):
    """Get document by ID request"""

    document_id: str = Field(..., description="Document ID to retrieve")
    include_content: bool = Field(True, description="Whether to include full content")

    class Config:
        json_schema_extra = {
            "example": {
                "document_id": "doc_abc123",
                "include_content": True,
            }
        }


class ListDocumentsRequest(BaseModel):
    """List documents request"""

    category: Optional[str] = Field(default=None, description="Filter by category")
    tags: Optional[list[str]] = Field(default=None, description="Filter by tags (AND logic)")
    limit: int = Field(50, description="Maximum number of documents to return")
    offset: int = Field(0, description="Pagination offset")

    class Config:
        json_schema_extra = {
            "example": {
                "category": "tech",
                "tags": ["ml", "python"],
                "limit": 20,
                "offset": 0,
            }
        }


class GetMetadataRequest(BaseModel):
    """Get document metadata request"""

    document_id: str = Field(..., description="Document ID")

    class Config:
        json_schema_extra = {
            "example": {
                "document_id": "doc_abc123",
            }
        }


class CreateDocumentRequest(BaseModel):
    """Create new document request"""

    title: str = Field(..., description="Document title")
    content: str = Field(..., description="Markdown content")
    tags: list[str] = Field(default_factory=list, description="Document tags")
    category: Optional[str] = Field(default=None, description="Document category")
    source_url: Optional[str] = Field(default=None, description="Source URL if captured from web")
    author: Optional[str] = Field(default=None, description="Document author")
    additional_metadata: Optional[dict[str, Any]] = Field(default=None, description="Additional metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Introduction to Machine Learning",
                "content": "# Machine Learning\n\nContent goes here...",
                "tags": ["ml", "ai", "python"],
                "category": "tech",
                "source_url": "https://example.com/ml-intro",
                "author": "John Doe",
            }
        }


class UpdateDocumentRequest(BaseModel):
    """Update existing document request"""

    document_id: str = Field(..., description="Document ID to update")
    title: Optional[str] = Field(default=None, description="New title")
    content: Optional[str] = Field(default=None, description="New content")
    tags: Optional[list[str]] = Field(default=None, description="New tags")
    category: Optional[str] = Field(default=None, description="New category")
    additional_metadata: Optional[dict[str, Any]] = Field(default=None, description="Additional metadata to update")

    class Config:
        json_schema_extra = {
            "example": {
                "document_id": "doc_abc123",
                "title": "Updated Title",
                "tags": ["ml", "deep-learning"],
            }
        }


class GenerateEmbeddingsRequest(BaseModel):
    """Generate embeddings request"""

    document_id: str = Field(..., description="Document ID to generate embeddings for")
    model: str = Field("nomic-embed-text", description="Embedding model to use")
    force_regenerate: bool = Field(False, description="Force regeneration even if embeddings exist")

    class Config:
        json_schema_extra = {
            "example": {
                "document_id": "doc_abc123",
                "model": "nomic-embed-text",
                "force_regenerate": False,
            }
        }


class GenerateTagsRequest(BaseModel):
    """Generate tags for document request"""

    document_id: str = Field(..., description="Document ID to generate tags for")
    max_tags: int = Field(5, description="Maximum number of tags to generate")
    force_regenerate: bool = Field(False, description="Force regeneration even if tags exist")

    class Config:
        json_schema_extra = {
            "example": {
                "document_id": "doc_abc123",
                "max_tags": 5,
                "force_regenerate": False,
            }
        }


class CommitToGitRequest(BaseModel):
    """Commit changes to Git repository request"""

    file_paths: list[str] = Field(..., description="List of file paths to commit")
    commit_message: str = Field(..., description="Commit message")
    push: bool = Field(False, description="Whether to push after committing")

    class Config:
        json_schema_extra = {
            "example": {
                "file_paths": ["generated/2024-01-15-ml-basics.md"],
                "commit_message": "Add: ML basics document",
                "push": True,
            }
        }
