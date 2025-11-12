"""
Tests for Git MCP Tools
"""

from unittest.mock import MagicMock

import pytest

from prismweave_mcp.schemas.requests import CommitToGitRequest
from prismweave_mcp.tools.git import GitTools
from src.core.config import Config


@pytest.fixture
def mock_config():
    """Create a mock configuration"""
    config = MagicMock(spec=Config)
    config.documents_dir = "/test/documents"
    # Add mcp.paths if needed
    config.mcp = MagicMock()
    config.mcp.paths = MagicMock()
    config.mcp.paths.documents_root = "/test/documents"
    # Add required Config attributes
    config.ollama = MagicMock()
    config.processing = MagicMock()
    config.vector = MagicMock()
    return config


@pytest.fixture
def git_tools(mock_config):
    """Create GitTools instance"""
    return GitTools(mock_config)


@pytest.mark.asyncio
class TestGitTools:
    """Test suite for GitTools"""

    async def test_commit_to_git_success(self, git_tools):
        """Test successful git commit"""
        git_tools.git_manager.commit_changes = MagicMock(
            return_value={
                "success": True,
                "commit_sha": "abc123def456",  # git_manager returns commit_sha not commit_hash
                "files_committed": 2,
                "pushed": False,
            }
        )

        request = CommitToGitRequest(message="Test commit", paths=["doc1.md", "doc2.md"], push=False)

        result = await git_tools.commit_to_git(request)

        assert result["success"] is True
        assert result["commit_hash"] == "abc123def456"
        assert result["files_committed"] == 2
        assert result["pushed"] is False

        git_tools.git_manager.commit_changes.assert_called_once_with(
            message="Test commit", files=["doc1.md", "doc2.md"], push=False
        )

    async def test_commit_to_git_with_push(self, git_tools):
        """Test git commit with push"""
        git_tools.git_manager.commit_changes = MagicMock(
            return_value={"success": True, "commit_hash": "xyz789", "files_committed": 1, "pushed": True}
        )

        request = CommitToGitRequest(message="Test commit with push", paths=["doc.md"], push=True)

        result = await git_tools.commit_to_git(request)

        assert result["success"] is True
        assert result["pushed"] is True
        git_tools.git_manager.commit_changes.assert_called_once_with(
            message="Test commit with push", files=["doc.md"], push=True
        )

    async def test_commit_to_git_all_files(self, git_tools):
        """Test git commit with all files (None)"""
        git_tools.git_manager.commit_changes = MagicMock(
            return_value={
                "success": True,
                "commit_hash": "allfiles123",
                "files_committed": 3,
                "pushed": False,
            }
        )

        request = CommitToGitRequest(message="Commit all files", push=False)

        result = await git_tools.commit_to_git(request)

        assert result["success"] is True
        assert result["files_committed"] == 3
        git_tools.git_manager.commit_changes.assert_called_once_with(message="Commit all files", files=None, push=False)

    async def test_commit_to_git_failure(self, git_tools):
        """Test git commit failure"""
        git_tools.git_manager.commit_changes = MagicMock(return_value={"success": False, "error": "Nothing to commit"})

        request = CommitToGitRequest(message="Test commit", push=False)

        result = await git_tools.commit_to_git(request)

        assert "error" in result
        assert "error_code" in result
        assert result["error_code"] == "GIT_COMMIT_FAILED"
        assert "Nothing to commit" in result["error"]

    async def test_commit_to_git_exception(self, git_tools):
        """Test git commit exception handling"""
        git_tools.git_manager.commit_changes = MagicMock(side_effect=Exception("Git operation failed"))

        request = CommitToGitRequest(message="Test commit", push=False)

        result = await git_tools.commit_to_git(request)

        assert "error" in result
        assert "error_code" in result
        assert result["error_code"] == "GIT_OPERATION_EXCEPTION"
        assert "Git operation failed" in result["error"]

    async def test_commit_to_git_single_file(self, git_tools):
        """Test git commit with single file"""
        git_tools.git_manager.commit_changes = MagicMock(
            return_value={"success": True, "commit_sha": "single123", "files_committed": 1, "pushed": False}
        )

        request = CommitToGitRequest(message="Update single doc", paths=["doc.md"], push=False)

        result = await git_tools.commit_to_git(request)

        assert result["success"] is True
        assert result["files_committed"] == 1  # files_committed is a count (int), not a list

    async def test_commit_to_git_detailed_error(self, git_tools):
        """Test git commit with detailed error information"""
        git_tools.git_manager.commit_changes = MagicMock(
            return_value={"success": False, "error": "Repository is in detached HEAD state"}
        )

        request = CommitToGitRequest(message="Test commit", paths=["doc.md"], push=False)

        result = await git_tools.commit_to_git(request)

        assert "error" in result
        assert "error_code" in result
        assert result["error_code"] == "GIT_COMMIT_FAILED"
        assert "detached HEAD" in result["error"]
        assert result["details"]["message"] == "Test commit"
        assert result["details"]["paths"] == ["doc.md"]
