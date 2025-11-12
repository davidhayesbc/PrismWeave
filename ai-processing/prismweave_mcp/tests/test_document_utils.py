"""
Tests for document utility functions
"""

from datetime import datetime

from prismweave_mcp.utils.document_utils import (
    calculate_reading_time,
    count_words,
    extract_title_from_content,
    generate_document_id,
    generate_filename,
    generate_frontmatter,
    merge_metadata,
    parse_frontmatter,
    slugify,
    validate_markdown,
)


class TestParseFrontmatter:
    """Tests for parse_frontmatter function"""

    def test_valid_frontmatter(self) -> None:
        """Test parsing valid YAML frontmatter"""
        content = """---
title: My Article
tags: [ai, ml]
category: tech
---
# Content here
Some text."""

        metadata, body = parse_frontmatter(content)

        assert metadata["title"] == "My Article"
        assert metadata["tags"] == ["ai", "ml"]
        assert metadata["category"] == "tech"
        assert "# Content here" in body

    def test_no_frontmatter(self) -> None:
        """Test content without frontmatter"""
        content = "# Just content\n\nNo frontmatter here."

        metadata, body = parse_frontmatter(content)

        assert metadata == {}
        assert body == content

    def test_empty_content(self) -> None:
        """Test empty content"""
        metadata, body = parse_frontmatter("")

        assert metadata == {}
        assert body == ""


class TestGenerateFrontmatter:
    """Tests for generate_frontmatter function"""

    def test_generate_frontmatter(self) -> None:
        """Test generating frontmatter"""
        metadata = {"title": "Test", "tags": ["ai", "ml"]}

        frontmatter = generate_frontmatter(metadata)

        assert "---" in frontmatter
        assert "title: Test" in frontmatter


class TestGenerateDocumentId:
    """Tests for generate_document_id function"""

    def test_default_prefix(self) -> None:
        """Test ID generation with default prefix"""
        doc_id = generate_document_id()

        assert doc_id.startswith("doc_")
        assert len(doc_id) > 10

    def test_custom_prefix(self) -> None:
        """Test ID generation with custom prefix"""
        doc_id = generate_document_id(prefix="article")

        assert doc_id.startswith("article_")

    def test_uniqueness(self) -> None:
        """Test that generated IDs are unique"""
        id1 = generate_document_id()
        id2 = generate_document_id()

        assert id1 != id2


class TestSlugify:
    """Tests for slugify function"""

    def test_simple_text(self) -> None:
        """Test slugifying simple text"""
        assert slugify("Hello World") == "hello-world"

    def test_special_characters(self) -> None:
        """Test removing special characters"""
        assert slugify("Python & AI: A Guide!") == "python-ai-a-guide"

    def test_multiple_spaces(self) -> None:
        """Test handling multiple spaces"""
        assert slugify("Too   Many    Spaces") == "too-many-spaces"

    def test_max_length(self) -> None:
        """Test max length truncation"""
        long_text = "This is a very long title that should be truncated to fit the maximum length"
        result = slugify(long_text, max_length=20)

        assert len(result) <= 20
        assert not result.endswith("-")


class TestGenerateFilename:
    """Tests for generate_filename function"""

    def test_default_date(self) -> None:
        """Test filename generation with default date"""
        filename = generate_filename("My Article")

        assert filename.endswith("-my-article.md")
        assert len(filename.split("-")) >= 4  # YYYY-MM-DD-slug

    def test_custom_date(self) -> None:
        """Test filename generation with custom date"""
        date = datetime(2024, 1, 15)
        filename = generate_filename("Test Article", date=date)

        assert filename.startswith("2024-01-15-")
        assert filename.endswith("test-article.md")

    def test_custom_extension(self) -> None:
        """Test filename with custom extension"""
        filename = generate_filename("Document", extension=".txt")

        assert filename.endswith(".txt")


class TestValidateMarkdown:
    """Tests for validate_markdown function"""

    def test_valid_markdown(self) -> None:
        """Test validating valid markdown"""
        content = "# Valid markdown\n\nWith proper content and formatting."

        is_valid, issues = validate_markdown(content)

        assert is_valid is True
        assert len(issues) == 0

    def test_empty_content(self) -> None:
        """Test validating empty content"""
        is_valid, issues = validate_markdown("")

        assert is_valid is False
        assert any("empty" in issue.lower() for issue in issues)

    def test_too_short_content(self) -> None:
        """Test validating content that is too short"""
        is_valid, issues = validate_markdown("Hi")

        assert is_valid is False
        assert any("too short" in issue.lower() for issue in issues)

    def test_unclosed_code_block(self) -> None:
        """Test detecting unclosed code blocks"""
        content = "# Article\n\n```python\ncode here\nNo closing backticks"

        is_valid, issues = validate_markdown(content)

        assert is_valid is False
        assert any("code block" in issue.lower() for issue in issues)


class TestExtractTitleFromContent:
    """Tests for extract_title_from_content function"""

    def test_extract_from_heading(self) -> None:
        """Test extracting title from markdown heading"""
        content = "# My Article Title\n\nSome content here."

        title = extract_title_from_content(content)

        assert title == "My Article Title"

    def test_no_heading(self) -> None:
        """Test content without heading"""
        content = "Just some text without a heading."

        title = extract_title_from_content(content)

        assert title is None

    def test_with_frontmatter(self) -> None:
        """Test extracting title with frontmatter present"""
        content = """---
title: Frontmatter Title
---
# Heading Title

Content"""

        title = extract_title_from_content(content)

        assert title == "Heading Title"


class TestCountWords:
    """Tests for count_words function"""

    def test_simple_text(self) -> None:
        """Test counting words in simple text"""
        content = "# Title\n\nThis is a test with seven words."

        count = count_words(content)

        assert count == 8  # Including "Title"

    def test_exclude_code_blocks(self) -> None:
        """Test that code blocks are excluded"""
        content = """# Title

Some text here.

```python
def function():
    pass
```

More text."""

        count = count_words(content)

        # Should not count code block content
        assert count < 20

    def test_empty_content(self) -> None:
        """Test counting words in empty content"""
        assert count_words("") == 0


class TestCalculateReadingTime:
    """Tests for calculate_reading_time function"""

    def test_short_content(self) -> None:
        """Test reading time for short content"""
        content = "# Title\n\n" + " ".join(["word"] * 50)

        minutes = calculate_reading_time(content)

        assert minutes == 1  # Minimum is 1 minute

    def test_long_content(self) -> None:
        """Test reading time for long content"""
        content = "# Title\n\n" + " ".join(["word"] * 500)

        minutes = calculate_reading_time(content)

        assert minutes >= 2

    def test_custom_wpm(self) -> None:
        """Test with custom words per minute"""
        content = "# Title\n\n" + " ".join(["word"] * 400)

        minutes = calculate_reading_time(content, words_per_minute=100)

        assert minutes >= 4


class TestMergeMetadata:
    """Tests for merge_metadata function"""

    def test_merge_with_lists(self) -> None:
        """Test merging metadata with list values"""
        existing = {"tags": ["ai", "ml"], "title": "Original"}
        updates = {"tags": ["python"], "category": "tech"}

        merged = merge_metadata(existing, updates, merge_lists=True)

        assert "ai" in merged["tags"]
        assert "ml" in merged["tags"]
        assert "python" in merged["tags"]
        assert merged["title"] == "Original"
        assert merged["category"] == "tech"

    def test_replace_lists(self) -> None:
        """Test replacing list values"""
        existing = {"tags": ["ai", "ml"]}
        updates = {"tags": ["python"]}

        merged = merge_metadata(existing, updates, merge_lists=False)

        assert merged["tags"] == ["python"]

    def test_add_new_fields(self) -> None:
        """Test adding new metadata fields"""
        existing = {"title": "Test"}
        updates = {"category": "tech", "author": "John"}

        merged = merge_metadata(existing, updates)

        assert merged["category"] == "tech"
        assert merged["author"] == "John"
        assert merged["title"] == "Test"

    def test_duplicate_removal(self) -> None:
        """Test that duplicates are removed when merging lists"""
        existing = {"tags": ["ai", "ml"]}
        updates = {"tags": ["ai", "python"]}

        merged = merge_metadata(existing, updates, merge_lists=True)

        # Should only have one "ai"
        assert merged["tags"].count("ai") == 1
        assert "ml" in merged["tags"]
        assert "python" in merged["tags"]
