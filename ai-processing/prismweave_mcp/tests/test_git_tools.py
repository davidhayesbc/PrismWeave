"""
Tests for Git Tools (MCP Tool Layer)

Tests for git operations MCP tool implementations.
"""

import subprocess
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import pytest_asyncio

from prismweave_mcp.schemas.requests import CommitToGitRequest
from prismweave_mcp.tools.git import GitTools
from src.core.config import Config, MCPConfig, MCPPathsConfig


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
    )
    return config


@pytest.fixture
def temp_docs_dir():
    """Create temporary documents directory with git repo"""
    with tempfile.TemporaryDirectory() as tmpdir:
        docs_root = Path(tmpdir)

        # Initialize git repo
        subprocess.run(["git", "init"], cwd=docs_root, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=docs_root, check=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=docs_root, check=True)

        # Create directory structure
        (docs_root / "documents").mkdir()
        (docs_root / "generated").mkdir()

        # Create initial commit
        readme = docs_root / "README.md"
        readme.write_text("# Test Repository")
        subprocess.run(["git", "add", "README.md"], cwd=docs_root, check=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=docs_root, check=True)

        yield docs_root


@pytest_asyncio.fixture
async def git_tools(test_config, temp_docs_dir):
    """Create git tools with temp directory"""
    test_config.mcp.paths.documents_root = str(temp_docs_dir)
    return GitTools(test_config)


class TestCommitToGit:
    """Tests for commit_to_git tool"""

    @pytest.mark.asyncio
    async def test_commit_single_file(self, git_tools, temp_docs_dir):
        """Test committing a single file"""
        # Create a new file
        test_file = temp_docs_dir / "generated" / "test.md"
        test_file.write_text("# Test Document\n\nContent.")

        request = CommitToGitRequest(
            file_paths=["generated/test.md"], commit_message="Add test document", push=False
        )

        response = await git_tools.commit_to_git(request)

        assert "error" not in response
        assert response["success"] is True
        assert response["message"] == "Add test document"
        assert response["commit_hash"] is not None

    @pytest.mark.asyncio
    async def test_commit_multiple_files(self, git_tools, temp_docs_dir):
        """Test committing multiple files"""
        # Create multiple files
        file1 = temp_docs_dir / "generated" / "doc1.md"
        file2 = temp_docs_dir / "generated" / "doc2.md"
        file1.write_text("Doc 1")
        file2.write_text("Doc 2")

        request = CommitToGitRequest(
            file_paths=["generated/doc1.md", "generated/doc2.md"], commit_message="Add two documents", push=False
        )

        response = await git_tools.commit_to_git(request)

        assert "error" not in response
        assert response["success"] is True

    @pytest.mark.asyncio
    async def test_commit_no_files_specified(self, git_tools, temp_docs_dir):
        """Test committing without specifying files"""
        # Create a file
        test_file = temp_docs_dir / "generated" / "test.md"
        test_file.write_text("Content")

        # Pass None/empty for file_paths to commit all changes
        request = CommitToGitRequest(file_paths=[], commit_message="Commit all changes", push=False)

        response = await git_tools.commit_to_git(request)

        # Should handle empty file list (behavior depends on GitManager implementation)
        # Either succeeds or returns no changes
        assert "error" not in response or "no changes" in response.get("error", "").lower()

    @pytest.mark.asyncio
    async def test_commit_with_push(self, git_tools, temp_docs_dir):
        """Test committing with push flag"""
        # Create a file
        test_file = temp_docs_dir / "generated" / "test.md"
        test_file.write_text("Content")

        # Mock the git manager's commit_changes to avoid actual push
        async def mock_commit(message, files, push):
            return {
                "success": True,
                "commit_sha": "abc123",
                "files_committed": 1,
                "pushed": True,
                "message": "Committed and pushed",
            }

        git_tools.git_manager.commit_changes = mock_commit

        request = CommitToGitRequest(file_paths=["generated/test.md"], commit_message="Test commit", push=True)

        response = await git_tools.commit_to_git(request)

        assert "error" not in response
        assert response["success"] is True

    @pytest.mark.asyncio
    async def test_commit_failure(self, git_tools, temp_docs_dir):
        """Test commit failure handling"""
        # Mock git manager to return failure
        async def mock_commit_fail(message, files, push):
            return {"success": False, "error": "Commit failed", "commit_sha": None}

        await git_tools.git_manager.initialize()
        git_tools.git_manager.commit_changes = mock_commit_fail

        request = CommitToGitRequest(file_paths=["test.md"], commit_message="Failed commit", push=False)

        response = await git_tools.commit_to_git(request)

        assert "error" in response
        assert response["error_code"] == "GIT_COMMIT_FAILED"

    @pytest.mark.asyncio
    async def test_commit_exception_handling(self, git_tools):
        """Test commit handles exceptions"""
        # Mock git manager to raise exception
        async def mock_commit_exception(message, files, push):
            raise Exception("Git error")

        git_tools.git_manager.commit_changes = mock_commit_exception

        request = CommitToGitRequest(file_paths=["test.md"], commit_message="Test", push=False)

        response = await git_tools.commit_to_git(request)

        assert "error" in response
        assert "Git error" in response["error"]
        assert response["error_code"] == "GIT_OPERATION_EXCEPTION"

    @pytest.mark.asyncio
    async def test_commit_auto_initializes_git_manager(self, test_config, temp_docs_dir):
        """Test that commit auto-initializes git manager if needed"""
        test_config.mcp.paths.documents_root = str(temp_docs_dir)
        tools = GitTools(test_config)

        # Git manager should not be initialized yet
        assert tools.git_manager._git_tracker is None

        # Create a file
        test_file = temp_docs_dir / "generated" / "test.md"
        test_file.write_text("Content")

        request = CommitToGitRequest(file_paths=["generated/test.md"], commit_message="Auto init test", push=False)

        response = await tools.commit_to_git(request)

        # Should have auto-initialized
        assert tools.git_manager._git_tracker is not None

    @pytest.mark.asyncio
    async def test_commit_no_changes(self, git_tools, temp_docs_dir):
        """Test committing when there are no changes"""
        # Initialize git manager
        await git_tools.git_manager.initialize()

        # Don't create any new files
        request = CommitToGitRequest(file_paths=[], commit_message="No changes", push=False)

        response = await git_tools.commit_to_git(request)

        # Should succeed but indicate no changes
        assert "error" not in response
        # Response format depends on implementation


class TestGitToolsInitialization:
    """Tests for git tools initialization"""

    def test_git_tools_creation(self, test_config, temp_docs_dir):
        """Test creating git tools"""
        test_config.mcp.paths.documents_root = str(temp_docs_dir)
        tools = GitTools(test_config)

        assert tools.config == test_config
        assert tools.git_manager is not None

    @pytest.mark.asyncio
    async def test_git_manager_initialization_required(self, git_tools, temp_docs_dir):
        """Test that git manager needs initialization before use"""
        # Git manager should exist but not be initialized
        assert git_tools.git_manager._git_tracker is None

        # Initialize it
        await git_tools.git_manager.initialize()

        assert git_tools.git_manager._git_tracker is not None
        assert git_tools.git_manager._repo_path == temp_docs_dir


class TestCommitMessageHandling:
    """Tests for commit message handling"""

    @pytest.mark.asyncio
    async def test_custom_commit_message(self, git_tools, temp_docs_dir):
        """Test using custom commit message"""
        test_file = temp_docs_dir / "generated" / "test.md"
        test_file.write_text("Content")

        custom_message = "feat: Add new feature document"

        request = CommitToGitRequest(file_paths=["generated/test.md"], commit_message=custom_message, push=False)

        response = await git_tools.commit_to_git(request)

        assert "error" not in response
        assert response["message"] == custom_message

    @pytest.mark.asyncio
    async def test_multiline_commit_message(self, git_tools, temp_docs_dir):
        """Test multiline commit message"""
        test_file = temp_docs_dir / "generated" / "test.md"
        test_file.write_text("Content")

        multiline_message = """Add new document

This document contains important information
about the project."""

        request = CommitToGitRequest(file_paths=["generated/test.md"], commit_message=multiline_message, push=False)

        response = await git_tools.commit_to_git(request)

        assert "error" not in response
