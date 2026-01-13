from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

from src.core.config import Config

from .chroma_clusters import ClusterStoreConfig, ClusterVectorStore
from .models import Tag
from .ollama import OllamaConfig, ollama_embed
from .store import TaxonomyStore, TaxonomyStoreConfig, default_taxonomy_sqlite_path


@dataclass(frozen=True)
class TagEmbeddingOptions:
    use_description: bool = True


def embed_and_store_tags(
    config: Config,
    *,
    options: TagEmbeddingOptions = TagEmbeddingOptions(),
    sqlite_path: Optional[Path] = None,
) -> Dict[str, object]:
    documents_root = Path(config.mcp.paths.documents_root)

    sqlite_path = sqlite_path or default_taxonomy_sqlite_path(documents_root)
    store_sql = TaxonomyStore(TaxonomyStoreConfig(sqlite_path=sqlite_path))
    store_sql.initialize()

    tags_list = store_sql.list_tags()
    if not tags_list:
        raise RuntimeError(f"No tags found in taxonomy.sqlite. Run taxonomy normalize first. sqlite={sqlite_path}")

    tags: Dict[str, Tag] = {t.id: t for t in tags_list}

    embedder = OllamaConfig(host=config.ollama_host, timeout_seconds=int(config.ollama_timeout) * 3)
    tag_embeddings: Dict[str, list[float]] = {}

    for tag_id in sorted(tags.keys()):
        tag = tags[tag_id]
        text = tag.description if options.use_description else tag.name
        tag_embeddings[tag_id] = ollama_embed(embedder, model=config.embedding_model, text=text)

    store = ClusterVectorStore(
        ClusterStoreConfig(
            persist_path=Path(config.chroma_db_path),
        )
    )
    store.upsert_tag_embeddings(tag_embeddings, tags)

    return {
        "tags": len(tags),
        "tag_embeddings_collection": "tag-embeddings",
    }
