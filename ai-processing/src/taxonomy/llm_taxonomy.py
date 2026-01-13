from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from src.core.config import Config

from .articles import sample_representative_articles
from .models import Article, Cluster
from .normalize import ProposedTaxonomy
from .ollama import OllamaConfig, ollama_generate, parse_json_object


@dataclass(frozen=True)
class LlmProposalOptions:
    sample_size: int = 10
    max_content_chars: int = 800


def _cluster_prompt(summaries: List[Dict[str, str]]) -> str:
    parts: List[str] = []
    parts.append("You are designing a topic taxonomy.")
    parts.append("Here are N article summaries from one cluster.")
    parts.append("For this cluster:")
    parts.append("- Propose a concise high-level category name (2-5 words).")
    parts.append("- Optionally propose a subcategory name.")
    parts.append("- Propose 5-15 reusable tags.")
    parts.append("- Provide descriptions for the category and each tag.")
    parts.append("Return JSON with keys: category, subcategory (or null), tags.")
    parts.append("")
    parts.append("CLUSTER ARTICLES:")
    for idx, item in enumerate(summaries, start=1):
        parts.append(f"\n[{idx}] Title: {item['title']}")
        parts.append(f"URL: {item.get('url') or ''}")
        parts.append(f"Summary: {item['summary']}")
    parts.append("")
    parts.append(
        "Return JSON:\n"
        "{\n"
        '  "category": { "name": "...", "description": "..." },\n'
        '  "subcategory": { "name": "...", "description": "..." } or null,\n'
        '  "tags": [ { "name": "...", "description": "..." }, ... ]\n'
        "}"
    )

    return "\n".join(parts)


def propose_taxonomy_for_cluster(
    config: Config,
    *,
    cluster: Cluster,
    articles_by_id: Dict[str, Article],
    options: LlmProposalOptions = LlmProposalOptions(),
) -> ProposedTaxonomy:
    samples = sample_representative_articles(
        articles_by_id,
        cluster.article_ids,
        k=options.sample_size,
    )

    summaries: List[Dict[str, str]] = []
    for article in samples:
        text = article.summary or article.content or ""
        text = text.strip()[: options.max_content_chars]
        if not text:
            continue
        summaries.append({"title": article.title, "url": article.url or "", "summary": text})

    prompt = _cluster_prompt(summaries)

    output = ollama_generate(
        OllamaConfig(host=config.ollama_host, timeout_seconds=int(config.ollama_timeout) * 3),
        model=config.tagging_model,
        prompt=prompt,
        system="You return valid JSON only.",
        temperature=0.0,
    )

    payload = parse_json_object(output)

    category = payload.get("category") or {}
    subcategory = payload.get("subcategory")
    tags = payload.get("tags") or []

    category_name = str(category.get("name", "")).strip()
    category_description = str(category.get("description", "")).strip()

    subcategory_name: Optional[str] = None
    subcategory_description: Optional[str] = None

    if isinstance(subcategory, dict):
        subcategory_name = str(subcategory.get("name", "")).strip() or None
        subcategory_description = str(subcategory.get("description", "")).strip() or None

    tag_pairs: List[tuple[str, str]] = []
    for item in tags:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name", "")).strip()
        desc = str(item.get("description", "")).strip()
        if name:
            tag_pairs.append((name, desc))

    if not category_name:
        raise ValueError("LLM proposal missing category name")

    return ProposedTaxonomy(
        category_name=category_name,
        category_description=category_description or category_name,
        subcategory_name=subcategory_name,
        subcategory_description=subcategory_description,
        tags=tag_pairs,
    )
