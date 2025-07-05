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
from src.rag.rag_synthesizer import RAGSynthesizer, RAGQuery
from src.utils.config import get_config, reload_config

console = Console() if Console else None

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

async def rag_query(args):
    """Handle RAG question answering"""
    print_info(f"Processing RAG query: {args.question}")
    
    try:
        async with RAGSynthesizer() as rag:
            # Build RAG query
            query = RAGQuery(
                question=args.question,
                synthesis_style=args.style,
                max_context_documents=args.max_docs
            )
            
            # Add filters if specified
            if args.category:
                query.context_types = args.category
            
            if args.tags:
                query.required_tags = [tag.strip() for tag in args.tags.split(',')]
            
            # Execute query
            response = await rag.query(query)
            
            # Display results
            if args.format == "json":
                result = {
                    "question": response.question,
                    "answer": response.answer,
                    "confidence": response.confidence_score,
                    "processing_time": response.processing_time,
                    "model": response.synthesis_model,
                    "context_documents": response.context_document_count,
                    "sources": [
                        {
                            "title": src.title,
                            "path": src.document_path,
                            "similarity": src.similarity_score
                        } for src in response.sources
                    ]
                }
                print(json.dumps(result, indent=2))
            else:
                # Rich text display
                if console and Panel:
                    # Question panel
                    console.print(Panel(
                        response.question,
                        title="❓ Question",
                        border_style="blue"
                    ))
                    
                    # Answer panel
                    console.print(Panel(
                        response.answer,
                        title="💡 Answer",
                        border_style="green"
                    ))
                    
                    # Metadata
                    metadata_text = f"""
🤖 Model: {response.synthesis_model}
📊 Confidence: {response.confidence_score:.2f}
📚 Context Documents: {response.context_document_count}
⏱️  Processing Time: {response.processing_time:.2f}s
                    """.strip()
                    
                    console.print(Panel(
                        metadata_text,
                        title="📋 Metadata",
                        border_style="cyan"
                    ))
                    
                    # Sources table
                    if response.sources and Table:
                        sources_table = Table(title="📖 Sources")
                        sources_table.add_column("Title", style="cyan")
                        sources_table.add_column("Similarity", style="green")
                        sources_table.add_column("Path", style="dim")
                        
                        for src in response.sources[:5]:  # Show top 5 sources
                            sources_table.add_row(
                                src.title,
                                f"{src.similarity_score:.3f}",
                                str(Path(src.document_path).name)
                            )
                        
                        console.print(sources_table)
                
                else:
                    # Simple text output
                    print(f"\nQuestion: {response.question}")
                    print(f"\nAnswer:\n{response.answer}")
                    print(f"\nMetadata:")
                    print(f"  Model: {response.synthesis_model}")
                    print(f"  Confidence: {response.confidence_score:.2f}")
                    print(f"  Context Documents: {response.context_document_count}")
                    print(f"  Processing Time: {response.processing_time:.2f}s")
                    
                    if response.sources:
                        print(f"\nTop Sources:")
                        for i, src in enumerate(response.sources[:3], 1):
                            print(f"  {i}. {src.title} (similarity: {src.similarity_score:.3f})")

    except Exception as e:
        print_error(f"RAG query failed: {str(e)}")

async def technical_query(args):
    """Handle technical questions"""
    print_info(f"Processing technical query: {args.question}")
    
    try:
        async with RAGSynthesizer() as rag:
            # Parse technologies if provided
            technologies = []
            if args.technologies:
                technologies = [tech.strip() for tech in args.technologies.split(',')]
            
            # Execute technical query
            response = await rag.technical_query(args.question, technologies)
            
            # Display results
            if args.format == "json":
                result = {
                    "question": response.question,
                    "answer": response.answer,
                    "confidence": response.confidence_score,
                    "processing_time": response.processing_time,
                    "model": response.synthesis_model,
                    "context_documents": response.context_document_count,
                    "technologies": technologies,
                    "sources": [
                        {
                            "title": src.title,
                            "path": src.document_path,
                            "similarity": src.similarity_score,
                            "tags": src.metadata.get('tags', [])
                        } for src in response.sources
                    ]
                }
                print(json.dumps(result, indent=2))
            else:
                # Rich text display for technical content
                if console and Panel:
                    console.print(Panel(
                        response.question,
                        title="🔧 Technical Question",
                        border_style="blue"
                    ))
                    
                    console.print(Panel(
                        response.answer,
                        title="⚙️ Technical Answer",
                        border_style="green"
                    ))
                    
                    if technologies:
                        tech_text = ", ".join(technologies)
                        console.print(Panel(
                            tech_text,
                            title="🏷️ Focus Technologies",
                            border_style="yellow"
                        ))
                else:
                    print(f"\n🔧 Technical Question: {response.question}")
                    if technologies:
                        print(f"🏷️ Focus Technologies: {', '.join(technologies)}")
                    print(f"\n⚙️ Technical Answer:\n{response.answer}")

    except Exception as e:
        print_error(f"Technical query failed: {str(e)}")

async def research_synthesis(args):
    """Handle research synthesis"""
    print_info(f"Synthesizing research on: {args.topic}")
    
    try:
        async with RAGSynthesizer() as rag:
            # Execute research synthesis
            response = await rag.research_synthesis(args.topic)
            
            # Display results
            if args.format == "json":
                result = {
                    "topic": args.topic,
                    "synthesis": response.answer,
                    "confidence": response.confidence_score,
                    "processing_time": response.processing_time,
                    "model": response.synthesis_model,
                    "research_documents": response.context_document_count,
                    "sources": [
                        {
                            "title": src.title,
                            "path": src.document_path,
                            "similarity": src.similarity_score,
                            "category": src.metadata.get('category'),
                            "tags": src.metadata.get('tags', [])
                        } for src in response.sources
                    ]
                }
                print(json.dumps(result, indent=2))
            else:
                # Rich text display for research
                if console and Panel:
                    console.print(Panel(
                        args.topic,
                        title="🔬 Research Topic",
                        border_style="blue"
                    ))
                    
                    console.print(Panel(
                        response.answer,
                        title="📊 Research Synthesis",
                        border_style="green"
                    ))
                    
                    synthesis_metadata = f"""
📚 Research Documents Analyzed: {response.context_document_count}
🤖 Synthesis Model: {response.synthesis_model}
📊 Confidence: {response.confidence_score:.2f}
⏱️  Processing Time: {response.processing_time:.2f}s
                    """.strip()
                    
                    console.print(Panel(
                        synthesis_metadata,
                        title="📋 Synthesis Metadata",
                        border_style="cyan"
                    ))
                else:
                    print(f"\n🔬 Research Topic: {args.topic}")
                    print(f"\n📊 Research Synthesis:\n{response.answer}")
                    print(f"\n📚 Research Documents Analyzed: {response.context_document_count}")

    except Exception as e:
        print_error(f"Research synthesis failed: {str(e)}")

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
    
    # RAG Query command
    rag_parser = subparsers.add_parser("ask", help="Ask questions using RAG (Retrieval Augmented Generation)")
    rag_parser.add_argument("question", help="Question to ask")
    rag_parser.add_argument("--style", choices=["brief", "comprehensive", "technical"], default="comprehensive", help="Response style")
    rag_parser.add_argument("--category", action="append", help="Filter by document categories (can be used multiple times)")
    rag_parser.add_argument("--tags", help="Comma-separated list of required tags")
    rag_parser.add_argument("--max-docs", type=int, default=10, help="Maximum context documents to use")
    rag_parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    
    # Technical Query command
    tech_parser = subparsers.add_parser("tech", help="Ask technical questions with technology focus")
    tech_parser.add_argument("question", help="Technical question to ask")
    tech_parser.add_argument("--technologies", help="Comma-separated list of technologies to focus on")
    tech_parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    
    # Research Synthesis command
    research_parser = subparsers.add_parser("research", help="Synthesize research on a topic")
    research_parser.add_argument("topic", help="Research topic to synthesize")
    research_parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    
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
        
        elif args.command == "ask":
            asyncio.run(rag_query(args))
        
        elif args.command == "tech":
            asyncio.run(technical_query(args))
        
        elif args.command == "research":
            asyncio.run(research_synthesis(args))
        
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
