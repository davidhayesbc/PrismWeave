#!/usr/bin/env python3
"""PrismWeave Document Processing CLI."""

from __future__ import annotations

import click

from src.core.config import Config as _ConfigAlias
from src.cli.process_commands import process, sync
from src.cli.query_commands import count, list_docs, search, stats
from src.cli.export_command import export

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


def main() -> None:
    """Entry point for the CLI when executed directly."""
    cli()


if __name__ == "__main__":
    main()
