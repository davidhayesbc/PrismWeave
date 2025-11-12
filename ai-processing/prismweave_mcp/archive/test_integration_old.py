"""
Integration Tests for MCP Server

End-to-end tests for complete MCP workflows.
"""

import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from prismweave_mcp.prismweave_server import PrismWeaveMCPServer
from src.core.config import Config


@pytest.fixture
def temp_docs_dir():
    """Create temporary documents directory"""
    with tempfile.TemporaryDirectory() as tmpdir:
        docs_root = Path(tmpdir)
        generated_dir = docs_root / "generated"
        generated_dir.mkdir(parents=True)
        yield docs_root


@pytest.fixture
def integration_config(temp_docs_dir):
    """Create configuration for integration tests"""
    config = MagicMock(spec=Config)
    config.mcp = MagicMock()
    config.mcp.paths = MagicMock()
    config.mcp.paths.documents_root = str(temp_docs_dir)
    config.mcp.paths.generated_dir = str(temp_docs_dir / "generated")
    config.mcp.search = MagicMock()
    config.mcp.search.max_results = 20
    config.mcp.search.similarity_threshold = 0.6
    return config


@pytest.fixture
def integration_server(integration_config):
    """Create server instance for integration tests"""
    with patch("mcp.prismweave_server.get_config", return_value=integration_config):
        server = PrismWeaveMCPServer()
        return server


@pytest.mark.asyncio
async def test_workflow_create_search_retrieve(integration_server, temp_docs_dir):
    """Test complete workflow: create document -> search -> retrieve"""
    await integration_server.initialize()
    integration_server.register_tools()
    
    # Mock tools for workflow
    integration_server.document_tools.create_document = AsyncMock(
        return_value={
            "document_id": "test_doc_123",
            "path": str(temp_docs_dir / "generated" / "test-document.md"),
            "success": True
        }
    )
    
    integration_server.search_tools.search_documents = AsyncMock(
        return_value={
            "results": [
                {
                    "document_id": "test_doc_123",
                    "title": "Test Document",
                    "similarity": 0.95,
                    "snippet": "This is a test document"
                }
            ],
            "total": 1,
            "query": "test"
        }
    )
    
    integration_server.search_tools.get_document = AsyncMock(
        return_value={
            "document_id": "test_doc_123",
            "title": "Test Document",
            "content": "# Test Document\n\nThis is a test document",
            "metadata": {"tags": ["test"]}
        }
    )
    
    call_tool = integration_server.server._call_tool_handler
    
    # Step 1: Create document
    create_result = await call_tool(
        "create_document",
        {
            "title": "Test Document",
            "content": "# Test Document\n\nThis is a test document",
            "tags": ["test"]
        }
    )
    assert "test_doc_123" in create_result[0]["text"]
    
    # Step 2: Search for document
    search_result = await call_tool(
        "search_documents",
        {"query": "test"}
    )
    assert "test_doc_123" in search_result[0]["text"]
    
    # Step 3: Retrieve full document
    get_result = await call_tool(
        "get_document",
        {"document_id": "test_doc_123"}
    )
    assert "Test Document" in get_result[0]["text"]


@pytest.mark.asyncio
async def test_workflow_create_process_commit(integration_server):
    """Test workflow: create -> generate tags -> generate embeddings -> commit"""
    await integration_server.initialize()
    integration_server.register_tools()
    
    # Mock tools
    integration_server.document_tools.create_document = AsyncMock(
        return_value={
            "document_id": "new_doc_456",
            "path": "/generated/new-document.md",
            "success": True
        }
    )
    
    integration_server.processing_tools.generate_tags = AsyncMock(
        return_value={
            "document_id": "new_doc_456",
            "tags": ["ai", "machine-learning", "python"],
            "merge_existing": True
        }
    )
    
    integration_server.processing_tools.generate_embeddings = AsyncMock(
        return_value={
            "document_id": "new_doc_456",
            "chunks_processed": 5,
            "embeddings_count": 5
        }
    )
    
    integration_server.git_tools.commit_to_git = AsyncMock(
        return_value={
            "committed": True,
            "commit_sha": "abc123",
            "files_changed": 1
        }
    )
    
    call_tool = integration_server.server._call_tool_handler
    
    # Step 1: Create document (without auto-processing)
    create_result = await call_tool(
        "create_document",
        {
            "title": "AI Document",
            "content": "# AI Document\n\nAbout machine learning",
            "auto_process": False
        }
    )
    assert "new_doc_456" in create_result[0]["text"]
    
    # Step 2: Generate tags
    tags_result = await call_tool(
        "generate_tags",
        {"document_id": "new_doc_456"}
    )
    assert "tags" in tags_result[0]["text"].lower()
    
    # Step 3: Generate embeddings
    embed_result = await call_tool(
        "generate_embeddings",
        {"document_id": "new_doc_456"}
    )
    assert "chunks_processed" in embed_result[0]["text"].lower()
    
    # Step 4: Commit to git
    commit_result = await call_tool(
        "commit_to_git",
        {"message": "Add AI document with tags and embeddings"}
    )
    assert "committed" in commit_result[0]["text"].lower()


@pytest.mark.asyncio
async def test_workflow_update_reembed(integration_server):
    """Test workflow: update document -> regenerate embeddings"""
    await integration_server.initialize()
    integration_server.register_tools()
    
    # Mock tools
    integration_server.document_tools.update_document = AsyncMock(
        return_value={
            "document_id": "existing_doc",
            "path": "/generated/existing.md",
            "updated": True
        }
    )
    
    call_tool = integration_server.server._call_tool_handler
    
    # Update document with auto-reembedding
    update_result = await call_tool(
        "update_document",
        {
            "document_id": "existing_doc",
            "content": "Updated content with new information",
            "regenerate_embeddings": True
        }
    )
    
    assert "updated" in update_result[0]["text"].lower()


@pytest.mark.asyncio
async def test_workflow_search_with_filters(integration_server):
    """Test search workflow with multiple filters"""
    await integration_server.initialize()
    integration_server.register_tools()
    
    # Mock search with filters
    integration_server.search_tools.search_documents = AsyncMock(
        return_value={
            "results": [
                {
                    "document_id": "filtered_doc",
                    "title": "Filtered Document",
                    "tags": ["python", "tutorial"],
                    "category": "tech",
                    "similarity": 0.85
                }
            ],
            "total": 1,
            "filters_applied": {
                "tags": ["python"],
                "category": "tech",
                "date_from": "2025-01-01"
            }
        }
    )
    
    call_tool = integration_server.server._call_tool_handler
    
    # Search with multiple filters
    search_result = await call_tool(
        "search_documents",
        {
            "query": "python tutorial",
            "tags": ["python"],
            "category": "tech",
            "date_from": "2025-01-01",
            "max_results": 10,
            "similarity_threshold": 0.7
        }
    )
    
    assert "filtered_doc" in search_result[0]["text"]


@pytest.mark.asyncio
async def test_workflow_list_and_batch_process(integration_server):
    """Test workflow: list documents -> batch process"""
    await integration_server.initialize()
    integration_server.register_tools()
    
    # Mock list documents
    integration_server.search_tools.list_documents = AsyncMock(
        return_value={
            "documents": [
                {"document_id": "doc1", "title": "Doc 1"},
                {"document_id": "doc2", "title": "Doc 2"},
                {"document_id": "doc3", "title": "Doc 3"}
            ],
            "total": 3,
            "limit": 100,
            "offset": 0
        }
    )
    
    # Mock batch processing
    integration_server.processing_tools.generate_embeddings = AsyncMock(
        return_value={"success": True}
    )
    
    call_tool = integration_server.server._call_tool_handler
    
    # Step 1: List unprocessed documents
    list_result = await call_tool(
        "list_documents",
        {"include_generated": True, "limit": 100}
    )
    assert "doc1" in list_result[0]["text"]
    
    # Step 2: Process each document (simulated)
    for doc_id in ["doc1", "doc2", "doc3"]:
        embed_result = await call_tool(
            "generate_embeddings",
            {"document_id": doc_id}
        )
        assert "success" in embed_result[0]["text"].lower()


@pytest.mark.asyncio
async def test_workflow_error_recovery(integration_server):
    """Test workflow with error handling and recovery"""
    await integration_server.initialize()
    integration_server.register_tools()
    
    call_tool = integration_server.server._call_tool_handler
    
    # Try to get non-existent document (should return error)
    integration_server.search_tools.get_document = AsyncMock(
        side_effect=Exception("Document not found")
    )
    
    error_result = await call_tool(
        "get_document",
        {"document_id": "nonexistent"}
    )
    assert "error" in error_result[0]["text"].lower()
    
    # Try again with valid document (recovery)
    integration_server.search_tools.get_document = AsyncMock(
        return_value={
            "document_id": "valid_doc",
            "title": "Valid Document"
        }
    )
    
    success_result = await call_tool(
        "get_document",
        {"document_id": "valid_doc"}
    )
    assert "valid_doc" in success_result[0]["text"]


@pytest.mark.asyncio
async def test_workflow_concurrent_operations(integration_server):
    """Test handling concurrent tool calls"""
    await integration_server.initialize()
    integration_server.register_tools()
    
    # Mock tools with delays to simulate concurrent execution
    integration_server.search_tools.search_documents = AsyncMock(
        return_value={"results": [], "total": 0}
    )
    integration_server.search_tools.list_documents = AsyncMock(
        return_value={"documents": [], "total": 0}
    )
    
    call_tool = integration_server.server._call_tool_handler
    
    # Execute multiple operations concurrently
    import asyncio
    results = await asyncio.gather(
        call_tool("search_documents", {"query": "test1"}),
        call_tool("search_documents", {"query": "test2"}),
        call_tool("list_documents", {}),
        return_exceptions=True
    )
    
    # All should complete successfully
    assert len(results) == 3
    for result in results:
        assert isinstance(result, list)


@pytest.mark.asyncio
async def test_workflow_create_with_auto_commit(integration_server):
    """Test create document with auto-commit enabled"""
    await integration_server.initialize()
    integration_server.register_tools()
    
    # Mock document creation with auto-commit
    integration_server.document_tools.create_document = AsyncMock(
        return_value={
            "document_id": "auto_commit_doc",
            "path": "/generated/auto.md",
            "success": True,
            "auto_committed": True,
            "commit_sha": "xyz789"
        }
    )
    
    call_tool = integration_server.server._call_tool_handler
    
    # Create with auto-commit
    result = await call_tool(
        "create_document",
        {
            "title": "Auto Commit Doc",
            "content": "Content",
            "auto_commit": True
        }
    )
    
    assert "auto_commit_doc" in result[0]["text"]
    assert "commit" in result[0]["text"].lower()


@pytest.mark.asyncio
async def test_workflow_metadata_only_retrieval(integration_server):
    """Test retrieving document metadata without full content"""
    await integration_server.initialize()
    integration_server.register_tools()
    
    # Mock metadata retrieval
    integration_server.search_tools.get_document_metadata = AsyncMock(
        return_value={
            "document_id": "meta_doc",
            "title": "Metadata Document",
            "tags": ["metadata", "test"],
            "created_at": "2025-01-01T12:00:00",
            "word_count": 500
        }
    )
    
    call_tool = integration_server.server._call_tool_handler
    
    # Get metadata only
    result = await call_tool(
        "get_document_metadata",
        {"document_id": "meta_doc"}
    )
    
    assert "meta_doc" in result[0]["text"]
    assert "word_count" in result[0]["text"].lower()
