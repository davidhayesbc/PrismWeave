from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

from src.core.config import Config

from .artifacts import default_artifacts_dir, read_json
from .chroma_clusters import ClusterStoreConfig, ClusterVectorStore
from .models import Tag
from .ollama import OllamaConfig, ollama_embed


@dataclass(frozen=True)
class TagEmbeddingOptions:
    use_description: bool = True


def embed_and_store_tags(
    config: Config,
    *,
    artifacts_dir: Optional[Path] = None,
    options: TagEmbeddingOptions = TagEmbeddingOptions(),
) -> Dict[str, object]:
    documents_root = Path(config.mcp.paths.documents_root)
    artifacts_dir = artifacts_dir or default_artifacts_dir(documents_root)

    taxonomy_payload = read_json(artifacts_dir / "taxonomy.json")
    tags_payload = taxonomy_payload.get("tags") or []

    tags: Dict[str, Tag] = {t["id"]: Tag(**t) for t in tags_payload}

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
