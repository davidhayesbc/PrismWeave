"""
Pydantic models for API requests and responses
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class ArticleSummary(BaseModel):
    """Summary information for an article (used in list view)"""

    id: str = Field(..., description="Unique article identifier")
    title: str = Field(..., description="Article title")
    path: str = Field(..., description="Relative path to markdown file")
    topic: Optional[str] = Field(None, description="Article topic/category")
    tags: List[str] = Field(default_factory=list, description="Article tags")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    word_count: int = Field(..., description="Word count")
    excerpt: str = Field(..., description="Short excerpt")
    read_status: str = Field(..., description="Read status (read/unread)")
    x: Optional[float] = Field(None, description="X coordinate for visualization")
    y: Optional[float] = Field(None, description="Y coordinate for visualization")
    neighbors: Optional[List[str]] = Field(None, description="IDs of nearest neighbor articles")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "documents/tech/python-basics.md",
                "title": "Python Basics",
                "path": "documents/tech/python-basics.md",
                "topic": "programming",
                "tags": ["python", "tutorial"],
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-20T14:45:00Z",
                "word_count": 1250,
                "excerpt": "This article covers the fundamental concepts of Python programming...",
                "read_status": "unread",
                "x": 0.5,
                "y": 0.3,
                "neighbors": ["documents/tech/advanced-python.md"],
            }
        }


class ArticleDetail(ArticleSummary):
    """Detailed article information including full content"""

    content: str = Field(..., description="Full markdown content")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "documents/tech/python-basics.md",
                "title": "Python Basics",
                "path": "documents/tech/python-basics.md",
                "topic": "programming",
                "tags": ["python", "tutorial"],
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-20T14:45:00Z",
                "word_count": 1250,
                "excerpt": "This article covers the fundamental concepts...",
                "read_status": "unread",
                "x": 0.5,
                "y": 0.3,
                "content": "# Python Basics\n\nThis article covers...",
            }
        }


class UpdateArticleRequest(BaseModel):
    """Request body for updating an article"""

    title: Optional[str] = Field(None, description="Updated title")
    topic: Optional[str] = Field(None, description="Updated topic")
    tags: Optional[List[str]] = Field(None, description="Updated tags")
    read_status: Optional[str] = Field(None, description="Updated read status")
    content: Optional[str] = Field(None, description="Updated markdown content")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Python Basics - Updated",
                "topic": "programming",
                "tags": ["python", "tutorial", "beginner"],
                "read_status": "read",
                "content": "# Python Basics - Updated\n\nThis is the updated content...",
            }
        }


class RebuildResponse(BaseModel):
    """Response for visualization rebuild endpoint"""

    status: str = Field(..., description="Status of the rebuild operation")
    article_count: int = Field(..., description="Number of articles processed")
    message: str = Field(..., description="Human-readable status message")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "article_count": 42,
                "message": "Successfully rebuilt visualization index with 42 articles",
            }
        }
