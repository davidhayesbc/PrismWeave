"""
Tests for MCP Server

Unit tests for the PrismWeave MCP server.
"""

import asyncio
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from prismweave_mcp.prismweave_server import PrismWeaveMCPServer
from src.core.config import Config


@pytest.fixture
def mock_config():
    """Mock configuration"""
    config = MagicMock(spec=Config)
    config.mcp = MagicMock()
    config.mcp.paths = MagicMock()
    config.mcp.paths.documents_root = "/tmp/test_docs"
    return config


@pytest.fixture
def server(mock_config):
    """Create test server instance"""
    with patch("mcp.prismweave_server.get_config", return_value=mock_config):
        server = PrismWeaveMCPServer()
        return server


@pytest.mark.asyncio
async def test_server_initialization(server):
    """Test server initialization"""
    assert server.server is not None
    assert server.config is not None
    assert server.search_tools is not None
    assert server.document_tools is not None
    assert server.processing_tools is not None
    assert server.git_tools is not None
    assert not server._initialized


@pytest.mark.asyncio
async def test_server_initialize(server):
    """Test async initialization"""
    # Mock search tools initialization
    server.search_tools.initialize = AsyncMock()
    
    await server.initialize()
    
    assert server._initialized
    server.search_tools.initialize.assert_called_once()


@pytest.mark.asyncio
async def test_server_initialize_idempotent(server):
    """Test that initialization is idempotent"""
    server.search_tools.initialize = AsyncMock()
    
    # Initialize twice
    await server.initialize()
    await server.initialize()
    
    # Should only initialize once
    assert server.search_tools.initialize.call_count == 1


@pytest.mark.asyncio
async def test_server_initialize_handles_search_failure(server):
    """Test that server handles search initialization failures gracefully"""
    # Mock search tools to fail
    server.search_tools.initialize = AsyncMock(side_effect=Exception("ChromaDB not available"))
    
    # Should not raise, just log warning
    await server.initialize()
    
    assert server._initialized


@pytest.mark.asyncio
async def test_register_tools(server):
    """Test tool registration"""
    server.register_tools()
    
    # Verify tool handlers are registered
    # The decorators register handlers on the server
    assert hasattr(server.server, "_tool_list_handler")
    assert hasattr(server.server, "_call_tool_handler")


@pytest.mark.asyncio
async def test_list_tools(server):
    """Test listing available tools"""
    server.register_tools()
    
    # Get the registered list_tools handler
    list_tools_handler = server.server._tool_list_handler
    tools = await list_tools_handler()
    
    # Verify all expected tools are registered
    tool_names = [tool.name for tool in tools]
    expected_tools = [
        "search_documents",
        "get_document",
        "list_documents",
        "get_document_metadata",
        "create_document",
        "update_document",
        "generate_embeddings",
        "generate_tags",
        "commit_to_git"
    ]
    
    for expected_tool in expected_tools:
        assert expected_tool in tool_names, f"Tool {expected_tool} not registered"
    
    # Verify tool count
    assert len(tools) == len(expected_tools)


@pytest.mark.asyncio
async def test_call_tool_search_documents(server):
    """Test calling search_documents tool"""
    server.register_tools()
    await server.initialize()
    
    # Mock search_tools.search_documents
    mock_result = {
        "results": [],
        "total": 0,
        "query": "test query"
    }
    server.search_tools.search_documents = AsyncMock(return_value=mock_result)
    
    # Call the tool
    call_tool_handler = server.server._call_tool_handler
    result = await call_tool_handler("search_documents", {"query": "test query"})
    
    # Verify result
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["type"] == "text"
    assert "results" in result[0]["text"]


@pytest.mark.asyncio
async def test_call_tool_get_document(server):
    """Test calling get_document tool"""
    server.register_tools()
    await server.initialize()
    
    # Mock get_document
    mock_result = {
        "document_id": "test_id",
        "title": "Test Document",
        "content": "Test content"
    }
    server.search_tools.get_document = AsyncMock(return_value=mock_result)
    
    # Call the tool
    call_tool_handler = server.server._call_tool_handler
    result = await call_tool_handler("get_document", {"document_id": "test_id"})
    
    # Verify result
    assert isinstance(result, list)
    assert len(result) == 1
    assert "document_id" in result[0]["text"]


@pytest.mark.asyncio
async def test_call_tool_create_document(server):
    """Test calling create_document tool"""
    server.register_tools()
    await server.initialize()
    
    # Mock create_document
    mock_result = {
        "document_id": "new_doc_id",
        "path": "/generated/test.md",
        "success": True
    }
    server.document_tools.create_document = AsyncMock(return_value=mock_result)
    
    # Call the tool
    call_tool_handler = server.server._call_tool_handler
    result = await call_tool_handler(
        "create_document",
        {"title": "Test Doc", "content": "Test content"}
    )
    
    # Verify result
    assert isinstance(result, list)
    assert "document_id" in result[0]["text"]


@pytest.mark.asyncio
async def test_call_tool_unknown_tool(server):
    """Test calling unknown tool returns error"""
    server.register_tools()
    
    # Call non-existent tool
    call_tool_handler = server.server._call_tool_handler
    result = await call_tool_handler("unknown_tool", {})
    
    # Verify error response
    assert isinstance(result, list)
    assert "error" in result[0]["text"].lower()
    assert "unknown_tool" in result[0]["text"].lower()


@pytest.mark.asyncio
async def test_call_tool_handles_exceptions(server):
    """Test that tool call exceptions are handled gracefully"""
    server.register_tools()
    await server.initialize()
    
    # Mock search to raise exception
    server.search_tools.search_documents = AsyncMock(
        side_effect=Exception("Test error")
    )
    
    # Call the tool
    call_tool_handler = server.server._call_tool_handler
    result = await call_tool_handler("search_documents", {"query": "test"})
    
    # Verify error response
    assert isinstance(result, list)
    assert "error" in result[0]["text"].lower()


@pytest.mark.asyncio
async def test_shutdown(server):
    """Test graceful shutdown"""
    await server.initialize()
    
    # Should not raise
    await server.shutdown()


@pytest.mark.asyncio
async def test_shutdown_handles_errors(server):
    """Test that shutdown handles errors gracefully"""
    await server.initialize()
    
    # Mock search_manager to cause error during cleanup
    server.search_tools._initialized = True
    server.search_tools.search_manager = MagicMock()
    server.search_tools.search_manager.close = MagicMock(
        side_effect=Exception("Cleanup error")
    )
    
    # Should not raise
    await server.shutdown()


@pytest.mark.asyncio
async def test_tool_schemas_valid(server):
    """Test that all tool schemas are valid"""
    server.register_tools()
    
    # Get registered tools
    list_tools_handler = server.server._tool_list_handler
    tools = await list_tools_handler()
    
    # Verify each tool has valid schema
    for tool in tools:
        assert tool.name
        assert tool.description
        assert tool.inputSchema
        assert isinstance(tool.inputSchema, dict)
        assert tool.inputSchema.get("type") == "object"
        assert "properties" in tool.inputSchema


@pytest.mark.asyncio
async def test_all_tools_callable(server):
    """Test that all registered tools can be called"""
    server.register_tools()
    await server.initialize()
    
    # Mock all tool methods to return success
    server.search_tools.search_documents = AsyncMock(return_value={"success": True})
    server.search_tools.get_document = AsyncMock(return_value={"success": True})
    server.search_tools.list_documents = AsyncMock(return_value={"success": True})
    server.search_tools.get_document_metadata = AsyncMock(return_value={"success": True})
    server.document_tools.create_document = AsyncMock(return_value={"success": True})
    server.document_tools.update_document = AsyncMock(return_value={"success": True})
    server.processing_tools.generate_embeddings = AsyncMock(return_value={"success": True})
    server.processing_tools.generate_tags = AsyncMock(return_value={"success": True})
    server.git_tools.commit_to_git = AsyncMock(return_value={"success": True})
    
    # Get call handler
    call_tool_handler = server.server._call_tool_handler
    
    # Test each tool
    tools_to_test = [
        ("search_documents", {"query": "test"}),
        ("get_document", {"document_id": "test"}),
        ("list_documents", {}),
        ("get_document_metadata", {"document_id": "test"}),
        ("create_document", {"title": "test", "content": "test"}),
        ("update_document", {"document_id": "test"}),
        ("generate_embeddings", {"document_id": "test"}),
        ("generate_tags", {"document_id": "test"}),
        ("commit_to_git", {"message": "test"}),
    ]
    
    for tool_name, args in tools_to_test:
        result = await call_tool_handler(tool_name, args)
        assert isinstance(result, list)
        assert len(result) > 0
        assert result[0]["type"] == "text"
