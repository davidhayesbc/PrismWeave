"""
Tests for Git Manager
"""

import subprocess
from unittest.mock import MagicMock, patch

import pytest
import pytest_asyncio

from prismweave_mcp.managers.git_manager import GitManager
from src.core.config import Config


@pytest.fixture
def test_config(tmp_path):
    """Create a test configuration"""
    config = MagicMock(spec=Config)
    config.mcp = MagicMock()
    config.mcp.paths = MagicMock()
    config.mcp.paths.documents_root = str(tmp_path)
    return config


@pytest.fixture
def mock_git_tracker():
    """Create a mock GitTracker"""
    mock = MagicMock()
    mock.get_current_commit_hash.return_value = "abc123def456"
    mock._build_authenticated_remote.return_value = None
    return mock


@pytest_asyncio.fixture
async def git_manager(test_config, tmp_path, mock_git_tracker):
    """Create a Git Manager instance with mocked dependencies"""
    manager = GitManager(test_config)

    # Initialize a real git repo in temp directory
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=tmp_path, check=True)

    # Create initial commit
    test_file = tmp_path / "README.md"
    test_file.write_text("# Test Repository")
    subprocess.run(["git", "add", "README.md"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=tmp_path, check=True)

    await manager.initialize()

    # Replace git tracker with mock for controlled testing
    manager._git_tracker = mock_git_tracker

    yield manager


class TestGitManagerInitialization:
    """Tests for Git Manager initialization"""

    @pytest.mark.asyncio
    async def test_initialize_success(self, test_config, tmp_path):
        """Test successful initialization with valid git repo"""
        # Initialize git repo
        subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)

        manager = GitManager(test_config)
        await manager.initialize()

        assert manager._git_tracker is not None
        assert manager._repo_path == tmp_path

    @pytest.mark.asyncio
    async def test_initialize_not_git_repo(self, test_config, tmp_path):
        """Test initialization fails with non-git directory"""
        manager = GitManager(test_config)

        with pytest.raises(ValueError, match="not a git repository"):
            await manager.initialize()


class TestCommitChanges:
    """Tests for commit_changes method"""

    @pytest.mark.asyncio
    async def test_commit_all_changes(self, git_manager, tmp_path):
        """Test committing all changes"""
        # Create a new file
        test_file = tmp_path / "test.txt"
        test_file.write_text("Test content")

        result = await git_manager.commit_changes(message="Add test file")

        assert result["success"] is True
        assert result["files_committed"] == 1
        assert result["pushed"] is False
        assert "committed" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_commit_specific_files(self, git_manager, tmp_path):
        """Test committing specific files only"""
        # Create multiple files
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        file1.write_text("Content 1")
        file2.write_text("Content 2")

        # Commit only file1
        result = await git_manager.commit_changes(files=["file1.txt"], message="Add file1")

        assert result["success"] is True
        assert result["files_committed"] == 1

    @pytest.mark.asyncio
    async def test_commit_no_changes(self, git_manager, tmp_path):
        """Test committing when there are no changes"""
        result = await git_manager.commit_changes()

        assert result["success"] is True
        assert result["files_committed"] == 0
        assert "no changes" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_commit_with_push(self, git_manager, tmp_path):
        """Test committing with push to remote"""
        # Create a change
        test_file = tmp_path / "test.txt"
        test_file.write_text("Test content")

        # Mock the push to avoid actual network operations
        with patch.object(git_manager, "_push_to_remote", return_value={"success": True, "message": "Pushed"}):
            result = await git_manager.commit_changes(message="Test commit", push=True)

        assert result["success"] is True
        assert result["pushed"] is True

    @pytest.mark.asyncio
    async def test_commit_generates_default_message(self, git_manager, tmp_path):
        """Test that default commit message is generated if not provided"""
        # Create a change
        test_file = tmp_path / "test.txt"
        test_file.write_text("Test content")

        result = await git_manager.commit_changes()

        assert result["success"] is True
        # Verify a commit was made (would fail if message was invalid)
        assert result["files_committed"] > 0

    @pytest.mark.asyncio
    async def test_commit_error_handling(self, git_manager, tmp_path):
        """Test error handling during commit"""
        # Create a change
        test_file = tmp_path / "test.txt"
        test_file.write_text("Test content")

        # Mock subprocess to raise an error
        with patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "git", stderr=b"Test error")):
            result = await git_manager.commit_changes()

        assert result["success"] is False
        assert "failed" in result["message"].lower()


class TestGetRepoStatus:
    """Tests for get_repo_status method"""

    @pytest.mark.asyncio
    async def test_get_status_clean_repo(self, git_manager):
        """Test getting status of clean repository"""
        result = await git_manager.get_repo_status()

        assert result["success"] is True
        assert result["branch"] is not None
        assert result["commit_hash"] is not None
        assert result["has_uncommitted_changes"] is False
        assert len(result["uncommitted_files"]) == 0

    @pytest.mark.asyncio
    async def test_get_status_with_changes(self, git_manager, tmp_path):
        """Test getting status with uncommitted changes"""
        # Modify existing file
        readme = tmp_path / "README.md"
        readme.write_text("# Modified")

        result = await git_manager.get_repo_status()

        assert result["success"] is True
        # The file should show as having uncommitted changes
        assert result["has_uncommitted_changes"] is True or result["has_untracked_files"] is True
        # Verify we have some files in the status
        assert len(result["uncommitted_files"]) > 0 or len(result["untracked_files"]) > 0

    @pytest.mark.asyncio
    async def test_get_status_with_untracked(self, git_manager, tmp_path):
        """Test getting status with untracked files"""
        # Create new file
        new_file = tmp_path / "untracked.txt"
        new_file.write_text("New content")

        result = await git_manager.get_repo_status()

        assert result["success"] is True
        assert result["has_untracked_files"] is True
        assert "untracked.txt" in result["untracked_files"]

    @pytest.mark.asyncio
    async def test_get_status_remote_tracking(self, git_manager):
        """Test getting status with remote tracking info"""
        result = await git_manager.get_repo_status()

        assert result["success"] is True
        # ahead_of_remote and behind_remote should be present (0 if no remote)
        assert "ahead_of_remote" in result
        assert "behind_remote" in result


class TestAddFile:
    """Tests for add_file method"""

    @pytest.mark.asyncio
    async def test_add_file_success(self, git_manager, tmp_path):
        """Test successfully staging a file"""
        # Create a new file
        test_file = tmp_path / "new_file.txt"
        test_file.write_text("Content")

        result = await git_manager.add_file("new_file.txt")

        assert result["success"] is True
        assert result["file_path"] == "new_file.txt"
        assert "staged" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_add_file_not_found(self, git_manager):
        """Test staging a non-existent file"""
        result = await git_manager.add_file("nonexistent.txt")

        assert result["success"] is False
        assert "not found" in result["message"].lower()
        assert result["file_path"] == "nonexistent.txt"

    @pytest.mark.asyncio
    async def test_add_file_error_handling(self, git_manager, tmp_path):
        """Test error handling when staging fails"""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Content")

        # Mock subprocess to raise an error
        with patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "git", stderr=b"Test error")):
            result = await git_manager.add_file("test.txt")

        assert result["success"] is False
        assert "failed" in result["message"].lower()


class TestPullLatest:
    """Tests for pull_latest method"""

    @pytest.mark.asyncio
    async def test_pull_success(self, git_manager, mock_git_tracker):
        """Test successful pull from remote"""
        # Mock successful pull
        mock_git_tracker.pull_latest.return_value = True
        mock_git_tracker.get_current_commit_hash.return_value = "new123hash"

        result = await git_manager.pull_latest()

        assert result["success"] is True
        assert result["commit_hash"] == "new123hash"
        assert "pulled" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_pull_with_branch(self, git_manager, mock_git_tracker):
        """Test pulling specific branch"""
        mock_git_tracker.pull_latest.return_value = True

        result = await git_manager.pull_latest(branch="develop")

        assert result["success"] is True
        mock_git_tracker.pull_latest.assert_called_once_with(remote="origin", branch="develop", ff_only=True)

    @pytest.mark.asyncio
    async def test_pull_error(self, git_manager, mock_git_tracker):
        """Test error handling during pull"""
        mock_git_tracker.pull_latest.side_effect = RuntimeError("Pull failed")

        result = await git_manager.pull_latest()

        assert result["success"] is False
        assert "pull failed" in result["message"].lower()
        assert result["commit_hash"] is None


class TestEnsureInitialized:
    """Tests for _ensure_initialized method"""

    @pytest.mark.asyncio
    async def test_operations_require_initialization(self, test_config):
        """Test that operations fail if manager not initialized"""
        manager = GitManager(test_config)
        # Don't call initialize()

        with pytest.raises(RuntimeError, match="not initialized"):
            await manager.commit_changes()

        with pytest.raises(RuntimeError, match="not initialized"):
            await manager.get_repo_status()

        with pytest.raises(RuntimeError, match="not initialized"):
            await manager.add_file("test.txt")
