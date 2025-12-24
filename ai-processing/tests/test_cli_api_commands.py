from __future__ import annotations

import json
from types import SimpleNamespace

from click.testing import CliRunner

from cli import cli


def test_api_articles_prints_json(monkeypatch):
    def fake_request(method, url, json=None, timeout=None):
        assert method == "GET"
        assert url == "http://localhost:8000/articles"
        return SimpleNamespace(ok=True, status_code=200, text="", json=lambda: [{"id": "documents/a.md"}])

    monkeypatch.setattr("src.cli.api_commands.requests.request", fake_request)

    runner = CliRunner()
    result = runner.invoke(cli, ["api", "articles"])

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload[0]["id"] == "documents/a.md"


def test_api_get_encodes_article_id(monkeypatch):
    captured = {}

    def fake_request(method, url, json=None, timeout=None):
        captured["method"] = method
        captured["url"] = url
        return SimpleNamespace(ok=True, status_code=200, text="", json=lambda: {"id": "documents/x.md"})

    monkeypatch.setattr("src.cli.api_commands.requests.request", fake_request)

    runner = CliRunner()
    result = runner.invoke(cli, ["api", "get", "documents/unsorted/file name.md"])

    assert result.exit_code == 0
    assert captured["method"] == "GET"
    # spaces must be percent-encoded
    assert "file%20name.md" in captured["url"]
