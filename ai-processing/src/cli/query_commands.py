"""Query commands for PrismWeave CLI (list, count, search, stats)."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import List, Optional

import click

from src.cli_support import CliError, create_state
from src.core.embedding_store import EmbeddingStore

from .document_utils import get_document_content, get_document_metadata


def handle_cli_error(exc: CliError) -> None:
    """Handle CLI errors by printing and exiting."""
    print(f"❌ {exc}")
    sys.exit(1)


@click.command("list")
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, path_type=Path),
    help="Configuration file path (default: config.yaml)",
)
@click.option(
    "--max",
    "-m",
    "max_documents",
    type=int,
    default=50,
    help="Maximum number of files to show (default: 50)",
)
@click.option("--verbose", "-v", is_flag=True, help="Show detailed document information")
@click.option("--source-files", "-s", is_flag=True, help="Show unique source files only")
def list_docs(
    config: Optional[Path],
    max_documents: int,
    verbose: bool,
    source_files: bool,
) -> None:
    """List documents stored in the ChromaDB collection."""

    print("🔮 PrismWeave Document List")
    print("=" * 40)

    try:
        state = create_state(config, verbose)
        store = EmbeddingStore(state.config)

        if source_files:
            state.write("📂 Unique source files in collection:")
            files = store.get_unique_source_files()
            if not files:
                state.write("   No source files found in collection")
                return

            files_to_show = files[:max_documents] if max_documents else files
            for index, file_path in enumerate(files_to_show, start=1):
                state.write(f"   {index:3d}. {Path(file_path).name}")
                state.write_verbose(f"        📁 Full path: {file_path}")

            state.write(f"\n📊 Showing {len(files_to_show)} of {len(files)} unique source files")
            return

        state.write(f"📄 {'Document chunks' if verbose else 'Source files'} in collection (max: {max_documents}):\n")

        documents = store.list_documents(max_documents)
        if not documents:
            state.write("   No documents found in collection")
            verification = store.verify_embeddings()
            state.write(f"\n🔍 Collection info: {verification}")
            return

        if not verbose:
            all_documents = store.list_documents(None)
            if not all_documents:
                state.write("   No documents found in collection")
                verification = store.verify_embeddings()
                state.write(f"\n🔍 Collection info: {verification}")
                return

            source_groups = {}
            for doc in all_documents:
                source_file = doc["metadata"].get("source_file", "Unknown")
                source_groups.setdefault(source_file, []).append(doc)

            files_to_show = list(source_groups.items())[:max_documents]
            for index, (source_file, docs) in enumerate(files_to_show, start=1):
                file_name = Path(source_file).name if source_file != "Unknown" else "Unknown"
                state.write(f"   {index:3d}. {file_name}")
                state.write(f"        📄 Chunks: {len(docs)}")
                if docs and "tags" in docs[0]["metadata"]:
                    state.write(f"        🏷️  Tags: {docs[0]['metadata']['tags']}")
                total_chars = sum(doc["content_length"] for doc in docs)
                state.write(f"        📏 Total content: {total_chars:,} characters\n")

            files_shown = len(files_to_show)
            total_files = len(source_groups)
            total_chunks = sum(len(docs) for docs in source_groups.values())
            state.write(f"📊 Summary: {files_shown} files shown")
            state.write(f"   (Total in collection: {total_files} files, {total_chunks:,} chunks)")
            return

        for index, doc in enumerate(documents, start=1):
            metadata = doc["metadata"]
            source_file = metadata.get("source_file", "Unknown")
            file_name = Path(source_file).name if source_file != "Unknown" else "Unknown"
            state.write(f"   {index:3d}. Chunk ID: {doc['id']}")
            state.write(f"        📁 File: {file_name}")
            if "chunk_index" in metadata:
                chunk_info = f"{metadata['chunk_index'] + 1}/{metadata.get('total_chunks', '?')}"
                state.write(f"        🔢 Chunk: {chunk_info}")
            state.write(f"        📄 Length: {doc['content_length']} characters")
            if "tags" in metadata:
                state.write(f"        🏷️  Tags: {metadata['tags']}")
            state.write(f"        📝 Preview: {doc['content_preview']}\n")

        state.write(f"📊 Showing {len(documents)} chunks")
        total_count = store.get_document_count()
        if len(documents) < total_count:
            state.write(f"   (Total in collection: {total_count:,} chunks)")

    except CliError as exc:
        handle_cli_error(exc)


@click.command()
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, path_type=Path),
    help="Configuration file path (default: config.yaml)",
)
def count(config: Optional[Path]) -> None:
    """Show the total count of documents in the ChromaDB collection."""

    print("🔮 PrismWeave Document Count")
    print("=" * 40)

    try:
        state = create_state(config, verbose=False)
        store = EmbeddingStore(state.config)

        total_documents = store.get_document_count()
        unique_sources = len(store.get_unique_source_files())

        state.write("📊 Collection Statistics:")
        state.write(f"   📄 Total document chunks: {total_documents:,}")
        state.write(f"   📁 Unique source files: {unique_sources:,}")
        if total_documents and unique_sources:
            avg_chunks = total_documents / unique_sources
            state.write(f"   📈 Average chunks per file: {avg_chunks:.1f}")

        verification = store.verify_embeddings()
        state.write(f"   🗄️  Collection name: {verification.get('collection_name', 'Unknown')}")
        state.write(f"   💾 Storage path: {verification.get('persist_directory', 'Unknown')}")

    except CliError as exc:
        handle_cli_error(exc)


@click.command()
@click.argument("query")
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, path_type=Path),
    help="Configuration file path (default: config.yaml)",
)
@click.option(
    "--max",
    "-m",
    "max_results",
    type=int,
    default=10,
    help="Maximum number of results to return (default: 10)",
)
@click.option(
    "--threshold",
    "-t",
    type=float,
    default=0.0,
    help="Minimum similarity threshold (0.0-1.0, default: 0.0)",
)
@click.option("--verbose", "-v", is_flag=True, help="Show detailed search results")
@click.option("--filter-type", type=str, help="Filter results by file type (e.g., md, txt, pdf)")
def search(
    query: str,
    config: Optional[Path],
    max_results: int,
    threshold: float,
    *,
    verbose: bool,
    filter_type: Optional[str],
) -> None:
    """Search documents using semantic similarity."""

    try:
        state = create_state(config, verbose)
        store = EmbeddingStore(state.config)

        heading = "🔍 PrismWeave Semantic Search"
        if state.rich:
            state.rich.console.print(state.rich.Panel(heading, style="bold cyan"))
        else:
            state.write(heading)
            state.write("=" * 40)

        if state.rich:
            with state.rich.console.status(f"[bold green]Searching for: {query}..."):
                results = store.search_similar(query, k=max_results)
        else:
            state.write(f"\n🔎 Searching for: {query}")
            results = store.search_similar(query, k=max_results)

        if threshold > 0.0:
            filtered = []
            for doc in results:
                metadata = get_document_metadata(doc)
                if metadata.get("score", 0.0) >= threshold:
                    filtered.append(doc)
            results = filtered

        if filter_type:
            suffix = f".{filter_type.lstrip('.')}"
            filtered = []
            for doc in results:
                metadata = get_document_metadata(doc)
                if Path(metadata.get("source_file", "")).suffix == suffix:
                    filtered.append(doc)
            results = filtered

        if not results:
            state.write("\n❌ No results found")
            return

        state.write(f"\n✅ Found {len(results)} results\n")

        for index, doc in enumerate(results, start=1):
            metadata = get_document_metadata(doc)
            source_file = metadata.get("source_file", "Unknown")
            file_name = Path(source_file).name if source_file != "Unknown" else "Unknown"
            chunk_info = ""
            if "chunk_index" in metadata and "total_chunks" in metadata:
                chunk_info = f"{metadata['chunk_index'] + 1}/{metadata['total_chunks']}"

            content = get_document_content(doc)
            preview_length = 500 if verbose else 200
            preview = content[:preview_length]
            if len(content) > preview_length:
                preview += "..."

            tags = metadata.get("tags")
            score = metadata.get("score")
            lines: List[str] = [f"📁 File: {file_name}"]
            if chunk_info:
                lines.append(f"🔢 Chunk: {chunk_info}")
            if tags:
                lines.append(f"🏷️  Tags: {tags}")
            if score is not None:
                try:
                    lines.append(f"📈 Score: {float(score):.3f}")
                except (TypeError, ValueError):
                    lines.append(f"📈 Score: {score}")
            lines.append("\n📝 Content:\n" + preview)

            if state.rich:
                title = f"Result {index}: {file_name}"
                state.rich.console.print(state.rich.Panel("\n".join(lines), title=title, border_style="green"))
            else:
                state.write(f"{index}. {file_name}")
                for line in lines:
                    state.write(f"   {line}")
                state.write()

    except CliError as exc:
        handle_cli_error(exc)


@click.command()
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, path_type=Path),
    help="Configuration file path (default: config.yaml)",
)
@click.option("--detailed", "-d", is_flag=True, help="Show detailed analytics")
def stats(config: Optional[Path], detailed: bool) -> None:
    """Show collection statistics and analytics."""

    try:
        state = create_state(config, verbose=detailed)
        store = EmbeddingStore(state.config)

        heading = "📊 PrismWeave Collection Statistics"
        if state.rich:
            state.rich.console.print(state.rich.Panel(heading, style="bold cyan"))
        else:
            state.write(heading)
            state.write("=" * 40)

        total_chunks = store.get_document_count()
        source_files = store.get_unique_source_files()
        total_files = len(source_files)

        if total_chunks == 0:
            state.write("\n❌ No documents in collection")
            return

        avg_chunks = total_chunks / total_files if total_files else 0
        state.write()

        if state.rich:
            overview = state.rich.Table(title="Collection Overview", show_header=True)
            overview.add_column("Metric", style="cyan")
            overview.add_column("Value", style="green")
            overview.add_row("📄 Total Chunks", f"{total_chunks:,}")
            overview.add_row("📁 Source Files", f"{total_files:,}")
            overview.add_row("📈 Avg Chunks/File", f"{avg_chunks:.1f}")
            if detailed:
                documents = store.list_documents(None)
                total_content_length = sum(doc["content_length"] for doc in documents)
                if total_content_length:
                    overview.add_row("📏 Total Content", f"{total_content_length:,} chars")
                    overview.add_row(
                        "📊 Avg Chunk Size",
                        f"{total_content_length / total_chunks:.0f} chars",
                    )
            state.rich.console.print(overview)
        else:
            state.write("📊 Collection Overview:")
            state.write(f"   📄 Total chunks: {total_chunks:,}")
            state.write(f"   📁 Source files: {total_files:,}")
            state.write(f"   📈 Average chunks per file: {avg_chunks:.1f}")

        if detailed:
            documents = store.list_documents(None)
            file_types = {}
            tag_frequency = {}
            total_content = 0
            for doc in documents:
                metadata = doc["metadata"]
                source_file = metadata.get("source_file", "")
                if source_file:
                    ext = Path(source_file).suffix or "no extension"
                    file_types[ext] = file_types.get(ext, 0) + 1
                total_content += doc["content_length"]
                tags = metadata.get("tags", "")
                for tag in (item.strip() for item in tags.split(",")):
                    if tag:
                        tag_frequency[tag] = tag_frequency.get(tag, 0) + 1

            if state.rich and file_types:
                table = state.rich.Table(title="File Type Distribution", show_header=True)
                table.add_column("Extension", style="cyan")
                table.add_column("Count", style="green")
                table.add_column("Percentage", style="yellow")
                for ext, file_count in sorted(file_types.items(), key=lambda item: item[1], reverse=True):
                    table.add_row(ext, str(file_count), f"{(file_count / total_chunks) * 100:.1f}%")
                state.rich.console.print(table)
            elif file_types:
                state.write("\n📑 File Type Distribution:")
                for ext, file_count in sorted(file_types.items(), key=lambda item: item[1], reverse=True):
                    state.write(f"   {ext}: {file_count} ({(file_count / total_chunks) * 100:.1f}%)")

            if state.rich and tag_frequency:
                tag_table = state.rich.Table(title="Top 10 Tags", show_header=True)
                tag_table.add_column("Tag", style="cyan")
                tag_table.add_column("Frequency", style="green")
                for tag, freq in sorted(tag_frequency.items(), key=lambda item: item[1], reverse=True)[:10]:
                    tag_table.add_row(tag, str(freq))
                state.rich.console.print(tag_table)
            elif tag_frequency:
                state.write("\n🏷️  Top 10 Tags:")
                for tag, freq in sorted(tag_frequency.items(), key=lambda item: item[1], reverse=True)[:10]:
                    state.write(f"   {tag}: {freq}")

            if total_content:
                state.write(f"\n📏 Total content: {total_content:,} characters")
                state.write(f"📊 Average chunk size: {total_content / total_chunks:.0f} characters")

        verification = store.verify_embeddings()
        state.write(f"\nCollection: {verification.get('collection_name', 'Unknown')}")
        state.write(f"Storage: {verification.get('persist_directory', 'Unknown')}")

    except CliError as exc:
        handle_cli_error(exc)
