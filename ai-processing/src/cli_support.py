from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, NamedTuple, Optional

from src.core.config import Config
from src.core.git_tracker import GitTracker

SUPPORTED_EXTENSIONS = (".md", ".txt", ".pdf", ".docx", ".html", ".htm")


class CliError(Exception):
    """Raised when CLI setup encounters a user-facing error."""


class RichResources(NamedTuple):
    console: Any
    Table: Any
    Panel: Any
    Progress: Any
    SpinnerColumn: Any
    TextColumn: Any
    BarColumn: Any
    TaskProgressColumn: Any
    TimeRemainingColumn: Any


def get_rich_resources() -> Optional[RichResources]:
    """Return rich rendering helpers when the library is available."""

    try:
        from rich.console import Console
        from rich.panel import Panel
        from rich.progress import (
            BarColumn,
            Progress,
            SpinnerColumn,
            TaskProgressColumn,
            TextColumn,
            TimeRemainingColumn,
        )
        from rich.table import Table
    except ImportError:
        return None

    console = Console()
    return RichResources(
        console,
        Table,
        Panel,
        Progress,
        SpinnerColumn,
        TextColumn,
        BarColumn,
        TaskProgressColumn,
        TimeRemainingColumn,
    )


@dataclass
class CliState:
    """Shared run-time state for CLI commands."""

    config: Config
    git_tracker: Optional[GitTracker]
    verbose: bool = False
    rich: Optional[RichResources] = None

    @property
    def console(self) -> Optional[Any]:
        return self.rich.console if self.rich else None

    def write(self, message: str = "") -> None:
        if self.rich:
            self.rich.console.print(message)
        else:
            print(message)

    def write_verbose(self, message: str) -> None:
        if self.verbose:
            self.write(message)


def load_config(config_path: Optional[Path]) -> Config:
    """Load and validate configuration, raising CliError on failure."""

    try:
        if config_path:
            config = Config.from_file(config_path)
        else:
            default_config = Path(__file__).resolve().parent.parent / "config.yaml"
            config = Config.from_file(default_config) if default_config.exists() else Config()
    except Exception as exc:  # pragma: no cover - Config already tested elsewhere
        raise CliError(f"Configuration error: {exc}") from exc

    issues = config.validate()
    if issues:
        summary = "\n".join(f"   - {issue}" for issue in issues)
        raise CliError(f"Configuration issues:\n{summary}")

    return config


def ensure_ollama_available(config: Config) -> None:
    """Ensure Ollama is reachable before starting heavy work."""

    try:
        import requests

        response = requests.get(f"{config.ollama_host}/api/tags", timeout=5)
    except Exception as exc:  # pragma: no cover - network failures are environment specific
        raise CliError(f"Cannot connect to Ollama at {config.ollama_host}: {exc}") from exc

    if response.status_code != 200:
        raise CliError(
            f"Cannot connect to Ollama at {config.ollama_host}: status {response.status_code}"
        )


def resolve_repository(target_path: Path, repo_path: Optional[Path]) -> Optional[Path]:
    """Resolve the git repository root for a target path."""

    if repo_path:
        root = repo_path.resolve()
        if not (root / ".git").exists():
            raise CliError(f"Path is not a git repository: {root}")
        return root

    current = target_path.resolve()
    if current.is_file():
        current = current.parent

    while True:
        if (current / ".git").exists():
            return current
        if current.parent == current:
            break
        current = current.parent

    return None


def create_state(
    config_path: Optional[Path],
    verbose: bool,
    git_tracker: Optional[GitTracker] = None,
) -> CliState:
    """Assemble CliState with configuration and optional git tracker."""

    config = load_config(config_path)
    rich = get_rich_resources()
    return CliState(config=config, git_tracker=git_tracker, verbose=verbose, rich=rich)
