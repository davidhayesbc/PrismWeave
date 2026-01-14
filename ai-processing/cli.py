#!/usr/bin/env python3
"""PrismWeave Document Processing CLI.

Run via UV entry points:

    uv run prismweave-cli -- --help
    uv run prismweave-cli -- rebuild-db --yes

The legacy ``prismweave-process`` alias still invokes the same CLI.
"""

from __future__ import annotations

import shutil
import sqlite3
import time
from pathlib import Path

import click

from src.cli.api_commands import api
from src.cli.export_command import export
from src.cli.git_utils import initialize_git_tracker, print_git_summary
from src.cli.process_commands import process, rebuild_db, sync
from src.cli.processing_utils import process_directory
from src.cli.query_commands import count, list_docs, search, stats
from src.cli.taxonomy_commands import taxonomy
from src.cli.visualize_commands import visualize
from src.cli_support import CliError, create_state, ensure_ollama_available
from src.core.config import Config as _ConfigAlias
from src.core.document_processor import DocumentProcessor
from src.core.embedding_store import EmbeddingStore
from src.taxonomy.assignments import AssignmentOptions, run_article_tag_assignment
from src.taxonomy.models import Tag as _TaxonomyTag
from src.taxonomy.models import TaxonomyCategory as _TaxonomyCategory
from src.taxonomy.pipeline import ClusterPipelineOptions, run_clustering_pipeline
from src.taxonomy.proposals import ProposalRunOptions, run_cluster_proposals
from src.taxonomy.store import TaxonomyStore, TaxonomyStoreConfig, default_taxonomy_sqlite_path
from src.taxonomy.tag_embeddings import TagEmbeddingOptions, embed_and_store_tags
from src.taxonomy.taxonomy_builder import run_taxonomy_normalize_and_store

# Backwards compatibility for tests that patch cli.Config
Config = _ConfigAlias


@click.group()
def cli() -> None:
    """PrismWeave Document Processing CLI."""


@click.command(name="rebuild-everything")
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, path_type=Path),
    help="Configuration file path (default: config.yaml)",
)
@click.option("--verbose", "-v", is_flag=True, help="Show detailed output")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompts")
@click.option(
    "--algorithm",
    type=click.Choice(["kmeans", "hdbscan"], case_sensitive=False),
    default="kmeans",
    show_default=True,
    help="Clustering algorithm",
)
@click.option("--k", type=int, default=None, help="K for KMeans (default: sqrt(n/2))")
@click.option("--max-articles", type=int, default=None, help="Limit number of articles for clustering")
@click.option("--sample-size", type=int, default=10, show_default=True, help="Representative samples per cluster")
@click.option("--top-n", type=int, default=8, show_default=True, help="Max tags per article")
@click.option(
    "--min-confidence",
    type=float,
    default=0.15,
    show_default=True,
    help="Minimum confidence for embedding-based tags",
)
@click.option(
    "--tags-only",
    is_flag=True,
    help="Only rebuild tag embeddings + article tag assignments (keeps embeddings/clusters/taxonomy as-is)",
)
def rebuild_everything_cmd(
    config: Path | None,
    verbose: bool,
    yes: bool,
    algorithm: str,
    k: int | None,
    max_articles: int | None,
    sample_size: int,
    top_n: int,
    min_confidence: float,
    tags_only: bool,
) -> None:
    """Rebuild embeddings + clustering + taxonomy + assignments from scratch."""

    state = create_state(config, verbose)

    docs_root = Path(state.config.mcp.paths.documents_root).expanduser().resolve()
    chroma_path = Path(state.config.chroma_db_path).expanduser().resolve()
    processing_state_file = docs_root / ".prismweave" / "processing_state.sqlite"
    taxonomy_sqlite = default_taxonomy_sqlite_path(docs_root)
    taxonomy_artifacts_dir = docs_root / ".prismweave" / "taxonomy" / "artifacts"

    if not docs_root.exists():
        raise click.ClickException(f"Documents root not found: {docs_root}")

    state.write("🔮 PrismWeave Full Rebuild")
    state.write("=" * 40)
    state.write(f"📁 Documents root: {docs_root}")
    state.write(f"🧠 ChromaDB path: {chroma_path}")
    state.write(f"🗂️  Processing state: {processing_state_file}")
    state.write(f"🗄️  Taxonomy SQLite: {taxonomy_sqlite}")
    state.write(f"📦 Taxonomy artifacts: {taxonomy_artifacts_dir}")
    state.write()

    if not yes:
        prompt = (
            "This will RESET tag embeddings and DELETE all article tag assignments (taxonomy remains). Continue?"
            if tags_only
            else "This will DELETE the ChromaDB database, processing_state.sqlite, taxonomy.sqlite, and taxonomy artifacts. Continue?"
        )
        confirm = click.confirm(prompt, default=False)
        if not confirm:
            state.write("❎ Rebuild cancelled.")
            return

    # Attach git tracker (best-effort) for consistent processing behavior.
    repo_root = docs_root if (docs_root / ".git").exists() else None
    state.git_tracker = initialize_git_tracker(repo_root, verbose=verbose, strict=False)
    if repo_root and state.git_tracker:
        print_git_summary(state, repo_root)

    overall_start = time.time()

    try:
        state.write("🔍 Checking Ollama availability...")
        ensure_ollama_available(state.config)
        state.write_verbose("✅ Ollama is running\n")

        if tags_only:
            overall_start = time.time()
            state.write("🔁 Tag rebuild mode: skipping embeddings/clustering/proposals/taxonomy rebuild")
            state.write()

            taxonomy_json = taxonomy_artifacts_dir / "taxonomy.json"
            proposals_json = taxonomy_artifacts_dir / "cluster_proposals.json"

            # If taxonomy.json is missing but we have cluster proposals, we can reconstruct taxonomy
            # deterministically by running the normalize step.
            if not taxonomy_json.exists():
                if not proposals_json.exists():
                    # We can often regenerate proposals if clustering already ran.
                    # This keeps the spirit of "tags-only": we still skip embeddings+clustering,
                    # but we recover the missing downstream artifacts.
                    articles_json = taxonomy_artifacts_dir / "articles.json"
                    clusters_json = taxonomy_artifacts_dir / "clusters.json"
                    if not articles_json.exists() or not clusters_json.exists():
                        raise CliError(
                            "taxonomy.json not found in taxonomy artifacts. "
                            "Also missing cluster_proposals.json, and cannot re-run propose because "
                            "articles.json/clusters.json are missing. Run a full taxonomy build first "
                            "(cluster + propose + normalize), then retry --tags-only."
                        )

                    state.write("🧠 cluster_proposals.json missing; regenerating proposals via LLM...")
                    proposals_result = run_cluster_proposals(
                        state.config,
                        options=ProposalRunOptions(sample_size=sample_size),
                    )
                    state.write(f"   ✅ Generated {proposals_result['proposals']} proposals")
                    state.write(f"   📦 Artifacts: {proposals_result.get('artifacts_dir') or taxonomy_artifacts_dir}")
                    state.write()

                state.write("🗂️  taxonomy.json missing; regenerating taxonomy via normalize...")
                normalize_result = run_taxonomy_normalize_and_store(state.config)
                state.write(
                    f"   ✅ Stored taxonomy: {normalize_result['categories']} categories, {normalize_result['tags']} tags"
                )
                state.write(f"   🗄️  SQLite: {normalize_result['sqlite']}")
                state.write(f"   📦 Artifacts: {normalize_result.get('artifacts_dir') or taxonomy_artifacts_dir}")
                state.write()

                if not taxonomy_json.exists():
                    raise CliError(
                        "taxonomy normalize completed but taxonomy.json is still missing. "
                        "Check taxonomy artifacts directory permissions and retry."
                    )

            # Assignments require these artifacts; fail early with a targeted message.
            required_for_assign = [
                taxonomy_artifacts_dir / "articles.json",
                taxonomy_artifacts_dir / "clusters.json",
                proposals_json,
            ]
            missing = [p.name for p in required_for_assign if not p.exists()]
            if missing:
                raise CliError(
                    "Missing taxonomy artifacts required for tag assignment: "
                    + ", ".join(missing)
                    + ". Run a full taxonomy build first (cluster + propose), then normalize, then retry --tags-only."
                )

            # Ensure taxonomy SQLite exists. If it's missing (e.g., deleted manually), recreate the schema
            # and repopulate taxonomy tables from taxonomy.json so "taxonomy remains" holds true.
            if not taxonomy_sqlite.exists():
                state.write("🗄️  taxonomy.sqlite missing; recreating from taxonomy.json...")
                try:
                    payload = taxonomy_json.read_text(encoding="utf-8")
                except OSError as exc:
                    raise CliError(f"Failed to read {taxonomy_json}: {exc}") from exc

                # Parse without importing the shared JSON helper to keep this command self-contained.
                import json

                try:
                    taxonomy_payload = json.loads(payload)
                except json.JSONDecodeError as exc:
                    raise CliError(f"Invalid JSON in {taxonomy_json}: {exc}") from exc

                store = TaxonomyStore(TaxonomyStoreConfig(sqlite_path=taxonomy_sqlite))
                store.initialize()

                try:
                    categories = [_TaxonomyCategory(**c) for c in (taxonomy_payload.get("categories") or [])]
                    tags = [_TaxonomyTag(**t) for t in (taxonomy_payload.get("tags") or [])]
                except Exception as exc:
                    raise CliError(f"Failed to parse categories/tags from {taxonomy_json}: {exc}") from exc

                store.upsert_categories(categories)
                store.upsert_tags(tags)

                cluster_map = taxonomy_payload.get("cluster_category_map") or {}
                if isinstance(cluster_map, dict):
                    for cluster_id in sorted(cluster_map.keys()):
                        item = cluster_map.get(cluster_id) or {}
                        if not isinstance(item, dict):
                            continue
                        store.map_cluster_to_category(
                            str(cluster_id),
                            item.get("category_id"),
                            item.get("subcategory_id"),
                        )

                state.write("   ✅ Recreated taxonomy.sqlite from taxonomy.json")
                state.write()
            else:
                # Ensure schema exists even if the file exists but is empty/corrupt.
                TaxonomyStore(TaxonomyStoreConfig(sqlite_path=taxonomy_sqlite)).initialize()

            phase_start = time.time()
            state.write("[1/2] 🧹 Clearing existing article tag assignments...")
            try:
                with sqlite3.connect(str(taxonomy_sqlite)) as conn:
                    conn.execute("PRAGMA foreign_keys=ON;")
                    conn.execute("DELETE FROM article_tag_assignments;")
                    conn.commit()
                state.write(f"   ✅ Cleared assignments in {time.time() - phase_start:.1f}s")
            except sqlite3.Error as exc:
                raise CliError(f"Failed to clear article_tag_assignments in {taxonomy_sqlite}: {exc}") from exc
            state.write()

            phase_start = time.time()
            state.write("[2/2] 🏷️  Re-embedding tags + re-assigning tags to all articles...")
            embed_result = embed_and_store_tags(state.config, options=TagEmbeddingOptions(use_description=True))
            state.write(f"   ✅ Embedded {embed_result['tags']} tags into {embed_result['tag_embeddings_collection']}")

            assign_result = run_article_tag_assignment(
                state.config,
                options=AssignmentOptions(top_n=top_n, min_confidence=min_confidence),
            )
            state.write(
                f"   ✅ Wrote {assign_result['assignments']} tag assignments for {assign_result['articles']} articles in {time.time() - phase_start:.1f}s"
            )
            state.write(f"   🗄️  SQLite: {assign_result['sqlite']}")
            artifacts_dir = assign_result.get("artifacts_dir")
            if artifacts_dir:
                state.write(f"   📦 Artifacts: {artifacts_dir}")
            state.write()
            state.write(f"✅ Tag rebuild completed in {time.time() - overall_start:.1f}s")
            return

        # Phase 1: wipe + rebuild embeddings
        phase_start = time.time()
        state.write("[1/6] 🧹 Rebuilding embeddings (ChromaDB) from scratch...")

        processing_state_file.parent.mkdir(parents=True, exist_ok=True)
        if chroma_path.exists():
            shutil.rmtree(chroma_path)
            state.write("   🧹 Removed existing ChromaDB directory")
        chroma_path.mkdir(parents=True, exist_ok=True)

        if processing_state_file.exists():
            processing_state_file.unlink()
            state.write("   🗑️  Deleted processing_state.sqlite")

        processor = DocumentProcessor(state.config, state.git_tracker)
        store = EmbeddingStore(state.config, state.git_tracker)

        state.write("   ⚙️  Processing all documents...")
        success = process_directory(
            docs_root,
            state,
            processor,
            store,
            incremental=False,
            force=True,
        )
        if not success:
            raise CliError("Embeddings rebuild failed: no documents were processed")

        verification = store.verify_embeddings()
        if verification.get("status") != "success":
            raise CliError(f"Embeddings verification failed: {verification.get('error', 'unknown error')}")

        state.write(
            f"   ✅ Embeddings rebuilt in {time.time() - phase_start:.1f}s: {verification.get('document_count', 0)} chunks"
        )
        state.write()

        # Phase 2: wipe taxonomy (SQLite + artifacts)
        phase_start = time.time()
        state.write("[2/6] 🧹 Clearing taxonomy store + artifacts...")
        if taxonomy_sqlite.exists():
            taxonomy_sqlite.unlink()
            state.write("   🗑️  Deleted taxonomy.sqlite (includes any manual overrides)")
        if taxonomy_artifacts_dir.exists():
            shutil.rmtree(taxonomy_artifacts_dir)
            state.write("   🗑️  Deleted taxonomy artifacts directory")
        state.write(f"   ✅ Taxonomy cleared in {time.time() - phase_start:.1f}s")
        state.write()

        # Phase 3: clustering
        phase_start = time.time()
        state.write("[3/6] 🧩 Clustering articles...")
        result = run_clustering_pipeline(
            state.config,
            options=ClusterPipelineOptions(max_articles=max_articles, algorithm=algorithm, k=k),
        )
        state.write(
            f"   ✅ Clustered {result['articles']} articles into {result['clusters']} clusters in {time.time() - phase_start:.1f}s"
        )
        state.write(f"   📦 Artifacts: {result.get('artifacts_dir') or taxonomy_artifacts_dir}")
        state.write()

        # Phase 4: LLM proposals
        phase_start = time.time()
        state.write("[4/6] 🧠 Generating LLM proposals (category/subcategory/tags) per cluster...")
        result = run_cluster_proposals(state.config, options=ProposalRunOptions(sample_size=sample_size))
        state.write(f"   ✅ Generated {result['proposals']} proposals in {time.time() - phase_start:.1f}s")
        state.write(f"   📦 Artifacts: {result.get('artifacts_dir') or taxonomy_artifacts_dir}")
        state.write()

        # Phase 5: normalize taxonomy + embed tags
        phase_start = time.time()
        state.write("[5/6] 🗂️  Normalizing proposals into taxonomy + embedding tags...")
        normalize_result = run_taxonomy_normalize_and_store(state.config)
        state.write(
            f"   ✅ Stored taxonomy: {normalize_result['categories']} categories, {normalize_result['tags']} tags"
        )
        state.write(f"   🗄️  SQLite: {normalize_result['sqlite']}")
        state.write(f"   📦 Artifacts: {normalize_result.get('artifacts_dir') or taxonomy_artifacts_dir}")

        embed_result = embed_and_store_tags(state.config, options=TagEmbeddingOptions(use_description=True))
        state.write(f"   ✅ Embedded {embed_result['tags']} tags into {embed_result['tag_embeddings_collection']}")
        state.write(f"   ✅ Phase completed in {time.time() - phase_start:.1f}s")
        state.write()

        # Phase 6: assign tags to articles
        phase_start = time.time()
        state.write("[6/6] 🏷️  Assigning tags to all articles...")
        assign_result = run_article_tag_assignment(
            state.config,
            options=AssignmentOptions(top_n=top_n, min_confidence=min_confidence),
        )
        state.write(
            f"   ✅ Wrote {assign_result['assignments']} tag assignments for {assign_result['articles']} articles in {time.time() - phase_start:.1f}s"
        )
        state.write(f"   🗄️  SQLite: {assign_result['sqlite']}")
        state.write(f"   📦 Artifacts: {assign_result.get('artifacts_dir') or taxonomy_artifacts_dir}")

        state.write()
        state.write(f"✅ Full rebuild completed in {time.time() - overall_start:.1f}s")

    except CliError as exc:
        raise click.ClickException(str(exc)) from exc


# Add commands to the CLI group
cli.add_command(process)
cli.add_command(sync)
cli.add_command(list_docs, name="list")
cli.add_command(count)
cli.add_command(search)
cli.add_command(stats)
cli.add_command(export)
cli.add_command(rebuild_db)
cli.add_command(rebuild_everything_cmd)
cli.add_command(visualize)
cli.add_command(api)
cli.add_command(taxonomy)


def main() -> None:
    """Entry point for the CLI when executed directly."""
    cli()


if __name__ == "__main__":
    main()
