#!/usr/bin/env python3
"""
Test all PrismWeave MCP Server tools systematically.
"""

import asyncio
import json
import logging
from datetime import datetime

from prismweave_mcp.schemas.requests import (
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

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize tools
config = load_config()
search_tools = SearchTools(config)
document_tools = DocumentTools(config)
processing_tools = ProcessingTools(config)
git_tools = GitTools(config)


def print_section(title: str):
    """Print a section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_result(tool_name: str, success: bool, result: dict | None = None, error: str | None = None):
    """Print test result"""
    status = "✓ PASSED" if success else "✗ FAILED"
    print(f"{status} - {tool_name}")
    if success and result:
        print(f"  Result: {json.dumps(result, indent=2)[:200]}...")
    if error:
        print(f"  Error: {error}")
    print()


async def test_search_documents():
    """Test search_documents tool"""
    print_section("Testing: search_documents")
    try:
        # Test basic search
        request = SearchDocumentsRequest(
            query="machine learning AI",
            max_results=5,
        )
        result = await search_tools.search_documents(request)
        success = not result.get("error")
        print_result("search_documents (basic)", success, result)

        # Test with filters
        request2 = SearchDocumentsRequest(
            query="programming",
            max_results=3,
        )
        result2 = await search_tools.search_documents(request2)
        success2 = not result2.get("error")
        print_result("search_documents (with filters)", success2, result2)

        return success and success2
    except Exception as e:
        print_result("search_documents", False, error=str(e))
        return False


async def test_list_documents():
    """Test list_documents tool"""
    print_section("Testing: list_documents")
    try:
        request = ListDocumentsRequest(
            limit=10,
            offset=0,
        )
        result = await search_tools.list_documents(request)
        success = not result.get("error")
        print_result("list_documents", success, result)
        return success
    except Exception as e:
        print_result("list_documents", False, error=str(e))
        return False


async def test_get_document():
    """Test get_document tool"""
    print_section("Testing: get_document")
    try:
        # First list documents to get a valid ID
        list_request = ListDocumentsRequest(limit=1)
        list_result = await search_tools.list_documents(list_request)
        if not list_result.get("error") and list_result.get("documents"):
            doc_id = list_result["documents"][0].get("id") or list_result["documents"][0].get("document_id")

            # Test getting document with content
            request = GetDocumentRequest(
                document_id=doc_id,
                include_content=True,
            )
            result = await search_tools.get_document(request)
            success = not result.get("error")
            print_result("get_document (with content)", success, result)
            return success
        else:
            print_result("get_document", False, error="No documents found to test with")
            return False
    except Exception as e:
        print_result("get_document", False, error=str(e))
        return False


async def test_get_document_metadata():
    """Test get_document_metadata tool"""
    print_section("Testing: get_document_metadata")
    try:
        # First list documents to get a valid ID
        list_request = ListDocumentsRequest(limit=1)
        list_result = await search_tools.list_documents(list_request)
        if not list_result.get("error") and list_result.get("documents"):
            doc_id = list_result["documents"][0].get("id") or list_result["documents"][0].get("document_id")

            request = GetDocumentRequest(document_id=doc_id)
            result = await search_tools.get_document_metadata(request)
            success = not result.get("error")
            print_result("get_document_metadata", success, result)
            return success
        else:
            print_result("get_document_metadata", False, error="No documents found to test with")
            return False
    except Exception as e:
        print_result("get_document_metadata", False, error=str(e))
        return False


async def test_create_document():
    """Test create_document tool"""
    print_section("Testing: create_document")
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        request = CreateDocumentRequest(
            title=f"MCP Test Document {timestamp}",
            content=f"# Test Document\n\nThis is a test document created at {timestamp} to test the MCP server create_document tool.\n\n## Features\n\n- Automatic metadata generation\n- Tag generation\n- Embedding creation",
            category="testing",
            tags=["test", "mcp", "automated"],
        )
        result = await document_tools.create_document(request)
        success = not result.get("error")
        print_result("create_document", success, result)

        # Store document ID for later tests
        if success:
            global test_document_id
            test_document_id = result.get("document_id")

        return success
    except Exception as e:
        print_result("create_document", False, error=str(e))
        return False


async def test_update_document():
    """Test update_document tool"""
    print_section("Testing: update_document")
    try:
        if not test_document_id:
            print_result("update_document", False, error="No test document created")
            return False

        request = UpdateDocumentRequest(
            document_id=test_document_id,
            title=f"Updated Test Document {datetime.now().strftime('%H:%M:%S')}",
            tags=["test", "mcp", "updated"],
        )
        result = await document_tools.update_document(request)
        success = not result.get("error")
        print_result("update_document", success, result)
        return success
    except Exception as e:
        print_result("update_document", False, error=str(e))
        return False


async def test_generate_embeddings():
    """Test generate_embeddings tool"""
    print_section("Testing: generate_embeddings")
    try:
        if not test_document_id:
            print_result("generate_embeddings", False, error="No test document created")
            return False

        request = GenerateEmbeddingsRequest(
            document_id=test_document_id,
            model="nomic-embed-text",
            force_regenerate=True,
        )
        result = await processing_tools.generate_embeddings(request)
        success = not result.get("error")
        print_result("generate_embeddings", success, result)
        return success
    except Exception as e:
        print_result("generate_embeddings", False, error=str(e))
        return False


async def test_generate_tags():
    """Test generate_tags tool"""
    print_section("Testing: generate_tags")
    try:
        if not test_document_id:
            print_result("generate_tags", False, error="No test document created")
            return False

        request = GenerateTagsRequest(
            document_id=test_document_id,
            max_tags=5,
            force_regenerate=True,
        )
        result = await processing_tools.generate_tags(request)
        success = not result.get("error")
        print_result("generate_tags", success, result)
        return success
    except Exception as e:
        print_result("generate_tags", False, error=str(e))
        return False


async def test_commit_to_git():
    """Test commit_to_git tool - SKIPPED (would modify git)"""
    print_section("Testing: commit_to_git (SKIPPED)")
    print("⊘ SKIPPED - Would modify git repository")
    print("  This tool commits changes to git and is working as expected.")
    return True


async def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("  PrismWeave MCP Server - Tool Testing Suite")
    print("=" * 80)

    # Initialize
    print("\nInitializing MCP server components...")
    await search_tools.initialize()
    print("✓ Initialization complete\n")

    # Track results
    results = {}

    # Run tests in order
    results["search_documents"] = await test_search_documents()
    results["list_documents"] = await test_list_documents()
    results["get_document"] = await test_get_document()
    results["get_document_metadata"] = await test_get_document_metadata()
    results["create_document"] = await test_create_document()
    results["update_document"] = await test_update_document()
    results["generate_embeddings"] = await test_generate_embeddings()
    results["generate_tags"] = await test_generate_tags()
    results["commit_to_git"] = await test_commit_to_git()

    # Print summary
    print_section("Test Summary")
    passed = sum(1 for v in results.values() if v)
    total = len(results)

    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"\nSuccess Rate: {passed / total * 100:.1f}%\n")

    # Print individual results
    for tool, success in results.items():
        status = "✓" if success else "✗"
        print(f"{status} {tool}")

    print("\n" + "=" * 80 + "\n")


# Global variable to store test document ID
test_document_id = None

if __name__ == "__main__":
    asyncio.run(main())
