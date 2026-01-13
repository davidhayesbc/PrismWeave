# pyright: reportMissingImports=false

from __future__ import annotations

from pathlib import Path

import click

from src.cli_support import create_state, ensure_ollama_available
from src.taxonomy.assignments import AssignmentOptions, run_article_tag_assignment
from src.taxonomy.new_article import NewArticleTaggingOptions, tag_new_article
from src.taxonomy.pipeline import ClusterPipelineOptions, run_clustering_pipeline
from src.taxonomy.proposals import ProposalRunOptions, run_cluster_proposals
from src.taxonomy.tag_embeddings import TagEmbeddingOptions, embed_and_store_tags
from src.taxonomy.taxonomy_builder import run_taxonomy_normalize_and_store


@click.group()
def taxonomy() -> None:
    """Clustering + taxonomy + tagging pipeline."""


@taxonomy.command(name="cluster")
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, path_type=Path),
    help="Configuration file path (default: config.yaml)",
)
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
@click.option("--algorithm", type=click.Choice(["kmeans", "hdbscan"], case_sensitive=False), default="kmeans")
@click.option("--k", type=int, default=None, help="K for KMeans (default: sqrt(n/2))")
@click.option("--max-articles", type=int, default=None, help="Limit number of articles for clustering")
def cluster_cmd(
    config: Path | None,
    verbose: bool,
    algorithm: str,
    k: int | None,
    max_articles: int | None,
) -> None:
    """Build clusters from existing article embeddings and store centroid vectors in ChromaDB."""

    state = create_state(config, verbose)

    result = run_clustering_pipeline(
        state.config,
        options=ClusterPipelineOptions(max_articles=max_articles, algorithm=algorithm, k=k),
    )

    state.write(f"✅ Clustered {result['articles']} articles into {result['clusters']} clusters")
    if result.get("sqlite"):
        state.write(f"🗄️ SQLite: {result['sqlite']}")


@taxonomy.command(name="propose")
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, path_type=Path),
    help="Configuration file path (default: config.yaml)",
)
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
@click.option("--sample-size", type=int, default=10, help="Representative samples per cluster")
def propose_cmd(config: Path | None, verbose: bool, sample_size: int) -> None:
    """Use local LLM to propose category/subcategory/tags for each cluster."""

    state = create_state(config, verbose)
    state.write("🔍 Checking Ollama availability...")
    ensure_ollama_available(state.config)

    result = run_cluster_proposals(state.config, options=ProposalRunOptions(sample_size=sample_size))
    state.write(f"✅ Generated {result['proposals']} proposals")
    if result.get("sqlite"):
        state.write(f"🗄️ SQLite: {result['sqlite']}")


@taxonomy.command(name="normalize")
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, path_type=Path),
    help="Configuration file path (default: config.yaml)",
)
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def normalize_cmd(config: Path | None, verbose: bool) -> None:
    """Normalize/dedupe cluster proposals into a stable taxonomy and persist to SQLite."""

    state = create_state(config, verbose)
    result = run_taxonomy_normalize_and_store(state.config)
    state.write(f"✅ Stored taxonomy: {result['categories']} categories, {result['tags']} tags")
    state.write(f"🗄️ SQLite: {result['sqlite']}")


@taxonomy.command(name="embed-tags")
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, path_type=Path),
    help="Configuration file path (default: config.yaml)",
)
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def embed_tags_cmd(config: Path | None, verbose: bool) -> None:
    """Embed tag descriptions and store them in ChromaDB for fast tag assignment."""

    state = create_state(config, verbose)
    state.write("🔍 Checking Ollama availability...")
    ensure_ollama_available(state.config)

    result = embed_and_store_tags(state.config, options=TagEmbeddingOptions(use_description=True))
    state.write(f"✅ Embedded {result['tags']} tags")
    state.write(f"🧠 Collection: {result['tag_embeddings_collection']}")


@taxonomy.command(name="assign")
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, path_type=Path),
    help="Configuration file path (default: config.yaml)",
)
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
@click.option("--top-n", type=int, default=8, help="Max tags per article")
@click.option("--min-confidence", type=float, default=0.15, help="Minimum confidence for embedding-based tags")
def assign_cmd(config: Path | None, verbose: bool, top_n: int, min_confidence: float) -> None:
    """Assign tags to articles (proposal + embedding-based refinement) and persist to SQLite."""

    state = create_state(config, verbose)
    opts = AssignmentOptions(top_n=top_n, min_confidence=min_confidence)
    result = run_article_tag_assignment(state.config, options=opts)
    state.write(f"✅ Wrote {result['assignments']} tag assignments for {result['articles']} articles")
    state.write(f"🗄️ SQLite: {result['sqlite']}")


@taxonomy.command(name="tag-new")
@click.argument("path", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, path_type=Path),
    help="Configuration file path (default: config.yaml)",
)
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
@click.option("--top-n", type=int, default=8, help="Max tags")
@click.option("--min-confidence", type=float, default=0.15)
@click.option("--max-cluster-distance", type=float, default=1.5)
@click.option("--llm-refine", is_flag=True, help="Use LLM to refine tags")
def tag_new_cmd(
    path: Path,
    config: Path | None,
    verbose: bool,
    top_n: int,
    min_confidence: float,
    max_cluster_distance: float,
    llm_refine: bool,
) -> None:
    """Tag a new article file using existing cluster centroids and global tags."""

    state = create_state(config, verbose)
    state.write("🔍 Checking Ollama availability...")
    ensure_ollama_available(state.config)

    result = tag_new_article(
        state.config,
        article_path=path,
        options=NewArticleTaggingOptions(
            top_n=top_n,
            min_confidence=min_confidence,
            max_cluster_distance=max_cluster_distance,
            llm_refine=llm_refine,
        ),
    )

    state.write(f"✅ Tagged: {result['article_id']}")
    state.write(f"🧩 Cluster: {result.get('cluster_id')}")
    state.write(f"🏷️ Category: {result.get('category_id')} / {result.get('subcategory_id')}")
    tags_value = result.get("tags")
    tags_list = tags_value if isinstance(tags_value, list) else []
    state.write(f"🔖 Tags: {len(tags_list)}")
