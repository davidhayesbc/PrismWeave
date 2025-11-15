"""
PrismWeave MCP Server

Main MCP server implementation using FastMCP for document management and AI processing.
"""

import logging
from typing import Any

from fastmcp import FastMCP
from starlette.middleware.cors import CORSMiddleware

from prismweave_mcp.schemas.requests import (
    CommitToGitRequest,
    CreateDocumentRequest,
    GenerateEmbeddingsRequest,
    GenerateTagsRequest,
    GetDocumentRequest,
    ListDocumentsRequest,
    SearchDocumentsRequest,
    UpdateDocumentRequest,
)
from prismweave_mcp.tools.documents import DocumentTools
from prismweave_mcp.tools.git import GitTools
from prismweave_mcp.tools.processing import ProcessingTools
from prismweave_mcp.tools.search import SearchTools
from src.core.config import load_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("PrismWeave Document Manager")

# Initialize configuration and tools
config = load_config()
search_tools = SearchTools(config)
document_tools = DocumentTools(config)
processing_tools = ProcessingTools(config)
git_tools = GitTools(config)

# Track initialization
_initialized = False


async def ensure_initialized():
    """Ensure async components are initialized"""
    global _initialized
    if not _initialized:
        try:
            await search_tools.initialize()
            logger.info("Search tools initialized")
        except Exception as e:
            logger.warning(f"Search tools initialization failed: {e}")
        _initialized = True


@mcp.tool()
async def search_documents(
    query: str,
    max_results: int = config.mcp.search.max_results,
    similarity_threshold: float = config.mcp.search.similarity_threshold,
    tags: list[str] | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    include_generated: bool = True,
    include_captured: bool = True,
    category: str | None = None,
) -> dict[str, Any]:
    """Search for documents by semantic similarity.

    Use this tool when the caller asks to *find* or *search for* documents related to a
    natural-language query. The tool performs vector search and optional metadata filtering.

    Parameters:
        query (str, required): Natural-language text describing what to look for.
            Example: "summaries of Ollama model management".
        max_results (int, optional): Maximum number of hits to return. Defaults to
            ``config.mcp.search.max_results`` (20 in the standard configuration).
        similarity_threshold (float, optional): Minimum cosine similarity the match must
            meet. Accept values between 0 and 1. Defaults to
            ``config.mcp.search.similarity_threshold`` (0.45 by default).
        tags (list[str], optional): Only return documents containing *all* of these tags.
        date_from (str, optional): ISO-8601 date (``YYYY-MM-DD``). Results earlier than this
            date are excluded. Currently reserved for future filtering support.
        date_to (str, optional): ISO-8601 date (``YYYY-MM-DD``). Results after this date are
            excluded. Currently reserved for future filtering support.
        include_generated (bool, optional): When False, prefer captured documents. This flag
            is accepted for forward compatibility and presently has no effect.
        include_captured (bool, optional): When False, prefer generated documents. This flag
            is accepted for forward compatibility and presently has no effect.
        category (str, optional): Restrict results to a single category when available.

    Returns:
        dict[str, Any]: JSON-serializable payload containing matched documents, similarity
        scores, and the original query.
    """
    await ensure_initialized()
    request = SearchDocumentsRequest(
        query=query,
        max_results=max_results,
        similarity_threshold=similarity_threshold,
    )
    return await search_tools.search_documents(request)


@mcp.tool()
async def get_document(
    document_id: str | None = None,
    path: str | None = None,
    include_content: bool = True,
) -> dict[str, Any]:
    """Retrieve a single document for reading or inspection.

    Use this tool when the caller references a specific document they already know about
    (usually after ``search_documents`` or ``list_documents``).

    Parameters:
        document_id (str, required): Stable identifier stored in the document frontmatter.
            Provide this whenever available for deterministic retrieval.
        path (str, optional): Repository-relative path (e.g., ``documents/my-note.md``).
            Reserved for future support; current implementation requires ``document_id``.
        include_content (bool, optional): When False, omit the Markdown body and return only
            metadata. Defaults to True.

    Returns:
        dict[str, Any]: Document metadata and, when requested, Markdown content.
    """
    await ensure_initialized()
    request = GetDocumentRequest(
        document_id=document_id,
        include_content=include_content,
    )
    return await search_tools.get_document(request)


@mcp.tool()
async def list_documents(
    category: str | None = None,
    tags: list[str] | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    include_generated: bool = True,
    include_captured: bool = True,
    limit: int | None = None,
    offset: int = 0,
) -> dict[str, Any]:
    """Browse available documents without performing semantic ranking.

    Use this tool when the caller requests an overview or needs to iterate through
    documents by category or tag (for example, "show me all AI-generated documents").

    Parameters:
        category (str, optional): Restrict results to this category folder.
        tags (list[str], optional): Only return documents that contain all listed tags.
        date_from (str, optional): ISO-8601 date string. Reserved for future support.
        date_to (str, optional): ISO-8601 date string. Reserved for future support.
        include_generated (bool, optional): Future option to exclude generated documents.
            Accepted for compatibility; currently ignored.
        include_captured (bool, optional): Future option to exclude captured documents.
            Accepted for compatibility; currently ignored.
        limit (int, optional): Maximum number of entries to return. Defaults to the
            repository setting ``ListDocumentsRequest.limit`` (50 by default).
        offset (int, optional): Number of entries to skip for pagination. Defaults to 0.

    Returns:
        dict[str, Any]: Collection of document metadata plus total count statistics.
    """
    await ensure_initialized()
    request = ListDocumentsRequest(
        category=category,
        tags=tags,
        limit=limit,
        offset=offset,
    )
    return await search_tools.list_documents(request)


@mcp.tool()
async def get_document_metadata(
    document_id: str | None = None,
    path: str | None = None,
) -> dict[str, Any]:
    """Fetch metadata for a document while omitting the Markdown body.

    Use this tool when only frontmatter-derived fields are required (e.g., title, tags,
    timestamps) and the caller does not need the full content payload.

    Parameters:
        document_id (str, required): Unique identifier stored in frontmatter.
        path (str, optional): Placeholder for future path-based lookups (currently unused).

    Returns:
        dict[str, Any]: Metadata dictionary plus a success flag, or an error structure.
    """
    await ensure_initialized()
    request = GetDocumentRequest(
        document_id=document_id,
        include_content=False,
    )
    return await search_tools.get_document_metadata(request)


@mcp.tool()
async def create_document(
    title: str,
    content: str,
    category: str | None = None,
    tags: list[str] | None = None,
    metadata: dict[str, Any] | None = None,
    auto_process: bool = True,
    auto_commit: bool = False,
) -> dict[str, Any]:
    """Create and store a new Markdown document inside the generated collection.

    Use this after the caller supplies draft content that should be persisted.

    Parameters:
        title (str, required): Human-readable document title. Used to derive the filename.
        content (str, required): Markdown-formatted body text.
        category (str, optional): Category folder to place the document in. Defaults to the
            ``config.mcp.creation.default_category`` setting when omitted.
        tags (list[str], optional): Tags to include in frontmatter. Defaults to an empty list.
        metadata (dict[str, Any], optional): Additional frontmatter fields. Keys must be
            JSON-serializable.
        auto_process (bool, optional): When True (default), downstream workflows should
            enqueue tag and embedding generation.
        auto_commit (bool, optional): When True, follow-up automation should commit the
            created file to Git. Defaults to False.

    Returns:
        dict[str, Any]: Details about the newly created document, including its ID and path.
    """
    await ensure_initialized()
    request = CreateDocumentRequest(
        title=title,
        content=content,
        category=category,
        tags=tags,
        additional_metadata=metadata,
    )
    return await document_tools.create_document(request)


@mcp.tool()
async def update_document(
    document_id: str,
    title: str | None = None,
    content: str | None = None,
    tags: list[str] | None = None,
    category: str | None = None,
    additional_metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Modify an existing generated document.

    Use when the caller requests edits to content or frontmatter of a document that resides
    in the generated collection. Captured documents remain read-only.

    Parameters:
        document_id (str, required): Identifier of the generated document to update.
        title (str, optional): Replacement title.
        content (str, optional): Replacement Markdown body.
        tags (list[str], optional): Replacement tag list. Provide the full desired set.
        category (str, optional): Updated category destination.
        additional_metadata (dict[str, Any], optional): Frontmatter fields to merge with
            existing metadata.

    Returns:
        dict[str, Any]: Updated document representation or an error payload.
    """
    await ensure_initialized()
    request = UpdateDocumentRequest(
        document_id=document_id,
        title=title,
        content=content,
        tags=tags,
        category=category,
        additional_metadata=additional_metadata,
    )
    return await document_tools.update_document(request)


@mcp.tool()
async def generate_embeddings(
    document_id: str,
    model: str = "nomic-embed-text",
    force_regenerate: bool = False,
) -> dict[str, Any]:
    """Produce vector embeddings for semantic search and clustering.

    Use when downstream actions require updated embeddings (e.g., after updates) or when
    embeddings are missing.

    Parameters:
        document_id (str, required): Identifier of the document to embed.
        model (str, optional): Embedding model name compatible with the local Ollama setup.
            Defaults to ``"nomic-embed-text"``.
        force_regenerate (bool, optional): When True, re-create embeddings even if cached.
            Defaults to False.

    Returns:
        dict[str, Any]: Information about the embedding job and success status.
    """
    await ensure_initialized()
    request = GenerateEmbeddingsRequest(
        document_id=document_id,
        model=model,
        force_regenerate=force_regenerate,
    )
    return await processing_tools.generate_embeddings(request)


@mcp.tool()
async def generate_tags(
    document_id: str,
    max_tags: int = 5,
    force_regenerate: bool = False,
) -> dict[str, Any]:
    """Suggest topical tags for a document using the local AI pipeline.

    Use when the caller wants automatic tagging support for organization or search.

    Parameters:
        document_id (str, required): Identifier of the document to tag.
        max_tags (int, optional): Maximum number of tags to return. Defaults to 5.
        force_regenerate (bool, optional): When True, ignore cached tags and produce a fresh
            set. Defaults to False.

    Returns:
        dict[str, Any]: Collection of generated tags with confidence metadata if available.
    """
    await ensure_initialized()
    request = GenerateTagsRequest(
        document_id=document_id,
        max_tags=max_tags,
        force_regenerate=force_regenerate,
    )
    return await processing_tools.generate_tags(request)


@mcp.tool()
async def commit_to_git(
    commit_message: str,
    file_paths: list[str],
    push: bool = False,
) -> dict[str, Any]:
    """Create a Git commit containing document or metadata changes.

    Use this tool after writing or updating files when the caller explicitly asks to save or
    publish changes.

    Parameters:
        commit_message (str, required): Concise message describing the change.
        file_paths (list[str], required): Repository-relative paths to include in the commit.
        push (bool, optional): When True, push the resulting commit to the configured remote.
            Defaults to False; only enable when instructed.

    Returns:
        dict[str, Any]: Commit identifier, affected files, and optional push status.
    """
    await ensure_initialized()
    request = CommitToGitRequest(
        commit_message=commit_message,
        file_paths=file_paths,
        push=push,
    )
    return await git_tools.commit_to_git(request)


def main():
    """Main entry point for the MCP server"""
    import argparse

    parser = argparse.ArgumentParser(description="PrismWeave MCP Server")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host to bind to")
    parser.add_argument(
        "--transport",
        type=str,
        default="sse",
        choices=["sse", "stdio"],
        help="Transport type (default: sse for HTTP server)",
    )
    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)

    logger.info("Starting PrismWeave MCP Server")
    logger.info(f"Transport: {args.transport}")
    logger.info(f"Debug mode: {args.debug}")

    if args.transport == "sse":
        logger.info(f"HTTP Server: http://{args.host}:{args.port}")
        logger.info(f"SSE endpoint: http://{args.host}:{args.port}/sse")
        # Run with SSE transport (HTTP server) with CORS enabled for Inspector
        # CORS configuration for MCP Inspector
        uvicorn_config = {
            "app": None,  # Will be set by FastMCP
            "host": args.host,
            "port": args.port,
        }

        # Use uvicorn_config to add CORS headers
        from starlette.middleware import Middleware

        middleware = [
            Middleware(
                CORSMiddleware,
                allow_origins=["http://localhost:6274", "http://127.0.0.1:6274", "*"],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )
        ]

        mcp.run(
            transport="sse",
            host=args.host,
            port=args.port,
            middleware=middleware,
        )
    else:
        logger.info("Running with stdio transport")
        # Run with stdio transport
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
