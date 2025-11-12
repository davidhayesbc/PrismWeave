"""
PrismWeave MCP Server

Main MCP server implementation for document management and AI processing.
"""

import asyncio
import logging
import sys
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.tools.documents import DocumentTools
from mcp.tools.git import GitTools
from mcp.tools.processing import ProcessingTools
from mcp.tools.search import SearchTools
from mcp.types import Tool

from src.core.config import get_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,  # MCP uses stdout for protocol, stderr for logs
)
logger = logging.getLogger(__name__)


class PrismWeaveMCPServer:
    """PrismWeave MCP Server for document management and AI processing"""

    def __init__(self):
        """Initialize the MCP server"""
        self.server = Server("prismweave")
        self.config = get_config()

        # Initialize tool managers
        self.search_tools = SearchTools(self.config)
        self.document_tools = DocumentTools(self.config)
        self.processing_tools = ProcessingTools(self.config)
        self.git_tools = GitTools(self.config)

        self._initialized = False
        logger.info("PrismWeave MCP Server initialized")

    async def initialize(self) -> None:
        """Initialize async components"""
        if self._initialized:
            return

        logger.info("Initializing async components...")

        # Initialize search tools (requires ChromaDB connection)
        try:
            await self.search_tools.initialize()
            logger.info("Search tools initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize search tools: {e}")
            logger.warning("Search functionality may be limited")

        self._initialized = True
        logger.info("Server initialization complete")

    def register_tools(self) -> None:
        """Register all MCP tools with the server"""
        logger.info("Registering MCP tools...")

        # Search and retrieval tools
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List all available tools"""
            return [
                Tool(
                    name="search_documents",
                    description="Search documents using semantic search with optional filters",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search query text"},
                            "max_results": {
                                "type": "integer",
                                "description": "Maximum number of results to return",
                                "default": 20,
                            },
                            "similarity_threshold": {
                                "type": "number",
                                "description": "Minimum similarity score (0-1)",
                                "default": 0.6,
                            },
                            "tags": {"type": "array", "items": {"type": "string"}, "description": "Filter by tags"},
                            "date_from": {
                                "type": "string",
                                "description": "Filter documents from this date (ISO format)",
                            },
                            "date_to": {"type": "string", "description": "Filter documents to this date (ISO format)"},
                            "include_generated": {
                                "type": "boolean",
                                "description": "Include generated documents",
                                "default": True,
                            },
                            "include_captured": {
                                "type": "boolean",
                                "description": "Include captured documents",
                                "default": True,
                            },
                            "category": {"type": "string", "description": "Filter by category"},
                        },
                        "required": ["query"],
                    },
                ),
                mcp.types.Tool(
                    name="get_document",
                    description="Get a document by ID or path",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "document_id": {"type": "string", "description": "Document ID"},
                            "path": {"type": "string", "description": "Document path (alternative to document_id)"},
                            "include_content": {
                                "type": "boolean",
                                "description": "Include full document content",
                                "default": True,
                            },
                        },
                    },
                ),
                Tool(
                    name="list_documents",
                    description="List documents with optional filters",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "category": {"type": "string", "description": "Filter by category"},
                            "tags": {"type": "array", "items": {"type": "string"}, "description": "Filter by tags"},
                            "date_from": {
                                "type": "string",
                                "description": "Filter documents from this date (ISO format)",
                            },
                            "date_to": {"type": "string", "description": "Filter documents to this date (ISO format)"},
                            "include_generated": {
                                "type": "boolean",
                                "description": "Include generated documents",
                                "default": True,
                            },
                            "include_captured": {
                                "type": "boolean",
                                "description": "Include captured documents",
                                "default": True,
                            },
                            "limit": {"type": "integer", "description": "Maximum number of documents to return"},
                            "offset": {"type": "integer", "description": "Number of documents to skip", "default": 0},
                        },
                    },
                ),
                Tool(
                    name="get_document_metadata",
                    description="Get document metadata without full content",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "document_id": {"type": "string", "description": "Document ID"},
                            "path": {"type": "string", "description": "Document path (alternative to document_id)"},
                        },
                    },
                ),
                Tool(
                    name="create_document",
                    description="Create a new generated document",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "title": {"type": "string", "description": "Document title"},
                            "content": {"type": "string", "description": "Document content in markdown"},
                            "category": {"type": "string", "description": "Document category"},
                            "tags": {"type": "array", "items": {"type": "string"}, "description": "Document tags"},
                            "metadata": {"type": "object", "description": "Additional metadata"},
                            "auto_process": {
                                "type": "boolean",
                                "description": "Auto-generate tags and embeddings",
                                "default": True,
                            },
                            "auto_commit": {"type": "boolean", "description": "Auto-commit to git", "default": False},
                        },
                        "required": ["title", "content"],
                    },
                ),
                Tool(
                    name="update_document",
                    description="Update an existing generated document",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "document_id": {"type": "string", "description": "Document ID"},
                            "path": {"type": "string", "description": "Document path (alternative to document_id)"},
                            "title": {"type": "string", "description": "New document title"},
                            "content": {"type": "string", "description": "New document content"},
                            "tags": {"type": "array", "items": {"type": "string"}, "description": "New tags"},
                            "metadata": {"type": "object", "description": "Metadata to update"},
                            "regenerate_embeddings": {
                                "type": "boolean",
                                "description": "Regenerate embeddings after update",
                                "default": False,
                            },
                        },
                    },
                ),
                Tool(
                    name="generate_embeddings",
                    description="Generate embeddings for a document",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "document_id": {"type": "string", "description": "Document ID"},
                            "path": {"type": "string", "description": "Document path (alternative to document_id)"},
                            "force": {
                                "type": "boolean",
                                "description": "Force regeneration even if embeddings exist",
                                "default": False,
                            },
                        },
                    },
                ),
                Tool(
                    name="generate_tags",
                    description="Generate tags for a document using AI",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "document_id": {"type": "string", "description": "Document ID"},
                            "path": {"type": "string", "description": "Document path (alternative to document_id)"},
                            "merge_existing": {
                                "type": "boolean",
                                "description": "Merge with existing tags",
                                "default": True,
                            },
                            "max_tags": {
                                "type": "integer",
                                "description": "Maximum number of tags to generate",
                                "default": 10,
                            },
                        },
                    },
                ),
                Tool(
                    name="commit_to_git",
                    description="Commit changes to git repository",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "message": {"type": "string", "description": "Commit message"},
                            "paths": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Specific paths to commit (empty for all changes)",
                            },
                            "push": {"type": "boolean", "description": "Push to remote after commit", "default": False},
                        },
                        "required": ["message"],
                    },
                ),
            ]

        # Register tool call handlers
        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict[str, Any]) -> list[dict[str, Any]]:
            """Handle tool calls"""
            try:
                logger.info(f"Calling tool: {name}")
                logger.debug(f"Arguments: {arguments}")

                # Route to appropriate tool handler
                if name == "search_documents":
                    from mcp.schemas.requests import SearchDocumentsRequest

                    request = SearchDocumentsRequest(**arguments)
                    result = await self.search_tools.search_documents(request)

                elif name == "get_document":
                    from mcp.schemas.requests import GetDocumentRequest

                    request = GetDocumentRequest(**arguments)
                    result = await self.search_tools.get_document(request)

                elif name == "list_documents":
                    from mcp.schemas.requests import ListDocumentsRequest

                    request = ListDocumentsRequest(**arguments)
                    result = await self.search_tools.list_documents(request)

                elif name == "get_document_metadata":
                    from mcp.schemas.requests import GetDocumentRequest

                    request = GetDocumentRequest(**arguments)
                    result = await self.search_tools.get_document_metadata(request)

                elif name == "create_document":
                    from mcp.schemas.requests import CreateDocumentRequest

                    request = CreateDocumentRequest(**arguments)
                    result = await self.document_tools.create_document(request)

                elif name == "update_document":
                    from mcp.schemas.requests import UpdateDocumentRequest

                    request = UpdateDocumentRequest(**arguments)
                    result = await self.document_tools.update_document(request)

                elif name == "generate_embeddings":
                    from mcp.schemas.requests import GenerateEmbeddingsRequest

                    request = GenerateEmbeddingsRequest(**arguments)
                    result = await self.processing_tools.generate_embeddings(request)

                elif name == "generate_tags":
                    from mcp.schemas.requests import GenerateTagsRequest

                    request = GenerateTagsRequest(**arguments)
                    result = await self.processing_tools.generate_tags(request)

                elif name == "commit_to_git":
                    from mcp.schemas.requests import CommitToGitRequest

                    request = CommitToGitRequest(**arguments)
                    result = await self.git_tools.commit_to_git(request)

                else:
                    logger.error(f"Unknown tool: {name}")
                    result = {"error": f"Unknown tool: {name}", "code": "UNKNOWN_TOOL"}

                logger.info(f"Tool {name} completed successfully")
                return [{"type": "text", "text": str(result)}]

            except Exception as e:
                logger.error(f"Error calling tool {name}: {e}", exc_info=True)
                return [{"type": "text", "text": str({"error": str(e), "code": "TOOL_ERROR", "tool": name})}]

        logger.info("All MCP tools registered successfully")

    async def run(self) -> None:
        """Run the MCP server"""
        try:
            logger.info("Starting PrismWeave MCP Server...")

            # Initialize async components
            await self.initialize()

            # Register tools
            self.register_tools()

            # Run server with stdio transport
            logger.info("Server ready, listening on stdio...")
            async with stdio_server() as (read_stream, write_stream):
                await self.server.run(read_stream, write_stream, self.server.create_initialization_options())

        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt, shutting down...")
        except Exception as e:
            logger.error(f"Server error: {e}", exc_info=True)
            raise
        finally:
            await self.shutdown()

    async def shutdown(self) -> None:
        """Graceful shutdown"""
        logger.info("Shutting down PrismWeave MCP Server...")

        # Close any open connections/resources
        try:
            if self.search_tools._initialized and self.search_tools.search_manager:
                # ChromaDB cleanup if needed
                pass
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

        logger.info("Shutdown complete")


async def main():
    """Main entry point"""
    server = PrismWeaveMCPServer()
    await server.run()


def cli_main():
    """CLI entry point for running the server"""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    cli_main()
