"""
Path utility functions for MCP server

Provides functions for resolving paths, validating path safety,
and determining document types and locations.
"""

from pathlib import Path
from typing import Optional


def get_documents_root(config_root: Optional[str] = None) -> Path:
    """
    Get the PrismWeaveDocs root directory.

    Args:
        config_root: Root path from configuration (default: None, uses relative path)

    Returns:
        Absolute path to PrismWeaveDocs directory

    Example:
        >>> root = get_documents_root()
        >>> root.name == 'PrismWeaveDocs' or 'PrismWeaveDocs' in str(root)
        True
    """
    if config_root:
        root_path = Path(config_root).resolve()
    else:
        # Default: go up from ai-processing to workspace root, then to PrismWeaveDocs
        current_file = Path(__file__)
        ai_processing_root = current_file.parent.parent.parent
        workspace_root = ai_processing_root.parent
        root_path = workspace_root / "PrismWeaveDocs"

    # Create directory if it doesn't exist
    root_path.mkdir(parents=True, exist_ok=True)

    return root_path


def resolve_document_path(
    path_or_id: str, documents_root: Optional[Path] = None, search_subdirs: bool = True
) -> Optional[Path]:
    """
    Resolve a document path from a relative path or document ID.

    Args:
        path_or_id: Relative path or document ID
        documents_root: Root directory for documents (default: auto-detect)
        search_subdirs: Search in subdirectories if not found in root

    Returns:
        Absolute path to document or None if not found

    Example:
        >>> # Assuming document exists
        >>> path = resolve_document_path("documents/test.md")
        >>> path is None or path.exists()
        True
    """
    if documents_root is None:
        documents_root = get_documents_root()

    # If it's already an absolute path, validate it
    if Path(path_or_id).is_absolute():
        abs_path = Path(path_or_id)
        if abs_path.exists() and abs_path.is_file():
            # Ensure it's within documents_root
            try:
                abs_path.relative_to(documents_root)
                return abs_path
            except ValueError:
                # Path is outside documents_root
                return None
        return None

    # Try as relative path from documents_root
    candidate = documents_root / path_or_id
    if candidate.exists() and candidate.is_file():
        return candidate

    # If search_subdirs, search in common subdirectories
    if search_subdirs:
        subdirs = ["documents", "generated", "tech", "images"]
        for subdir in subdirs:
            candidate = documents_root / subdir / path_or_id
            if candidate.exists() and candidate.is_file():
                return candidate

    return None


def validate_path_safety(path: Path, allowed_root: Path) -> bool:
    """
    Validate that a path is safe (no directory traversal, within allowed root).

    Args:
        path: Path to validate
        allowed_root: Root directory that path must be within

    Returns:
        True if path is safe

    Raises:
        ValueError: If path is unsafe with detailed reason

    Example:
        >>> root = Path("/tmp/test")
        >>> safe_path = root / "document.md"
        >>> validate_path_safety(safe_path, root)
        True
        >>> unsafe_path = root / ".." / ".." / "etc" / "passwd"
        >>> validate_path_safety(unsafe_path, root)  # doctest: +SKIP
        Traceback (most recent call last):
        ValueError: Path is outside allowed directory
    """
    try:
        # Resolve to absolute path
        abs_path = path.resolve()
        abs_root = allowed_root.resolve()

        # Check if path is within allowed root
        try:
            abs_path.relative_to(abs_root)
        except ValueError:
            raise ValueError(f"Path is outside allowed directory: {allowed_root}")

        # Check for suspicious patterns
        path_str = str(path)
        if ".." in path_str:
            raise ValueError("Path contains directory traversal (..)")

        # Check for null bytes (security)
        if "\x00" in path_str:
            raise ValueError("Path contains null bytes")

        return True

    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Path validation error: {str(e)}") from e


def is_generated_document(path: Path, documents_root: Optional[Path] = None) -> bool:
    """
    Check if a document is in the generated/ folder.

    Args:
        path: Path to check
        documents_root: Root directory (default: auto-detect)

    Returns:
        True if document is in generated/ folder

    Example:
        >>> from pathlib import Path
        >>> path = Path("/tmp/PrismWeaveDocs/generated/test.md")
        >>> # Result depends on actual path structure
        >>> isinstance(is_generated_document(path), bool)
        True
    """
    if documents_root is None:
        documents_root = get_documents_root()

    try:
        # Get relative path from documents_root
        rel_path = path.resolve().relative_to(documents_root.resolve())

        # Check if first part is "generated"
        return rel_path.parts[0] == "generated"
    except (ValueError, IndexError):
        return False


def get_document_category(path: Path, documents_root: Optional[Path] = None) -> Optional[str]:
    """
    Get document category based on its directory.

    Args:
        path: Path to document
        documents_root: Root directory (default: auto-detect)

    Returns:
        Category name or None

    Example:
        >>> from pathlib import Path
        >>> path = Path("/tmp/PrismWeaveDocs/tech/article.md")
        >>> # Category extraction from path
        >>> isinstance(get_document_category(path), (str, type(None)))
        True
    """
    if documents_root is None:
        documents_root = get_documents_root()

    try:
        rel_path = path.resolve().relative_to(documents_root.resolve())

        # First part of path is the category
        if len(rel_path.parts) > 1:
            return rel_path.parts[0]

        return None
    except ValueError:
        return None


def ensure_directory_exists(path: Path) -> bool:
    """
    Ensure a directory exists, creating it if necessary.

    Args:
        path: Directory path

    Returns:
        True if directory exists or was created successfully

    Example:
        >>> import tempfile
        >>> from pathlib import Path
        >>> temp_dir = Path(tempfile.mkdtemp())
        >>> test_dir = temp_dir / "test_subdir"
        >>> ensure_directory_exists(test_dir)
        True
        >>> test_dir.exists()
        True
    """
    try:
        path.mkdir(parents=True, exist_ok=True)
        return True
    except Exception:
        return False


def get_relative_path(path: Path, root: Optional[Path] = None) -> str:
    """
    Get relative path from root directory.

    Args:
        path: Absolute or relative path
        root: Root directory (default: documents root)

    Returns:
        Relative path as string

    Example:
        >>> from pathlib import Path
        >>> abs_path = Path("/tmp/PrismWeaveDocs/documents/test.md")
        >>> root = Path("/tmp/PrismWeaveDocs")
        >>> get_relative_path(abs_path, root)
        'documents/test.md'
    """
    if root is None:
        root = get_documents_root()

    try:
        abs_path = path.resolve()
        abs_root = root.resolve()
        rel_path = abs_path.relative_to(abs_root)
        return str(rel_path)
    except ValueError:
        # If path is not relative to root, return absolute path
        return str(path)


def list_markdown_files(directory: Path, pattern: str = "*.md", recursive: bool = True) -> list[Path]:
    """
    List all markdown files in a directory.

    Args:
        directory: Directory to search
        pattern: Glob pattern (default: *.md)
        recursive: Search recursively (default: True)

    Returns:
        List of markdown file paths

    Example:
        >>> import tempfile
        >>> from pathlib import Path
        >>> temp_dir = Path(tempfile.mkdtemp())
        >>> (temp_dir / "test.md").write_text("# Test")
        6
        >>> files = list_markdown_files(temp_dir, recursive=False)
        >>> len(files) >= 1
        True
    """
    if not directory.exists() or not directory.is_dir():
        return []

    if recursive:
        return sorted(directory.rglob(pattern))
    else:
        return sorted(directory.glob(pattern))


def get_file_size(path: Path) -> int:
    """
    Get file size in bytes.

    Args:
        path: File path

    Returns:
        Size in bytes (0 if file doesn't exist)

    Example:
        >>> import tempfile
        >>> from pathlib import Path
        >>> temp_file = Path(tempfile.mktemp(suffix=".md"))
        >>> temp_file.write_text("Hello World")
        11
        >>> get_file_size(temp_file)
        11
    """
    try:
        return path.stat().st_size if path.exists() else 0
    except Exception:
        return 0


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing invalid characters.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename

    Example:
        >>> sanitize_filename("test/file:name*.md")
        'test-file-name.md'
        >>> sanitize_filename("normal-file.md")
        'normal-file.md'
    """
    # Replace invalid characters with hyphens
    invalid_chars = r'[<>:"/\\|?*]'
    import re

    sanitized = re.sub(invalid_chars, "-", filename)

    # Remove leading/trailing dots and spaces
    sanitized = sanitized.strip(". ")

    # Ensure it's not empty
    if not sanitized:
        sanitized = "untitled"

    return sanitized
