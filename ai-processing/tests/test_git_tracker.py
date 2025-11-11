"""
Tests for GitTracker - Git integration and incremental processing
"""

import json
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.core.git_tracker import GitTracker


@pytest.fixture
def git_repo():
    """Create a temporary git repository for testing"""
    with tempfile.TemporaryDirectory() as temp_dir:
        repo_path = Path(temp_dir)

        # Initialize git repository
        subprocess.run(["git", "init"], cwd=repo_path, check=True, capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"], cwd=repo_path, check=True, capture_output=True
        )
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo_path, check=True, capture_output=True)

        # Create initial commit
        readme = repo_path / "README.md"
        readme.write_text("# Test Repository\n\nThis is a test.")
        subprocess.run(["git", "add", "README.md"], cwd=repo_path, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo_path, check=True, capture_output=True)

        yield repo_path


class TestGitTrackerInitialization:
    """Test GitTracker initialization and setup"""

    def test_tracker_initialization(self, git_repo):
        """Test that GitTracker can be initialized with a valid git repo"""
        tracker = GitTracker(git_repo)

        assert tracker.repo_path == git_repo.resolve()
        assert tracker.state_file.parent.name == ".prismweave"
        assert tracker.state_file.name == "processing_state.json"

    def test_tracker_creates_state_directory(self, git_repo):
        """Test that GitTracker creates .prismweave directory"""
        tracker = GitTracker(git_repo)

        state_dir = git_repo / ".prismweave"
        assert state_dir.exists()
        assert state_dir.is_dir()

    def test_tracker_fails_on_non_git_directory(self):
        """Test that GitTracker raises error for non-git directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            with pytest.raises(ValueError, match="not a git repository"):
                GitTracker(Path(temp_dir))

    def test_custom_state_file_path(self, git_repo):
        """Test using custom state file path"""
        custom_state = git_repo / "custom_state.json"
        tracker = GitTracker(git_repo, state_file=custom_state)

        assert tracker.state_file == custom_state


class TestGitOperations:
    """Test basic git operations"""

    def test_get_current_commit_hash(self, git_repo):
        """Test getting current commit hash"""
        tracker = GitTracker(git_repo)

        commit_hash = tracker.get_current_commit_hash()

        assert commit_hash is not None
        assert len(commit_hash) == 40  # SHA1 hash length
        assert all(c in "0123456789abcdef" for c in commit_hash)

    def test_get_file_last_commit_hash(self, git_repo):
        """Test getting last commit hash for a file"""
        tracker = GitTracker(git_repo)

        readme = git_repo / "README.md"
        commit_hash = tracker.get_file_last_commit_hash(readme)

        assert commit_hash is not None
        assert len(commit_hash) == 40

    def test_get_file_last_commit_hash_nonexistent(self, git_repo):
        """Test getting commit hash for non-existent file"""
        tracker = GitTracker(git_repo)

        nonexistent = git_repo / "nonexistent.md"
        commit_hash = tracker.get_file_last_commit_hash(nonexistent)

        assert commit_hash is None

    def test_get_file_content_hash(self, git_repo):
        """Test generating content hash for a file"""
        tracker = GitTracker(git_repo)

        # Create a test file
        test_file = git_repo / "test.md"
        test_file.write_text("Test content")

        content_hash = tracker.get_file_content_hash(test_file)

        assert content_hash is not None
        assert len(content_hash) == 64  # SHA256 hash length

        # Same content should produce same hash
        content_hash2 = tracker.get_file_content_hash(test_file)
        assert content_hash == content_hash2

        # Different content should produce different hash
        test_file.write_text("Different content")
        content_hash3 = tracker.get_file_content_hash(test_file)
        assert content_hash != content_hash3


class TestFileChanges:
    """Test file change detection"""

    def test_get_changed_files_all(self, git_repo):
        """Test getting all tracked files"""
        tracker = GitTracker(git_repo)

        files = tracker.get_changed_files(since_commit=None)

        assert len(files) >= 1
        assert any(f.name == "README.md" for f in files)

    def test_get_changed_files_with_filter(self, git_repo):
        """Test getting files with extension filter"""
        tracker = GitTracker(git_repo)

        # Add multiple file types
        (git_repo / "test.md").write_text("Markdown")
        (git_repo / "test.txt").write_text("Text")
        (git_repo / "test.pdf").write_text("PDF")
        subprocess.run(["git", "add", "."], cwd=git_repo, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Add test files"], cwd=git_repo, check=True, capture_output=True)

        # Filter for markdown files only
        md_files = tracker.get_changed_files(since_commit=None, file_extensions={".md"})

        assert all(f.suffix == ".md" for f in md_files)
        assert len(md_files) >= 2  # README.md and test.md

    def test_get_changed_files_since_commit(self, git_repo):
        """Test getting files changed since a specific commit"""
        tracker = GitTracker(git_repo)

        # Get initial commit hash
        initial_commit = tracker.get_current_commit_hash()

        # Add new file and commit
        new_file = git_repo / "new.md"
        new_file.write_text("New file")
        subprocess.run(["git", "add", "new.md"], cwd=git_repo, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Add new file"], cwd=git_repo, check=True, capture_output=True)

        # Get files changed since initial commit
        changed_files = tracker.get_changed_files(since_commit=initial_commit)

        assert len(changed_files) == 1
        assert changed_files[0].name == "new.md"


class TestProcessingState:
    """Test processing state management"""

    def test_load_processing_state_initial(self, git_repo):
        """Test loading initial (empty) processing state"""
        tracker = GitTracker(git_repo)

        state = tracker.load_processing_state()

        assert state["version"] == "1.0.0"
        assert state["last_processed_commit"] is None
        assert state["processed_files"] == {}
        assert state["last_update"] is None

    def test_save_and_load_processing_state(self, git_repo):
        """Test saving and loading processing state"""
        tracker = GitTracker(git_repo)

        # Create and save state
        state = {
            "version": "1.0.0",
            "last_processed_commit": "abc123",
            "processed_files": {"test.md": {"processed_at": "2025-11-03"}},
            "last_update": None,
        }

        tracker.save_processing_state(state)

        # Load state
        loaded_state = tracker.load_processing_state()

        assert loaded_state["version"] == "1.0.0"
        assert loaded_state["last_processed_commit"] == "abc123"
        assert "test.md" in loaded_state["processed_files"]
        assert loaded_state["last_update"] is not None

    def test_mark_file_processed(self, git_repo):
        """Test marking a file as processed"""
        tracker = GitTracker(git_repo)

        test_file = git_repo / "test.md"
        test_file.write_text("Test content")

        tracker.mark_file_processed(test_file)

        # Verify state was saved
        state = tracker.load_processing_state()
        relative_path = str(test_file.relative_to(git_repo))

        assert relative_path in state["processed_files"]
        assert "processed_at" in state["processed_files"][relative_path]
        assert "commit_hash" in state["processed_files"][relative_path]
        assert "content_hash" in state["processed_files"][relative_path]

    def test_is_file_processed(self, git_repo):
        """Test checking if file has been processed"""
        tracker = GitTracker(git_repo)

        test_file = git_repo / "test.md"
        test_file.write_text("Test content")

        # File should not be processed initially
        assert tracker.is_file_processed(test_file) == False

        # Mark file as processed
        tracker.mark_file_processed(test_file)

        # File should now be marked as processed
        assert tracker.is_file_processed(test_file) == True

    def test_is_file_processed_detects_changes(self, git_repo):
        """Test that is_file_processed detects content changes"""
        tracker = GitTracker(git_repo)

        test_file = git_repo / "test.md"
        test_file.write_text("Original content")

        # Mark as processed
        tracker.mark_file_processed(test_file)
        assert tracker.is_file_processed(test_file) == True

        # Change content
        test_file.write_text("Modified content")

        # Should now detect as unprocessed due to content change
        assert tracker.is_file_processed(test_file) == False


class TestUnprocessedFiles:
    """Test finding unprocessed files"""

    def test_get_unprocessed_files_all_new(self, git_repo):
        """Test getting unprocessed files when all are new"""
        tracker = GitTracker(git_repo)

        # Add some test files
        (git_repo / "doc1.md").write_text("Doc 1")
        (git_repo / "doc2.md").write_text("Doc 2")
        subprocess.run(["git", "add", "."], cwd=git_repo, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Add docs"], cwd=git_repo, check=True, capture_output=True)

        unprocessed = tracker.get_unprocessed_files(file_extensions={".md"})

        # All files should be unprocessed
        assert len(unprocessed) >= 3  # README.md, doc1.md, doc2.md

    def test_get_unprocessed_files_some_processed(self, git_repo):
        """Test getting unprocessed files when some are already processed"""
        tracker = GitTracker(git_repo)

        # Add test files
        file1 = git_repo / "doc1.md"
        file2 = git_repo / "doc2.md"
        file1.write_text("Doc 1")
        file2.write_text("Doc 2")
        subprocess.run(["git", "add", "."], cwd=git_repo, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Add docs"], cwd=git_repo, check=True, capture_output=True)

        # Mark one file as processed
        tracker.mark_file_processed(file1)

        unprocessed = tracker.get_unprocessed_files(file_extensions={".md"})

        # Should not include the processed file
        assert file1 not in unprocessed
        assert file2 in unprocessed


class TestProcessingSummary:
    """Test processing summary functionality"""

    def test_get_processing_summary(self, git_repo):
        """Test getting processing summary"""
        tracker = GitTracker(git_repo)

        # Add test files
        (git_repo / "doc1.md").write_text("Doc 1")
        (git_repo / "doc2.md").write_text("Doc 2")
        subprocess.run(["git", "add", "."], cwd=git_repo, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Add docs"], cwd=git_repo, check=True, capture_output=True)

        # Mark one file as processed
        tracker.mark_file_processed(git_repo / "doc1.md")

        summary = tracker.get_processing_summary()

        assert "total_tracked_files" in summary
        assert "processed_files" in summary
        assert "unprocessed_files" in summary
        assert "current_commit" in summary
        assert summary["processed_files"] == 1
        assert summary["unprocessed_files"] > 0

    def test_reset_processing_state(self, git_repo):
        """Test resetting processing state"""
        tracker = GitTracker(git_repo)

        # Mark some files as processed
        test_file = git_repo / "test.md"
        test_file.write_text("Test")
        tracker.mark_file_processed(test_file)

        # Verify file is marked as processed
        assert tracker.is_file_processed(test_file) == True

        # Reset state
        tracker.reset_processing_state()

        # File should no longer be marked as processed
        assert tracker.is_file_processed(test_file) == False

        # State should be empty
        state = tracker.load_processing_state()
        assert state["processed_files"] == {}
        assert state["last_processed_commit"] is None

    def test_update_last_processed_commit(self, git_repo):
        """Test updating last processed commit"""
        tracker = GitTracker(git_repo)

        current_commit = tracker.get_current_commit_hash()

        tracker.update_last_processed_commit()

        state = tracker.load_processing_state()
        assert state["last_processed_commit"] == current_commit


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
