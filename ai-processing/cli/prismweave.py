#!/usr/bin/env python3
"""
PrismWeave CLI - Command line interface for document processing and search
"""

import asyncio
import sys
import time
from pathlib import Path
from typing import List, Optional, Dict, Any
import json
import argparse

try:
    import click
    from rich.console import Console
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.panel import Panel
    from rich.text import Text
except ImportError:
    click = None
    Console = None
    Table = None
    Progress = None
    Panel = None
    Text = None

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from src.processors.document_processor import DocumentProcessor
from src.search.semantic_search import SemanticSearch
from src.utils.config import get_config, reload_config

console = Console() if Console else None

def print_info(message: str):
    """Print info message"""
    if console:
        console.print(f"[blue]ℹ[/blue] {message}")
    else:
        print(f"INFO: {message}")

def print_success(message: str):
    """Print success message"""
    if console:
        console.print(f"[green]✓[/green] {message}")
    else:
        print(f"SUCCESS: {message}")

def print_error(message: str):
    """Print error message"""
    if console:
        console.print(f"[red]✗[/red] {message}")
    else:
        print(f"ERROR: {message}")

def print_warning(message: str):
    """Print warning message"""
    if console:
        console.print(f"[yellow]⚠[/yellow] {message}")
    else:
        print(f"WARNING: {message}")

async def process_documents(documents_path: str, output_format: str = "table", single_file: bool = False):
    """Process documents in the specified directory or a single file"""
    docs_path = Path(documents_path)
    
    if not docs_path.exists():
        print_error(f"Path not found: {documents_path}")
        return
    
    # Handle single file processing
    if single_file or docs_path.is_file():
        if not docs_path.is_file():
            print_error(f"File not found: {documents_path}")
            return
        
        if not docs_path.suffix.lower() == '.md':
            print_error(f"File must be a markdown (.md) file: {documents_path}")
            return
        
        md_files = [docs_path]
        print_info(f"Processing single file: {docs_path.name}")
    else:
        # Find all markdown files in directory
        md_files = list(docs_path.rglob("*.md"))
        if not md_files:
            print_warning(f"No markdown files found in {documents_path}")
            return
        
        print_info(f"Found {len(md_files)} markdown files to process")
    
    async with DocumentProcessor() as processor:
        # Check if Ollama is available
        health = await processor.health_check()
        if not health["ollama_available"]:
            print_error("Ollama server not available. Please start Ollama and try again.")
            return
        
        print_info(f"Available models: {', '.join(health['models_available'])}")
        
        # Process documents
        if console and Progress:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Processing documents...", total=len(md_files))
                
                results = []
                for file_path in md_files:
                    progress.update(task, description=f"Processing {file_path.name}")
                    result = await processor.process_document(file_path)
                    results.append(result)
                    progress.advance(task)
        else:
            print_info("Processing documents...")
            results = await processor.process_batch(md_files)
        
        # Display results
        successful = [r for r in results if r.success]
        failed = [r for r in results if not r.success]
        
        print_success(f"Successfully processed {len(successful)} documents")
        if failed:
            print_error(f"Failed to process {len(failed)} documents")
        
        if output_format == "json":
            output = {
                "summary": {
                    "total_documents": len(md_files),
                    "successful": len(successful),
                    "failed": len(failed),
                    "processing_time": sum(r.processing_time for r in results)
                },
                "results": [
                    {
                        "document": r.document_path,
                        "success": r.success,
                        "category": r.suggested_category,
                        "quality_score": r.quality_score,
                        "tags": r.suggested_tags,
                        "summary": r.generated_summary[:200] + "..." if len(r.generated_summary) > 200 else r.generated_summary,
                        "processing_time": r.processing_time,
                        "error": r.error
                    }
                    for r in results
                ]
            }
            print(json.dumps(output, indent=2, default=str))
        
        elif output_format == "table" and console and Table:
            table = Table(title="Document Processing Results")
            table.add_column("Document", style="cyan")
            table.add_column("Category", style="magenta")
            table.add_column("Quality", style="green")
            table.add_column("Tags", style="blue")
            table.add_column("Status", style="yellow")
            
            for result in results[:20]:  # Limit to first 20 for display
                doc_name = Path(result.document_path).name
                category = result.suggested_category if result.success else "error"
                quality = f"{result.quality_score:.1f}" if result.success else "N/A"
                tags = ", ".join(result.suggested_tags[:3]) if result.success and result.suggested_tags else "None"
                status = "✓" if result.success else "✗"
                
                table.add_row(doc_name, category, quality, tags, status)
            
            console.print(table)
            
            if len(results) > 20:
                print_info(f"Showing first 20 results. Total: {len(results)}")
        
        else:
            # Simple text output
            for result in results:
                if result.success:
                    print(f"✓ {Path(result.document_path).name} -> {result.suggested_category} (Quality: {result.quality_score:.1f})")
                else:
                    print(f"✗ {Path(result.document_path).name} -> Error: {result.error}")

async def search_documents(query: str, max_results: int = 10, search_type: str = "semantic"):
    """Search documents using semantic search"""
    print_info(f"Searching for: '{query}'")
    
    async with SemanticSearch() as search_engine:
        # Check if search engine is ready
        health = await search_engine.health_check()
        if not health["search_engine_ready"]:
            print_error("Search engine not ready. Please process documents first.")
            return
        
        if health["indexed_documents"] == 0:
            print_warning("No documents indexed. Please run 'prismweave process' first.")
            return
        
        print_info(f"Searching {health['indexed_documents']} indexed documents")
        
        # Perform search
        response = await search_engine.search(
            query=query,
            max_results=max_results,
            search_type=search_type
        )
        
        if not response.results:
            print_warning("No results found")
            return
        
        print_success(f"Found {len(response.results)} results in {response.search_time:.2f}s")
        
        if console and Table:
            table = Table(title=f"Search Results for '{query}'")
            table.add_column("Rank", style="dim")
            table.add_column("Document", style="cyan")
            table.add_column("Score", style="green")
            table.add_column("Snippet", style="white")
            
            for result in response.results:
                doc_name = Path(result.document_path).name
                score = f"{result.similarity_score:.3f}"
                snippet = result.snippet[:100] + "..." if len(result.snippet) > 100 else result.snippet
                
                table.add_row(str(result.rank), doc_name, score, snippet)
            
            console.print(table)
        else:
            # Simple text output
            for result in response.results:
                print(f"{result.rank}. {Path(result.document_path).name} (Score: {result.similarity_score:.3f})")
                print(f"   {result.snippet[:150]}...")
                print()

async def show_status():
    """Show system status and statistics"""
    config = get_config()
    
    print_info("PrismWeave AI Processing Status")
    print()
    
    # Test Ollama connection
    async with DocumentProcessor() as processor:
        health = await processor.health_check()
        
        if console and Panel:
            # Ollama status
            ollama_status = "🟢 Connected" if health["ollama_available"] else "🔴 Disconnected"
            console.print(Panel(
                f"[bold]Ollama Server:[/bold] {ollama_status}\n"
                f"[bold]Available Models:[/bold] {len(health.get('models_available', []))}\n"
                f"[bold]Models:[/bold] {', '.join(health.get('models_available', [])[:3])}{'...' if len(health.get('models_available', [])) > 3 else ''}",
                title="AI Engine Status"
            ))
        else:
            print(f"Ollama Server: {'Connected' if health['ollama_available'] else 'Disconnected'}")
            print(f"Available Models: {', '.join(health.get('models_available', []))}")
        
        # Processing statistics
        stats = processor.get_statistics()
        if console and Panel:
            console.print(Panel(
                f"[bold]Processed Documents:[/bold] {stats['processed_count']}\n"
                f"[bold]Processing Errors:[/bold] {stats['error_count']}\n"
                f"[bold]Average Processing Time:[/bold] {stats.get('average_processing_time', 0):.2f}s",
                title="Processing Statistics"
            ))
        else:
            print(f"\nProcessing Statistics:")
            print(f"  Processed Documents: {stats['processed_count']}")
            print(f"  Processing Errors: {stats['error_count']}")
            print(f"  Average Processing Time: {stats.get('average_processing_time', 0):.2f}s")
    
    # Search engine status
    async with SemanticSearch() as search_engine:
        search_health = await search_engine.health_check()
        search_stats = search_engine.get_statistics()
        
        if console and Panel:
            console.print(Panel(
                f"[bold]Search Engine:[/bold] {'🟢 Ready' if search_health['search_engine_ready'] else '🔴 Not Ready'}\n"
                f"[bold]Indexed Documents:[/bold] {search_health['indexed_documents']}\n"
                f"[bold]Total Searches:[/bold] {search_stats['total_searches']}\n"
                f"[bold]Average Search Time:[/bold] {search_stats.get('average_search_time', 0):.3f}s",
                title="Search Engine Status"
            ))
        else:
            print(f"\nSearch Engine: {'Ready' if search_health['search_engine_ready'] else 'Not Ready'}")
            print(f"  Indexed Documents: {search_health['indexed_documents']}")
            print(f"  Total Searches: {search_stats['total_searches']}")
            print(f"  Average Search Time: {search_stats.get('average_search_time', 0):.3f}s")

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="PrismWeave AI Document Processing CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Process command
    process_parser = subparsers.add_parser("process", help="Process documents with AI analysis")
    process_parser.add_argument("path", nargs="?", default=None, help="Documents directory path or single file path")
    process_parser.add_argument("--format", choices=["table", "json"], default="table", help="Output format")
    process_parser.add_argument("--single-file", action="store_true", help="Process a single markdown file instead of a directory")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search documents")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--max-results", type=int, default=10, help="Maximum results to return")
    search_parser.add_argument("--type", choices=["semantic", "hybrid", "keyword"], default="semantic", help="Search type")
    
    # Status command
    subparsers.add_parser("status", help="Show system status")
    
    # Config command
    config_parser = subparsers.add_parser("config", help="Show configuration")
    config_parser.add_argument("--reload", action="store_true", help="Reload configuration")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == "process":
            docs_path = args.path
            if not docs_path:
                config = get_config()
                docs_path = str(config.get_documents_path())
            
            asyncio.run(process_documents(docs_path, args.format, args.single_file))
        
        elif args.command == "search":
            asyncio.run(search_documents(args.query, args.max_results, args.type))
        
        elif args.command == "status":
            asyncio.run(show_status())
        
        elif args.command == "config":
            if args.reload:
                config = reload_config()
                print_success("Configuration reloaded")
            else:
                config = get_config()
            
            print_info("Current Configuration:")
            print(f"  Ollama Host: {config.ollama.host}")
            print(f"  Documents Path: {config.get_documents_path()}")
            print(f"  Vector DB Type: {config.vector_db.type}")
            print(f"  Processing Batch Size: {config.processing.batch_size}")
    
    except KeyboardInterrupt:
        print_info("Operation cancelled by user")
    except Exception as e:
        print_error(f"Command failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

def uv_main():
    """Entry point for UV compatibility"""
    main()
