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
from datetime import datetime
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
    from src.models.ollama_client import OllamaClient
    from src.processors.langchain_document_processor import LangChainDocumentProcessor as DocumentProcessor
    from src.search.semantic_search import SemanticSearch
    from src.utils.vector_verification import VectorVerifier, quick_health_check, get_embeddings_summary
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
@click.option('--add-to-vector', is_flag=True, help='Add processed documents to vector database')
@click.option('--verify-embeddings', is_flag=True, help='Verify embeddings after processing')
@click.pass_context
def process(ctx, path, output, recursive, add_to_vector, verify_embeddings):
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
            embedding_results = {}
            
            # Initialize vector search if needed
            search_engine = None
            if add_to_vector:
                search_engine = SemanticSearch(config.vector)
                await search_engine.initialize()
            
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
                        
                        # Add to vector database if requested
                        if add_to_vector and search_engine:
                            # Create document ID from file path
                            document_id = str(file_path.relative_to(path_obj.parent if path_obj.is_file() else path_obj))
                            
                            # Read file content for embedding
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                            
                            # Combine metadata with analysis
                            embedding_metadata = {
                                **metadata,
                                'title': analysis.summary.split('.')[0] if analysis.summary else file_path.name,
                                'category': analysis.category,
                                'tags': analysis.tags,
                                'word_count': analysis.word_count,
                                'reading_time': analysis.reading_time,
                                'confidence': analysis.confidence,
                                'processed_at': datetime.now().isoformat()
                            }
                            
                            embedding_success = await search_engine.add_document(
                                document_id=document_id,
                                content=content,
                                metadata=embedding_metadata
                            )
                            
                            embedding_results[document_id] = embedding_success
                            
                            if embedding_success:
                                console.print(f"  ✅ {file_path.name} - {analysis.category} - {len(analysis.tags)} tags - [green]embedded[/green]")
                            else:
                                console.print(f"  ⚠️ {file_path.name} - {analysis.category} - {len(analysis.tags)} tags - [yellow]embedding failed[/yellow]")
                        else:
                            # Display progress without embedding info
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
            console.print(f"\n[green]Document analysis completed ({successful}/{len(files)} files successfully)[/green]")
            
            # Display embedding summary
            if add_to_vector:
                embedded_count = sum(1 for success in embedding_results.values() if success)
                console.print(f"[blue]Vector database: {embedded_count}/{len(embedding_results)} documents embedded[/blue]")
            
            # Verify embeddings if requested
            if verify_embeddings and add_to_vector and embedding_results:
                console.print("\n[blue]Verifying embeddings...[/blue]")
                
                verification_results = {}
                async with VectorVerifier() as verifier:
                    for doc_id, was_embedded in embedding_results.items():
                        if was_embedded:
                            verification = await verifier.verify_document_embedding(doc_id)
                            verification_results[doc_id] = verification
                
                # Display verification results
                verified_count = sum(1 for v in verification_results.values() if v.get('found', False))
                searchable_count = sum(1 for v in verification_results.values() if v.get('searchable', False))
                
                console.print(f"[green]Verification: {verified_count}/{len(verification_results)} documents found in vector DB[/green]")
                console.print(f"[green]Searchability: {searchable_count}/{len(verification_results)} documents searchable[/green]")
                
                # Show any verification issues
                for doc_id, verification in verification_results.items():
                    if not verification.get('found', False):
                        console.print(f"  ❌ {doc_id}: {verification.get('error', 'Not found')}")
                    elif verification.get('searchable') is False:
                        console.print(f"  ⚠️ {doc_id}: Found but not searchable")
            
            # Save results if output specified
            if output:
                output_path = Path(output)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                output_data = {
                    'processing_results': results,
                    'embedding_results': embedding_results if add_to_vector else None,
                    'verification_results': verification_results if verify_embeddings and add_to_vector else None,
                    'summary': {
                        'total_files': len(files),
                        'successful_analysis': successful,
                        'embedded_documents': sum(1 for success in embedding_results.values() if success) if add_to_vector else 0,
                        'verified_documents': verified_count if verify_embeddings and add_to_vector else 0,
                        'processed_at': datetime.now().isoformat()
                    }
                }
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(output_data, f, indent=2, default=str)
                
                console.print(f"Results saved to: {output_path}")
                
            # Clean up
            if search_engine:
                await search_engine.close()
                
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
                similarity = f"{result.similarity:.3f}"
                title = result.metadata.get('title', 'Unknown')
                summary = result.metadata.get('summary', 'No summary available')
                
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

@cli.command()
@click.pass_context
def vector_health(ctx):
    """Check vector database health and embeddings status"""
    async def _vector_health():
        console.print("[blue]Checking Vector Database Health...[/blue]")
        
        try:
            async with VectorVerifier() as verifier:
                health_report = await verifier.comprehensive_health_check()
                
                # Overall status
                health_score = verifier._calculate_health_score(
                    health_report.database_accessible,
                    health_report.collection_exists,
                    health_report.document_count,
                    health_report.embedding_model_available,
                    health_report.integrity_check_passed
                )
                
                status_color = "green" if health_score >= 80 else "yellow" if health_score >= 50 else "red"
                console.print(f"\n[{status_color}]Overall Health Score: {health_score:.1f}/100[/{status_color}]")
                
                # Detailed health table
                table = Table(title="Vector Database Health Report")
                table.add_column("Component", style="cyan")
                table.add_column("Status", style="green")
                table.add_column("Details")
                
                # Database accessibility
                db_status = "✅ Accessible" if health_report.database_accessible else "❌ Inaccessible"
                table.add_row("Database", db_status, f"ChromaDB connection")
                
                # Collection existence
                collection_status = "✅ Exists" if health_report.collection_exists else "❌ Missing"
                table.add_row("Collection", collection_status, f"'{ctx.obj['config'].vector.collection_name}'")
                
                # Document count
                doc_status = f"✅ {health_report.document_count} documents" if health_report.document_count > 0 else "⚠️ Empty"
                table.add_row("Documents", doc_status, f"Size: {health_report.database_size_mb:.1f} MB")
                
                # Embedding model
                model_status = "✅ Available" if health_report.embedding_model_available else "❌ Missing"
                from src.utils.config_simplified import get_model_for_purpose
                model_name = get_model_for_purpose('embedding')
                table.add_row("Embedding Model", model_status, model_name)
                
                # Integrity check
                integrity_status = "✅ Passed" if health_report.integrity_check_passed else "❌ Failed"
                table.add_row("Integrity", integrity_status, "Database consistency check")
                
                # Last updated
                if health_report.last_updated:
                    last_updated = datetime.fromisoformat(health_report.last_updated).strftime("%Y-%m-%d %H:%M")
                    table.add_row("Last Updated", "📅", last_updated)
                
                console.print(table)
                
                # Performance metrics
                if health_report.performance_metrics:
                    console.print("\n[cyan]Performance Metrics:[/cyan]")
                    for metric, value in health_report.performance_metrics.items():
                        if isinstance(value, (int, float)):
                            console.print(f"  {metric}: {value:.2f}")
                        else:
                            console.print(f"  {metric}: {value}")
                
                # Sample documents
                if health_report.sample_documents:
                    console.print(f"\n[cyan]Sample Documents ({len(health_report.sample_documents)}):[/cyan]")
                    for doc in health_report.sample_documents[:3]:
                        doc_id = doc.get('id', 'Unknown')
                        metadata = doc.get('metadata', {})
                        title = metadata.get('title', metadata.get('filename', 'No title'))
                        console.print(f"  • {doc_id}: {title}")
                
                # Issues and recommendations
                if health_report.issues:
                    console.print("\n[red]Issues Found:[/red]")
                    for issue in health_report.issues:
                        console.print(f"  ❌ {issue}")
                
                if health_report.recommendations:
                    console.print("\n[yellow]Recommendations:[/yellow]")
                    for rec in health_report.recommendations:
                        console.print(f"  💡 {rec}")
                
        except Exception as e:
            console.print(f"[red]Vector health check failed: {e}[/red]")
    
    asyncio.run(_vector_health())

@cli.command()
@click.option('--limit', '-l', default=10, help='Number of documents to list')
@click.option('--verbose', '-v', is_flag=True, help='Show detailed information')
@click.pass_context
def vector_list(ctx, limit, verbose):
    """List documents in the vector database"""
    async def _vector_list():
        console.print(f"[blue]Listing Vector Database Documents (limit: {limit})...[/blue]")
        
        try:
            config = ctx.obj['config']
            search_engine = SemanticSearch(config.vector)
            
            async with search_engine:
                documents = await search_engine.list_documents(limit=limit)
                total_count = await search_engine.get_document_count()
                
                if not documents:
                    console.print("[yellow]No documents found in vector database[/yellow]")
                    return
                
                console.print(f"\n[green]Found {len(documents)} documents (total: {total_count})[/green]")
                
                if verbose:
                    # Detailed table
                    table = Table(title="Vector Database Documents (Detailed)")
                    table.add_column("ID", style="cyan", max_width=30)
                    table.add_column("Title", style="green", max_width=40)
                    table.add_column("Metadata", max_width=50)
                    table.add_column("Content Preview", max_width=60)
                    
                    for doc in documents:
                        doc_id = doc.get('id', 'Unknown')
                        metadata = doc.get('metadata', {})
                        title = metadata.get('title', metadata.get('filename', 'No title'))
                        
                        # Format metadata
                        meta_items = []
                        if metadata.get('category'):
                            meta_items.append(f"Category: {metadata['category']}")
                        if metadata.get('tags'):
                            tags = metadata['tags'][:3]  # Show first 3 tags
                            meta_items.append(f"Tags: {', '.join(tags)}")
                        if metadata.get('word_count'):
                            meta_items.append(f"Words: {metadata['word_count']}")
                        
                        meta_str = '\n'.join(meta_items) if meta_items else 'No metadata'
                        content_preview = doc.get('content_preview', 'No content preview')
                        
                        table.add_row(doc_id, title, meta_str, content_preview)
                else:
                    # Simple table
                    table = Table(title="Vector Database Documents")
                    table.add_column("ID", style="cyan")
                    table.add_column("Title", style="green")
                    table.add_column("Category", style="yellow")
                    table.add_column("Word Count", style="blue")
                    
                    for doc in documents:
                        doc_id = doc.get('id', 'Unknown')
                        metadata = doc.get('metadata', {})
                        title = metadata.get('title', metadata.get('filename', 'No title'))
                        category = metadata.get('category', 'uncategorized')
                        word_count = str(metadata.get('word_count', 'N/A'))
                        
                        table.add_row(doc_id, title, category, word_count)
                
                console.print(table)
                
        except Exception as e:
            console.print(f"[red]Vector list failed: {e}[/red]")
    
    asyncio.run(_vector_list())

@cli.command()
@click.argument('document_id')
@click.pass_context
def vector_verify(ctx, document_id):
    """Verify that a specific document is properly embedded"""
    async def _vector_verify():
        console.print(f"[blue]Verifying document embedding: {document_id}[/blue]")
        
        try:
            async with VectorVerifier() as verifier:
                result = await verifier.verify_document_embedding(document_id)
                
                if result.get('found'):
                    console.print(f"[green]✅ Document found in vector database[/green]")
                    
                    doc = result.get('document', {})
                    metadata = doc.get('metadata', {})
                    
                    # Document details
                    table = Table(title=f"Document: {document_id}")
                    table.add_column("Property", style="cyan")
                    table.add_column("Value", style="green")
                    
                    table.add_row("ID", document_id)
                    if metadata.get('title'):
                        table.add_row("Title", metadata['title'])
                    if metadata.get('category'):
                        table.add_row("Category", metadata['category'])
                    if metadata.get('tags'):
                        table.add_row("Tags", ', '.join(metadata['tags'][:5]))
                    if metadata.get('word_count'):
                        table.add_row("Word Count", str(metadata['word_count']))
                    
                    content_preview = doc.get('content_preview', '')
                    if content_preview:
                        table.add_row("Content Preview", content_preview)
                    
                    console.print(table)
                    
                    # Search test results
                    if result.get('searchable') is not None:
                        if result['searchable']:
                            console.print(f"[green]✅ Document is searchable (found in {result['search_results_count']} search results)[/green]")
                        else:
                            console.print(f"[yellow]⚠️ Document may not be properly indexed for search[/yellow]")
                    else:
                        console.print(f"[blue]ℹ️ {result.get('note', 'No search test performed')}[/blue]")
                else:
                    error = result.get('error', 'Unknown error')
                    console.print(f"[red]❌ Document not found: {error}[/red]")
                    
        except Exception as e:
            console.print(f"[red]Document verification failed: {e}[/red]")
    
    asyncio.run(_vector_verify())

@cli.command()
@click.option('--output', '-o', type=click.Path(), help='Output file for export')
@click.pass_context
def vector_export(ctx, output):
    """Export vector database information to a file"""
    async def _vector_export():
        if not output:
            output_path = Path(f"vector_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        else:
            output_path = Path(output)
        
        console.print(f"[blue]Exporting vector database info to: {output_path}[/blue]")
        
        try:
            async with VectorVerifier() as verifier:
                success = await verifier.export_embeddings_info(output_path)
                
                if success:
                    file_size = output_path.stat().st_size / 1024  # KB
                    console.print(f"[green]✅ Export completed: {output_path} ({file_size:.1f} KB)[/green]")
                else:
                    console.print(f"[red]❌ Export failed[/red]")
                    
        except Exception as e:
            console.print(f"[red]Export failed: {e}[/red]")
    
    asyncio.run(_vector_export())

@cli.command()
@click.pass_context  
def vector_stats(ctx):
    """Show quick vector database statistics"""
    async def _vector_stats():
        console.print("[blue]Vector Database Statistics...[/blue]")
        
        try:
            summary = await get_embeddings_summary()
            
            if 'error' in summary:
                console.print(f"[red]Error getting stats: {summary['error']}[/red]")
                return
            
            table = Table(title="Vector Database Quick Stats")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green")
            
            table.add_row("Documents", str(summary.get('document_count', 0)))
            table.add_row("Database Size", f"{summary.get('database_size_mb', 0):.1f} MB")
            
            accessible = summary.get('database_accessible', False)
            table.add_row("Accessible", "✅ Yes" if accessible else "❌ No")
            
            model_available = summary.get('embedding_model_available', False)
            table.add_row("Embedding Model", "✅ Available" if model_available else "❌ Missing")
            
            console.print(table)
            
        except Exception as e:
            console.print(f"[red]Stats failed: {e}[/red]")
    
    asyncio.run(_vector_stats())


def run_async_command(func):
    """Decorator to run async commands"""
    def wrapper(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))
    return wrapper

if __name__ == "__main__":
    cli()
