"""
Git Manager for PrismWeave MCP Server

Wraps GitTracker functionality with MCP-compatible interface for version control operations.
"""

import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional

from src.core.config import Config
from src.core.git_tracker import GitTracker


class GitManager:
    """Manager for git operations on PrismWeaveDocs repository"""

    def __init__(self, config: Config):
        """
        Initialize Git Manager

        Args:
            config: Configuration object with paths
        """
        self.config = config
        self._git_tracker: Optional[GitTracker] = None
        self._repo_path: Optional[Path] = None

    async def initialize(self) -> None:
        """
        Initialize git tracker with repository path

        Raises:
            ValueError: If repository path is not a git repository
        """
        # Get repository path from config
        docs_root = Path(self.config.mcp.paths.documents_root).resolve()

        # Check if it's a git repository
        if not self._is_git_repo(docs_root):
            raise ValueError(f"Path {docs_root} is not a git repository")

        self._repo_path = docs_root
        self._git_tracker = GitTracker(repo_path=self._repo_path)

    def _is_git_repo(self, path: Path) -> bool:
        """Check if path is a git repository"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"], cwd=path, capture_output=True, text=True, check=True
            )
            return result.returncode == 0
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def _ensure_initialized(self) -> None:
        """
        Ensure git tracker is initialized

        Raises:
            RuntimeError: If git manager has not been initialized
        """
        if self._git_tracker is None or self._repo_path is None:
            raise RuntimeError("Git manager not initialized. Call initialize() first.")

    @property
    def git_tracker(self) -> GitTracker:
        """
        Get the initialized git tracker

        Returns:
            GitTracker instance

        Raises:
            RuntimeError: If git manager has not been initialized
        """
        if self._git_tracker is None:
            raise RuntimeError("Git manager not initialized. Call initialize() first.")
        return self._git_tracker

    @property
    def repo_path(self) -> Path:
        """
        Get the repository path

        Returns:
            Path to the git repository

        Raises:
            RuntimeError: If git manager has not been initialized
        """
        if self._repo_path is None:
            raise RuntimeError("Git manager not initialized. Call initialize() first.")
        return self._repo_path

    async def commit_changes(
        self,
        files: Optional[list[str]] = None,
        message: Optional[str] = None,
        push: bool = False,
        remote: str = "origin",
        branch: Optional[str] = None,
    ) -> dict:
        """
        Commit changes to git repository

        Args:
            files: List of file paths to commit (relative to repo root). If None, commits all changes.
            message: Commit message. If None, generates default message.
            push: Whether to push to remote after commit
            remote: Remote name (default: origin)
            branch: Branch name (default: current branch)

        Returns:
            Dict with:
                - success (bool): Whether operation succeeded
                - message (str): Status message
                - commit_hash (str): New commit hash if successful
                - files_committed (int): Number of files committed
                - pushed (bool): Whether push was successful (if requested)
        """
        self._ensure_initialized()

        try:
            # Check if there are any changes
            status_result = subprocess.run(
                ["git", "status", "--porcelain"], cwd=self.repo_path, capture_output=True, text=True, check=True
            )

            if not status_result.stdout.strip():
                return {
                    "success": True,
                    "message": "No changes to commit",
                    "commit_hash": self.git_tracker.get_current_commit_hash(),
                    "files_committed": 0,
                    "pushed": False,
                }

            # Stage files
            if files:
                # Stage specific files
                for file_path in files:
                    subprocess.run(["git", "add", file_path], cwd=self.repo_path, check=True)
            else:
                # Stage all changes
                subprocess.run(["git", "add", "-A"], cwd=self.repo_path, check=True)

            # Check how many files were staged
            staged_result = subprocess.run(
                ["git", "diff", "--cached", "--name-only"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
            )

            staged_files = [f for f in staged_result.stdout.strip().split("\n") if f]

            if not staged_files:
                return {
                    "success": True,
                    "message": "No changes staged for commit",
                    "commit_hash": self.git_tracker.get_current_commit_hash(),
                    "files_committed": 0,
                    "pushed": False,
                }

            # Generate commit message if not provided
            if not message:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                message = f"chore: update documents ({len(staged_files)} files) - {timestamp}"

            # Commit changes
            subprocess.run(["git", "commit", "-m", message], cwd=self.repo_path, check=True)

            new_commit_hash = self.git_tracker.get_current_commit_hash()

            result = {
                "success": True,
                "message": f"Successfully committed {len(staged_files)} file(s)",
                "commit_hash": new_commit_hash,
                "files_committed": len(staged_files),
                "pushed": False,
            }

            # Push if requested
            if push:
                push_result = await self._push_to_remote(remote, branch)
                result["pushed"] = push_result["success"]
                if not push_result["success"]:
                    result["message"] += f" (push failed: {push_result['message']})"

            return result

        except subprocess.CalledProcessError as e:
            stderr = e.stderr.strip() if e.stderr else str(e)
            return {
                "success": False,
                "message": f"Git commit failed: {stderr}",
                "commit_hash": None,
                "files_committed": 0,
                "pushed": False,
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Unexpected error during commit: {str(e)}",
                "commit_hash": None,
                "files_committed": 0,
                "pushed": False,
            }

    async def _push_to_remote(self, remote: str, branch: Optional[str]) -> dict:
        """
        Push commits to remote repository

        Args:
            remote: Remote name
            branch: Branch name (if None, uses current branch)

        Returns:
            Dict with success status and message
        """
        try:
            # Get current branch if not specified
            if not branch:
                branch_result = subprocess.run(
                    ["git", "branch", "--show-current"], cwd=self.repo_path, capture_output=True, text=True, check=True
                )
                branch = branch_result.stdout.strip()

            # Try to build authenticated remote URL
            authenticated_remote = self.git_tracker._build_authenticated_remote(remote)
            remote_arg = authenticated_remote or remote

            # Push to remote
            subprocess.run(
                ["git", "push", remote_arg, branch], cwd=self.repo_path, capture_output=True, text=True, check=True
            )

            return {"success": True, "message": f"Successfully pushed to {remote}/{branch}"}

        except subprocess.CalledProcessError as e:
            stderr = e.stderr.strip() if e.stderr else str(e)
            return {"success": False, "message": f"Push failed: {stderr}"}

    async def get_repo_status(self) -> dict:
        """
        Get current repository status

        Returns:
            Dict with:
                - success (bool): Whether operation succeeded
                - branch (str): Current branch name
                - commit_hash (str): Current commit hash
                - has_uncommitted_changes (bool): Whether there are uncommitted changes
                - uncommitted_files (list): List of uncommitted files
                - has_untracked_files (bool): Whether there are untracked files
                - untracked_files (list): List of untracked files
                - ahead_of_remote (int): Number of commits ahead of remote
                - behind_remote (int): Number of commits behind remote
                - message (str): Status message
        """
        self._ensure_initialized()

        try:
            # Get current branch
            branch_result = subprocess.run(
                ["git", "branch", "--show-current"], cwd=self.repo_path, capture_output=True, text=True, check=True
            )
            branch = branch_result.stdout.strip()

            # Get current commit hash
            commit_hash = self.git_tracker.get_current_commit_hash()

            # Get status
            status_result = subprocess.run(
                ["git", "status", "--porcelain"], cwd=self.repo_path, capture_output=True, text=True, check=True
            )

            # Parse status output
            uncommitted_files = []
            untracked_files = []

            for line in status_result.stdout.strip().split("\n"):
                if not line:
                    continue

                status_code = line[:2]
                file_path = line[3:]

                if status_code.strip() == "??":
                    untracked_files.append(file_path)
                else:
                    uncommitted_files.append(file_path)

            # Check remote tracking
            ahead = 0
            behind = 0

            try:
                tracking_result = subprocess.run(
                    ["git", "rev-list", "--left-right", "--count", "HEAD...@{u}"],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True,
                    check=True,
                )

                counts = tracking_result.stdout.strip().split()
                if len(counts) == 2:
                    ahead = int(counts[0])
                    behind = int(counts[1])
            except subprocess.CalledProcessError:
                # No upstream branch configured or other error
                pass

            return {
                "success": True,
                "branch": branch,
                "commit_hash": commit_hash,
                "has_uncommitted_changes": len(uncommitted_files) > 0,
                "uncommitted_files": uncommitted_files,
                "has_untracked_files": len(untracked_files) > 0,
                "untracked_files": untracked_files,
                "ahead_of_remote": ahead,
                "behind_remote": behind,
                "message": "Repository status retrieved successfully",
            }

        except subprocess.CalledProcessError as e:
            stderr = e.stderr.strip() if e.stderr else str(e)
            return {"success": False, "message": f"Failed to get repository status: {stderr}"}
        except Exception as e:
            return {"success": False, "message": f"Unexpected error getting status: {str(e)}"}

    async def add_file(self, file_path: str) -> dict:
        """
        Stage a file for commit

        Args:
            file_path: Path to file (relative to repository root)

        Returns:
            Dict with:
                - success (bool): Whether operation succeeded
                - message (str): Status message
                - file_path (str): Path that was staged
        """
        self._ensure_initialized()

        try:
            # Check if file exists
            full_path = self.repo_path / file_path
            if not full_path.exists():
                return {"success": False, "message": f"File not found: {file_path}", "file_path": file_path}

            # Stage the file
            subprocess.run(["git", "add", file_path], cwd=self.repo_path, check=True)

            return {"success": True, "message": f"Successfully staged file: {file_path}", "file_path": file_path}

        except subprocess.CalledProcessError as e:
            stderr = e.stderr.strip() if e.stderr else str(e)
            return {"success": False, "message": f"Failed to stage file: {stderr}", "file_path": file_path}
        except Exception as e:
            return {"success": False, "message": f"Unexpected error staging file: {str(e)}", "file_path": file_path}

    async def pull_latest(self, remote: str = "origin", branch: Optional[str] = None, ff_only: bool = True) -> dict:
        """
        Pull latest changes from remote repository

        Args:
            remote: Remote name (default: origin)
            branch: Branch name (default: current branch)
            ff_only: Only allow fast-forward merges

        Returns:
            Dict with:
                - success (bool): Whether operation succeeded
                - message (str): Status message
                - commit_hash (str): New commit hash after pull
        """
        self._ensure_initialized()

        try:
            # Use GitTracker's pull method
            self.git_tracker.pull_latest(remote=remote, branch=branch, ff_only=ff_only)

            new_commit_hash = self.git_tracker.get_current_commit_hash()

            return {"success": True, "message": f"Successfully pulled from {remote}", "commit_hash": new_commit_hash}

        except RuntimeError as e:
            return {"success": False, "message": str(e), "commit_hash": None}
        except Exception as e:
            return {"success": False, "message": f"Unexpected error during pull: {str(e)}", "commit_hash": None}
