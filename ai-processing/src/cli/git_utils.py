"""Git repository utilities for CLI."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from src.cli_support import CliError, CliState
from src.core.git_tracker import GitTracker


def auto_detect_repository() -> Optional[Path]:
    """Auto-detect a git repository from common locations."""
    current = Path.cwd()
    if (current / ".git").exists():
        return current

    for candidate in (
        current / "PrismWeaveDocs",
        current.parent / "PrismWeaveDocs",
        current / "documents",
        current / "docs",
    ):
        if (candidate / ".git").exists():
            return candidate
    return None


def initialize_git_tracker(
    repo_root: Optional[Path],
    *,
    verbose: bool,
    strict: bool,
) -> Optional[GitTracker]:
    """Initialize git tracking for the repository."""
    if not repo_root:
        return None

    try:
        tracker = GitTracker(repo_root)
    except (OSError, ValueError, RuntimeError) as exc:  # pragma: no cover - depends on git setup
        if strict:
            raise CliError(f"Failed to initialize git tracking: {exc}") from exc
        print(f"⚠️  Warning: Git tracking not available: {exc}")
        return None

    if verbose:
        print("🔁 Pulling latest changes from remote...")
    try:
        tracker.pull_latest()
        if verbose:
            print("   ✅ Repository up to date")
    except (OSError, RuntimeError) as exc:  # pragma: no cover - depends on git setup
        print(f"⚠️  Warning: Failed to pull latest changes: {exc}")

    return tracker


def print_git_summary(state: CliState, repo_root: Path) -> None:
    """Print git repository processing summary."""
    if not state.verbose or not state.git_tracker:
        return
    summary = state.git_tracker.get_processing_summary()
    state.write_verbose(f"🔄 Git repository: {repo_root}")
    state.write_verbose(
        f"📊 Processing state: {summary['processed_files']} processed, {summary['unprocessed_files']} unprocessed"
    )
    state.write_verbose("")
