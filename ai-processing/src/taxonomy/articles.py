from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import frontmatter

from src.core.config import Config

from .chroma_io import ChromaConnection, group_embeddings_by_article, open_persistent_client
from .models import Article
from .similarity import mean_vector


@dataclass(frozen=True)
class ArticleBuildOptions:
    max_articles: Optional[int] = None
    max_content_chars: int = 8000
    summary_chars: int = 600


def _read_article_content(article_id: str, *, max_chars: int) -> str:
    path = Path(article_id)
    if not path.exists() or not path.is_file():
        return ""

    # Markdown frontmatter-aware read where possible.
    if path.suffix.lower() == ".md":
        try:
            post = frontmatter.load(path)
            return (post.content or "")[:max_chars]
        except Exception:
            # Fall back to plain read.
            pass

    try:
        return path.read_text(encoding="utf-8", errors="ignore")[:max_chars]
    except Exception:
        return ""


def _infer_title(metadata: Dict[str, Any], article_id: str) -> str:
    title = metadata.get("title")
    if isinstance(title, str) and title.strip():
        return title.strip()

    path = Path(article_id)
    return path.stem or article_id


def _infer_url(metadata: Dict[str, Any]) -> Optional[str]:
    for key in ("url", "source_url", "sourceUrl"):
        value = metadata.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def load_articles_from_chroma(config: Config, *, options: ArticleBuildOptions = ArticleBuildOptions()) -> List[Article]:
    """Load article-level embeddings by averaging chunk embeddings in ChromaDB."""

    client = open_persistent_client(ChromaConnection(persist_path=Path(config.chroma_db_path)))
    collection = client.get_collection(name=config.collection_name)

    embeddings_by_article, metadata_by_article = group_embeddings_by_article(collection)

    article_ids = sorted(embeddings_by_article.keys())
    if options.max_articles is not None:
        article_ids = article_ids[: max(0, int(options.max_articles))]

    articles: List[Article] = []
    for article_id in article_ids:
        vectors = embeddings_by_article.get(article_id, [])
        centroid = mean_vector(vectors)
        if not centroid:
            continue

        metadata = metadata_by_article.get(article_id, {})
        title = _infer_title(metadata, article_id)
        url = _infer_url(metadata)
        content = _read_article_content(article_id, max_chars=options.max_content_chars)
        summary = None
        if content:
            summary = content[: options.summary_chars].strip() or None

        articles.append(
            Article(
                id=article_id,
                title=title,
                url=url,
                content=content,
                summary=summary,
                embedding=centroid,
            )
        )

    return articles


def sample_representative_articles(
    articles_by_id: Dict[str, Article],
    article_ids: List[str],
    *,
    k: int,
) -> List[Article]:
    """Deterministic sample: take the first k by sorted article_id."""

    selected = []
    for article_id in sorted(article_ids)[: max(0, int(k))]:
        article = articles_by_id.get(article_id)
        if article:
            selected.append(article)
    return selected
