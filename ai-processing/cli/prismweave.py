#!/usr/bin/env python3
"""
PrismWeave CLI - Simplified AI Document Processing Interface
Clean, straightforward interface without complex fallback mechanisms
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import List, Optional
import json

try:
    import click
    from rich.console import Console
    from rich.table import Table
    from rich.progress import Progress, TaskID
    from rich.logging import RichHandler
    from rich.panel import Panel
except ImportError as e:
    print(f"ERROR: Required dependencies not installed: {e}")
    print("Please install with: pip install click rich")
    sys.exit(1)

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

try:
    from src.models.ollama_client_simplified import OllamaClient
    from src.processors.document_processor_simplified import DocumentProcessor
    from src.utils.semantic_search import SemanticSearch
    from src.utils.config_simplified import get_config, load_config, Config
except ImportError as e:
    print(f"ERROR: PrismWeave modules not found: {e}")
    print("Please ensure you're running from the correct directory and modules are available")
    sys.exit(1)

# Setup rich console
console = Console()

# Setup logging
def setup_logging(level: str = "INFO"):
    """Setup logging with rich handler"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=console, rich_tracebacks=True)]
    )

@click.group()
@click.option('--config', '-c', type=click.Path(exists=True), help='Configuration file path')
@click.option('--log-level', default='INFO', help='Logging level')
@click.pass_context
def cli(ctx, config, log_level):
    """PrismWeave AI Processing - Simplified Interface"""
    ctx.ensure_object(dict)
    
    # Setup logging
    setup_logging(log_level)
    
    # Load configuration
    if config:
        ctx.obj['config'] = load_config(Path(config))
    else:
        ctx.obj['config'] = get_config()
    
    # Validate configuration
    issues = ctx.obj['config'].validate()
    if issues:
        console.print("[red]Configuration issues found:[/red]")
        for issue in issues:
            console.print(f"  - {issue}")
        raise click.Abort()

@cli.command()
@click.pass_context
def health(ctx):
    """Check system health and model availability"""
    async def _health():
        config = ctx.obj['config']
        
        console.print("[blue]Checking PrismWeave AI Health...[/blue]")
        
        try:
            async with OllamaClient(host=config.ollama.host, timeout=config.ollama.timeout) as client:
                health_info = await client.health_check()
                
                # Display health information
                table = Table(title="System Health")
                table.add_column("Component", style="cyan")
                table.add_column("Status", style="green")
                table.add_column("Details")
                
                # Server status
                server_status = "✅ Available" if health_info["server_available"] else "❌ Unavailable"
                table.add_row("Ollama Server", server_status, config.ollama.host)
                
                # Models status
                models_status = f"✅ {health_info['models_count']} models" if health_info["models_count"] > 0 else "❌ No models"
                table.add_row("Models", models_status, ", ".join(health_info["available_models"][:3]))
                
                # Configuration
                table.add_row("Configuration", "✅ Valid" if config.is_valid() else "❌ Invalid", f"Log level: {config.log_level}")
                
                console.print(table)
                
                # Check configured models
                if health_info["server_available"]:
                    console.print("\n[blue]Checking configured models...[/blue]")
                    
                    model_table = Table(title="Configured Models")
                    model_table.add_column("Purpose", style="cyan")
                    model_table.add_column("Model", style="yellow")
                    model_table.add_column("Status", style="green")
                    
                    for purpose, model_name in config.ollama.models.items():
                        available = await client.model_exists(model_name)
                        status = "✅ Available" if available else "❌ Not found"
                        model_table.add_row(purpose.title(), model_name, status)
                    
                    console.print(model_table)
        except Exception as e:
            console.print(f"[red]Health check failed: {e}[/red]")
    
    asyncio.run(_health())

@cli.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), help='Output file for results')
@click.option('--recursive', '-r', is_flag=True, help='Process directories recursively')
@click.pass_context
def process(ctx, path, output, recursive):
    """Process documents and generate AI analysis"""
    async def _process():
        config = ctx.obj['config']
        path_obj = Path(path)
        
        # Collect files to process
        if path_obj.is_file():
            files = [path_obj]
        elif path_obj.is_dir():
            pattern = "**/*.md" if recursive else "*.md"
            files = list(path_obj.glob(pattern))
        else:
            console.print(f"[red]Invalid path: {path_obj}[/red]")
            return
        
        if not files:
            console.print("[yellow]No markdown files found[/yellow]")
            return
        
        console.print(f"[blue]Processing {len(files)} files...[/blue]")
        
        try:
            processor = DocumentProcessor()
            results = []
            
            with Progress() as progress:
                task = progress.add_task("Processing files...", total=len(files))
                
                for file_path in files:
                    try:
                        progress.update(task, description=f"Processing {file_path.name}")
                        analysis, metadata = await processor.process_file(file_path)
                        
                        result = {
                            'file': str(file_path),
                            'analysis': {
                                'summary': analysis.summary,
                                'tags': analysis.tags,
                                'category': analysis.category,
                                'word_count': analysis.word_count,
                                'reading_time': analysis.reading_time,
                                'language': analysis.language,
                                'readability_score': analysis.readability_score,
                                'key_topics': analysis.key_topics,
                                'confidence': analysis.confidence
                            },
                            'metadata': metadata
                        }
                        results.append(result)
                        
                        # Display progress
                        console.print(f"  ✅ {file_path.name} - {analysis.category} - {len(analysis.tags)} tags")
                        
                    except Exception as e:
                        console.print(f"  ❌ {file_path.name} - Error: {e}")
                        results.append({
                            'file': str(file_path),
                            'error': str(e)
                        })
                    
                    progress.advance(task)
            
            # Display summary
            successful = sum(1 for r in results if 'analysis' in r)
            console.print(f"\n[green]Processed {successful}/{len(files)} files successfully[/green]")
            
            # Save results if output specified
            if output:
                output_path = Path(output)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=2, default=str)
                
                console.print(f"Results saved to: {output_path}")
        except Exception as e:
            console.print(f"[red]Processing failed: {e}[/red]")
    
    asyncio.run(_process())

@cli.command()
@click.argument('query')
@click.option('--limit', '-l', default=5, help='Maximum number of results')
@click.option('--threshold', '-t', default=0.7, help='Similarity threshold')
@click.pass_context
def search(ctx, query, limit, threshold):
    """Search documents using semantic similarity"""
    async def _search():
        config = ctx.obj['config']
        
        console.print(f"[blue]Searching for: '{query}'[/blue]")
        
        try:
            search_engine = SemanticSearch(config.vector)
            results = await search_engine.search(
                query=query,
                max_results=limit,
                similarity_threshold=threshold
            )
            
            if not results:
                console.print("[yellow]No matching documents found[/yellow]")
                return
            
            # Display results
            table = Table(title=f"Search Results for '{query}'")
            table.add_column("Document", style="cyan")
            table.add_column("Similarity", style="green")
            table.add_column("Summary")
            
            for result in results:
                similarity = f"{result.get('similarity', 0):.3f}"
                title = result.get('metadata', {}).get('title', 'Unknown')
                summary = result.get('metadata', {}).get('summary', 'No summary available')
                
                table.add_row(title, similarity, summary[:100] + "..." if len(summary) > 100 else summary)
            
            console.print(table)
            
        except Exception as e:
            console.print(f"[red]Search failed: {e}[/red]")
    
    asyncio.run(_search())

@cli.command()
@click.argument('question')
@click.option('--context-docs', '-n', default=3, help='Number of context documents to use')
@click.pass_context
def ask(ctx, question, context_docs):
    """Ask a question using RAG (Retrieval Augmented Generation)"""
    async def _ask():
        config = ctx.obj['config']
        
        console.print(f"[blue]Question: {question}[/blue]")
        
        try:
            # Search for relevant context
            search_engine = SemanticSearch(config.vector)
            context_results = await search_engine.search(
                query=question,
                max_results=context_docs,
                similarity_threshold=0.5
            )
            
            if not context_results:
                console.print("[yellow]No relevant documents found for context[/yellow]")
                return
            
            # Build context from search results
            context_texts = []
            for result in context_results:
                doc_title = result.get('metadata', {}).get('title', 'Unknown')
                doc_content = result.get('content', '')
                context_texts.append(f"Document: {doc_title}\n{doc_content}")
            
            context = "\n\n---\n\n".join(context_texts)
            
            # Generate answer using large model
            async with OllamaClient(host=config.ollama.host, timeout=config.ollama.timeout) as client:
                large_model = config.get_model('large')
                
                prompt = f"""Based on the following context documents, answer this question: {question}

Context:
{context}

Please provide a comprehensive answer based on the information in the context documents. If the context doesn't contain enough information to answer the question, say so.

Answer:"""
                
                console.print("[blue]Generating answer...[/blue]")
                
                result = await client.generate(
                    model=large_model,
                    prompt=prompt,
                    options={'temperature': 0.3}  # Lower temperature for more factual responses
                )
                
                # Display answer
                console.print(f"\n[green]Answer:[/green]")
                console.print(result.response)
                
                # Show context sources
                console.print(f"\n[dim]Based on {len(context_results)} documents:[/dim]")
                for result in context_results:
                    title = result.get('metadata', {}).get('title', 'Unknown')
                    similarity = result.get('similarity', 0)
                    console.print(f"  - {title} (similarity: {similarity:.3f})")
        
        except Exception as e:
            console.print(f"[red]Question answering failed: {e}[/red]")
    
    asyncio.run(_ask())

@cli.command()
@click.option('--model', help='Specific model to list/pull')
@click.option('--pull', is_flag=True, help='Pull/download the model')
@click.pass_context
def models(ctx, model, pull):
    """List available models or pull a specific model"""
    async def _models():
        config = ctx.obj['config']
        
        try:
            async with OllamaClient(host=config.ollama.host, timeout=config.ollama.timeout) as client:
                if pull and model:
                    console.print(f"[blue]Pulling model: {model}[/blue]")
                    success = await client.pull_model(model)
                    if success:
                        console.print(f"[green]Successfully pulled {model}[/green]")
                    else:
                        console.print(f"[red]Failed to pull {model}[/red]")
                    return
                
                # List models
                console.print("[blue]Listing available models...[/blue]")
                models_list = await client.list_models()
                
                if not models_list:
                    console.print("[yellow]No models found[/yellow]")
                    return
                
                table = Table(title="Available Models")
                table.add_column("Name", style="cyan")
                table.add_column("Size", style="green")
                table.add_column("Modified", style="yellow")
                
                for model_info in models_list:
                    size_gb = model_info.size / (1024**3)
                    table.add_row(
                        model_info.name,
                        f"{size_gb:.1f} GB",
                        model_info.modified
                    )
                
                console.print(table)
        except Exception as e:
            console.print(f"[red]Models command failed: {e}[/red]")
    
    asyncio.run(_models())

@cli.command()
@click.pass_context
def config_show(ctx):
    """Show current configuration"""
    config = ctx.obj['config']
    
    console.print("[blue]Current Configuration:[/blue]")
    
    # Ollama configuration
    console.print("\n[cyan]Ollama:[/cyan]")
    console.print(f"  Host: {config.ollama.host}")
    console.print(f"  Timeout: {config.ollama.timeout}s")
    console.print(f"  Models:")
    for purpose, model in config.ollama.models.items():
        console.print(f"    {purpose}: {model}")
    
    # Processing configuration
    console.print("\n[cyan]Processing:[/cyan]")
    console.print(f"  Max concurrent: {config.processing.max_concurrent}")
    console.print(f"  Chunk size: {config.processing.chunk_size}")
    console.print(f"  Summary timeout: {config.processing.summary_timeout}s")
    
    # Vector configuration
    console.print("\n[cyan]Vector Database:[/cyan]")
    console.print(f"  Collection: {config.vector.collection_name}")
    console.print(f"  Directory (relative): {config.vector.persist_directory}")
    
    # Calculate and display absolute path
    persist_path = Path(config.vector.persist_directory)
    if persist_path.is_absolute():
        abs_path = persist_path
    else:
        abs_path = Path.cwd() / persist_path
    console.print(f"  Directory (absolute): {abs_path.resolve()}")
    
    # Check if directory exists
    if abs_path.exists():
        console.print(f"  Status: ✅ Directory exists")
    else:
        console.print(f"  Status: ⚠️  Directory does not exist")
    
    console.print(f"  Max results: {config.vector.max_results}")
    console.print(f"  Similarity threshold: {config.vector.similarity_threshold}")
    
    # Validation
    issues = config.validate()
    if issues:
        console.print("\n[red]Configuration Issues:[/red]")
        for issue in issues:
            console.print(f"  - {issue}")
    else:
        console.print("\n[green]✅ Configuration is valid[/green]")


def run_async_command(func):
    """Decorator to run async commands"""
    def wrapper(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))
    return wrapper

if __name__ == "__main__":
    cli()
