from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Dict

from src.core.metadata_index import ArticleMetadata, build_metadata_index, load_existing_index, save_index


def test_article_metadata_from_markdown_preserves_basic_fields(tmp_path: Path) -> None:
    md = tmp_path / "doc.md"
    md.write_text(
        """---
title: Sample
topic: testing
tags: [one, two]
---

First paragraph.

Second paragraph.
""",
        encoding="utf-8",
    )

    article = ArticleMetadata.from_markdown_file(md)

    assert article.id
    assert article.path == str(md)
    assert article.title == "Sample"
    assert article.topic == "testing"
    assert article.tags == ["one", "two"]
    assert article.word_count > 0
    assert article.excerpt.startswith("First paragraph")
    assert article.read_status == "unread"


def test_build_metadata_index_scans_markdown_and_persists_index(tmp_path: Path) -> None:
    docs = tmp_path / "documents"
    docs.mkdir()
    nested = docs / "nested"
    nested.mkdir()

    file1 = docs / "a.md"
    file1.write_text("# A\n\nContent here.", encoding="utf-8")
    file2 = nested / "b.md"
    file2.write_text("# B\n\nMore content.", encoding="utf-8")

    index_path = docs / ".prismweave" / "index" / "articles.json"

    index = build_metadata_index(docs, index_path)

    assert index
    assert index_path.exists()

    # Load raw JSON and ensure keys/fields look correct
    raw: Dict[str, dict] = json.loads(index_path.read_text(encoding="utf-8"))
    assert len(raw) == len(index)
    example = next(iter(raw.values()))
    assert "title" in example
    assert "created_at" in example
    assert "updated_at" in example
    assert "word_count" in example


def test_build_metadata_index_preserves_read_status(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    file1 = docs / "doc.md"
    file1.write_text("# Title\n\nBody", encoding="utf-8")

    index_path = docs / ".prismweave" / "index" / "articles.json"

    index = build_metadata_index(docs, index_path)
    # Mark as read and save
    article_id = next(iter(index.keys()))
    index[article_id].read_status = "read"
    save_index(index, index_path)

    # Rebuild and confirm status is preserved
    updated = build_metadata_index(docs, index_path)
    assert updated[article_id].read_status == "read"


def test_load_existing_index_handles_missing_file(tmp_path: Path) -> None:
    index_path = tmp_path / "missing.json"
    result = load_existing_index(index_path)
    assert result == {}


def test_save_and_load_round_trip(tmp_path: Path) -> None:
    index_path = tmp_path / "articles.json"
    now = datetime.utcnow()
    article = ArticleMetadata(
        id="id1",
        path="/tmp/doc.md",
        title="Title",
        topic=None,
        tags=["a"],
        created_at=now,
        updated_at=now,
        word_count=10,
        excerpt="Excerpt",
        read_status="unread",
    )

    save_index({article.id: article}, index_path)
    loaded = load_existing_index(index_path)
    assert article.id in loaded
    restored = loaded[article.id]
    assert restored.title == article.title
    assert restored.tags == article.tags
