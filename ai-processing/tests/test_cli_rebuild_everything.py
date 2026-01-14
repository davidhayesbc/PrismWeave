"""Tests for the rebuild-everything CLI command.

These are lightweight contract tests: the command should not crash when
pipeline helpers don't return legacy keys like `artifacts_dir`.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from cli import rebuild_everything_cmd
from src.core.config import Config


def test_rebuild_everything_does_not_require_artifacts_dir(tmp_path: Path) -> None:
    runner = CliRunner()

    docs_root = tmp_path / "PrismWeaveDocs"
    docs_root.mkdir()

    # rebuild-everything expects this directory to exist
    chroma_path = tmp_path / "chroma_db"
    chroma_path.mkdir()

    # processing_state.sqlite is deleted by the command; create it to prove deletion is safe
    processing_state = docs_root / ".prismweave" / "processing_state.sqlite"
    processing_state.parent.mkdir(parents=True, exist_ok=True)
    processing_state.write_text("stub")

    taxonomy_sqlite = docs_root / ".prismweave" / "taxonomy" / "taxonomy.sqlite"
    taxonomy_sqlite.parent.mkdir(parents=True, exist_ok=True)

    config = Config()
    config.chroma_db_path = str(chroma_path)
    config.mcp.paths.documents_root = str(docs_root)

    store_instance = MagicMock()
    store_instance.verify_embeddings.return_value = {
        "status": "success",
        "document_count": 1,
        "collection_name": "documents",
        "search_functional": True,
    }

    with (
        patch("src.cli_support.Config.from_file", return_value=config),
        patch("cli.ensure_ollama_available"),
        patch("cli.initialize_git_tracker", return_value=None),
        patch("cli.print_git_summary"),
        patch("cli.DocumentProcessor"),
        patch("cli.EmbeddingStore", return_value=store_instance),
        patch("cli.process_directory", return_value=True),
        # Return dicts WITHOUT artifacts_dir (this is what used to crash)
        patch(
            "cli.run_clustering_pipeline",
            return_value={
                "articles": 3,
                "clusters": 2,
                "sqlite": str(taxonomy_sqlite),
                "clusters_collection": "clusters",
            },
        ),
        patch(
            "cli.run_cluster_proposals", return_value={"clusters": 2, "proposals": 2, "sqlite": str(taxonomy_sqlite)}
        ),
        patch(
            "cli.run_taxonomy_normalize_and_store",
            return_value={"categories": 1, "tags": 2, "sqlite": str(taxonomy_sqlite)},
        ),
        patch("cli.embed_and_store_tags", return_value={"tags": 2, "tag_embeddings_collection": "tag-embeddings"}),
        patch(
            "cli.run_article_tag_assignment",
            return_value={"articles": 3, "assignments": 7, "sqlite": str(taxonomy_sqlite)},
        ),
    ):
        result = runner.invoke(rebuild_everything_cmd, ["--yes"], catch_exceptions=False)

    assert result.exit_code == 0
    assert not processing_state.exists(), "processing_state.sqlite should be deleted"
