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
    """
    Search documents using semantic search with optional filters.

    Args:
        query: Search query text
        max_results: Maximum number of results to return (default: 20)
        similarity_threshold: Minimum similarity score 0-1 (default: 0.6)
        tags: Filter by tags
        date_from: Filter documents from this date (ISO format)
        date_to: Filter documents to this date (ISO format)
        include_generated: Include generated documents (default: True)
        include_captured: Include captured documents (default: True)
        category: Filter by category

    Returns:
        Search results with documents, scores, and snippets
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
    """
    Get a document by ID or path.

    Args:
        document_id: Document ID
        path: Document path (alternative to document_id)
        include_content: Include full document content (default: True)

    Returns:
        Document with metadata and optionally content
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
    """
    List documents with optional filters.

    Args:
        category: Filter by category
        tags: Filter by tags
        date_from: Filter documents from this date (ISO format)
        date_to: Filter documents to this date (ISO format)
        include_generated: Include generated documents (default: True)
        include_captured: Include captured documents (default: True)
        limit: Maximum number of documents to return
        offset: Number of documents to skip (default: 0)

    Returns:
        List of documents with metadata
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
    """
    Get document metadata without full content.

    Args:
        document_id: Document ID
        path: Document path (alternative to document_id)

    Returns:
        Document metadata only
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
    """
    Create a new generated document.

    Args:
        title: Document title
        content: Document content in markdown
        category: Document category
        tags: Document tags
        metadata: Additional metadata
        auto_process: Auto-generate tags and embeddings (default: True)
        auto_commit: Auto-commit to git (default: False)

    Returns:
        Created document information
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
    """
    Update an existing generated document.

    Args:
        document_id: Document ID to update
        title: New document title
        content: New document content
        tags: New tags
        category: New category
        additional_metadata: Additional metadata to update

    Returns:
        Updated document information
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
    """
    Generate embeddings for a document.

    Args:
        document_id: Document ID to generate embeddings for
        model: Embedding model to use (default: nomic-embed-text)
        force_regenerate: Force regeneration even if embeddings exist (default: False)

    Returns:
        Embedding generation results
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
    """
    Generate tags for a document using AI.

    Args:
        document_id: Document ID to generate tags for
        max_tags: Maximum number of tags to generate (default: 5)
        force_regenerate: Force regeneration even if tags exist (default: False)

    Returns:
        Generated tags
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
    """
    Commit changes to git repository.

    Args:
        commit_message: Commit message
        file_paths: List of file paths to commit
        push: Push to remote after commit (default: False)

    Returns:
        Commit results
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
