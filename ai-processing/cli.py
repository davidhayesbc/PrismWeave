#!/usr/bin/env python3
"""PrismWeave Document Processing CLI.

Run via UV entry points:

    uv run prismweave-cli -- --help
    uv run prismweave-cli -- rebuild-db --yes

The legacy ``prismweave-process`` alias still invokes the same CLI.
"""

from __future__ import annotations

import click

from src.cli.api_commands import api
from src.cli.export_command import export
from src.cli.process_commands import process, rebuild_db, sync
from src.cli.query_commands import count, list_docs, search, stats
from src.cli.taxonomy_commands import taxonomy
from src.cli.visualize_commands import visualize
from src.core.config import Config as _ConfigAlias

# Backwards compatibility for tests that patch cli.Config
Config = _ConfigAlias


@click.group()
def cli() -> None:
    """PrismWeave Document Processing CLI."""


# Add commands to the CLI group
cli.add_command(process)
cli.add_command(sync)
cli.add_command(list_docs, name="list")
cli.add_command(count)
cli.add_command(search)
cli.add_command(stats)
cli.add_command(export)
cli.add_command(rebuild_db)
cli.add_command(visualize)
cli.add_command(api)
cli.add_command(taxonomy)


def main() -> None:
    """Entry point for the CLI when executed directly."""
    cli()


if __name__ == "__main__":
    main()
