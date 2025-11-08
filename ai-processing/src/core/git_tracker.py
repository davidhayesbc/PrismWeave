"""
Git integration utilities for tracking document changes and processing state
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import hashlib
from urllib.parse import quote, urlparse, urlunparse


class GitTracker:
    """Track git changes and document processing state"""
    
    def __init__(self, repo_path: Path, state_file: Optional[Path] = None):
        """
        Initialize GitTracker
        
        Args:
            repo_path: Path to the git repository
            state_file: Path to the processing state file (default: .prismweave/processing_state.json)
        """
        self.repo_path = Path(repo_path).resolve()
        self.state_file = state_file or (self.repo_path / ".prismweave" / "processing_state.json")
        
        # Ensure the state directory exists
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize git repository check
        if not self._is_git_repo():
            raise ValueError(f"Path {self.repo_path} is not a git repository")

        self.github_username, self.github_pat = self._load_git_credentials()
    
    def _is_git_repo(self) -> bool:
        """Check if the path is a git repository"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.returncode == 0
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def get_current_commit_hash(self) -> str:
        """Get the current git commit hash"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to get current commit hash: {e}")
    
    def get_file_last_commit_hash(self, file_path: Path) -> Optional[str]:
        """
        Get the last commit hash that modified a specific file
        
        Args:
            file_path: Path to the file (relative to repo root)
            
        Returns:
            Commit hash or None if file not in git history
        """
        try:
            # Convert to relative path from repo root
            relative_path = file_path.relative_to(self.repo_path)
            
            result = subprocess.run(
                ["git", "log", "-1", "--format=%H", "--", str(relative_path)],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            commit_hash = result.stdout.strip()
            return commit_hash if commit_hash else None
            
        except (subprocess.CalledProcessError, ValueError):
            return None
    
    def get_changed_files(self, since_commit: Optional[str] = None, file_extensions: Optional[Set[str]] = None) -> List[Path]:
        """
        Get list of files that have changed since a specific commit
        
        Args:
            since_commit: Commit hash to compare from (None for all files)
            file_extensions: Set of file extensions to filter (.md, .pdf, etc.)
            
        Returns:
            List of changed file paths
        """
        try:
            if since_commit:
                # Get files changed since specific commit
                cmd = ["git", "diff", "--name-only", f"{since_commit}..HEAD"]
            else:
                # Get all tracked files
                cmd = ["git", "ls-files"]
            
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            changed_files = []
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                
                file_path = self.repo_path / line
                
                # Check if file exists (might have been deleted)
                if not file_path.exists():
                    continue
                
                # Filter by file extensions if specified
                if file_extensions and file_path.suffix.lower() not in file_extensions:
                    continue
                
                changed_files.append(file_path)
            
            return changed_files
            
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to get changed files: {e}")
    
    def load_processing_state(self) -> Dict:
        """Load the processing state from the state file"""
        if not self.state_file.exists():
            return {
                "version": "1.0.0",
                "last_processed_commit": None,
                "processed_files": {},
                "last_update": None
            }
        
        try:
            with open(self.state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Failed to load processing state: {e}")
            return {
                "version": "1.0.0",
                "last_processed_commit": None,
                "processed_files": {},
                "last_update": None
            }
    
    def save_processing_state(self, state: Dict) -> None:
        """Save the processing state to the state file"""
        state["last_update"] = datetime.now().isoformat()
        
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
        except IOError as e:
            raise RuntimeError(f"Failed to save processing state: {e}")
    
    def get_file_content_hash(self, file_path: Path) -> str:
        """
        Generate a content hash for a file to detect content changes
        
        Args:
            file_path: Path to the file
            
        Returns:
            SHA256 hash of the file content
        """
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            return hashlib.sha256(content).hexdigest()
        except IOError as e:
            raise RuntimeError(f"Failed to read file {file_path}: {e}")
    
    def mark_file_processed(self, file_path: Path, commit_hash: Optional[str] = None) -> None:
        """
        Mark a file as processed in the state tracking
        
        Args:
            file_path: Path to the processed file
            commit_hash: Git commit hash when file was processed (default: current HEAD)
        """
        state = self.load_processing_state()
        
        if commit_hash is None:
            commit_hash = self.get_current_commit_hash()
        
        relative_path = str(file_path.relative_to(self.repo_path))
        content_hash = self.get_file_content_hash(file_path)
        
        state["processed_files"][relative_path] = {
            "processed_at": datetime.now().isoformat(),
            "commit_hash": commit_hash,
            "content_hash": content_hash,
            "file_size": file_path.stat().st_size,
            "last_modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
        }
        
        self.save_processing_state(state)
    
    def is_file_processed(self, file_path: Path) -> bool:
        """
        Check if a file has been processed and hasn't changed since
        
        Args:
            file_path: Path to check
            
        Returns:
            True if file has been processed and is unchanged
        """
        state = self.load_processing_state()
        relative_path = str(file_path.relative_to(self.repo_path))
        
        if relative_path not in state["processed_files"]:
            return False
        
        file_info = state["processed_files"][relative_path]
        
        # Check if file content has changed
        try:
            current_content_hash = self.get_file_content_hash(file_path)
            return current_content_hash == file_info.get("content_hash")
        except RuntimeError:
            # File might have been deleted or is inaccessible
            return False
    
    def get_unprocessed_files(self, file_extensions: Optional[Set[str]] = None) -> List[Path]:
        """
        Get list of files that need processing (new or changed)
        
        Args:
            file_extensions: Set of file extensions to consider
            
        Returns:
            List of file paths that need processing
        """
        # Get all files in the repository
        all_files = self.get_changed_files(since_commit=None, file_extensions=file_extensions)
        
        # Filter to only unprocessed files
        unprocessed_files = []
        for file_path in all_files:
            if not self.is_file_processed(file_path):
                unprocessed_files.append(file_path)
        
        return unprocessed_files
    
    def get_processing_summary(self) -> Dict:
        """
        Get a summary of processing state
        
        Returns:
            Dictionary with processing statistics
        """
        state = self.load_processing_state()
        
        # Count supported files
        supported_extensions = {'.md', '.txt', '.pdf', '.docx', '.html', '.htm'}
        all_files = self.get_changed_files(since_commit=None, file_extensions=supported_extensions)
        unprocessed_files = self.get_unprocessed_files(file_extensions=supported_extensions)
        
        return {
            "total_tracked_files": len(all_files),
            "processed_files": len(state["processed_files"]),
            "unprocessed_files": len(unprocessed_files),
            "last_processed_commit": state.get("last_processed_commit"),
            "current_commit": self.get_current_commit_hash(),
            "last_update": state.get("last_update"),
            "state_file": str(self.state_file)
        }
    
    def reset_processing_state(self) -> None:
        """Reset all processing state (marks all files as unprocessed)"""
        state = {
            "version": "1.0.0",
            "last_processed_commit": None,
            "processed_files": {},
            "last_update": None
        }
        self.save_processing_state(state)
    
    def update_last_processed_commit(self) -> None:
        """Update the last processed commit to current HEAD"""
        state = self.load_processing_state()
        state["last_processed_commit"] = self.get_current_commit_hash()
        self.save_processing_state(state)

    def _load_git_credentials(self) -> Tuple[Optional[str], Optional[str]]:
        """Load GitHub credentials from a .env file within the repository."""

        env_path = self.repo_path / ".env"

        if not env_path.exists():
            return None, None

        credentials: Dict[str, str] = {}

        try:
            with env_path.open("r", encoding="utf-8") as env_file:
                for raw_line in env_file:
                    line = raw_line.strip()
                    if not line or line.startswith("#"):
                        continue

                    if "=" not in line:
                        continue

                    key, value = line.split("=", 1)
                    credentials[key.strip()] = value.strip()
        except IOError:
            return None, None

        username = credentials.get("GITHUB_USERNAME") or credentials.get("GIT_USERNAME")
        token = credentials.get("GITHUB_PAT") or credentials.get("GITHUB_TOKEN") or credentials.get("GIT_PAT")

        return username or None, token or None

    def _build_authenticated_remote(self, remote: str) -> Optional[str]:
        """Return a remote URL injected with credentials when available."""

        if not self.github_username or not self.github_pat:
            return None

        try:
            result = subprocess.run(
                ["git", "remote", "get-url", remote],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
            )
        except subprocess.CalledProcessError:
            return None

        remote_url = result.stdout.strip()
        if not remote_url:
            return None

        parsed = urlparse(remote_url)

        if parsed.scheme not in {"http", "https"}:
            return None

        hostname = parsed.hostname or ""
        if not hostname:
            return None

        netloc = hostname
        if parsed.port:
            netloc = f"{netloc}:{parsed.port}"

        username = quote(self.github_username, safe="")
        token = quote(self.github_pat, safe="")

        netloc = f"{username}:{token}@{netloc}"

        return urlunparse(
            (
                parsed.scheme,
                netloc,
                parsed.path,
                parsed.params,
                parsed.query,
                parsed.fragment,
            )
        )

    def pull_latest(self, remote: Optional[str] = "origin", branch: Optional[str] = None, *, ff_only: bool = True) -> bool:
        """Pull the latest changes from the remote repository."""

        # If no branch specified, get the current branch
        if not branch:
            try:
                branch_result = subprocess.run(
                    ["git", "branch", "--show-current"],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True,
                    check=True,
                )
                branch = branch_result.stdout.strip()
            except subprocess.CalledProcessError:
                # If we can't get current branch, use 'main' as default
                branch = "main"

        cmd = ["git", "pull"]
        if ff_only:
            cmd.append("--ff-only")

        if remote:
            remote_arg = self._build_authenticated_remote(remote) or remote
            cmd.append(remote_arg)
            cmd.append(branch)

        try:
            subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
            )
            return True
        except subprocess.CalledProcessError as exc:
            stderr = exc.stderr.strip() if exc.stderr else str(exc)
            raise RuntimeError(f"Failed to pull latest changes: {stderr}")

    def commit_processing_state(self, message: Optional[str] = None) -> bool:
        """Commit the processing state file if it has changed."""

        relative_state = str(self.state_file.relative_to(self.repo_path))

        try:
            status_result = subprocess.run(
                ["git", "status", "--porcelain", "--", relative_state],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
            )
        except subprocess.CalledProcessError as exc:
            stderr = exc.stderr.strip() if exc.stderr else str(exc)
            raise RuntimeError(f"Failed to check processing state status: {stderr}")

        if not status_result.stdout.strip():
            return False  # No changes to commit

        try:
            subprocess.run(
                ["git", "add", relative_state],
                cwd=self.repo_path,
                check=True,
            )
        except subprocess.CalledProcessError as exc:
            stderr = exc.stderr.strip() if exc.stderr else str(exc)
            raise RuntimeError(f"Failed to stage processing state: {stderr}")

        commit_message = message or "chore: update processing state"

        try:
            subprocess.run(
                ["git", "commit", "-m", commit_message],
                cwd=self.repo_path,
                check=True,
            )
            return True
        except subprocess.CalledProcessError as exc:
            stderr = exc.stderr.strip() if exc.stderr else str(exc)
            raise RuntimeError(f"Failed to commit processing state: {stderr}")
