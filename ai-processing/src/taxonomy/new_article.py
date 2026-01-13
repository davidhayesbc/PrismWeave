from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from src.core.config import Config

from .chroma_clusters import ClusterStoreConfig, ClusterVectorStore
from .models import ArticleTagAssignment, Tag
from .ollama import OllamaConfig, ollama_embed, ollama_generate, parse_json_object
from .store import TaxonomyStore, TaxonomyStoreConfig, default_taxonomy_sqlite_path


@dataclass(frozen=True)
class NewArticleTaggingOptions:
    max_chars_for_embedding: int = 8000
    top_n: int = 8
    min_confidence: float = 0.15
    max_cluster_distance: float = 1.5
    llm_refine: bool = False
    llm_top_n: int = 10


def _distance_to_confidence(distance: float) -> float:
    return 1.0 / (1.0 + max(distance, 0.0))


def _read_text(path: Path, *, max_chars: int) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")[:max_chars]


def _llm_choose_tags(config: Config, *, article_text: str, tag_names: List[str], max_tags: int) -> List[str]:
    prompt = (
        "Given this article and the global tag list, choose the most relevant tags.\n"
        f'Return JSON: {{ "tags": ["tag-name", ...] }} with 1-{max_tags} items.\n\n'
        f"ARTICLE:\n{article_text[:1200]}\n\n"
        "GLOBAL TAGS:\n" + "\n".join(f"- {name}" for name in tag_names)
    )

    output = ollama_generate(
        OllamaConfig(host=config.ollama_host, timeout_seconds=int(config.ollama_timeout) * 3),
        model=config.tagging_model,
        prompt=prompt,
        system="You return valid JSON only.",
        temperature=0.0,
    )

    payload = parse_json_object(output)
    tags = payload.get("tags")
    if not isinstance(tags, list):
        return []

    selected: List[str] = []
    for item in tags:
        if isinstance(item, str) and item.strip():
            selected.append(item.strip())
    return selected[:max_tags]


def tag_new_article(
    config: Config,
    *,
    article_path: Path,
    options: NewArticleTaggingOptions = NewArticleTaggingOptions(),
) -> Dict[str, object]:
    if not article_path.exists() or not article_path.is_file():
        raise ValueError(f"Article path not found: {article_path}")

    content = _read_text(article_path, max_chars=options.max_chars_for_embedding)
    if not content.strip():
        raise ValueError("Article content was empty")

    embedder = OllamaConfig(host=config.ollama_host, timeout_seconds=int(config.ollama_timeout) * 3)
    embedding = ollama_embed(embedder, model=config.embedding_model, text=content)

    vector_store = ClusterVectorStore(ClusterStoreConfig(persist_path=Path(config.chroma_db_path)))
    cluster_query = vector_store.query_nearest_cluster(embedding, n_results=1)

    cluster_id: Optional[str] = None
    cluster_distance: Optional[float] = None

    ids = (cluster_query.get("ids") or [[]])[0]
    distances = (cluster_query.get("distances") or [[]])[0]

    if ids and distances:
        cluster_id = str(ids[0])
        cluster_distance = float(distances[0])

    if cluster_id is None or cluster_distance is None or cluster_distance > options.max_cluster_distance:
        cluster_id = None

    # Look up category/subcategory mapping from SQLite
    documents_root = Path(config.mcp.paths.documents_root)
    store = TaxonomyStore(TaxonomyStoreConfig(sqlite_path=default_taxonomy_sqlite_path(documents_root)))
    store.initialize()
    cluster_map = store.get_cluster_category_map()

    category_id: Optional[str] = None
    subcategory_id: Optional[str] = None
    if cluster_id and cluster_id in cluster_map:
        category_id, subcategory_id = cluster_map[cluster_id]

    # Tag assignment
    tags = store.list_tags()
    tags_by_id: Dict[str, Tag] = {t.id: t for t in tags}

    by_tag_id: Dict[str, float] = {}

    try:
        tag_results = vector_store.query_tag_embeddings(embedding, n_results=max(1, int(options.top_n)))
        tag_ids = (tag_results.get("ids") or [[]])[0]
        tag_distances = (tag_results.get("distances") or [[]])[0]
        for tag_id, dist in zip(tag_ids, tag_distances):
            conf = _distance_to_confidence(float(dist))
            if conf >= options.min_confidence:
                by_tag_id[str(tag_id)] = max(by_tag_id.get(str(tag_id), 0.0), conf)
    except Exception:
        # Tag embedding collection might not exist
        pass

    if options.llm_refine and tags:
        chosen = _llm_choose_tags(
            config, article_text=content, tag_names=[t.name for t in tags], max_tags=options.llm_top_n
        )
        name_to_id = {t.name: t.id for t in tags}
        for name in chosen:
            tag_id = name_to_id.get(name)
            if tag_id:
                by_tag_id[tag_id] = max(by_tag_id.get(tag_id, 0.0), 0.8)

    assignments: List[ArticleTagAssignment] = []
    for tag_id, confidence in sorted(by_tag_id.items(), key=lambda kv: (-kv[1], kv[0]))[: max(0, int(options.top_n))]:
        assignments.append(
            ArticleTagAssignment(article_id=str(article_path), tag_id=tag_id, confidence=float(confidence))
        )

    store.upsert_article_tag_assignments(assignments)

    return {
        "article_id": str(article_path),
        "cluster_id": cluster_id,
        "cluster_distance": cluster_distance,
        "category_id": category_id,
        "subcategory_id": subcategory_id,
        "tags": [
            {
                "tag_id": a.tag_id,
                "name": tags_by_id[a.tag_id].name if a.tag_id in tags_by_id else a.tag_id,
                "confidence": a.confidence,
            }
            for a in assignments
        ],
    }
