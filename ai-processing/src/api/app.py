"""
FastAPI application for PrismWeave visualization layer
"""

import os
import sys
from pathlib import Path
from typing import List, Optional

import frontmatter
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import Config, load_config
from src.core.embedding_store import EmbeddingStore
from src.core.git_tracker import GitTracker
from src.core.metadata_index import (
    INDEX_RELATIVE_PATH,
    ArticleMetadata,
    build_metadata_index,
    load_existing_index,
    save_index,
)

from .models import ArticleDetail, ArticleSummary, RebuildResponse, UpdateArticleRequest

# Initialize FastAPI app
app = FastAPI(
    title="PrismWeave Visualization API",
    description="HTTP API for PrismWeave document visualization and management",
    version="0.1.0",
)

# Add CORS middleware for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state (initialized on startup)
config: Optional[Config] = None
documents_root: Optional[Path] = None
index_path: Optional[Path] = None
legacy_index_path: Optional[Path] = None
index_path_is_override: bool = False


@app.on_event("startup")
async def startup_event():
    """Initialize configuration and paths on startup"""
    global config, documents_root, index_path, legacy_index_path, index_path_is_override

    # Load configuration
    config = load_config()
    documents_root = Path(os.environ.get("DOCUMENTS_PATH", config.mcp.paths.documents_root)).expanduser().resolve()
    legacy_index_path = documents_root / INDEX_RELATIVE_PATH

    configured_index_path = os.environ.get("ARTICLE_INDEX_PATH") or os.environ.get("INDEX_PATH")
    if configured_index_path:
        index_path_is_override = True
        index_path = Path(configured_index_path).expanduser().resolve()
    else:
        index_path_is_override = False
        index_path = legacy_index_path

    if not documents_root.exists():
        print(f"Warning: Documents root does not exist: {documents_root}", file=sys.stderr)


def _path_status(path: Path) -> str:
    """Return a stable status for a path without throwing."""

    try:
        path.stat()
        return "ok"
    except FileNotFoundError:
        return "missing"
    except PermissionError:
        return "denied"
    except OSError:
        return "error"


def _index_candidates() -> List[Path]:
    candidates: List[Path] = []
    if index_path is not None:
        candidates.append(index_path)
    # Only fall back to the legacy index path when no override is configured.
    # This avoids raising errors due to permission-denied on bind mounts when the
    # intended (override) path is merely missing.
    if (not index_path_is_override) and legacy_index_path is not None and legacy_index_path not in candidates:
        candidates.append(legacy_index_path)
    return candidates


def _select_readable_index_path() -> Path:
    for candidate in _index_candidates():
        path_state = _path_status(candidate)
        if path_state == "ok":
            return candidate
        if path_state == "denied":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=(
                    "Permission denied reading article index. "
                    f"Index path: {candidate}. "
                    "Fix file ownership/permissions on the host (e.g. chown/chmod) "
                    "or set INDEX_PATH/ARTICLE_INDEX_PATH to a writable location inside the container."
                ),
            )

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Article index not found. Run 'visualize build-index' (or POST /visualization/rebuild) first.",
    )


def _ensure_writable_index_path(target: Path) -> None:
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Cannot create/write article index directory due to permissions. "
                f"Index path: {target} ({e}). "
                "Set INDEX_PATH/ARTICLE_INDEX_PATH to a writable location."
            ),
        )
    except OSError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to prepare index directory {target.parent}: {e}",
        )


def _article_metadata_to_summary(article: ArticleMetadata) -> ArticleSummary:
    """Convert ArticleMetadata to ArticleSummary Pydantic model"""
    return ArticleSummary(
        id=article.id,
        title=article.title,
        path=article.path,
        topic=article.topic,
        tags=article.tags,
        created_at=article.created_at,
        updated_at=article.updated_at,
        word_count=article.word_count,
        excerpt=article.excerpt,
        read_status=article.read_status,
        x=article.x,
        y=article.y,
        neighbors=article.neighbors,
    )


@app.get("/", tags=["root"])
async def root():
    """Root endpoint with API information"""
    return {
        "name": "PrismWeave Visualization API",
        "version": "0.1.0",
        "endpoints": {
            "articles": "/articles",
            "article_detail": "/articles/{id}",
            "rebuild": "/visualization/rebuild",
        },
    }


@app.get("/health", tags=["health"])
async def health():
    """Health check endpoint for container orchestrators."""

    documents_root_value = str(documents_root) if documents_root is not None else None
    documents_root_status = _path_status(documents_root) if documents_root is not None else "uninitialized"
    index_candidates = [str(p) for p in _index_candidates()]
    index_candidate_statuses = {str(p): _path_status(p) for p in _index_candidates()}

    overall_status = "healthy" if documents_root_status in {"ok", "missing"} else "degraded"

    return {
        "status": overall_status,
        "service": "prismweave-visualization-api",
        "version": "0.1.0",
        "documents_root": documents_root_value,
        "documents_root_status": documents_root_status,
        "index_candidates": index_candidates,
        "index_candidate_statuses": index_candidate_statuses,
    }


@app.get("/articles", response_model=List[ArticleSummary], tags=["articles"])
async def get_articles():
    """
    Get list of all articles with metadata and visualization coordinates.

    Returns a list of article summaries including:
    - Basic metadata (id, title, topic, tags, etc.)
    - Visualization coordinates (x, y) if available
    - Optional neighbor IDs for drawing edges
    """
    selected_index_path = _select_readable_index_path()

    # Load the metadata index
    index = load_existing_index(selected_index_path)

    if not index:
        return []

    # Convert to response models
    articles = [_article_metadata_to_summary(article) for article in index.values()]

    return articles


@app.get("/articles/{article_id:path}", response_model=ArticleDetail, tags=["articles"])
async def get_article(article_id: str):
    """
    Get detailed information for a specific article including full content.

    Args:
        article_id: Article identifier (typically the file path)

    Returns:
        ArticleDetail with metadata and full markdown content
    """
    selected_index_path = _select_readable_index_path()

    # Load the metadata index
    index = load_existing_index(selected_index_path)

    # Find the article
    article = index.get(article_id)
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Article not found: {article_id}",
        )

    # Load the full markdown content
    article_path = documents_root / article.path
    article_path_state = _path_status(article_path)
    if article_path_state == "missing":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Article file not found: {article.path}",
        )
    if article_path_state == "denied":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Permission denied reading article file: {article.path}",
        )
    if article_path_state != "ok":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to access article file: {article.path}",
        )

    try:
        with open(article_path, encoding="utf-8") as f:
            content = f.read()
    except (OSError, UnicodeDecodeError) as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to read article: {e}",
        )

    # Create response model
    return ArticleDetail(
        id=article.id,
        title=article.title,
        path=article.path,
        topic=article.topic,
        tags=article.tags,
        created_at=article.created_at,
        updated_at=article.updated_at,
        word_count=article.word_count,
        excerpt=article.excerpt,
        read_status=article.read_status,
        x=article.x,
        y=article.y,
        neighbors=article.neighbors,
        content=content,
    )


@app.put("/articles/{article_id:path}", response_model=ArticleDetail, tags=["articles"])
async def update_article(article_id: str, update_request: UpdateArticleRequest):
    """
    Update an article's metadata and/or content.

    Args:
        article_id: Article identifier (typically the file path)
        update_request: Fields to update (all optional)

    Returns:
        Updated ArticleDetail

    Notes:
        - Updates markdown file on disk with new frontmatter/content
        - Updates metadata index
        - Automatically marks article as 'read' if not already
        - Does NOT automatically recompute embeddings/layout
    """
    selected_index_path = _select_readable_index_path()

    # Load the metadata index
    index = load_existing_index(selected_index_path)

    # Find the article
    article = index.get(article_id)
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Article not found: {article_id}",
        )

    # Load the markdown file
    article_path = documents_root / article.path
    article_path_state = _path_status(article_path)
    if article_path_state == "missing":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Article file not found: {article.path}",
        )
    if article_path_state == "denied":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Permission denied reading article file: {article.path}",
        )
    if article_path_state != "ok":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to access article file: {article.path}",
        )

    try:
        post = frontmatter.load(article_path)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to read article: {e}",
        )

    # Update fields that were provided
    if update_request.title is not None:
        post["title"] = update_request.title
        article.title = update_request.title

    if update_request.topic is not None:
        post["topic"] = update_request.topic
        article.topic = update_request.topic

    if update_request.tags is not None:
        post["tags"] = update_request.tags
        article.tags = update_request.tags

    if update_request.read_status is not None:
        article.read_status = update_request.read_status

    if update_request.content is not None:
        post.content = update_request.content
        # Recount words
        article.word_count = len(update_request.content.split())

    # Mark as read if not already
    if article.read_status == "unread":
        article.read_status = "read"

    # Write the updated markdown file
    try:
        with open(article_path, "w", encoding="utf-8") as f:
            f.write(frontmatter.dumps(post))
    except (OSError, UnicodeEncodeError) as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to write article: {e}",
        )

    # Update the index
    index[article_id] = article
    if index_path is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API not properly initialized",
        )
    _ensure_writable_index_path(index_path)
    save_index(index, index_path)

    # Return the updated article
    return ArticleDetail(
        id=article.id,
        title=article.title,
        path=article.path,
        topic=article.topic,
        tags=article.tags,
        created_at=article.created_at,
        updated_at=article.updated_at,
        word_count=article.word_count,
        excerpt=article.excerpt,
        read_status=article.read_status,
        x=article.x,
        y=article.y,
        neighbors=article.neighbors,
        content=post.content,
    )


@app.delete("/articles/{article_id:path}", status_code=status.HTTP_204_NO_CONTENT, tags=["articles"])
async def delete_article(article_id: str):
    """
    Delete an article (removes markdown file, metadata index entry, and Chroma records).

    Args:
        article_id: Article identifier (typically the file path)

    Returns:
        204 No Content on success
    """
    selected_index_path = _select_readable_index_path()

    # Load the metadata index
    index = load_existing_index(selected_index_path)

    # Find the article
    article = index.get(article_id)
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Article not found: {article_id}",
        )

    # Delete the markdown file
    article_path = documents_root / article.path
    if _path_status(article_path) == "ok":
        try:
            article_path.unlink()
        except OSError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete article file: {e}",
            )

    # Remove from Chroma
    try:
        git_tracker = GitTracker(documents_root, config)
        store = EmbeddingStore(config, git_tracker)
        store.remove_file_documents(article_path)
    except Exception as e:
        # Log but don't fail if Chroma removal fails
        print(f"Warning: Failed to remove from Chroma: {e}", file=sys.stderr)

    # Remove from index
    del index[article_id]
    if index_path is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API not properly initialized",
        )
    _ensure_writable_index_path(index_path)
    save_index(index, index_path)

    return None


@app.post("/visualization/rebuild", response_model=RebuildResponse, tags=["visualization"])
async def rebuild_visualization():
    """
    Rebuild the visualization index (metadata + layout).

    Triggers the same process as 'visualize build-index' CLI command:
    - Scans documents directory for markdown files
    - Extracts metadata and computes layout
    - Updates the metadata index

    Returns:
        RebuildResponse with status and article count
    """
    if documents_root is None or index_path is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API not properly initialized",
        )

    if not documents_root.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Documents root not found: {documents_root}",
        )

    try:
        _ensure_writable_index_path(index_path)
        # Rebuild the metadata index (this also computes layout if embeddings exist)
        index = build_metadata_index(documents_root, index_path)

        return RebuildResponse(
            status="success",
            article_count=len(index),
            message=f"Successfully rebuilt visualization index with {len(index)} articles",
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to rebuild visualization: {e}",
        )


# Entry point for running with uvicorn
def main():
    """Run the API server"""
    import uvicorn

    port = int(os.environ.get("API_PORT", "8001"))
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
