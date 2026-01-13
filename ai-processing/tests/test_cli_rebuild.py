"""Tests for the rebuild-db CLI command."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from src.cli.process_commands import rebuild_db
from src.core.config import Config


def test_rebuild_db_cleans_state_and_runs_processing(tmp_path):
    """Rebuild command should clear chroma data, remove processing state, and process documents."""

    runner = CliRunner()

    docs_root = tmp_path / "PrismWeaveDocs"
    docs_root.mkdir()
    (docs_root / "documents").mkdir()

    chroma_path = tmp_path / "chroma_db"
    chroma_path.mkdir()
    stale_file = chroma_path / "old.bin"
    stale_file.write_text("stale")

    processing_state = docs_root / ".prismweave" / "processing_state.sqlite"
    processing_state.parent.mkdir(parents=True, exist_ok=True)
    processing_state.write_text("stub")

    config = Config()
    config.chroma_db_path = str(chroma_path)
    config.mcp.paths.documents_root = str(docs_root)

    with (
        patch("src.cli_support.Config.from_file", return_value=config),
        patch("src.cli.process_commands.ensure_ollama_available"),
        patch("src.cli.process_commands.DocumentProcessor") as processor_cls,
        patch("src.cli.process_commands.EmbeddingStore") as store_cls,
        patch("src.cli.process_commands.process_directory", return_value=True) as process_dir_mock,
    ):
        store_instance = MagicMock()
        store_instance.verify_embeddings.return_value = {
            "status": "success",
            "document_count": 3,
            "collection_name": "documents",
            "search_functional": True,
        }
        store_cls.return_value = store_instance

        result = runner.invoke(rebuild_db, ["--yes"])

    assert result.exit_code == 0
    assert not stale_file.exists(), "ChromaDB contents should be removed"
    assert processing_state.exists() is False, "processing_state.sqlite should be deleted"

    process_dir_mock.assert_called_once()
    args, kwargs = process_dir_mock.call_args
    assert Path(args[0]) == docs_root
    assert kwargs["force"] is True
    processor_cls.assert_called_once()
    store_cls.assert_called_once()
