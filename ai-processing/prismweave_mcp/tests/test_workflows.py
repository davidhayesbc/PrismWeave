"""
Integration Tests for End-to-End Workflows

Tests complete workflows that exercise multiple components together.
"""

import subprocess
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from prismweave_mcp.schemas.requests import (
    CommitToGitRequest,
    CreateDocumentRequest,
    GenerateEmbeddingsRequest,
    SearchDocumentsRequest,
)
from prismweave_mcp.tools.documents import DocumentTools
from prismweave_mcp.tools.git import GitTools
from prismweave_mcp.tools.processing import ProcessingTools
from prismweave_mcp.tools.search import SearchTools
from src.core.config import Config, MCPConfig, MCPCreationConfig, MCPPathsConfig, MCPSearchConfig


@pytest.fixture
def test_config():
    """Create test configuration"""
    config = Config()
    config.mcp = MCPConfig(
        paths=MCPPathsConfig(
            documents_root="test_docs",
            documents_dir="documents",
            generated_dir="generated",
            images_dir="images",
            tech_dir="tech",
        ),
        creation=MCPCreationConfig(
            default_category="general",
        ),
        search=MCPSearchConfig(max_results=20, similarity_threshold=0.6, default_filters={}),
    )
    return config


@pytest.fixture
def temp_git_repo():
    """Create temporary git repository"""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_root = Path(tmpdir)

        # Initialize git repo
        subprocess.run(["git", "init"], cwd=repo_root, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo_root, check=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo_root, check=True)

        # Create directory structure
        (repo_root / "documents").mkdir()
        (repo_root / "generated").mkdir()
        (repo_root / "tech").mkdir()

        # Create initial commit
        readme = repo_root / "README.md"
        readme.write_text("# Test Repository")
        subprocess.run(["git", "add", "README.md"], cwd=repo_root, check=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo_root, check=True)

        yield repo_root


class TestCreateSearchWorkflow:
    """Test creating a document and searching for it"""

    @pytest.mark.asyncio
    async def test_create_and_search(self, test_config, temp_git_repo):
        """Test complete workflow: create document, generate embeddings, search"""
        test_config.mcp.paths.documents_root = str(temp_git_repo)

        # Set ChromaDB path to temp directory to avoid conflicts
        test_config.chroma_db_path = str(temp_git_repo / ".prismweave" / "chroma_db")

        # Step 1: Create document
        doc_tools = DocumentTools(test_config)
        create_request = CreateDocumentRequest(
            title="Machine Learning Basics",
            content="""# Machine Learning

Machine learning is a subset of artificial intelligence that enables systems to learn from data.""",
            tags=["ml", "ai"],
            category="tech",
        )

        create_response = await doc_tools.create_document(create_request)

        assert "error" not in create_response
        doc_id = create_response["document_id"]

        # Step 2: Generate embeddings (mock to avoid actual AI processing)
        processing_tools = ProcessingTools(test_config)
        await processing_tools.initialize()

        # Index the created document in the embedding store for ID lookup
        if processing_tools.processing_manager and processing_tools.processing_manager.embedding_store:
            from src.core.document_processor import DocumentProcessor

            doc_file_path = temp_git_repo / "generated" / "tech" / f"{create_response['path'].split('/')[-1]}"

            # Use DocumentProcessor to properly generate chunks with embeddings
            processor = DocumentProcessor(test_config)
            try:
                chunks = processor.process_document(doc_file_path)
                processing_tools.processing_manager.embedding_store.add_document(doc_file_path, chunks)
            except Exception as e:
                print(f"Warning: Failed to index document in embedding store: {e}")

        async def mock_generate_embeddings(*args, **kwargs):
            return {"success": True, "chunks_processed": 2, "message": "Success"}

        processing_tools.processing_manager.generate_embeddings = mock_generate_embeddings

        embed_request = GenerateEmbeddingsRequest(document_id=doc_id)
        embed_response = await processing_tools.generate_embeddings(embed_request)

        assert "error" not in embed_response
        assert embed_response["embedding_count"] == 2

        # Step 3: Search for the document (mock search results)
        search_tools = SearchTools(test_config)
        await search_tools.initialize()

        from prismweave_mcp.schemas.responses import SearchResult

        mock_search_result = SearchResult(
            document_id=doc_id,
            path="generated/tech/machine-learning-basics.md",
            score=0.95,
            excerpt="Machine learning is a subset of artificial intelligence",
            title="Machine Learning Basics",
        )

        search_tools.search_manager.search_documents = MagicMock(return_value=([mock_search_result], 1))

        search_request = SearchDocumentsRequest(query="machine learning")
        search_response = await search_tools.search_documents(search_request)

        assert "error" not in search_response
        assert search_response["total_results"] >= 1
        assert any("machine learning" in r["title"].lower() for r in search_response["results"])


class TestCreateCommitWorkflow:
    """Test creating a document and committing to git"""

    @pytest.mark.asyncio
    async def test_create_and_commit(self, test_config, temp_git_repo):
        """Test workflow: create document and commit to git"""
        test_config.mcp.paths.documents_root = str(temp_git_repo)

        # Step 1: Create document
        doc_tools = DocumentTools(test_config)
        create_request = CreateDocumentRequest(title="Test Article", content="# Test\n\nContent here.", tags=["test"])

        create_response = await doc_tools.create_document(create_request)

        assert "error" not in create_response
        created_path = create_response["path"]

        # Step 2: Commit to git
        git_tools = GitTools(test_config)
        await git_tools.git_manager.initialize()

        # Get relative path for git
        relative_path = Path(created_path).relative_to(temp_git_repo)

        commit_request = CommitToGitRequest(
            file_paths=[str(relative_path)], commit_message="Add test article", push=False
        )

        commit_response = await git_tools.commit_to_git(commit_request)

        assert "error" not in commit_response
        assert commit_response["success"] is True
        assert commit_response["commit_hash"] is not None


class TestFullDocumentLifecycle:
    """Test complete document lifecycle"""

    @pytest.mark.asyncio
    async def test_full_lifecycle(self, test_config, temp_git_repo):
        """Test full document lifecycle: create, update, embed, tag, commit"""
        test_config.mcp.paths.documents_root = str(temp_git_repo)

        # Set ChromaDB path to temp directory to avoid conflicts
        test_config.chroma_db_path = str(temp_git_repo / ".prismweave" / "chroma_db")

        # Initialize tools
        doc_tools = DocumentTools(test_config)
        processing_tools = ProcessingTools(test_config)
        git_tools = GitTools(test_config)

        await processing_tools.initialize()
        await git_tools.git_manager.initialize()

        # Step 1: Create document
        create_request = CreateDocumentRequest(
            title="Initial Title", content="# Initial\n\nInitial content.", tags=["draft"]
        )

        create_response = await doc_tools.create_document(create_request)
        assert "error" not in create_response
        doc_id = create_response["document_id"]

        # Index the created document in the embedding store for ID lookup
        if processing_tools.processing_manager and processing_tools.processing_manager.embedding_store:
            from src.core.document_processor import DocumentProcessor

            doc_file_path = temp_git_repo / create_response["path"]

            # Use DocumentProcessor to properly generate chunks with embeddings
            processor = DocumentProcessor(test_config)
            try:
                chunks = processor.process_document(doc_file_path)
                processing_tools.processing_manager.embedding_store.add_document(doc_file_path, chunks)
            except Exception as e:
                print(f"Warning: Failed to index document in embedding store: {e}")

        # Step 2: Update document
        from prismweave_mcp.schemas.requests import UpdateDocumentRequest

        update_request = UpdateDocumentRequest(document_id=doc_id, title="Updated Title", tags=["final", "published"])

        update_response = await doc_tools.update_document(update_request)
        assert "error" not in update_response
        assert "title" in update_response["updated_fields"]

        # Step 3: Generate embeddings (mocked)
        async def mock_generate_embeddings(*args, **kwargs):
            return {"success": True, "chunks_processed": 3, "message": "Success"}

        processing_tools.processing_manager.generate_embeddings = mock_generate_embeddings

        embed_request = GenerateEmbeddingsRequest(document_id=doc_id)
        embed_response = await processing_tools.generate_embeddings(embed_request)
        assert "error" not in embed_response

        # Step 4: Generate tags (mocked)
        from prismweave_mcp.schemas.requests import GenerateTagsRequest

        async def mock_generate_tags(*args, **kwargs):
            return {"success": True, "tags": ["article", "content"], "confidence": 0.8}

        processing_tools.processing_manager.generate_tags = mock_generate_tags

        tag_request = GenerateTagsRequest(document_id=doc_id, max_tags=5)
        tag_response = await processing_tools.generate_tags(tag_request)
        assert "error" not in tag_response
        assert len(tag_response["tags"]) > 0

        # Step 5: Commit to git
        created_path = Path(create_response["path"])
        relative_path = created_path.relative_to(temp_git_repo)

        commit_request = CommitToGitRequest(
            file_paths=[str(relative_path)], commit_message="Complete document lifecycle", push=False
        )

        commit_response = await git_tools.commit_to_git(commit_request)
        assert "error" not in commit_response
        assert commit_response["success"] is True


class TestMultiDocumentWorkflow:
    """Test workflows with multiple documents"""

    @pytest.mark.asyncio
    async def test_create_multiple_and_list(self, test_config, temp_git_repo):
        """Test creating multiple documents and listing them"""
        test_config.mcp.paths.documents_root = str(temp_git_repo)

        doc_tools = DocumentTools(test_config)
        search_tools = SearchTools(test_config)

        # Create multiple documents
        doc_ids = []
        for i in range(3):
            create_request = CreateDocumentRequest(
                title=f"Document {i}", content=f"# Doc {i}\n\nContent {i}.", tags=[f"tag{i}"]
            )

            create_response = await doc_tools.create_document(create_request)
            assert "error" not in create_response
            doc_ids.append(create_response["document_id"])

        # List documents
        from prismweave_mcp.schemas.requests import ListDocumentsRequest

        list_request = ListDocumentsRequest(limit=10, offset=0)
        list_response = await search_tools.list_documents(list_request)

        assert "error" not in list_response
        assert list_response["total_count"] >= 3


class TestErrorRecoveryWorkflow:
    """Test error handling in workflows"""

    @pytest.mark.asyncio
    async def test_create_invalid_then_valid(self, test_config, temp_git_repo):
        """Test creating invalid document, then valid one"""
        test_config.mcp.paths.documents_root = str(temp_git_repo)

        doc_tools = DocumentTools(test_config)

        # Try to create invalid document (empty content)
        invalid_request = CreateDocumentRequest(title="Invalid", content="")

        invalid_response = await doc_tools.create_document(invalid_request)
        assert "error" in invalid_response

        # Create valid document
        valid_request = CreateDocumentRequest(title="Valid", content="# Valid\n\nContent.")

        valid_response = await doc_tools.create_document(valid_request)
        assert "error" not in valid_response
        assert valid_response["document_id"] is not None

    @pytest.mark.asyncio
    async def test_update_nonexistent_then_create(self, test_config, temp_git_repo):
        """Test trying to update nonexistent doc, then creating it"""
        test_config.mcp.paths.documents_root = str(temp_git_repo)

        doc_tools = DocumentTools(test_config)

        # Try to update nonexistent document
        from prismweave_mcp.schemas.requests import UpdateDocumentRequest

        update_request = UpdateDocumentRequest(document_id="nonexistent", title="New Title")

        update_response = await doc_tools.update_document(update_request)
        assert "error" in update_response

        # Create the document
        create_request = CreateDocumentRequest(title="New Document", content="# New\n\nContent.")

        create_response = await doc_tools.create_document(create_request)
        assert "error" not in create_response

        # Now update should work
        doc_id = create_response["document_id"]

        # But it needs to be in generated/ to be updateable
        # (The created document is already there)
        update_request2 = UpdateDocumentRequest(document_id=doc_id, title="Updated Title")

        update_response2 = await doc_tools.update_document(update_request2)
        assert "error" not in update_response2
