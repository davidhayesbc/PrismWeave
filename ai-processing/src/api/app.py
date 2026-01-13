"""
FastAPI application for PrismWeave visualization layer
"""

import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import List, Optional

import frontmatter
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import Config, load_config
from src.core.embedding_store import EmbeddingStore
from src.core.git_tracker import GitTracker
from src.core.layout import compute_fallback_layout, compute_layout_from_embeddings, compute_nearest_neighbors
from src.core.metadata_index import (
    INDEX_RELATIVE_PATH,
    ArticleMetadata,
    build_metadata_index,
    load_existing_index,
    save_index,
)
from src.taxonomy.artifacts import default_artifacts_dir, read_json
from src.taxonomy.store import TaxonomyStore, TaxonomyStoreConfig, default_taxonomy_sqlite_path

from .models import ArticleDetail, ArticleSummary, RebuildResponse, TaxonomyTagAssignment, UpdateArticleRequest

# Global state (initialized on startup)
config: Optional[Config] = None
documents_root: Optional[Path] = None
index_path: Optional[Path] = None
legacy_index_path: Optional[Path] = None
index_path_is_override: bool = False

logger = logging.getLogger("prismweave.ai.api")


def _initialize_state() -> None:
    """Initialize configuration and paths (used by FastAPI lifespan)."""
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
        logger.warning("Documents root does not exist: %s", documents_root)


@asynccontextmanager
async def lifespan(_: FastAPI):
    _initialize_state()

    # Emit a clear startup log so Docker logs show where this API is listening.
    api_port = int(os.environ.get("API_PORT", "8000"))
    api_host = os.environ.get("API_HOST", "0.0.0.0")
    display_host = "localhost" if api_host in {"0.0.0.0", "::"} else api_host

    logger.info(
        "Listening on http://%s:%s (local: http://%s:%s)",
        api_host,
        api_port,
        display_host,
        api_port,
    )
    logger.info("Health: http://%s:%s/health", display_host, api_port)
    yield


# Initialize FastAPI app with comprehensive OpenAPI documentation
app = FastAPI(
    title="PrismWeave Visualization API",
    description="""
    # PrismWeave Visualization API
    
    HTTP API for PrismWeave document visualization and management.
    
    ## Features
    
    - **Article Management**: CRUD operations for captured documents
    - **Visualization**: 2D graph visualization with semantic embeddings
    - **Metadata**: Rich metadata extraction and indexing
    - **Search**: Semantic search capabilities
    
    ## Endpoints
    
    - `/articles` - List all articles with metadata
    - `/articles/{id}` - Get, update, or delete a specific article
    - `/visualization/rebuild` - Rebuild the visualization index
    - `/health` - Health check endpoint
    
    ## Data Flow
    
    1. Articles are captured via browser extension
    2. Metadata is extracted and indexed
    3. Embeddings are generated for semantic similarity
    4. 2D coordinates are computed for visualization
    5. Frontend displays interactive graph
    """,
    version="0.1.0",
    lifespan=lifespan,
    contact={
        "name": "PrismWeave Team",
        "url": "https://github.com/davidhayesbc/PrismWeave",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=[
        {
            "name": "root",
            "description": "API root and information endpoints",
        },
        {
            "name": "health",
            "description": "Health check and status monitoring",
        },
        {
            "name": "articles",
            "description": "Article management operations (CRUD)",
        },
        {
            "name": "visualization",
            "description": "Visualization index and rebuild operations",
        },
    ],
)

# Add CORS middleware for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


def _load_taxonomy_enrichment(
    *,
    docs_root: Path,
    article_ids: List[str],
) -> dict[str, dict[str, object]]:
    """Best-effort taxonomy enrichment for a set of articles.

    Returns a mapping: article_id -> enrichment dict containing taxonomy fields.
    Never raises; failures degrade to an empty mapping.
    """

    try:
        sqlite_path = default_taxonomy_sqlite_path(docs_root)
        if not sqlite_path.exists():
            return {}

        store = TaxonomyStore(TaxonomyStoreConfig(sqlite_path=sqlite_path))
        # Initialize is safe/cheap; ensures tables exist if the file is present.
        store.initialize()

        # Cluster membership comes from taxonomy artifacts (clusters.json)
        artifacts_dir = default_artifacts_dir(docs_root)
        clusters_path = artifacts_dir / "clusters.json"
        article_to_cluster: dict[str, str] = {}
        if clusters_path.exists():
            try:
                clusters_payload = read_json(clusters_path) or []
                if isinstance(clusters_payload, list):
                    for cluster in clusters_payload:
                        if not isinstance(cluster, dict):
                            continue
                        cluster_id = str(cluster.get("id", "")).strip()
                        if not cluster_id:
                            continue
                        for aid in cluster.get("article_ids") or []:
                            if aid:
                                raw_id = str(aid)
                                article_to_cluster[raw_id] = cluster_id
                                # Also map absolute paths back to repo-relative paths when possible.
                                # The taxonomy pipeline historically used absolute file paths as ids,
                                # but the visualization index uses docs-root-relative paths.
                                try:
                                    p = Path(raw_id)
                                    if p.is_absolute():
                                        rel = p.resolve().relative_to(docs_root.resolve()).as_posix()
                                        article_to_cluster[rel] = cluster_id
                                except Exception:
                                    pass
            except Exception:
                # Artifacts are optional.
                pass

        # Cluster -> category/subcategory mapping and category names from SQLite.
        cluster_category_map = store.get_cluster_category_map()
        category_map = store.get_category_map()

        # Tag assignments and tag name lookup from SQLite.
        # Be resilient to article_id format differences between systems (relative vs absolute).
        expanded_article_ids: list[str] = []
        absolute_by_canonical: dict[str, str] = {}
        for canonical_id in article_ids:
            expanded_article_ids.append(canonical_id)
            try:
                abs_id = (docs_root / canonical_id).resolve()
                absolute_by_canonical[canonical_id] = str(abs_id)
                expanded_article_ids.append(str(abs_id))
            except Exception:
                continue

        # Deduplicate while keeping order.
        seen: set[str] = set()
        expanded_article_ids = [x for x in expanded_article_ids if not (x in seen or seen.add(x))]

        assignments_by_article = store.get_article_tags_for_articles(expanded_article_ids)
        tag_map = store.get_tag_map()

        enrichment: dict[str, dict[str, object]] = {}
        for article_id in article_ids:
            cluster_id = article_to_cluster.get(article_id)
            category_id = None
            subcategory_id = None
            if cluster_id and cluster_id in cluster_category_map:
                category_id, subcategory_id = cluster_category_map.get(cluster_id, (None, None))

            category_name = category_map.get(category_id).name if category_id and category_id in category_map else None
            subcategory_name = (
                category_map.get(subcategory_id).name if subcategory_id and subcategory_id in category_map else None
            )

            raw_assignments = assignments_by_article.get(article_id, [])
            if not raw_assignments:
                alt = absolute_by_canonical.get(article_id)
                if alt:
                    raw_assignments = assignments_by_article.get(alt, [])
            tag_assignments: list[TaxonomyTagAssignment] = []
            tag_names: list[str] = []
            for a in raw_assignments:
                tag = tag_map.get(a.tag_id)
                name = tag.name if tag else a.tag_id
                tag_assignments.append(TaxonomyTagAssignment(id=a.tag_id, name=name, confidence=float(a.confidence)))
                tag_names.append(name)

            enrichment[article_id] = {
                "taxonomy_cluster_id": cluster_id,
                "taxonomy_category_id": category_id,
                "taxonomy_category": category_name,
                "taxonomy_subcategory_id": subcategory_id,
                "taxonomy_subcategory": subcategory_name,
                "taxonomy_tag_assignments": tag_assignments,
                "taxonomy_tags": tag_names,
            }

        return enrichment
    except Exception:
        return {}


def _apply_layout_to_index(index: dict[str, ArticleMetadata], docs_root: Path) -> int:
    """Populate x/y and neighbors for the given index.

    Prefers embeddings when available; otherwise falls back to a deterministic
    grid layout. Always returns a coordinate mapping for every index entry.
    """

    # Base layout is always available.
    layout_coords = compute_fallback_layout(index.keys())

    # Overlay embedding-derived layout when possible.
    try:
        if config is not None:
            git_tracker = GitTracker(docs_root, config)
            store = EmbeddingStore(config, git_tracker)

            article_embeddings: dict[str, list[float]] = {}
            for article in index.values():
                try:
                    vector = store.get_article_embedding(docs_root / article.path)
                    if vector is not None:
                        article_embeddings[article.id] = list(vector)
                except Exception:
                    continue

            if article_embeddings:
                embedding_coords = compute_layout_from_embeddings(article_embeddings)
                layout_coords.update(embedding_coords)
    except Exception:
        # Embeddings are an enhancement; visualization should still work.
        pass

    neighbors_map = compute_nearest_neighbors(layout_coords, k=5)

    updated = 0
    for article_id, article in index.items():
        coords = layout_coords.get(article_id)
        if coords is None:
            continue
        article.x = float(coords[0])
        article.y = float(coords[1])
        article.neighbors = neighbors_map.get(article_id, [])
        updated += 1

    return updated


@app.get(
    "/",
    tags=["root"],
    summary="API Information",
    description="Get API metadata and available endpoints",
    response_description="API information and endpoint links",
)
async def root():
    """
    Get API information and available endpoints.

    Returns basic API metadata including version, available endpoints,
    and links to API documentation.
    """
    return {
        "name": "PrismWeave Visualization API",
        "version": "0.1.0",
        "description": "HTTP API for PrismWeave document visualization and management",
        "documentation": "/docs",
        "redoc": "/redoc",
        "openapi_schema": "/openapi.json",
        "endpoints": {
            "health": "/health",
            "articles_list": "/articles",
            "article_detail": "/articles/{id}",
            "article_update": "PUT /articles/{id}",
            "article_delete": "DELETE /articles/{id}",
            "visualization_rebuild": "/visualization/rebuild",
        },
    }


@app.get(
    "/health",
    tags=["health"],
    summary="Health Check",
    description="Check API health status and resource availability",
    response_description="Health status with detailed diagnostics",
)
async def health():
    """
    Health check endpoint for container orchestrators and monitoring.

    Returns detailed health status including:
    - Overall service status (healthy/degraded)
    - Documents root directory status
    - Index file availability and status
    - Service metadata (version, name)

    This endpoint is used by Docker health checks and load balancers
    to determine if the service is ready to accept requests.
    """

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


@app.get(
    "/articles",
    response_model=List[ArticleSummary],
    tags=["articles"],
    summary="List All Articles",
    description="Get a list of all articles with metadata and visualization coordinates",
    response_description="List of article summaries with metadata and coordinates",
)
async def get_articles():
    """
    Get list of all articles with metadata and visualization coordinates.

    Returns a comprehensive list of all articles in the system, each containing:

    **Metadata:**
    - Article ID (typically file path)
    - Title and topic
    - Tags for categorization
    - Word count and excerpt
    - Creation and update timestamps
    - Read status (read/unread)

    **Visualization Data:**
    - X/Y coordinates for 2D graph visualization
    - Neighbor IDs for drawing edges between related articles

    The coordinates are computed from semantic embeddings when available,
    falling back to a deterministic grid layout otherwise.

    **Example Response:**
    ```json
    [
      {
        "id": "documents/tech/python-basics.md",
        "title": "Python Basics",
        "topic": "programming",
        "tags": ["python", "tutorial"],
        "x": 0.5,
        "y": 0.3,
        "neighbors": ["documents/tech/advanced-python.md"]
      }
    ]
    ```
    """
    selected_index_path = _select_readable_index_path()

    # Load the metadata index
    index = load_existing_index(selected_index_path)

    if not index:
        return []

    # Ensure we always have a usable layout for visualization.
    # Older indexes (or metadata-only rebuilds) can have null x/y/neighbors.
    if documents_root is not None and any(a.x is None or a.y is None for a in index.values()):
        try:
            _apply_layout_to_index(index, documents_root)
        except Exception:
            # Fall back to returning whatever we have.
            pass

    # Convert to response models
    index_values = list(index.values())
    article_ids = [a.id for a in index_values]
    taxonomy = _load_taxonomy_enrichment(docs_root=documents_root, article_ids=article_ids) if documents_root else {}

    articles: List[ArticleSummary] = []
    for article in index_values:
        summary = _article_metadata_to_summary(article)
        enrich = taxonomy.get(article.id)
        if enrich:
            summary.taxonomy_cluster_id = enrich.get("taxonomy_cluster_id")  # type: ignore[assignment]
            summary.taxonomy_category_id = enrich.get("taxonomy_category_id")  # type: ignore[assignment]
            summary.taxonomy_category = enrich.get("taxonomy_category")  # type: ignore[assignment]
            summary.taxonomy_subcategory_id = enrich.get("taxonomy_subcategory_id")  # type: ignore[assignment]
            summary.taxonomy_subcategory = enrich.get("taxonomy_subcategory")  # type: ignore[assignment]
            summary.taxonomy_tag_assignments = enrich.get("taxonomy_tag_assignments") or []  # type: ignore[assignment]
            summary.taxonomy_tags = enrich.get("taxonomy_tags") or []  # type: ignore[assignment]
        articles.append(summary)

    return articles


@app.get(
    "/articles/{article_id:path}",
    response_model=ArticleDetail,
    tags=["articles"],
    summary="Get Article Details",
    description="Get detailed information for a specific article including full markdown content",
    response_description="Article details with full content and metadata",
    responses={
        200: {
            "description": "Article found and returned successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "documents/tech/python-basics.md",
                        "title": "Python Basics",
                        "content": "# Python Basics\n\nThis article covers...",
                        "word_count": 1250,
                    }
                }
            },
        },
        404: {"description": "Article not found"},
        500: {"description": "Server error reading article"},
    },
)
async def get_article(article_id: str):
    """
    Get detailed information for a specific article including full content.

    Retrieves complete article data including all metadata fields and the
    full markdown content. Useful for displaying article details in the UI
    or for editing operations.

    **Path Parameters:**
    - `article_id`: Article identifier (typically the relative file path)
      Example: `documents/tech/python-basics.md`

    **Returns:**
    - All metadata fields (same as ArticleSummary)
    - Full markdown content with frontmatter

    **Error Cases:**
    - 404: Article not found in index or file missing
    - 500: Permission denied or file read error
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

    taxonomy = _load_taxonomy_enrichment(docs_root=documents_root, article_ids=[article.id]) if documents_root else {}
    enrich = taxonomy.get(article.id)

    # Create response model
    detail = ArticleDetail(
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

    if enrich:
        detail.taxonomy_cluster_id = enrich.get("taxonomy_cluster_id")  # type: ignore[assignment]
        detail.taxonomy_category_id = enrich.get("taxonomy_category_id")  # type: ignore[assignment]
        detail.taxonomy_category = enrich.get("taxonomy_category")  # type: ignore[assignment]
        detail.taxonomy_subcategory_id = enrich.get("taxonomy_subcategory_id")  # type: ignore[assignment]
        detail.taxonomy_subcategory = enrich.get("taxonomy_subcategory")  # type: ignore[assignment]
        detail.taxonomy_tag_assignments = enrich.get("taxonomy_tag_assignments") or []  # type: ignore[assignment]
        detail.taxonomy_tags = enrich.get("taxonomy_tags") or []  # type: ignore[assignment]

    return detail


@app.put(
    "/articles/{article_id:path}",
    response_model=ArticleDetail,
    tags=["articles"],
    summary="Update Article",
    description="Update an article's metadata and/or content",
    response_description="Updated article with all changes applied",
    responses={
        200: {"description": "Article updated successfully"},
        404: {"description": "Article not found"},
        500: {"description": "Server error updating article"},
    },
)
async def update_article(article_id: str, update_request: UpdateArticleRequest):
    """
    Update an article's metadata and/or content.

    Allows partial updates to any combination of fields. Only provided
    fields will be updated; others remain unchanged.

    **Path Parameters:**
    - `article_id`: Article identifier (file path)

    **Request Body Fields (all optional):**
    - `title`: Update article title
    - `topic`: Update topic/category
    - `tags`: Update tag list (replaces existing)
    - `read_status`: Update read status (read/unread)
    - `content`: Update markdown content (triggers word recount)

    **Behavior:**
    - Updates markdown file on disk with new frontmatter/content
    - Updates metadata index
    - Automatically marks article as 'read' if not already
    - Does NOT automatically recompute embeddings (call rebuild for that)

    **Returns:**
    - Complete updated ArticleDetail

    **Example Request:**
    ```json
    {
      "title": "Python Basics - Updated",
      "tags": ["python", "tutorial", "beginner"],
      "read_status": "read"
    }
    ```
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

    taxonomy = _load_taxonomy_enrichment(docs_root=documents_root, article_ids=[article.id]) if documents_root else {}
    enrich = taxonomy.get(article.id)

    # Return the updated article
    detail = ArticleDetail(
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

    if enrich:
        detail.taxonomy_cluster_id = enrich.get("taxonomy_cluster_id")  # type: ignore[assignment]
        detail.taxonomy_category_id = enrich.get("taxonomy_category_id")  # type: ignore[assignment]
        detail.taxonomy_category = enrich.get("taxonomy_category")  # type: ignore[assignment]
        detail.taxonomy_subcategory_id = enrich.get("taxonomy_subcategory_id")  # type: ignore[assignment]
        detail.taxonomy_subcategory = enrich.get("taxonomy_subcategory")  # type: ignore[assignment]
        detail.taxonomy_tag_assignments = enrich.get("taxonomy_tag_assignments") or []  # type: ignore[assignment]
        detail.taxonomy_tags = enrich.get("taxonomy_tags") or []  # type: ignore[assignment]

    return detail


@app.delete(
    "/articles/{article_id:path}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["articles"],
    summary="Delete Article",
    description="Permanently delete an article and all associated data",
    response_description="Article deleted successfully (no content)",
    responses={
        204: {"description": "Article deleted successfully"},
        404: {"description": "Article not found"},
        500: {"description": "Server error deleting article"},
    },
)
async def delete_article(article_id: str):
    """
    Permanently delete an article and all associated data.

    Removes all traces of the article from the system:

    **Deletion Steps:**
    1. Deletes markdown file from disk
    2. Removes entry from metadata index
    3. Removes embeddings from Chroma vector database

    **Path Parameters:**
    - `article_id`: Article identifier (file path)

    **Returns:**
    - 204 No Content on success

    **Warning:**
    This operation is permanent and cannot be undone.
    Make sure to back up important articles before deletion.

    **Error Cases:**
    - 404: Article not found in index
    - 500: File system or database error
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
        logger.warning("Failed to remove from Chroma: %s", e)

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


@app.post(
    "/visualization/rebuild",
    response_model=RebuildResponse,
    tags=["visualization"],
    summary="Rebuild Visualization Index",
    description="Rebuild the entire visualization index with metadata and layout",
    response_description="Rebuild status with article count",
    responses={
        200: {
            "description": "Index rebuilt successfully",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "article_count": 42,
                        "message": "Successfully rebuilt visualization index with 42 articles",
                    }
                }
            },
        },
        404: {"description": "Documents directory not found"},
        500: {"description": "Server error during rebuild"},
    },
)
async def rebuild_visualization():
    """
    Rebuild the entire visualization index with metadata and layout.

    Performs a complete rebuild of the visualization index, equivalent to
    running the `visualize build-index` CLI command.

    **Rebuild Process:**
    1. Scans documents directory for all markdown files
    2. Extracts metadata from frontmatter
    3. Computes 2D layout coordinates:
       - Uses semantic embeddings when available
       - Falls back to deterministic grid layout
    4. Computes nearest neighbors for each article
    5. Saves updated index to disk

    **When to Use:**
    - After adding many new articles
    - After updating embeddings
    - When visualization appears incorrect
    - To refresh metadata from updated files

    **Performance:**
    - Processing time scales with document count
    - Embedding generation (if needed) is the slowest step
    - Typically takes 1-5 seconds for 100 documents

    **Returns:**
    - Status (success/error)
    - Number of articles processed
    - Human-readable status message
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
        # Rebuild the metadata index.
        index = build_metadata_index(documents_root, index_path)

        # Always compute a layout (embeddings if available; deterministic fallback otherwise)
        _apply_layout_to_index(index, documents_root)

        save_index(index, index_path)

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

    port = int(os.environ.get("API_PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
