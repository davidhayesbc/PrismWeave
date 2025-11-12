"""
Tests for MCP Server

Unit tests for the PrismWeave MCP server using FastMCP.

Note: Most tool tests are blocked due to FastMCP's FunctionTool wrapper.
Tools are decorated with @mcp.tool() which wraps them in FunctionTool objects
that cannot be called directly. Integration testing via MCP protocol is needed.
"""

import pytest


@pytest.mark.asyncio
async def test_server_imports():
    """Test that server module can be imported and has required attributes"""
    from prismweave_mcp import server

    assert hasattr(server, "mcp")
    assert hasattr(server, "search_documents")
    assert hasattr(server, "get_document")
    assert hasattr(server, "create_document")
    assert hasattr(server, "update_document")
    assert hasattr(server, "generate_embeddings")
    assert hasattr(server, "generate_tags")
    assert hasattr(server, "commit_to_git")
    assert hasattr(server, "list_documents")
    assert hasattr(server, "get_document_metadata")


@pytest.mark.asyncio
async def test_server_initialization():
    """Test that server components are initialized"""
    from prismweave_mcp import server

    assert server.config is not None
    assert server.search_tools is not None
    assert server.document_tools is not None
    assert server.processing_tools is not None
    assert server.git_tools is not None
