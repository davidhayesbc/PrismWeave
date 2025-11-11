"""Utilities for extracting document metadata and content."""

from __future__ import annotations

from typing import Any


def get_document_metadata(document: Any) -> dict:
    """Extract metadata from a document object."""
    metadata = getattr(document, "metadata", None)
    if isinstance(metadata, dict):
        return metadata
    metadata = getattr(document, "meta", None)
    return metadata if isinstance(metadata, dict) else {}


def get_document_content(document: Any) -> str:
    """Extract content from a document object."""
    content = getattr(document, "page_content", None)
    if isinstance(content, str):
        return content
    content = getattr(document, "content", "")
    return content if isinstance(content, str) else ""
