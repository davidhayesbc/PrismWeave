"""
Document utility functions for MCP server

Provides functions for parsing frontmatter, generating IDs, slugifying titles,
and validating markdown documents.
"""

import re
import uuid
from datetime import datetime
from typing import Any, Optional

import frontmatter
import markdown


def parse_frontmatter(content: str) -> tuple[dict[str, Any], str]:
    """
    Parse YAML frontmatter from markdown content.

    Args:
        content: Markdown content with optional frontmatter

    Returns:
        Tuple of (metadata_dict, content_without_frontmatter)

    Example:
        >>> metadata, content = parse_frontmatter('''---
        ... title: My Article
        ... tags: [ai, ml]
        ... ---
        ... # Content here
        ... ''')
        >>> metadata['title']
        'My Article'
    """
    try:
        post = frontmatter.loads(content)
        return dict(post.metadata), post.content
    except Exception as e:
        # If parsing fails, return empty metadata and original content
        return {}, content


def generate_frontmatter(metadata: dict[str, Any]) -> str:
    """
    Generate YAML frontmatter from metadata dictionary.

    Args:
        metadata: Dictionary of metadata fields

    Returns:
        YAML frontmatter string with delimiters

    Example:
        >>> fm = generate_frontmatter({'title': 'Test', 'tags': ['ai']})
        >>> '---' in fm
        True
    """
    post = frontmatter.Post("", **metadata)
    return frontmatter.dumps(post).split("\n---\n")[0] + "\n---\n"


def generate_document_id(prefix: str = "doc") -> str:
    """
    Generate a unique document ID.

    Args:
        prefix: Prefix for the ID (default: "doc")

    Returns:
        Unique document ID in format: prefix_uuid

    Example:
        >>> doc_id = generate_document_id()
        >>> doc_id.startswith('doc_')
        True
        >>> len(doc_id) > 10
        True
    """
    unique_id = str(uuid.uuid4())
    return f"{prefix}_{unique_id}"


def slugify(text: str, max_length: int = 100) -> str:
    """
    Convert text to a URL-friendly slug.

    Args:
        text: Text to slugify
        max_length: Maximum length of resulting slug

    Returns:
        Slugified text

    Example:
        >>> slugify("Hello World!")
        'hello-world'
        >>> slugify("Python & AI: A Guide")
        'python-ai-a-guide'
    """
    # Convert to lowercase
    text = text.lower()

    # Remove special characters and replace spaces with hyphens
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[-\s]+", "-", text)

    # Remove leading/trailing hyphens
    text = text.strip("-")

    # Truncate to max_length
    if len(text) > max_length:
        text = text[:max_length].rsplit("-", 1)[0]

    return text


def generate_filename(title: str, date: Optional[datetime] = None, extension: str = ".md") -> str:
    """
    Generate a filename from a title.

    Args:
        title: Document title
        date: Optional date to prepend (default: today)
        extension: File extension (default: .md)

    Returns:
        Filename in format: YYYY-MM-DD-slugified-title.ext

    Example:
        >>> filename = generate_filename("My Article")
        >>> filename.endswith('-my-article.md')
        True
        >>> '-' in filename
        True
    """
    if date is None:
        date = datetime.now()

    date_prefix = date.strftime("%Y-%m-%d")
    slug = slugify(title)

    return f"{date_prefix}-{slug}{extension}"


def validate_markdown(content: str) -> tuple[bool, list[str]]:
    """
    Validate markdown content and return any issues.

    Args:
        content: Markdown content to validate

    Returns:
        Tuple of (is_valid, list_of_issues)

    Example:
        >>> is_valid, issues = validate_markdown("# Valid markdown\\n\\nWith content")
        >>> is_valid
        True
        >>> len(issues)
        0
    """
    issues = []

    # Check if content is empty
    if not content or not content.strip():
        issues.append("Content is empty")
        return False, issues

    # Check if content is too short
    if len(content.strip()) < 10:
        issues.append("Content is too short (< 10 characters)")

    # Try to parse as markdown
    try:
        html = markdown.markdown(content)
        if not html or not html.strip():
            issues.append("Markdown parsing resulted in empty HTML")
    except Exception as e:
        issues.append(f"Markdown parsing error: {str(e)}")

    # Check for common issues
    if content.count("```") % 2 != 0:
        issues.append("Unclosed code block (odd number of ```)")

    # Check for valid YAML frontmatter if present
    if content.strip().startswith("---"):
        try:
            parse_frontmatter(content)
        except Exception as e:
            issues.append(f"Invalid frontmatter: {str(e)}")

    return len(issues) == 0, issues


def extract_title_from_content(content: str) -> Optional[str]:
    """
    Extract title from markdown content (first # heading).

    Args:
        content: Markdown content

    Returns:
        Title string or None if not found

    Example:
        >>> extract_title_from_content("# My Title\\n\\nContent here")
        'My Title'
        >>> extract_title_from_content("No title here")
        >>> 
    """
    # Remove frontmatter first
    _, clean_content = parse_frontmatter(content)

    # Look for first level-1 heading
    match = re.search(r"^#\s+(.+)$", clean_content, re.MULTILINE)
    if match:
        return match.group(1).strip()

    return None


def count_words(content: str) -> int:
    """
    Count words in markdown content (excluding frontmatter and code blocks).

    Args:
        content: Markdown content

    Returns:
        Word count

    Example:
        >>> count_words("# Title\\n\\nThis is a test.")
        5
    """
    # Remove frontmatter
    _, clean_content = parse_frontmatter(content)

    # Remove code blocks
    clean_content = re.sub(r"```.*?```", "", clean_content, flags=re.DOTALL)

    # Remove inline code
    clean_content = re.sub(r"`[^`]+`", "", clean_content)

    # Remove markdown syntax
    clean_content = re.sub(r"[#*_\[\]()!]", " ", clean_content)

    # Count words
    words = clean_content.split()
    return len([w for w in words if w.strip()])


def calculate_reading_time(content: str, words_per_minute: int = 200) -> int:
    """
    Calculate estimated reading time in minutes.

    Args:
        content: Markdown content
        words_per_minute: Reading speed (default: 200)

    Returns:
        Reading time in minutes (minimum 1)

    Example:
        >>> calculate_reading_time("# Title\\n\\n" + " ".join(["word"] * 300))
        2
    """
    word_count = count_words(content)
    minutes = max(1, round(word_count / words_per_minute))
    return minutes


def merge_metadata(existing: dict[str, Any], updates: dict[str, Any], merge_lists: bool = True) -> dict[str, Any]:
    """
    Merge metadata dictionaries intelligently.

    Args:
        existing: Existing metadata
        updates: New metadata to merge
        merge_lists: If True, merge list values; if False, replace them

    Returns:
        Merged metadata dictionary

    Example:
        >>> existing = {'tags': ['ai'], 'title': 'Old'}
        >>> updates = {'tags': ['ml'], 'category': 'tech'}
        >>> merged = merge_metadata(existing, updates)
        >>> 'ai' in merged['tags'] and 'ml' in merged['tags']
        True
        >>> merged['title']
        'Old'
    """
    result = existing.copy()

    for key, value in updates.items():
        if key in result and merge_lists and isinstance(result[key], list) and isinstance(value, list):
            # Merge lists and remove duplicates
            combined = result[key] + value
            result[key] = list(dict.fromkeys(combined))  # Preserve order while removing duplicates
        else:
            # Replace or add
            result[key] = value

    return result
