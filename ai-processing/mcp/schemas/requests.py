"""
Pydantic request schemas for MCP tools
"""

from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator


class SearchDocumentsRequest(BaseModel):
    """Request schema for searching documents"""

    query: str = Field(..., description="Search query text")
    max_results: int = Field(20, ge=1, le=100, description="Maximum number of results to return")
    similarity_threshold: float = Field(0.6, ge=0.0, le=1.0, description="Minimum similarity score")
    filters: Optional[dict[str, Any]] = Field(default=None, description="Additional filters (tags, date, etc)")
    include_content: bool = Field(True, description="Include full document content in results")

    class Config:
        json_schema_extra = {
            "example": {
                "query": "machine learning with Python",
                "max_results": 10,
                "similarity_threshold": 0.7,
                "filters": {"tags": ["python", "ai"]},
                "include_content": True,
            }
        }


class GetDocumentRequest(BaseModel):
    """Request schema for retrieving a single document"""

    document_id: Optional[str] = Field(default=None, description="Document ID (if known)")
    path: Optional[str] = Field(default=None, description="Relative path to document")
    include_metadata: bool = Field(True, description="Include document metadata")

    @field_validator("document_id", "path")
    @classmethod
    def check_at_least_one(cls, v: Optional[str], info) -> Optional[str]:
        """Ensure at least one of document_id or path is provided"""
        # This will be validated at the model level
        return v

    def model_post_init(self, __context: Any) -> None:
        """Ensure at least one identifier is provided"""
        if not self.document_id and not self.path:
            raise ValueError("Either document_id or path must be provided")

    class Config:
        json_schema_extra = {"example": {"document_id": "doc_abc123", "include_metadata": True}}


class ListDocumentsRequest(BaseModel):
    """Request schema for listing documents"""

    directory: Optional[str] = Field(default=None, description="Directory to list (None for all)")
    pattern: Optional[str] = Field(default=None, description="File pattern to match (glob)")
    limit: int = Field(100, ge=1, le=1000, description="Maximum number of documents to return")
    offset: int = Field(0, ge=0, description="Offset for pagination")
    sort_by: str = Field("date", description="Sort field (date, title, size)")
    sort_order: str = Field("desc", description="Sort order (asc, desc)")

    @field_validator("sort_by")
    @classmethod
    def validate_sort_by(cls, v: str) -> str:
        """Validate sort_by field"""
        allowed = {"date", "title", "size", "modified"}
        if v not in allowed:
            raise ValueError(f"sort_by must be one of {allowed}")
        return v

    @field_validator("sort_order")
    @classmethod
    def validate_sort_order(cls, v: str) -> str:
        """Validate sort_order field"""
        allowed = {"asc", "desc"}
        if v not in allowed:
            raise ValueError(f"sort_order must be one of {allowed}")
        return v

    class Config:
        json_schema_extra = {
            "example": {"directory": "generated", "limit": 50, "offset": 0, "sort_by": "date", "sort_order": "desc"}
        }


class GetDocumentMetadataRequest(BaseModel):
    """Request schema for retrieving document metadata only"""

    document_id: Optional[str] = Field(default=None, description="Document ID")
    path: Optional[str] = Field(default=None, description="Relative path to document")

    def model_post_init(self, __context: Any) -> None:
        """Ensure at least one identifier is provided"""
        if not self.document_id and not self.path:
            raise ValueError("Either document_id or path must be provided")

    class Config:
        json_schema_extra = {"example": {"path": "generated/2024-01-15-my-article.md"}}


class CreateDocumentRequest(BaseModel):
    """Request schema for creating a new document"""

    title: str = Field(..., min_length=1, max_length=500, description="Document title")
    content: str = Field(..., min_length=1, description="Markdown content")
    tags: list[str] = Field(default_factory=list, description="Document tags")
    category: Optional[str] = Field(default=None, description="Document category")
    metadata: Optional[dict[str, Any]] = Field(default=None, description="Additional metadata")
    auto_process: bool = Field(True, description="Automatically generate tags and embeddings")
    auto_commit: bool = Field(False, description="Automatically commit to git")
    filename: Optional[str] = Field(default=None, description="Custom filename (auto-generated if None)")

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: list[str]) -> list[str]:
        """Validate and normalize tags"""
        return [tag.strip().lower() for tag in v if tag.strip()]

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Understanding Machine Learning",
                "content": "# Machine Learning\n\nThis is an introduction...",
                "tags": ["ml", "ai", "python"],
                "category": "tech",
                "auto_process": True,
                "auto_commit": False,
            }
        }


class UpdateDocumentRequest(BaseModel):
    """Request schema for updating an existing document"""

    document_id: Optional[str] = Field(default=None, description="Document ID")
    path: Optional[str] = Field(default=None, description="Relative path to document")
    title: Optional[str] = Field(default=None, min_length=1, max_length=500, description="New title")
    content: Optional[str] = Field(default=None, min_length=1, description="New content")
    tags: Optional[list[str]] = Field(default=None, description="Updated tags")
    metadata: Optional[dict[str, Any]] = Field(default=None, description="Updated metadata")
    regenerate_embeddings: bool = Field(False, description="Regenerate embeddings after update")
    auto_commit: bool = Field(False, description="Automatically commit to git")

    def model_post_init(self, __context: Any) -> None:
        """Ensure at least one identifier and one update field is provided"""
        if not self.document_id and not self.path:
            raise ValueError("Either document_id or path must be provided")
        if not any([self.title, self.content, self.tags, self.metadata]):
            raise ValueError("At least one field to update must be provided")

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: Optional[list[str]]) -> Optional[list[str]]:
        """Validate and normalize tags"""
        if v is None:
            return None
        return [tag.strip().lower() for tag in v if tag.strip()]

    class Config:
        json_schema_extra = {
            "example": {
                "path": "generated/2024-01-15-my-article.md",
                "content": "# Updated Content\n\nNew information...",
                "tags": ["updated", "ml"],
                "regenerate_embeddings": True,
            }
        }


class GenerateEmbeddingsRequest(BaseModel):
    """Request schema for generating embeddings for a document"""

    document_id: Optional[str] = Field(default=None, description="Document ID")
    path: Optional[str] = Field(default=None, description="Relative path to document")
    force_regenerate: bool = Field(False, description="Regenerate even if embeddings exist")

    def model_post_init(self, __context: Any) -> None:
        """Ensure at least one identifier is provided"""
        if not self.document_id and not self.path:
            raise ValueError("Either document_id or path must be provided")

    class Config:
        json_schema_extra = {"example": {"path": "generated/2024-01-15-my-article.md", "force_regenerate": False}}


class GenerateTagsRequest(BaseModel):
    """Request schema for generating tags for a document using AI"""

    document_id: Optional[str] = Field(default=None, description="Document ID")
    path: Optional[str] = Field(default=None, description="Relative path to document")
    max_tags: int = Field(5, ge=1, le=20, description="Maximum number of tags to generate")
    merge_with_existing: bool = Field(True, description="Merge with existing tags or replace")

    def model_post_init(self, __context: Any) -> None:
        """Ensure at least one identifier is provided"""
        if not self.document_id and not self.path:
            raise ValueError("Either document_id or path must be provided")

    class Config:
        json_schema_extra = {
            "example": {"path": "generated/2024-01-15-my-article.md", "max_tags": 5, "merge_with_existing": True}
        }


class CommitToGitRequest(BaseModel):
    """Request schema for committing changes to git"""

    message: str = Field(..., min_length=1, max_length=500, description="Commit message")
    paths: Optional[list[str]] = Field(default=None, description="Specific paths to commit (None for all changes)")
    push: bool = Field(False, description="Push to remote after commit")
    branch: Optional[str] = Field(default=None, description="Branch to commit to (None for current branch)")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Add new machine learning article",
                "paths": ["generated/2024-01-15-ml-intro.md"],
                "push": False,
            }
        }
