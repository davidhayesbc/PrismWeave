from __future__ import annotations

import json
import os
from typing import Any
from urllib.parse import quote

import click
import requests


def _get_base_url(base_url: str | None) -> str:
    env = os.environ.get("PRISMWEAVE_API_URL")
    return (base_url or env or "http://localhost:8000").rstrip("/")


def _request(method: str, url: str, *, json_body: dict[str, Any] | None = None) -> Any:
    response = requests.request(method, url, json=json_body, timeout=30)
    if not response.ok:
        raise click.ClickException(f"{method} {url} failed: {response.status_code} {response.text}")
    if response.status_code == 204:
        return None
    return response.json()


@click.group()
@click.option(
    "--base-url",
    default=None,
    help="REST API base URL (default: PRISMWEAVE_API_URL or http://localhost:8000)",
)
@click.pass_context
def api(ctx: click.Context, base_url: str | None) -> None:
    """Interact with the PrismWeave REST API (visualization endpoints)."""

    ctx.ensure_object(dict)
    ctx.obj["base_url"] = _get_base_url(base_url)


@api.command(name="articles")
@click.pass_context
def list_articles(ctx: click.Context) -> None:
    """List article summaries."""

    base_url: str = ctx.obj["base_url"]
    data = _request("GET", f"{base_url}/articles")
    click.echo(json.dumps(data, indent=2, sort_keys=True))


@api.command(name="get")
@click.argument("article_id")
@click.pass_context
def get_article(ctx: click.Context, article_id: str) -> None:
    """Get a single article (metadata + markdown content)."""

    base_url: str = ctx.obj["base_url"]
    # Article IDs are path-like; requests will encode properly via prepared URL
    url = f"{base_url}/articles/{quote(article_id, safe='')}"
    data = _request("GET", url)
    click.echo(json.dumps(data, indent=2, sort_keys=True))


@api.command(name="rebuild")
@click.pass_context
def rebuild(ctx: click.Context) -> None:
    """Rebuild the visualization index (metadata/layout)."""

    base_url: str = ctx.obj["base_url"]
    data = _request("POST", f"{base_url}/visualization/rebuild")
    click.echo(json.dumps(data, indent=2, sort_keys=True))


@api.command(name="update")
@click.argument("article_id")
@click.option("--title", default=None)
@click.option("--topic", default=None)
@click.option("--tags", default=None, help="Comma-separated tags")
@click.option("--read-status", default=None, type=click.Choice(["unread", "read"], case_sensitive=False))
@click.option("--content", default=None)
@click.pass_context
def update(
    ctx: click.Context,
    article_id: str,
    title: str | None,
    topic: str | None,
    tags: str | None,
    read_status: str | None,
    content: str | None,
) -> None:
    """Update an article."""

    base_url: str = ctx.obj["base_url"]
    payload: dict[str, Any] = {}
    if title is not None:
        payload["title"] = title
    if topic is not None:
        payload["topic"] = topic
    if tags is not None:
        payload["tags"] = [t.strip() for t in tags.split(",") if t.strip()]
    if read_status is not None:
        payload["read_status"] = read_status
    if content is not None:
        payload["content"] = content

    url = f"{base_url}/articles/{quote(article_id, safe='')}"
    data = _request("PUT", url, json_body=payload)
    click.echo(json.dumps(data, indent=2, sort_keys=True))


@api.command(name="delete")
@click.argument("article_id")
@click.pass_context
def delete(ctx: click.Context, article_id: str) -> None:
    """Delete an article."""

    base_url: str = ctx.obj["base_url"]
    url = f"{base_url}/articles/{quote(article_id, safe='')}"
    _request("DELETE", url)
    click.echo("Deleted")


__all__ = ["api"]
