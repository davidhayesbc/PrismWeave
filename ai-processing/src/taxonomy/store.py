from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from .models import Article, ArticleTagAssignment, Cluster, Tag, TaxonomyCategory


@dataclass(frozen=True)
class TaxonomyStoreConfig:
    sqlite_path: Path


class TaxonomyStore:
    """SQLite-backed store for taxonomy and assignments.

    This deliberately does NOT use ChromaDB for taxonomy persistence.
    """

    def __init__(self, config: TaxonomyStoreConfig):
        self._path = config.sqlite_path
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self._path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
        return conn

    def initialize(self) -> None:
        with self.connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS taxonomy_categories (
                  id TEXT PRIMARY KEY,
                  name TEXT NOT NULL,
                  description TEXT NOT NULL,
                  parent_id TEXT NULL,
                  level INTEGER NOT NULL,
                  created_at TEXT NOT NULL DEFAULT (datetime('now')),
                  updated_at TEXT NOT NULL DEFAULT (datetime('now'))
                );

                CREATE TABLE IF NOT EXISTS tags (
                  id TEXT PRIMARY KEY,
                  name TEXT NOT NULL,
                  normalized_name TEXT NOT NULL,
                  description TEXT NOT NULL,
                  category_id TEXT NULL,
                  created_at TEXT NOT NULL DEFAULT (datetime('now')),
                  updated_at TEXT NOT NULL DEFAULT (datetime('now'))
                );

                CREATE UNIQUE INDEX IF NOT EXISTS idx_tags_normalized_name ON tags(normalized_name);

                CREATE TABLE IF NOT EXISTS cluster_category_map (
                  cluster_id TEXT PRIMARY KEY,
                  category_id TEXT NULL,
                  subcategory_id TEXT NULL,
                  updated_at TEXT NOT NULL DEFAULT (datetime('now')),
                  notes TEXT NULL
                );

                CREATE TABLE IF NOT EXISTS article_tag_assignments (
                  article_id TEXT NOT NULL,
                  tag_id TEXT NOT NULL,
                  confidence REAL NOT NULL,
                  assigned_at TEXT NOT NULL DEFAULT (datetime('now')),
                  PRIMARY KEY(article_id, tag_id)
                );

                CREATE TABLE IF NOT EXISTS manual_overrides (
                  article_id TEXT NOT NULL,
                  override_json TEXT NOT NULL,
                  updated_at TEXT NOT NULL DEFAULT (datetime('now')),
                  PRIMARY KEY(article_id)
                );

                -- Snapshot storage for taxonomy pipeline artifacts.
                -- These replace JSON artifacts under .prismweave/taxonomy/artifacts.
                CREATE TABLE IF NOT EXISTS articles (
                  id TEXT PRIMARY KEY,
                  title TEXT NOT NULL,
                  url TEXT NULL,
                  content TEXT NOT NULL,
                  summary TEXT NULL,
                  embedding_json TEXT NOT NULL,
                  updated_at TEXT NOT NULL DEFAULT (datetime('now'))
                );

                CREATE TABLE IF NOT EXISTS clusters (
                  id TEXT PRIMARY KEY,
                  centroid_embedding_json TEXT NOT NULL,
                  metadata_json TEXT NOT NULL,
                  category_id TEXT NULL,
                  subcategory_id TEXT NULL,
                  updated_at TEXT NOT NULL DEFAULT (datetime('now'))
                );

                CREATE TABLE IF NOT EXISTS cluster_articles (
                  cluster_id TEXT NOT NULL,
                  article_id TEXT NOT NULL,
                  PRIMARY KEY(cluster_id, article_id),
                  FOREIGN KEY(cluster_id) REFERENCES clusters(id) ON DELETE CASCADE
                );

                CREATE INDEX IF NOT EXISTS idx_cluster_articles_article ON cluster_articles(article_id);

                CREATE TABLE IF NOT EXISTS cluster_proposals (
                  cluster_id TEXT PRIMARY KEY,
                  category_json TEXT NOT NULL,
                  subcategory_json TEXT NULL,
                  tags_json TEXT NOT NULL,
                  updated_at TEXT NOT NULL DEFAULT (datetime('now'))
                );
                """
            )

    def upsert_articles(self, articles: Iterable[Article]) -> None:
        with self.connect() as conn:
            for article in articles:
                conn.execute(
                    """
                    INSERT INTO articles(id, title, url, content, summary, embedding_json)
                    VALUES(?, ?, ?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET
                      title=excluded.title,
                      url=excluded.url,
                      content=excluded.content,
                      summary=excluded.summary,
                      embedding_json=excluded.embedding_json,
                      updated_at=datetime('now');
                    """,
                    (
                        article.id,
                        article.title,
                        article.url,
                        article.content,
                        article.summary,
                        json.dumps(article.embedding, separators=(",", ":")),
                    ),
                )

    def list_articles(self) -> list[Article]:
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT id, title, url, content, summary, embedding_json FROM articles ORDER BY id"
            ).fetchall()

        out: list[Article] = []
        for row in rows:
            try:
                embedding = json.loads(row["embedding_json"]) if row["embedding_json"] else []
            except Exception:
                embedding = []

            out.append(
                Article(
                    id=row["id"],
                    title=row["title"],
                    url=row["url"],
                    content=row["content"],
                    summary=row["summary"],
                    embedding=list(embedding) if isinstance(embedding, list) else [],
                )
            )
        return out

    def upsert_clusters(self, clusters: Iterable[Cluster]) -> None:
        with self.connect() as conn:
            for cluster in clusters:
                conn.execute(
                    """
                    INSERT INTO clusters(id, centroid_embedding_json, metadata_json, category_id, subcategory_id)
                    VALUES(?, ?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET
                      centroid_embedding_json=excluded.centroid_embedding_json,
                      metadata_json=excluded.metadata_json,
                      category_id=excluded.category_id,
                      subcategory_id=excluded.subcategory_id,
                      updated_at=datetime('now');
                    """,
                    (
                        cluster.id,
                        json.dumps(cluster.centroid_embedding, separators=(",", ":")),
                        json.dumps(cluster.metadata or {}, sort_keys=True, separators=(",", ":")),
                        cluster.category_id,
                        cluster.subcategory_id,
                    ),
                )

                # Replace membership for this cluster.
                conn.execute("DELETE FROM cluster_articles WHERE cluster_id=?", (cluster.id,))
                for article_id in cluster.article_ids:
                    if not article_id:
                        continue
                    conn.execute(
                        """
                        INSERT OR IGNORE INTO cluster_articles(cluster_id, article_id)
                        VALUES(?, ?)
                        """,
                        (cluster.id, str(article_id)),
                    )

    def list_clusters(self) -> list[Cluster]:
        with self.connect() as conn:
            cluster_rows = conn.execute(
                "SELECT id, centroid_embedding_json, metadata_json, category_id, subcategory_id FROM clusters ORDER BY id"
            ).fetchall()
            membership_rows = conn.execute(
                "SELECT cluster_id, article_id FROM cluster_articles ORDER BY cluster_id, article_id"
            ).fetchall()

        articles_by_cluster: dict[str, list[str]] = {}
        for row in membership_rows:
            articles_by_cluster.setdefault(row["cluster_id"], []).append(row["article_id"])

        out: list[Cluster] = []
        for row in cluster_rows:
            try:
                centroid = json.loads(row["centroid_embedding_json"]) if row["centroid_embedding_json"] else []
            except Exception:
                centroid = []
            try:
                metadata = json.loads(row["metadata_json"]) if row["metadata_json"] else {}
            except Exception:
                metadata = {}

            out.append(
                Cluster(
                    id=row["id"],
                    article_ids=articles_by_cluster.get(row["id"], []),
                    centroid_embedding=list(centroid) if isinstance(centroid, list) else [],
                    category_id=row["category_id"],
                    subcategory_id=row["subcategory_id"],
                    metadata=metadata if isinstance(metadata, dict) else {},
                )
            )
        return out

    def get_article_to_cluster_map(self) -> dict[str, str]:
        with self.connect() as conn:
            rows = conn.execute("SELECT article_id, cluster_id FROM cluster_articles").fetchall()
        return {row["article_id"]: row["cluster_id"] for row in rows}

    def upsert_cluster_proposals(self, proposals: Iterable[dict]) -> None:
        """Persist LLM cluster proposals.

        Payload items should follow the shape written by the legacy JSON artifact:
        {cluster_id, category, subcategory, tags}
        """

        with self.connect() as conn:
            for item in proposals:
                if not isinstance(item, dict):
                    continue
                cluster_id = str(item.get("cluster_id", "") or "").strip()
                if not cluster_id:
                    continue
                category = item.get("category") or {}
                subcategory = item.get("subcategory")
                tags = item.get("tags") or []

                conn.execute(
                    """
                    INSERT INTO cluster_proposals(cluster_id, category_json, subcategory_json, tags_json)
                    VALUES(?, ?, ?, ?)
                    ON CONFLICT(cluster_id) DO UPDATE SET
                      category_json=excluded.category_json,
                      subcategory_json=excluded.subcategory_json,
                      tags_json=excluded.tags_json,
                      updated_at=datetime('now');
                    """,
                    (
                        cluster_id,
                        json.dumps(category, sort_keys=True, separators=(",", ":")),
                        (
                            json.dumps(subcategory, sort_keys=True, separators=(",", ":"))
                            if subcategory is not None
                            else None
                        ),
                        json.dumps(tags, sort_keys=True, separators=(",", ":")),
                    ),
                )

    def list_cluster_proposals(self) -> list[dict]:
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT cluster_id, category_json, subcategory_json, tags_json FROM cluster_proposals ORDER BY cluster_id"
            ).fetchall()

        out: list[dict] = []
        for row in rows:
            try:
                category = json.loads(row["category_json"]) if row["category_json"] else {}
            except Exception:
                category = {}
            try:
                subcategory = json.loads(row["subcategory_json"]) if row["subcategory_json"] else None
            except Exception:
                subcategory = None
            try:
                tags = json.loads(row["tags_json"]) if row["tags_json"] else []
            except Exception:
                tags = []
            out.append(
                {
                    "cluster_id": row["cluster_id"],
                    "category": category if isinstance(category, dict) else {},
                    "subcategory": subcategory if isinstance(subcategory, dict) else None,
                    "tags": tags if isinstance(tags, list) else [],
                }
            )
        return out

    def upsert_categories(self, categories: Iterable[TaxonomyCategory]) -> None:
        with self.connect() as conn:
            for category in categories:
                conn.execute(
                    """
                    INSERT INTO taxonomy_categories(id, name, description, parent_id, level)
                    VALUES(?, ?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET
                      name=excluded.name,
                      description=excluded.description,
                      parent_id=excluded.parent_id,
                      level=excluded.level,
                      updated_at=datetime('now');
                    """,
                    (category.id, category.name, category.description, category.parent_id, int(category.level)),
                )

    def upsert_tags(self, tags: Iterable[Tag]) -> None:
        with self.connect() as conn:
            for tag in tags:
                conn.execute(
                    """
                    INSERT INTO tags(id, name, normalized_name, description, category_id)
                    VALUES(?, ?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET
                      name=excluded.name,
                      normalized_name=excluded.normalized_name,
                      description=excluded.description,
                      category_id=excluded.category_id,
                      updated_at=datetime('now');
                    """,
                    (tag.id, tag.name, tag.normalized_name, tag.description, tag.category_id),
                )

    def list_categories(self) -> list[TaxonomyCategory]:
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT id, name, description, parent_id, level FROM taxonomy_categories ORDER BY id"
            ).fetchall()
        return [
            TaxonomyCategory(
                id=row["id"],
                name=row["name"],
                description=row["description"],
                parent_id=row["parent_id"],
                level=int(row["level"]),
            )
            for row in rows
        ]

    def get_category_map(self) -> dict[str, TaxonomyCategory]:
        return {c.id: c for c in self.list_categories()}

    def get_tag_map(self) -> dict[str, Tag]:
        return {t.id: t for t in self.list_tags()}

    def list_tags(self) -> list[Tag]:
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT id, name, normalized_name, description, category_id FROM tags ORDER BY id"
            ).fetchall()
        return [
            Tag(
                id=row["id"],
                name=row["name"],
                normalized_name=row["normalized_name"],
                description=row["description"],
                category_id=row["category_id"],
            )
            for row in rows
        ]

    def map_cluster_to_category(
        self,
        cluster_id: str,
        category_id: str | None,
        subcategory_id: str | None = None,
        *,
        notes: str | None = None,
    ) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO cluster_category_map(cluster_id, category_id, subcategory_id, notes)
                VALUES(?, ?, ?, ?)
                ON CONFLICT(cluster_id) DO UPDATE SET
                  category_id=excluded.category_id,
                  subcategory_id=excluded.subcategory_id,
                  notes=excluded.notes,
                  updated_at=datetime('now');
                """,
                (cluster_id, category_id, subcategory_id, notes),
            )

    def get_cluster_category_map(self) -> dict[str, tuple[str | None, str | None]]:
        with self.connect() as conn:
            rows = conn.execute("SELECT cluster_id, category_id, subcategory_id FROM cluster_category_map").fetchall()
        return {row["cluster_id"]: (row["category_id"], row["subcategory_id"]) for row in rows}

    def upsert_article_tag_assignments(self, assignments: Iterable[ArticleTagAssignment]) -> None:
        with self.connect() as conn:
            for assignment in assignments:
                conn.execute(
                    """
                    INSERT INTO article_tag_assignments(article_id, tag_id, confidence)
                    VALUES(?, ?, ?)
                    ON CONFLICT(article_id, tag_id) DO UPDATE SET
                      confidence=excluded.confidence,
                      assigned_at=datetime('now');
                    """,
                    (assignment.article_id, assignment.tag_id, float(assignment.confidence)),
                )

    def get_article_tags(self, article_id: str) -> list[ArticleTagAssignment]:
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT article_id, tag_id, confidence
                FROM article_tag_assignments
                WHERE article_id=?
                ORDER BY confidence DESC, tag_id ASC
                """,
                (article_id,),
            ).fetchall()

        return [
            ArticleTagAssignment(
                article_id=row["article_id"], tag_id=row["tag_id"], confidence=float(row["confidence"])
            )
            for row in rows
        ]

    def get_article_tags_for_articles(self, article_ids: Iterable[str]) -> dict[str, list[ArticleTagAssignment]]:
        ids = [str(i) for i in article_ids if str(i)]
        if not ids:
            return {}

        # SQLite has a variable limit; chunk to stay well below it.
        chunk_size = 900
        out: dict[str, list[ArticleTagAssignment]] = {}

        with self.connect() as conn:
            for i in range(0, len(ids), chunk_size):
                chunk = ids[i : i + chunk_size]
                placeholders = ",".join("?" for _ in chunk)
                rows = conn.execute(
                    f"""
                    SELECT article_id, tag_id, confidence
                    FROM article_tag_assignments
                    WHERE article_id IN ({placeholders})
                    ORDER BY article_id ASC, confidence DESC, tag_id ASC
                    """,
                    tuple(chunk),
                ).fetchall()

                for row in rows:
                    article_id = row["article_id"]
                    out.setdefault(article_id, []).append(
                        ArticleTagAssignment(
                            article_id=article_id,
                            tag_id=row["tag_id"],
                            confidence=float(row["confidence"]),
                        )
                    )

        return out

    def set_manual_override(self, article_id: str, override: dict[str, object]) -> None:
        payload = json.dumps(override, sort_keys=True)
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO manual_overrides(article_id, override_json)
                VALUES(?, ?)
                ON CONFLICT(article_id) DO UPDATE SET
                  override_json=excluded.override_json,
                  updated_at=datetime('now');
                """,
                (article_id, payload),
            )

    def get_manual_override(self, article_id: str) -> dict[str, object] | None:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT override_json FROM manual_overrides WHERE article_id=?",
                (article_id,),
            ).fetchone()
        if not row:
            return None
        try:
            return json.loads(row["override_json"])
        except Exception:
            return None


def default_taxonomy_sqlite_path(documents_root: Path) -> Path:
    return documents_root / ".prismweave" / "taxonomy.sqlite"
