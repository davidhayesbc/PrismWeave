"""
Tests for path utility functions
"""

import tempfile
from pathlib import Path

from mcp.utils.path_utils import (
    ensure_directory_exists,
    get_document_category,
    get_documents_root,
    get_file_size,
    get_relative_path,
    is_generated_document,
    list_markdown_files,
    resolve_document_path,
    sanitize_filename,
    validate_path_safety,
)


class TestGetDocumentsRoot:
    """Tests for get_documents_root function"""

    def test_default_root(self) -> None:
        """Test getting default documents root"""
        root = get_documents_root()

        assert root.exists()
        assert root.is_dir()

    def test_custom_root(self) -> None:
        """Test getting custom documents root"""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = get_documents_root(config_root=temp_dir)

            assert root.exists()
            assert str(root) == str(Path(temp_dir).resolve())


class TestResolveDocumentPath:
    """Tests for resolve_document_path function"""

    def test_resolve_existing_file(self) -> None:
        """Test resolving an existing file"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            docs_dir = temp_path / "documents"
            docs_dir.mkdir()

            test_file = docs_dir / "test.md"
            test_file.write_text("# Test")

            resolved = resolve_document_path("documents/test.md", documents_root=temp_path, search_subdirs=False)

            assert resolved is not None
            assert resolved.exists()
            assert resolved.name == "test.md"

    def test_resolve_nonexistent_file(self) -> None:
        """Test resolving a non-existent file"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            resolved = resolve_document_path("nonexistent.md", documents_root=temp_path)

            assert resolved is None

    def test_search_subdirectories(self) -> None:
        """Test searching in subdirectories"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            generated_dir = temp_path / "generated"
            generated_dir.mkdir()

            test_file = generated_dir / "article.md"
            test_file.write_text("# Article")

            # Should find file when searching subdirs
            resolved = resolve_document_path("article.md", documents_root=temp_path, search_subdirs=True)

            assert resolved is not None
            assert resolved.exists()


class TestValidatePathSafety:
    """Tests for validate_path_safety function"""

    def test_safe_path(self) -> None:
        """Test validating a safe path"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            safe_file = temp_path / "document.md"

            is_safe, error = validate_path_safety(safe_file, temp_path)

            assert is_safe is True
            assert error is None

    def test_directory_traversal(self) -> None:
        """Test detecting directory traversal"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            unsafe_path = temp_path / ".." / ".." / "etc" / "passwd"

            is_safe, error = validate_path_safety(unsafe_path, temp_path)

            assert is_safe is False
            assert error is not None

    def test_path_outside_root(self) -> None:
        """Test detecting paths outside allowed root"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            outside_path = Path("/tmp/outside.md")

            is_safe, error = validate_path_safety(outside_path, temp_path)

            assert is_safe is False
            assert "outside allowed directory" in error.lower()


class TestIsGeneratedDocument:
    """Tests for is_generated_document function"""

    def test_generated_document(self) -> None:
        """Test identifying a generated document"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            generated_dir = temp_path / "generated"
            generated_dir.mkdir()

            doc_path = generated_dir / "article.md"
            doc_path.write_text("# Article")

            assert is_generated_document(doc_path, documents_root=temp_path) is True

    def test_non_generated_document(self) -> None:
        """Test identifying a non-generated document"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            docs_dir = temp_path / "documents"
            docs_dir.mkdir()

            doc_path = docs_dir / "article.md"
            doc_path.write_text("# Article")

            assert is_generated_document(doc_path, documents_root=temp_path) is False


class TestGetDocumentCategory:
    """Tests for get_document_category function"""

    def test_tech_category(self) -> None:
        """Test extracting tech category"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            tech_dir = temp_path / "tech"
            tech_dir.mkdir()

            doc_path = tech_dir / "article.md"
            doc_path.write_text("# Article")

            category = get_document_category(doc_path, documents_root=temp_path)

            assert category == "tech"

    def test_no_category(self) -> None:
        """Test document without category (in root)"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            doc_path = temp_path / "article.md"
            doc_path.write_text("# Article")

            category = get_document_category(doc_path, documents_root=temp_path)

            assert category is None


class TestEnsureDirectoryExists:
    """Tests for ensure_directory_exists function"""

    def test_create_directory(self) -> None:
        """Test creating a new directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            new_dir = temp_path / "test_dir" / "nested"

            result = ensure_directory_exists(new_dir)

            assert result is True
            assert new_dir.exists()
            assert new_dir.is_dir()

    def test_existing_directory(self) -> None:
        """Test with existing directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            result = ensure_directory_exists(temp_path)

            assert result is True


class TestGetRelativePath:
    """Tests for get_relative_path function"""

    def test_relative_to_root(self) -> None:
        """Test getting relative path from root"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            docs_dir = temp_path / "documents"
            docs_dir.mkdir()

            doc_path = docs_dir / "test.md"
            doc_path.write_text("# Test")

            rel_path = get_relative_path(doc_path, root=temp_path)

            assert rel_path == "documents/test.md"


class TestListMarkdownFiles:
    """Tests for list_markdown_files function"""

    def test_list_markdown_files(self) -> None:
        """Test listing markdown files"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create test files
            (temp_path / "file1.md").write_text("# File 1")
            (temp_path / "file2.md").write_text("# File 2")
            (temp_path / "file3.txt").write_text("Not markdown")

            files = list_markdown_files(temp_path, recursive=False)

            assert len(files) == 2
            assert all(f.suffix == ".md" for f in files)

    def test_recursive_listing(self) -> None:
        """Test recursive markdown file listing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create nested structure
            subdir = temp_path / "subdir"
            subdir.mkdir()

            (temp_path / "root.md").write_text("# Root")
            (subdir / "nested.md").write_text("# Nested")

            files = list_markdown_files(temp_path, recursive=True)

            assert len(files) == 2


class TestGetFileSize:
    """Tests for get_file_size function"""

    def test_existing_file(self) -> None:
        """Test getting size of existing file"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            test_file = temp_path / "test.md"

            content = "Hello World"
            test_file.write_text(content)

            size = get_file_size(test_file)

            assert size == len(content)

    def test_nonexistent_file(self) -> None:
        """Test getting size of non-existent file"""
        size = get_file_size(Path("/nonexistent/file.md"))

        assert size == 0


class TestSanitizeFilename:
    """Tests for sanitize_filename function"""

    def test_remove_invalid_characters(self) -> None:
        """Test removing invalid characters"""
        result = sanitize_filename("test/file:name*.md")

        assert "/" not in result
        assert ":" not in result
        assert "*" not in result

    def test_normal_filename(self) -> None:
        """Test that normal filenames are unchanged"""
        result = sanitize_filename("normal-file-name.md")

        assert result == "normal-file-name.md"

    def test_empty_filename(self) -> None:
        """Test handling empty filename"""
        result = sanitize_filename("...")

        assert result == "untitled"

    def test_trim_spaces_and_dots(self) -> None:
        """Test trimming spaces and dots"""
        result = sanitize_filename("  .test.md.  ")

        assert not result.startswith(" ")
        assert not result.startswith(".")
        assert not result.endswith(" ")
        assert not result.endswith(".")
