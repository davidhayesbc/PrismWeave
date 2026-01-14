"""Regression tests for ProcessingStateStore resilience.

The processing state SQLite file can be deleted during a rebuild. The store
should recreate its schema automatically on the next write.
"""

from pathlib import Path

from src.core.processing_state_store import ProcessingStateStore, ProcessingStateStoreConfig


def test_processing_state_store_recreates_schema_if_file_deleted(tmp_path: Path) -> None:
    sqlite_path = tmp_path / "processing_state.sqlite"

    store = ProcessingStateStore(ProcessingStateStoreConfig(sqlite_path=sqlite_path))
    assert sqlite_path.exists()

    # Simulate rebuild deleting the SQLite file after the store was constructed.
    sqlite_path.unlink()
    assert not sqlite_path.exists()

    # This should NOT raise (historically: sqlite3.OperationalError: no such table: processing_meta)
    store.set_last_processed_commit("deadbeef")

    assert sqlite_path.exists()
    assert store.get_last_processed_commit() == "deadbeef"
