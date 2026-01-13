"""SQLite-backed storage for PrismWeave processing state.

This replaces the legacy `.prismweave/processing_state.json` file with a small
SQLite database so we can scale to large repositories without constantly
rewriting a giant JSON blob.

The store preserves the logical JSON shape used by older code:

{
  "version": "1.0.0",
  "last_processed_commit": "...",
  "processed_files": {
     "path/to/file": {"processed_at": ..., "commit_hash": ..., ...},
  },
  "last_update": "..."
}

But callers should prefer the incremental APIs (upsert/get) for performance.
"""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

DEFAULT_VERSION = "1.0.0"


def default_processing_state_sqlite_path(repo_path: Path) -> Path:
    return Path(repo_path) / ".prismweave" / "processing_state.sqlite"


@dataclass(frozen=True)
class ProcessingStateStoreConfig:
    sqlite_path: Path


class ProcessingStateStore:
    def __init__(self, config: ProcessingStateStoreConfig):
        self.config = config
        self.sqlite_path = Path(config.sqlite_path)
        self.sqlite_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.sqlite_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS processing_meta (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS processed_files (
                    path TEXT PRIMARY KEY,
                    processed_at TEXT,
                    commit_hash TEXT,
                    content_hash TEXT,
                    file_size INTEGER,
                    last_modified TEXT
                )
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_processed_files_commit_hash ON processed_files(commit_hash)")

            # Ensure default version is present.
            version = self.get_meta("version")
            if not version:
                self.set_meta("version", DEFAULT_VERSION)

    def get_meta(self, key: str) -> str | None:
        with self._connect() as conn:
            row = conn.execute("SELECT value FROM processing_meta WHERE key = ?", (key,)).fetchone()
            return str(row[0]) if row else None

    def set_meta(self, key: str, value: str | None) -> None:
        with self._connect() as conn:
            if value is None:
                conn.execute("DELETE FROM processing_meta WHERE key = ?", (key,))
            else:
                conn.execute(
                    "INSERT INTO processing_meta(key, value) VALUES(?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                    (key, value),
                )

    def touch_last_update(self, timestamp: str | None = None) -> None:
        self.set_meta("last_update", timestamp or datetime.now().isoformat())

    def get_last_processed_commit(self) -> str | None:
        return self.get_meta("last_processed_commit")

    def set_last_processed_commit(self, commit_hash: str | None) -> None:
        self.set_meta("last_processed_commit", commit_hash)
        self.touch_last_update()

    def get_processed_file(self, relative_path: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT path, processed_at, commit_hash, content_hash, file_size, last_modified
                FROM processed_files
                WHERE path = ?
                """,
                (relative_path,),
            ).fetchone()

        if not row:
            return None

        return {
            "processed_at": row["processed_at"],
            "commit_hash": row["commit_hash"],
            "content_hash": row["content_hash"],
            "file_size": row["file_size"],
            "last_modified": row["last_modified"],
        }

    def upsert_processed_file(self, relative_path: str, info: dict[str, Any]) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO processed_files(
                    path, processed_at, commit_hash, content_hash, file_size, last_modified
                ) VALUES(?, ?, ?, ?, ?, ?)
                ON CONFLICT(path) DO UPDATE SET
                    processed_at=excluded.processed_at,
                    commit_hash=excluded.commit_hash,
                    content_hash=excluded.content_hash,
                    file_size=excluded.file_size,
                    last_modified=excluded.last_modified
                """,
                (
                    relative_path,
                    info.get("processed_at"),
                    info.get("commit_hash"),
                    info.get("content_hash"),
                    info.get("file_size"),
                    info.get("last_modified"),
                ),
            )

        self.touch_last_update()

    def iter_processed_files(self) -> Iterable[tuple[str, dict[str, Any]]]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT path, processed_at, commit_hash, content_hash, file_size, last_modified FROM processed_files"
            ).fetchall()

        for row in rows:
            yield str(row["path"]), {
                "processed_at": row["processed_at"],
                "commit_hash": row["commit_hash"],
                "content_hash": row["content_hash"],
                "file_size": row["file_size"],
                "last_modified": row["last_modified"],
            }

    def clear_processed_files(self) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM processed_files")
        self.touch_last_update()

    def load_state(self) -> dict[str, Any]:
        version = self.get_meta("version") or DEFAULT_VERSION
        state: dict[str, Any] = {
            "version": version,
            "last_processed_commit": self.get_meta("last_processed_commit"),
            "processed_files": {},
            "last_update": self.get_meta("last_update"),
        }

        processed: dict[str, Any] = {}
        for path, info in self.iter_processed_files():
            processed[path] = info
        state["processed_files"] = processed
        return state

    def save_state(self, state: dict[str, Any]) -> None:
        version = str(state.get("version") or DEFAULT_VERSION)
        last_processed_commit = state.get("last_processed_commit")
        last_update = state.get("last_update")

        with self._connect() as conn:
            conn.execute(
                "INSERT INTO processing_meta(key, value) VALUES(?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                ("version", version),
            )
            if last_processed_commit is None:
                conn.execute("DELETE FROM processing_meta WHERE key = ?", ("last_processed_commit",))
            else:
                conn.execute(
                    "INSERT INTO processing_meta(key, value) VALUES(?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                    ("last_processed_commit", str(last_processed_commit)),
                )

            # Replace all processed files (used mainly for tests/migration).
            conn.execute("DELETE FROM processed_files")
            processed_files = state.get("processed_files") or {}
            if isinstance(processed_files, dict):
                rows = []
                for path, info in processed_files.items():
                    if not isinstance(info, dict):
                        continue
                    rows.append(
                        (
                            str(path),
                            info.get("processed_at"),
                            info.get("commit_hash"),
                            info.get("content_hash"),
                            info.get("file_size"),
                            info.get("last_modified"),
                        )
                    )
                if rows:
                    conn.executemany(
                        """
                        INSERT INTO processed_files(
                            path, processed_at, commit_hash, content_hash, file_size, last_modified
                        ) VALUES(?, ?, ?, ?, ?, ?)
                        """,
                        rows,
                    )

        # Preserve provided last_update if supplied, else update now.
        if last_update:
            self.set_meta("last_update", str(last_update))
        else:
            self.touch_last_update()

    def migrate_from_json(self, json_path: Path) -> bool:
        """Import the legacy JSON file into this SQLite DB.

        Returns True if migration succeeded and data was imported.
        """

        json_path = Path(json_path)
        if not json_path.exists():
            return False

        try:
            payload = json_path.read_text(encoding="utf-8")
            data = json.loads(payload)
        except (OSError, json.JSONDecodeError):
            return False

        if not isinstance(data, dict):
            return False

        self.save_state(data)
        return True
