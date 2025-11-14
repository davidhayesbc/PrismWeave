"""
PrismWeave MCP Server

Main MCP server implementation for document management and AI processing.
Supports both stdio (for legacy clients) and HTTP/SSE transports.
"""

import logging
import sys
from typing import Any, Optional

from mcp.server.fastmcp import FastMCP

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


# Initialize FastMCP server with HTTP/SSE transport
mcp = FastMCP(
    "prismweave",
    instructions="""PrismWeave MCP Server provides document management and AI processing capabilities.
    
Available features:
- Semantic search across documents
- Document creation and management
- AI-powered tag generation and embeddings
- Git version control integration
    """,
    host="127.0.0.1",
    port=8000,
    sse_path="/sse",
    message_path="/messages",
    debug=False,
)

# Initialize configuration and tool managers
config = load_config()
search_tools = SearchTools(config)
document_tools = DocumentTools(config)
processing_tools = ProcessingTools(config)
git_tools = GitTools(config)


async def initialize_tools():
    """Initialize async tools"""
    global search_tools
    logger.info("Initializing search tools...")
    try:
        await search_tools.initialize()
        logger.info("Search tools initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize search tools: {e}")
        logger.warning("Search functionality may be limited")


# Register search and retrieval tools
@mcp.tool(description="Search documents using semantic search with optional filters")
async def search_documents(
    query: str,
    max_results: int = 20,
    similarity_threshold: float = 0.6,
    tags: Optional[list[str]] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    include_generated: bool = True,
    include_captured: bool = True,
    category: Optional[str] = None,
) -> dict[str, Any]:
    """Search documents using semantic search with optional filters"""
    try:
        from prismweave_mcp.schemas.requests import SearchDocumentsRequest

        request = SearchDocumentsRequest(
            query=query,
            max_results=max_results,
            similarity_threshold=similarity_threshold,
            tags=tags,
            date_from=date_from,
            date_to=date_to,
            include_generated=include_generated,
            include_captured=include_captured,
            category=category,
        )
        result = await search_tools.search_documents(request)
        return result
    except Exception as e:
        logger.error(f"Error in search_documents: {e}", exc_info=True)
        return {"error": str(e), "code": "SEARCH_ERROR"}


@mcp.tool(description="Get a document by ID or path")
async def get_document(
    document_id: Optional[str] = None,
    path: Optional[str] = None,
    include_content: bool = True,
) -> dict[str, Any]:
    """Get a document by ID or path"""
    try:
        from prismweave_mcp.schemas.requests import GetDocumentRequest

        request = GetDocumentRequest(
            document_id=document_id,
            path=path,
            include_content=include_content,
        )
        result = await search_tools.get_document(request)
        return result
    except Exception as e:
        logger.error(f"Error in get_document: {e}", exc_info=True)
        return {"error": str(e), "code": "GET_DOCUMENT_ERROR"}


@mcp.tool(description="List documents with optional filters")
async def list_documents(
    category: Optional[str] = None,
    tags: Optional[list[str]] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    include_generated: bool = True,
    include_captured: bool = True,
    limit: Optional[int] = None,
    offset: int = 0,
) -> dict[str, Any]:
    """List documents with optional filters"""
    try:
        from prismweave_mcp.schemas.requests import ListDocumentsRequest

        request = ListDocumentsRequest(
            category=category,
            tags=tags,
            date_from=date_from,
            date_to=date_to,
            include_generated=include_generated,
            include_captured=include_captured,
            limit=limit,
            offset=offset,
        )
        result = await search_tools.list_documents(request)
        return result
    except Exception as e:
        logger.error(f"Error in list_documents: {e}", exc_info=True)
        return {"error": str(e), "code": "LIST_DOCUMENTS_ERROR"}


@mcp.tool(description="Get document metadata without full content")
async def get_document_metadata(
    document_id: Optional[str] = None,
    path: Optional[str] = None,
) -> dict[str, Any]:
    """Get document metadata without full content"""
    try:
        from prismweave_mcp.schemas.requests import GetDocumentRequest

        request = GetDocumentRequest(
            document_id=document_id,
            path=path,
        )
        result = await search_tools.get_document_metadata(request)
        return result
    except Exception as e:
        logger.error(f"Error in get_document_metadata: {e}", exc_info=True)
        return {"error": str(e), "code": "GET_METADATA_ERROR"}


@mcp.tool(description="Create a new generated document")
async def create_document(
    title: str,
    content: str,
    category: Optional[str] = None,
    tags: Optional[list[str]] = None,
    metadata: Optional[dict[str, Any]] = None,
    auto_process: bool = True,
    auto_commit: bool = False,
) -> dict[str, Any]:
    """Create a new generated document"""
    try:
        from prismweave_mcp.schemas.requests import CreateDocumentRequest

        request = CreateDocumentRequest(
            title=title,
            content=content,
            category=category,
            tags=tags,
            metadata=metadata,
            auto_process=auto_process,
            auto_commit=auto_commit,
        )
        result = await document_tools.create_document(request)
        return result
    except Exception as e:
        logger.error(f"Error in create_document: {e}", exc_info=True)
        return {"error": str(e), "code": "CREATE_DOCUMENT_ERROR"}


@mcp.tool(description="Update an existing generated document")
async def update_document(
    document_id: Optional[str] = None,
    path: Optional[str] = None,
    title: Optional[str] = None,
    content: Optional[str] = None,
    tags: Optional[list[str]] = None,
    metadata: Optional[dict[str, Any]] = None,
    regenerate_embeddings: bool = False,
) -> dict[str, Any]:
    """Update an existing generated document"""
    try:
        from prismweave_mcp.schemas.requests import UpdateDocumentRequest

        request = UpdateDocumentRequest(
            document_id=document_id,
            path=path,
            title=title,
            content=content,
            tags=tags,
            metadata=metadata,
            regenerate_embeddings=regenerate_embeddings,
        )
        result = await document_tools.update_document(request)
        return result
    except Exception as e:
        logger.error(f"Error in update_document: {e}", exc_info=True)
        return {"error": str(e), "code": "UPDATE_DOCUMENT_ERROR"}


@mcp.tool(description="Generate embeddings for a document")
async def generate_embeddings(
    document_id: Optional[str] = None,
    path: Optional[str] = None,
    force: bool = False,
) -> dict[str, Any]:
    """Generate embeddings for a document"""
    try:
        from prismweave_mcp.schemas.requests import GenerateEmbeddingsRequest

        request = GenerateEmbeddingsRequest(
            document_id=document_id,
            path=path,
            force=force,
        )
        result = await processing_tools.generate_embeddings(request)
        return result
    except Exception as e:
        logger.error(f"Error in generate_embeddings: {e}", exc_info=True)
        return {"error": str(e), "code": "GENERATE_EMBEDDINGS_ERROR"}


@mcp.tool(description="Generate tags for a document using AI")
async def generate_tags(
    document_id: Optional[str] = None,
    path: Optional[str] = None,
    merge_existing: bool = True,
    max_tags: int = 10,
) -> dict[str, Any]:
    """Generate tags for a document using AI"""
    try:
        from prismweave_mcp.schemas.requests import GenerateTagsRequest

        request = GenerateTagsRequest(
            document_id=document_id,
            path=path,
            merge_existing=merge_existing,
            max_tags=max_tags,
        )
        result = await processing_tools.generate_tags(request)
        return result
    except Exception as e:
        logger.error(f"Error in generate_tags: {e}", exc_info=True)
        return {"error": str(e), "code": "GENERATE_TAGS_ERROR"}


@mcp.tool(description="Commit changes to git repository")
async def commit_to_git(
    message: str,
    paths: Optional[list[str]] = None,
    push: bool = False,
) -> dict[str, Any]:
    """Commit changes to git repository"""
    try:
        from prismweave_mcp.schemas.requests import CommitToGitRequest

        request = CommitToGitRequest(
            message=message,
            paths=paths,
            push=push,
        )
        result = await git_tools.commit_to_git(request)
        return result
    except Exception as e:
        logger.error(f"Error in commit_to_git: {e}", exc_info=True)
        return {"error": str(e), "code": "COMMIT_ERROR"}


def cli_main():
    """CLI entry point for running the server"""
    import argparse

    parser = argparse.ArgumentParser(description="PrismWeave MCP Server")
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host to bind to (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to (default: 8000)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode",
    )

    args = parser.parse_args()

    # Update FastMCP configuration
    mcp.host = args.host
    mcp.port = args.port
    mcp.debug = args.debug

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        logger.info(f"Starting PrismWeave MCP Server on http://{args.host}:{args.port}")
        logger.info(f"SSE endpoint: http://{args.host}:{args.port}/sse")
        logger.info(f"Messages endpoint: http://{args.host}:{args.port}/messages")

        # Initialize tools before running
        import asyncio

        asyncio.run(initialize_tools())

        # Run the FastMCP server (this will use SSE by default)
        # Run in async mode with SSE
        asyncio.run(mcp.run_sse_async())

    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    cli_main()
