"""
Pydantic request schemas for MCP tools

Note: Using class Config (Pydantic v1 style) - warnings suppressed in pytest.ini
"""

from typing import Any, Optional

from pydantic import BaseModel, Field


class SearchDocumentsRequest(BaseModel):
    """Search documents request"""

    query: str = Field(..., description="(Required) Natural-language search query text.")
    max_results: int = Field(
        20,
        description="(Optional) Maximum number of results to return. Defaults to 20 if not provided.",
    )
    similarity_threshold: float = Field(
        0.45,
        description="(Optional) Minimum cosine similarity score between 0 and 1. Defaults to 0.45.",
    )
    tags: Optional[list[str]] = Field(
        default=None,
        description="(Optional) Filter by tags; documents must contain every tag in this list.",
    )
    category: Optional[str] = Field(
        default=None,
        description="(Optional) Filter by category folder (e.g., 'tech').",
    )
    generated_only: bool = Field(
        default=False,
        description="(Optional) When True, only return AI-generated documents. Defaults to False.",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "query": "machine learning concepts",
                "max_results": 10,
                "similarity_threshold": 0.7,
                "tags": ["ml", "python"],
                "category": "tech",
                "generated_only": False,
            }
        }


class GetDocumentRequest(BaseModel):
    """Request to get a document by ID or path"""

    document_id: Optional[str] = Field(default=None, description="Document ID")
    path: Optional[str] = Field(default=None, description="Document path (relative to docs root)")
    include_content: bool = Field(default=True, description="Include document content")


class ListDocumentsRequest(BaseModel):
    """List documents request"""

    category: Optional[str] = Field(
        default=None,
        description="(Optional) Restrict results to this category folder (e.g., 'tech').",
    )
    tags: Optional[list[str]] = Field(
        default=None,
        description="(Optional) Filter by tags using AND logic; all tags must be present.",
    )
    limit: int = Field(
        50,
        description="(Optional) Maximum number of documents to return. Defaults to 50 when omitted.",
    )
    offset: int = Field(0, description="(Optional) Number of documents to skip for pagination. Defaults to 0.")

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

    document_id: str = Field(..., description="(Required) Document ID for the metadata lookup.")

    class Config:
        json_schema_extra = {
            "example": {
                "document_id": "doc_abc123",
            }
        }


class CreateDocumentRequest(BaseModel):
    """Create new document request"""

    title: str = Field(..., description="(Required) Human-readable document title.")
    content: str = Field(
        ...,
        description="(Required) Markdown-formatted content string.",
    )
    tags: list[str] = Field(
        default_factory=list,
        description="(Optional) Ordered list of tags to store in frontmatter. Defaults to empty list.",
    )
    category: Optional[str] = Field(
        default=None,
        description="(Optional) Category folder; when omitted, defaults to configuration default.",
    )
    source_url: Optional[str] = Field(
        default=None,
        description="(Optional) Absolute source URL when content is derived from the web.",
    )
    author: Optional[str] = Field(default=None, description="(Optional) Document author name.")
    additional_metadata: Optional[dict[str, Any]] = Field(
        default=None,
        description="(Optional) Additional frontmatter fields as a JSON-serializable dictionary.",
    )

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

    document_id: str = Field(..., description="(Required) Document ID of the generated file to update.")
    title: Optional[str] = Field(default=None, description="(Optional) Replacement title.")
    content: Optional[str] = Field(default=None, description="(Optional) Replacement Markdown content.")
    tags: Optional[list[str]] = Field(
        default=None,
        description="(Optional) Replacement tag list; supply the full desired set.",
    )
    category: Optional[str] = Field(default=None, description="(Optional) Updated category value.")
    additional_metadata: Optional[dict[str, Any]] = Field(
        default=None,
        description="(Optional) Metadata fields to merge with the document's existing frontmatter.",
    )

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

    document_id: str = Field(..., description="(Required) Document ID to generate embeddings for.")
    model: str = Field(
        "nomic-embed-text",
        description="(Optional) Embedding model identifier. Defaults to 'nomic-embed-text'.",
    )
    force_regenerate: bool = Field(
        False,
        description="(Optional) When True, re-create embeddings even if they already exist. Defaults to False.",
    )

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

    document_id: str = Field(..., description="(Required) Document ID to generate tags for.")
    max_tags: int = Field(
        5,
        description="(Optional) Maximum number of tags to generate. Defaults to 5.",
    )
    force_regenerate: bool = Field(
        False,
        description="(Optional) When True, generate new tags even if tags already exist. Defaults to False.",
    )

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

    file_paths: list[str] = Field(
        ...,
        description="(Required) Repository-relative file paths to include in the commit.",
    )
    commit_message: str = Field(..., description="(Required) Commit message summarizing the change.")
    push: bool = Field(
        False,
        description="(Optional) When True, push the commit to the remote repository after creation. Defaults to False.",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "file_paths": ["generated/2024-01-15-ml-basics.md"],
                "commit_message": "Add: ML basics document",
                "push": True,
            }
        }
