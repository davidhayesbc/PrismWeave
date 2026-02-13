"""Tests for the new API routers (search, documents, processing, taxonomy, health, rebuild).

These tests use the Starlette TestClient with the FastAPI app.  All heavy
dependencies (EmbeddingStore, DocumentProcessor, config, Ollama) are mocked so
the tests run in isolation and don't require external services.
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from starlette.testclient import TestClient

from src.core.config import Config

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _reset_deps():
    """Reset the singleton caches in src.api.deps between tests."""
    import src.api.deps as deps_mod

    deps_mod._config = None
    deps_mod._store = None
    deps_mod._processor = None
    yield
    deps_mod._config = None
    deps_mod._store = None
    deps_mod._processor = None


@pytest.fixture()
def mock_config():
    cfg = Config()
    cfg.chroma_db_path = "/tmp/test-chroma"
    return cfg


@pytest.fixture()
def mock_store():
    store = MagicMock()
    store.search_similar.return_value = []
    store.list_documents.return_value = []
    store.get_document_count.return_value = 0
    store.get_unique_source_files.return_value = []
    store.verify_embeddings.return_value = {
        "status": "success",
        "collection_name": "test",
        "persist_directory": "/tmp/test-chroma",
        "document_count": 0,
    }
    store.get_file_document_count.return_value = 0
    store.remove_file_documents.return_value = None
    store.add_document.return_value = None
    return store


@pytest.fixture()
def mock_processor():
    proc = MagicMock()
    proc.process_document.return_value = [
        MagicMock(content="chunk-1"),
        MagicMock(content="chunk-2"),
    ]
    return proc


@pytest.fixture()
def client(mock_config, mock_store, mock_processor):
    """Provide a TestClient with all deps pre-patched."""
    with (
        patch("src.api.deps.get_config", return_value=mock_config),
        patch("src.api.deps.get_embedding_store", return_value=mock_store),
        patch("src.api.deps.get_document_processor", return_value=mock_processor),
        patch("src.api.routers.search.get_embedding_store", return_value=mock_store),
        patch("src.api.routers.documents.get_embedding_store", return_value=mock_store),
        patch("src.api.routers.documents.get_config", return_value=mock_config),
        patch("src.api.routers.processing.get_config", return_value=mock_config),
        patch("src.api.routers.processing.get_embedding_store", return_value=mock_store),
        patch("src.api.routers.processing.get_document_processor", return_value=mock_processor),
        patch("src.api.routers.health.get_config", return_value=mock_config),
        patch(
            "src.api.routers.health.check_ollama_available",
            return_value={"available": True, "host": "http://localhost:11434", "models": ["phi3:mini"]},
        ),
        patch("src.api.routers.taxonomy.get_config", return_value=mock_config),
        patch(
            "src.api.routers.taxonomy.check_ollama_available",
            return_value={"available": True, "host": "http://localhost:11434", "models": []},
        ),
        patch("src.api.routers.rebuild.get_config", return_value=mock_config),
        patch(
            "src.api.routers.rebuild.check_ollama_available",
            return_value={"available": True, "host": "http://localhost:11434", "models": []},
        ),
    ):
        from src.api.app import app

        yield TestClient(app, raise_server_exceptions=False)


# ---------------------------------------------------------------------------
# Root & existing health
# ---------------------------------------------------------------------------


class TestRootEndpoint:
    def test_root_returns_api_info(self, client: TestClient):
        resp = client.get("/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "PrismWeave API"
        assert "endpoints" in data
        assert "search" in data["endpoints"]


# ---------------------------------------------------------------------------
# Search router
# ---------------------------------------------------------------------------


class TestSearchRouter:
    def test_post_search_empty_collection(self, client: TestClient):
        resp = client.post("/search", json={"query": "hello world"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["query"] == "hello world"
        assert data["total_results"] == 0
        assert data["results"] == []

    def test_get_search_empty_collection(self, client: TestClient):
        resp = client.get("/search", params={"q": "test query"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["query"] == "test query"

    def test_post_search_validation_requires_query(self, client: TestClient):
        resp = client.post("/search", json={})
        assert resp.status_code == 422  # Validation error

    def test_post_search_with_results(self, client: TestClient, mock_store):
        # Build a mock Haystack Document
        doc = MagicMock()
        doc.id = "chunk-1"
        doc.content = "Hello world from document"
        doc.score = 0.95
        doc.meta = {
            "source_file": "/docs/test.md",
            "chunk_index": 0,
            "total_chunks": 1,
            "tags": "python,test",
        }
        mock_store.search_similar.return_value = [doc]

        resp = client.post("/search", json={"query": "hello"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_results"] == 1
        assert data["results"][0]["file_name"] == "test.md"
        assert data["results"][0]["score"] == 0.95

    def test_post_search_threshold_filters(self, client: TestClient, mock_store):
        doc = MagicMock()
        doc.id = "chunk-1"
        doc.content = "low score"
        doc.score = 0.3
        doc.meta = {"source_file": "test.md"}
        mock_store.search_similar.return_value = [doc]

        resp = client.post("/search", json={"query": "test", "threshold": 0.5})
        assert resp.status_code == 200
        assert resp.json()["total_results"] == 0  # Filtered out

    def test_post_search_filter_type(self, client: TestClient, mock_store):
        doc = MagicMock()
        doc.id = "c1"
        doc.content = "text"
        doc.score = 0.9
        doc.meta = {"source_file": "note.txt"}
        mock_store.search_similar.return_value = [doc]

        resp = client.post("/search", json={"query": "test", "filter_type": "md"})
        assert resp.status_code == 200
        assert resp.json()["total_results"] == 0  # .txt filtered out


# ---------------------------------------------------------------------------
# Documents router
# ---------------------------------------------------------------------------


class TestDocumentsRouter:
    def test_list_documents_empty(self, client: TestClient):
        resp = client.get("/documents")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_chunks"] == 0
        assert data["chunks"] == []

    def test_document_count(self, client: TestClient):
        resp = client.get("/documents/count")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_chunks"] == 0
        assert data["unique_source_files"] == 0

    def test_document_stats(self, client: TestClient):
        resp = client.get("/documents/stats")
        assert resp.status_code == 200
        data = resp.json()
        assert "total_chunks" in data
        assert "collection_name" in data

    def test_export_empty_returns_404(self, client: TestClient):
        resp = client.post("/documents/export", json={"format": "json"})
        assert resp.status_code == 404

    def test_export_json(self, client: TestClient, mock_store):
        mock_store.list_documents.return_value = [
            {
                "id": "chunk-1",
                "metadata": {"source_file": "test.md", "chunk_index": 0, "total_chunks": 1, "tags": ""},
                "content_length": 100,
                "content_preview": "hello",
            }
        ]
        resp = client.post("/documents/export", json={"format": "json"})
        assert resp.status_code == 200
        assert "application/json" in resp.headers["content-type"]

    def test_export_csv(self, client: TestClient, mock_store):
        mock_store.list_documents.return_value = [
            {
                "id": "chunk-1",
                "metadata": {"source_file": "test.md", "chunk_index": 0, "total_chunks": 1, "tags": ""},
                "content_length": 100,
                "content_preview": "hello",
            }
        ]
        resp = client.post("/documents/export", json={"format": "csv"})
        assert resp.status_code == 200
        assert "text/csv" in resp.headers["content-type"]


# ---------------------------------------------------------------------------
# Processing router
# ---------------------------------------------------------------------------


class TestProcessingRouter:
    def test_process_file_not_found(self, client: TestClient, mock_config):
        resp = client.post("/processing/file", json={"path": "/nonexistent/file.md"})
        assert resp.status_code == 404

    def test_process_file_unsupported_type(self, client: TestClient):
        with tempfile.NamedTemporaryFile(suffix=".xyz", delete=False) as f:
            f.write(b"data")
            path = f.name
        try:
            resp = client.post("/processing/file", json={"path": path})
            assert resp.status_code == 400
        finally:
            Path(path).unlink(missing_ok=True)

    def test_process_file_success(self, client: TestClient, mock_store, mock_processor):
        with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
            f.write(b"# Test\n\nSome content")
            path = f.name
        try:
            resp = client.post("/processing/file", json={"path": path})
            assert resp.status_code == 200
            data = resp.json()
            assert data["status"] == "success"
            assert data["files_processed"] == 1
        finally:
            Path(path).unlink(missing_ok=True)

    def test_process_file_skipped_already_processed(self, client: TestClient, mock_store):
        mock_store.get_file_document_count.return_value = 5

        with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
            f.write(b"# Test")
            path = f.name
        try:
            resp = client.post("/processing/file", json={"path": path, "force": False})
            assert resp.status_code == 200
            data = resp.json()
            assert data["status"] == "skipped"
        finally:
            Path(path).unlink(missing_ok=True)

    def test_process_directory_not_found(self, client: TestClient):
        resp = client.post("/processing/directory", json={"path": "/nonexistent/dir"})
        assert resp.status_code == 404

    def test_process_directory_empty(self, client: TestClient):
        with tempfile.TemporaryDirectory() as d:
            resp = client.post("/processing/directory", json={"path": d})
            assert resp.status_code == 200
            data = resp.json()
            assert data["status"] == "success"
            assert "No supported files" in data["message"]


# ---------------------------------------------------------------------------
# Health router
# ---------------------------------------------------------------------------


class TestHealthRouter:
    def test_detailed_health(self, client: TestClient):
        resp = client.get("/health/detailed")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] in ("healthy", "degraded", "unhealthy")
        assert data["ollama"]["available"] is True

    def test_llm_server_health(self, client: TestClient):
        """Test /health/ollama endpoint (mock only, no network)."""
        resp = client.get("/health/ollama")
        assert resp.status_code == 200
        data = resp.json()
        assert data["available"] is True
        assert data["host"] == "http://localhost:11434"


# ---------------------------------------------------------------------------
# Taxonomy router
# ---------------------------------------------------------------------------


class TestTaxonomyRouter:
    def test_cluster_endpoint(self, client: TestClient):
        with patch("src.taxonomy.pipeline.run_clustering_pipeline", return_value={"articles": 10, "clusters": 3}):
            resp = client.post("/taxonomy/cluster", json={"algorithm": "kmeans"})
            assert resp.status_code == 200
            data = resp.json()
            assert data["status"] == "success"

    def test_propose_requires_llm_server(self, client: TestClient, mock_config):
        """Propose returns 503 when LLM server is unavailable (mock only)."""
        with (
            patch("src.api.deps.get_config", return_value=mock_config),
            patch(
                "src.api.deps.check_ollama_available",
                return_value={"available": False, "host": "http://localhost:11434", "error": "not running"},
            ),
            patch(
                "src.api.routers.taxonomy.check_ollama_available",
                return_value={"available": False, "host": "http://localhost:11434", "error": "not running"},
            ),
        ):
            resp = client.post("/taxonomy/propose", json={"sample_size": 5})
            assert resp.status_code == 503

    def test_tag_new_file_not_found(self, client: TestClient):
        resp = client.post("/taxonomy/tag-new", json={"path": "/nonexistent/article.md"})
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Rebuild router
# ---------------------------------------------------------------------------


class TestRebuildRouter:
    def test_rebuild_embeddings_requires_llm_server(self, client: TestClient, mock_config):
        """Rebuild embeddings returns 503 when LLM server is unavailable (mock only)."""
        with (
            patch("src.api.deps.get_config", return_value=mock_config),
            patch(
                "src.api.deps.check_ollama_available",
                return_value={"available": False, "host": "http://localhost:11434", "error": "not running"},
            ),
            patch(
                "src.api.routers.rebuild.check_ollama_available",
                return_value={"available": False, "host": "http://localhost:11434", "error": "not running"},
            ),
        ):
            resp = client.post("/rebuild/embeddings", json={})
            assert resp.status_code == 503

    def test_rebuild_everything_requires_llm_server(self, client: TestClient, mock_config):
        """Rebuild everything returns 503 when LLM server is unavailable (mock only)."""
        with (
            patch("src.api.deps.get_config", return_value=mock_config),
            patch(
                "src.api.deps.check_ollama_available",
                return_value={"available": False, "host": "http://localhost:11434", "error": "not running"},
            ),
            patch(
                "src.api.routers.rebuild.check_ollama_available",
                return_value={"available": False, "host": "http://localhost:11434", "error": "not running"},
            ),
        ):
            resp = client.post("/rebuild/everything", json={})
            assert resp.status_code == 503


# ---------------------------------------------------------------------------
# OpenAPI schema validation
# ---------------------------------------------------------------------------


class TestOpenAPISchema:
    def test_openapi_schema_generated(self, client: TestClient):
        resp = client.get("/openapi.json")
        assert resp.status_code == 200
        schema = resp.json()
        assert schema["info"]["title"] == "PrismWeave API"
        assert schema["info"]["version"] == "0.2.0"

    def test_openapi_has_new_paths(self, client: TestClient):
        resp = client.get("/openapi.json")
        schema = resp.json()
        paths = schema["paths"]
        expected_paths = [
            "/search",
            "/documents",
            "/documents/count",
            "/documents/stats",
            "/documents/export",
            "/processing/file",
            "/processing/directory",
            "/taxonomy/cluster",
            "/taxonomy/propose",
            "/taxonomy/normalize",
            "/taxonomy/embed-tags",
            "/taxonomy/assign",
            "/taxonomy/tag-new",
            "/health/detailed",
            "/health/ollama",
            "/rebuild/embeddings",
            "/rebuild/everything",
        ]
        for path in expected_paths:
            assert path in paths, f"Missing path in OpenAPI schema: {path}"

    def test_openapi_has_tags(self, client: TestClient):
        resp = client.get("/openapi.json")
        schema = resp.json()
        tag_names = [t["name"] for t in schema.get("tags", [])]
        for expected_tag in ["search", "documents", "processing", "taxonomy", "rebuild", "health"]:
            assert expected_tag in tag_names, f"Missing tag: {expected_tag}"

    def test_swagger_docs_reachable(self, client: TestClient):
        resp = client.get("/docs")
        assert resp.status_code == 200

    def test_redoc_reachable(self, client: TestClient):
        resp = client.get("/redoc")
        assert resp.status_code == 200
