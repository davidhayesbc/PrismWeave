from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import chromadb


@dataclass(frozen=True)
class ChromaConnection:
    persist_path: Path


def open_persistent_client(conn: ChromaConnection) -> chromadb.PersistentClient:
    return chromadb.PersistentClient(path=str(conn.persist_path))


def iter_collection_embeddings(
    collection: Any,
    *,
    batch_size: int = 2048,
    include: Optional[List[str]] = None,
) -> Iterable[Dict[str, List[Any]]]:
    """Iterate over a Chroma collection using get(limit, offset).

    Chroma's Python API returns a dict of lists.
    """

    # NOTE: In chromadb, ids are always returned; they are not a valid `include` item.
    include = include or ["embeddings", "metadatas", "documents"]
    offset = 0

    while True:
        page = collection.get(limit=batch_size, offset=offset, include=include)
        raw_ids = page.get("ids")
        ids = list(raw_ids) if raw_ids is not None else []
        if len(ids) == 0:
            break
        yield page
        offset += len(ids)


def extract_article_key(metadata: Optional[Dict[str, Any]]) -> Optional[str]:
    if not metadata:
        return None

    for key in ("source_file", "file_path", "source"):
        value = metadata.get(key)
        if isinstance(value, str) and value.strip():
            return value

    return None


def group_embeddings_by_article(
    collection: Any,
    *,
    batch_size: int = 2048,
) -> Tuple[Dict[str, List[List[float]]], Dict[str, Dict[str, Any]]]:
    """Group chunk embeddings into article buckets.

    Returns:
      - embeddings_by_article: article_id -> list of embeddings
      - metadata_by_article: article_id -> representative metadata (first seen)
    """

    embeddings_by_article: Dict[str, List[List[float]]] = {}
    metadata_by_article: Dict[str, Dict[str, Any]] = {}

    for page in iter_collection_embeddings(collection, batch_size=batch_size):
        raw_embeddings = page.get("embeddings")
        raw_metadatas = page.get("metadatas")

        embeddings = list(raw_embeddings) if raw_embeddings is not None else []
        metadatas = list(raw_metadatas) if raw_metadatas is not None else []

        for embedding, metadata in zip(embeddings, metadatas):
            article_key = extract_article_key(metadata)
            if not article_key:
                continue

            try:
                embedding_list = list(embedding) if embedding is not None else []
                if len(embedding_list) == 0:
                    continue
                embeddings_by_article.setdefault(article_key, []).append([float(x) for x in embedding_list])
            except TypeError:
                continue
            if article_key not in metadata_by_article:
                metadata_by_article[article_key] = dict(metadata or {})

    return embeddings_by_article, metadata_by_article
