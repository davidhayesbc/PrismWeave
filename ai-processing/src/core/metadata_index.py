from __future__ import annotations

import sys
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import frontmatter

INDEX_RELATIVE_PATH = Path(".prismweave/index/articles.json")


@dataclass
class ArticleMetadata:
    """Lightweight metadata representation for a markdown article.

    This model is intentionally simple and decoupled from the rest of the
    processing pipeline so it can be used by both the CLI and future API
    layers.
    """

    id: str
    path: str
    title: str
    topic: Optional[str]
    tags: List[str]
    created_at: datetime
    updated_at: datetime
    word_count: int
    excerpt: str
    read_status: str

    @classmethod
    def from_markdown_file(
        cls,
        file_path: Path,
        *,
        existing: Optional[ArticleMetadata] = None,
    ) -> ArticleMetadata:
        """Create an ArticleMetadata instance from a markdown file.

        The method preserves the existing read_status when provided and
        falls back to "unread" for new documents.
        """

        if not file_path.exists():
            raise FileNotFoundError(file_path)

        text = file_path.read_text(encoding="utf-8")
        try:
            post = frontmatter.loads(text)
        except Exception as exc:  # pragma: no cover - defensive logging
            raise ValueError(f"Failed to parse frontmatter in {file_path}: {exc}") from exc

        body = str(post.content or "").strip()
        words = body.split()
        word_count = len(words)
        excerpt = _build_excerpt(body)

        stat = file_path.stat()
        created_at = datetime.fromtimestamp(stat.st_ctime)
        updated_at = datetime.fromtimestamp(stat.st_mtime)

        meta = post.metadata or {}
        title = str(meta.get("title") or file_path.stem)
        topic = meta.get("topic")
        raw_tags = meta.get("tags")
        tags: List[str]
        if isinstance(raw_tags, list):
            tags = [str(t) for t in raw_tags]
        elif isinstance(raw_tags, str):
            tags = [t.strip() for t in raw_tags.split(",") if t.strip()]
        else:
            tags = []

        article_id = meta.get("id") or _derive_id(file_path)
        read_status = (existing.read_status if existing else None) or "unread"

        return cls(
            id=str(article_id),
            path=str(file_path),
            title=title,
            topic=str(topic) if topic is not None else None,
            tags=tags,
            created_at=created_at,
            updated_at=updated_at,
            word_count=word_count,
            excerpt=excerpt,
            read_status=read_status,
        )


def _derive_id(path: Path) -> str:
    """Derive a stable identifier from the path.

    Currently this is the POSIX path relative to the documents root. The
    documents root is expected to be managed by the caller; this helper only
    ensures a stable textual representation.
    """

    return path.as_posix()


def _build_excerpt(body: str, max_words: int = 60) -> str:
    if not body:
        return ""
    first_paragraph = body.split("\n\n", 1)[0].strip()
    words = first_paragraph.split()
    if len(words) <= max_words:
        return first_paragraph
    return " ".join(words[:max_words]) + " "  # indicates truncation


def load_existing_index(index_path: Path) -> Dict[str, ArticleMetadata]:
    """Load an existing index if present.

    Returns a mapping of article id to ArticleMetadata. Missing or
    malformed files result in an empty index rather than raising, so
    callers can rebuild safely.
    """

    if not index_path.exists():
        return {}

    import json

    try:
        raw = json.loads(index_path.read_text(encoding="utf-8"))
    except Exception:
        return {}

    index: Dict[str, ArticleMetadata] = {}
    for key, value in raw.items():
        try:
            created_at = datetime.fromisoformat(value["created_at"])
            updated_at = datetime.fromisoformat(value["updated_at"])
            index[key] = ArticleMetadata(
                id=value["id"],
                path=value["path"],
                title=value["title"],
                topic=value.get("topic"),
                tags=list(value.get("tags") or []),
                created_at=created_at,
                updated_at=updated_at,
                word_count=int(value.get("word_count", 0)),
                excerpt=value.get("excerpt", ""),
                read_status=value.get("read_status", "unread"),
            )
        except Exception:
            continue
    return index


def save_index(index: Dict[str, ArticleMetadata], index_path: Path) -> None:
    """Persist the index to disk as JSON.

    Dates are stored using ISO 8601 for portability.
    """

    import json

    serializable: Dict[str, Dict[str, object]] = {}
    for key, article in index.items():
        data = asdict(article)
        data["created_at"] = article.created_at.isoformat()
        data["updated_at"] = article.updated_at.isoformat()
        serializable[key] = data

    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text(json.dumps(serializable, indent=2, sort_keys=True), encoding="utf-8")


def build_metadata_index(documents_root: Path, index_path: Optional[Path] = None) -> Dict[str, ArticleMetadata]:
    """Scan the documents tree and rebuild the metadata index.

    The function adds new documents, updates changed ones and removes
    entries whose files no longer exist.
    """

    if not documents_root.exists():
        raise FileNotFoundError(documents_root)

    index_path = index_path or (documents_root / INDEX_RELATIVE_PATH)

    existing_index = load_existing_index(index_path)
    updated_index: Dict[str, ArticleMetadata] = {}

    markdown_files: Iterable[Path] = documents_root.rglob("*.md")

    for md_file in markdown_files:
        try:
            # If we previously indexed this file, preserve read_status.
            previous = next((a for a in existing_index.values() if a.path == str(md_file)), None)
            article = ArticleMetadata.from_markdown_file(md_file, existing=previous)
            updated_index[article.id] = article
        except FileNotFoundError:
            continue
        except ValueError as exc:
            print(f"[metadata-index] {exc}", file=sys.stderr)
            raise

    save_index(updated_index, index_path)
    return updated_index


__all__ = [
    "ArticleMetadata",
    "INDEX_RELATIVE_PATH",
    "build_metadata_index",
    "load_existing_index",
    "save_index",
]
