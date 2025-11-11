"""Export command for PrismWeave CLI."""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import click

from src.cli_support import CliError, create_state
from src.core.embedding_store import EmbeddingStore


def handle_cli_error(exc: CliError) -> None:
    """Handle CLI errors by printing and exiting."""
    print(f"❌ {exc}")
    sys.exit(1)


@click.command()
@click.argument("output_file", type=click.Path(path_type=Path))
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, path_type=Path),
    help="Configuration file path (default: config.yaml)",
)
@click.option(
    "--format",
    "-f",
    type=click.Choice(["json", "csv"]),
    default="json",
    help="Export format (default: json)",
)
@click.option("--filter-type", type=str, help="Filter by file type (e.g., md, txt, pdf)")
@click.option("--include-content", is_flag=True, help="Include full content in export (JSON only)")
@click.option("--max", "-m", "max_docs", type=int, help="Maximum number of documents to export")
def export(
    output_file: Path,
    config: Optional[Path],
    format: str,
    filter_type: Optional[str],
    include_content: bool,
    max_docs: Optional[int],
) -> None:
    """Export documents and metadata to JSON or CSV."""

    print("💾 PrismWeave Document Export")
    print("=" * 40)

    try:
        state = create_state(config, verbose=False)
        store = EmbeddingStore(state.config)

        state.write("\n📥 Retrieving documents...")
        documents = store.list_documents(max_docs)
        if not documents:
            state.write("❌ No documents to export")
            return

        if filter_type:
            suffix = f".{filter_type.lstrip('.')}"
            documents = [
                doc
                for doc in documents
                if Path(doc["metadata"].get("source_file", "")).suffix == suffix
            ]
            if not documents:
                state.write(f"❌ No documents found with file type: {filter_type}")
                return
            state.write(f"🔍 Filtered to {len(documents)} documents with type: {filter_type}")

        export_data = {
            "export_date": datetime.now().isoformat(),
            "total_documents": len(documents),
            "collection_name": state.config.collection_name,
            "documents": [],
        }

        for doc in documents:
            metadata = doc["metadata"]
            payload = {
                "id": doc["id"],
                "source_file": metadata.get("source_file", "Unknown"),
                "chunk_index": metadata.get("chunk_index"),
                "total_chunks": metadata.get("total_chunks"),
                "tags": metadata.get("tags", ""),
                "content_length": doc["content_length"],
            }

            if include_content and format == "json":
                try:
                    full_docs = store.document_store.get_documents(ids=[doc["id"]])
                    if full_docs:
                        payload["content"] = full_docs[0].content
                    else:
                        payload["content_preview"] = doc["content_preview"]
                except Exception as exc:  # pragma: no cover - external dependency
                    state.write(f"⚠️  Warning: Failed to fetch full content: {exc}")
                    payload["content_preview"] = doc["content_preview"]
            else:
                payload["content_preview"] = doc["content_preview"]

            export_data["documents"].append(payload)

        if format == "json":
            state.write(f"\n💾 Exporting to JSON: {output_file}")
            with output_file.open("w", encoding="utf-8") as handle:
                json.dump(export_data, handle, indent=2, ensure_ascii=False)
        else:
            state.write(f"\n💾 Exporting to CSV: {output_file}")
            import csv

            with output_file.open("w", newline="", encoding="utf-8") as handle:
                fieldnames = [
                    "id",
                    "source_file",
                    "chunk_index",
                    "total_chunks",
                    "tags",
                    "content_length",
                    "content_preview",
                ]
                writer = csv.DictWriter(handle, fieldnames=fieldnames)
                writer.writeheader()
                for payload in export_data["documents"]:
                    writer.writerow(
                        {
                            "id": payload["id"],
                            "source_file": payload.get("source_file", ""),
                            "chunk_index": payload.get("chunk_index", ""),
                            "total_chunks": payload.get("total_chunks", ""),
                            "tags": payload.get("tags", ""),
                            "content_length": payload.get("content_length", 0),
                            "content_preview": payload.get(
                                "content_preview",
                                payload.get("content", ""),
                            ),
                        }
                    )

        state.write(f"✅ Exported {len(documents)} documents to {output_file}")
        state.write(f"   File size: {output_file.stat().st_size / 1024:.1f} KB")

    except CliError as exc:
        handle_cli_error(exc)
