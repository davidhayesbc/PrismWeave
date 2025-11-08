#!/usr/bin/env python3
"""
PrismWeave Document Processing CLI

Process documents and generate embeddings using Haystack and Ollama.
Supports markdown, PDF, DOCX, HTML, and text files.
"""

import sys
import click
from pathlib import Path
from typing import Optional
import json
from datetime import datetime
import time

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Try to import rich for progress bars, fall back to basic output
try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn
    from rich.table import Table
    from rich.panel import Panel
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    
if RICH_AVAILABLE:
    console = Console()

from src.core.config import Config
from src.core.document_processor import DocumentProcessor
from src.core.embedding_store import EmbeddingStore
from src.core.git_tracker import GitTracker


def check_ollama_connection(config: Config) -> bool:
    """Check if Ollama is available and running"""
    try:
        import requests
        response = requests.get(f"{config.ollama_host}/api/tags", timeout=5)
        return response.status_code == 200
    except Exception:
        return False


def find_git_repository(start_path: Path) -> Optional[Path]:
    """Locate the nearest git repository root for the provided path."""

    current = start_path.resolve()
    if current.is_file():
        current = current.parent

    while True:
        if (current / ".git").exists():
            return current
        if current == current.parent:
            break
        current = current.parent
    return None


def process_single_file(file_path: Path, config: Config, git_tracker: Optional[GitTracker] = None, verbose: bool = False, force: bool = False):
    """Process a single document file"""
    
    # Check if file needs processing (unless force is specified)
    if not force and git_tracker and git_tracker.is_file_processed(file_path):
        if verbose:
            print(f"⏭️  Skipping {file_path.name} (already processed and unchanged)")
        return True
    
    if verbose:
        print(f"🔮 Processing: {file_path}")
        print(f"🤖 Using model: {config.embedding_model}")
        print(f"💾 Storage: {config.chroma_db_path}")
        print()
    
    # Initialize components
    processor = DocumentProcessor(config, git_tracker)
    store = EmbeddingStore(config, git_tracker)
    
    try:
        # Check if file already has embeddings and remove them (for updates)
        existing_count = store.get_file_document_count(file_path)
        if existing_count > 0:
            if verbose:
                print(f"🔄 Found {existing_count} existing chunks, removing for update...")
            store.remove_file_documents(file_path)
        
        # Process the document
        if verbose:
            print("📄 Loading and processing document...")
        chunks = processor.process_document(file_path)
        
        if chunks:
            if verbose:
                print(f"✅ Generated {len(chunks)} chunks")
            
            # Store embeddings
            if verbose:
                print("🔗 Generating and storing embeddings...")
            store.add_document(file_path, chunks)
            
            # Verify storage if verbose
            if verbose:
                print("🔍 Verifying embeddings storage...")
                verification = store.verify_embeddings()
                print(f"✅ Verification result: {verification}")
                
                # Show some metadata examples
                print("\n📊 Sample chunk metadata:")
                for i, chunk in enumerate(chunks[:2]):  # Show first 2 chunks
                    print(f"  Chunk {i+1}:")
                    print(f"    Content preview: {chunk.page_content[:100]}...")
                    print(f"    Metadata keys: {list(chunk.metadata.keys())}")
                    if 'tags' in chunk.metadata:
                        print(f"    Tags: {chunk.metadata['tags']}")
                    print()
            else:
                print(f"✅ Processed {file_path.name} ({len(chunks)} chunks)")
                
        else:
            print(f"❌ No chunks generated for {file_path}")
            return False
            
        return True
            
    except Exception as e:
        print(f"❌ Error processing {file_path.name}: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        return False


def process_directory(input_dir: Path, config: Config, git_tracker: Optional[GitTracker] = None, verbose: bool = False, incremental: bool = False, force: bool = False):
    """Process all supported files in a directory with enhanced progress reporting"""
    
    # Supported file extensions
    supported_extensions = {'.md', '.txt', '.pdf', '.docx', '.html', '.htm'}
    
    # Find files to process
    if incremental and git_tracker:
        # Only process new or changed files
        files_to_process = git_tracker.get_unprocessed_files(file_extensions=supported_extensions)
        if verbose:
            print(f"📂 Incremental mode: Found {len(files_to_process)} unprocessed files")
    else:
        # Find all supported files
        files_to_process = []
        for ext in supported_extensions:
            files_to_process.extend(list(input_dir.rglob(f"*{ext}")))
        
        if verbose:
            mode_text = "force mode" if force else "full mode"
            print(f"📂 Processing in {mode_text}: Found {len(files_to_process)} files")
    
    if not files_to_process:
        if incremental:
            print("✅ No new or changed files to process")
            return True
        else:
            print(f"❌ No supported files found in {input_dir}")
            print(f"   Supported extensions: {', '.join(supported_extensions)}")
            return False
    
    if verbose:
        print()
    
    # Process files with progress bar if rich is available
    success_count = 0
    error_count = 0
    skipped_count = 0
    start_time = time.time()
    
    if RICH_AVAILABLE and len(files_to_process) > 5:
        # Use rich progress bar for large batches
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeRemainingColumn(),
            console=console
        ) as progress:
            task = progress.add_task("[cyan]Processing documents...", total=len(files_to_process))
            
            for file_path in files_to_process:
                progress.update(task, description=f"[cyan]Processing: {file_path.name}")
                try:
                    if process_single_file(file_path, config, git_tracker, verbose=False, force=force):
                        success_count += 1
                    else:
                        error_count += 1
                except KeyboardInterrupt:
                    console.print("\n[yellow]⏹️  Processing interrupted by user[/yellow]")
                    break
                except Exception as e:
                    console.print(f"[red]❌ Error processing {file_path.name}: {e}[/red]")
                    error_count += 1
                finally:
                    progress.update(task, advance=1)
    else:
        # Fallback to simple output
        for i, file_path in enumerate(files_to_process, 1):
            print(f"[{i}/{len(files_to_process)}] Processing: {file_path.name}")
            try:
                if process_single_file(file_path, config, git_tracker, verbose=False, force=force):
                    success_count += 1
                else:
                    error_count += 1
            except KeyboardInterrupt:
                print("\n⏹️  Processing interrupted by user")
                break
            except Exception as e:
                print(f"❌ Error processing {file_path.name}: {e}")
                error_count += 1
    
    # Summary with timing
    elapsed_time = time.time() - start_time
    
    if RICH_AVAILABLE:
        # Rich formatted summary
        summary_table = Table(title="Processing Summary")
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="green")
        
        summary_table.add_row("✅ Successful", str(success_count))
        if error_count > 0:
            summary_table.add_row("❌ Failed", str(error_count))
        summary_table.add_row("⏱️  Time Elapsed", f"{elapsed_time:.1f}s")
        if success_count > 0:
            summary_table.add_row("📈 Avg Time/File", f"{elapsed_time/success_count:.2f}s")
        
        console.print("\n")
        console.print(summary_table)
    else:
        # Simple text summary
        print(f"\n📊 Processing Summary:")
        print(f"   ✅ Successfully processed: {success_count} files")
        if error_count > 0:
            print(f"   ❌ Failed to process: {error_count} files")
        print(f"   ⏱️  Time elapsed: {elapsed_time:.1f}s")
        if success_count > 0:
            print(f"   📈 Average time per file: {elapsed_time/success_count:.2f}s")
    
    # Update git tracker state if successful
    if success_count > 0 and git_tracker:
        try:
            git_tracker.update_last_processed_commit()
            if verbose:
                print("   🔄 Updated processing state")
        except Exception as e:
            print(f"   ⚠️  Warning: Failed to update processing state: {e}")
    
    return success_count > 0


def main():
    """Entry point for the CLI"""
    cli()


@click.group()
def cli():
    """PrismWeave Document Processing CLI"""
    pass


@cli.command()
@click.argument('path', type=click.Path(exists=True, path_type=Path))
@click.option('--config', '-c', type=click.Path(exists=True, path_type=Path), 
              help='Configuration file path (default: config.yaml)')
@click.option('--verbose', '-v', is_flag=True, 
              help='Show detailed output and metadata')
@click.option('--verify', is_flag=True, 
              help='Verify embeddings storage after processing')
@click.option('--clear', is_flag=True, 
              help='Clear existing embeddings before processing')
@click.option('--incremental', '-i', is_flag=True,
              help='Only process new or changed files (requires git repository)')
@click.option('--force', '-f', is_flag=True,
              help='Force reprocessing of all files, even if already processed')
@click.option('--repo-path', type=click.Path(exists=True, path_type=Path),
              help='Path to git repository (default: auto-detect from path)')
def process(path: Path, config: Optional[Path], verbose: bool, verify: bool, clear: bool, 
            incremental: bool, force: bool, repo_path: Optional[Path]):
    """
    Process documents and generate embeddings using Haystack and Ollama.
    
    PATH can be either a single file or a directory.
    
    Examples:
    
    \b
        # Process a single file
        python cli.py process document.md
        
        # Process all files in a directory
        python cli.py process ../PrismWeaveDocs/documents
        
        # Process with verbose output
        python cli.py process document.md --verbose
        
        # Clear existing embeddings and reprocess
        python cli.py process ../docs --clear --verify
        
        # Process only new or changed files (incremental)
        python cli.py process ../PrismWeaveDocs/documents --incremental
        
        # Force reprocess all files
        python cli.py process ../docs --force
    """
    
    print("🔮 PrismWeave Document Processor")
    print("=" * 40)
    
    # Validate conflicting options
    if incremental and force:
        print("❌ Cannot use --incremental and --force together")
        sys.exit(1)
    
    if incremental and clear:
        print("❌ Cannot use --incremental and --clear together")
        sys.exit(1)
    
    # Initialize git tracking if a repository is available
    git_tracker: Optional[GitTracker] = None
    repo_root: Optional[Path] = None

    if repo_path:
        repo_root = repo_path.resolve()
    else:
        repo_root = find_git_repository(path)

    if repo_root:
        try:
            git_tracker = GitTracker(repo_root)

            if verbose:
                print(f"🔄 Git repository: {repo_root}")
                summary = git_tracker.get_processing_summary()
                print(f"📊 Processing state: {summary['processed_files']} processed, {summary['unprocessed_files']} unprocessed")

            try:
                if verbose:
                    print("🔁 Pulling latest changes from remote...")
                git_tracker.pull_latest()
                if verbose:
                    print("   ✅ Repository up to date")
            except Exception as e:
                print(f"⚠️  Warning: Failed to pull latest changes: {e}")

            if verbose:
                print()

        except Exception as e:
            if incremental or repo_path:
                print(f"❌ Failed to initialize git tracking: {e}")
                if incremental:
                    print("   Incremental processing requires a git repository")
                sys.exit(1)
            else:
                print(f"⚠️  Warning: Git tracking not available: {e}")
                git_tracker = None
    else:
        if repo_path:
            print(f"❌ Path is not a git repository: {repo_path}")
            sys.exit(1)
        if incremental:
            print("❌ Incremental processing requires a git repository")
            sys.exit(1)
    
    # Load configuration
    try:
        if config:
            config_obj = Config.from_file(config)
        else:
            # Try default config file
            default_config = Path(__file__).parent / "config.yaml"
            if default_config.exists():
                config_obj = Config.from_file(default_config)
            else:
                config_obj = Config()
        
        validation_issues = config_obj.validate()
        if validation_issues:
            print("❌ Configuration issues:")
            for issue in validation_issues:
                print(f"   - {issue}")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        sys.exit(1)
    
    # Display configuration
    if verbose:
        print(f"🤖 Using model: {config_obj.embedding_model}")
        print(f"💾 Storage: {config_obj.chroma_db_path}")
        print(f"📏 Chunk size: {config_obj.chunk_size} characters")
        print()
    
    # Check if Ollama is available
    print("🔍 Checking Ollama availability...")
    if not check_ollama_connection(config_obj):
        print(f"❌ Cannot connect to Ollama at {config_obj.ollama_host}")
        print("\n💡 Make sure Ollama is running:")
        print("   ollama serve")
        print(f"   ollama pull {config_obj.embedding_model}")
        sys.exit(1)
    
    if verbose:
        print("✅ Ollama is running")
        print()
    
    # Clear embeddings if requested
    if clear:
        print("🗑️  Clearing existing embeddings...")
        store = EmbeddingStore(config_obj, git_tracker)
        store.clear_collection()
        
        # Also reset git processing state if available
        if git_tracker:
            git_tracker.reset_processing_state()
            print("🔄 Reset processing state")
        
        print("✅ Embeddings cleared")
        print()
    
    # Determine if path is file or directory and process accordingly
    try:
        if path.is_file():
            print(f"📄 Processing single file: {path}")
            if incremental:
                print("   (Note: Incremental mode applies to directory processing)")
            print()
            success = process_single_file(path, config_obj, git_tracker, verbose=verbose, force=force)
            
        elif path.is_dir():
            mode_desc = "incremental" if incremental else ("force" if force else "standard")
            print(f"📂 Processing directory: {path} (mode: {mode_desc})")
            print()
            success = process_directory(path, config_obj, git_tracker, verbose=verbose, 
                                      incremental=incremental, force=force)
            
        else:
            print(f"❌ Path is neither a file nor a directory: {path}")
            sys.exit(1)
        
        if not success:
            sys.exit(1)
        
        # Verify embeddings if requested
        if verify:
            print("\n🔍 Verifying embeddings storage...")
            store = EmbeddingStore(config_obj, git_tracker)
            verification = store.verify_embeddings()
            print(f"✅ Verification result: {verification}")

        if git_tracker:
            try:
                git_tracker.commit_processing_state()
                if verbose:
                    print("📝 Committed processing state")
            except Exception as e:
                print(f"⚠️  Warning: Failed to commit processing state: {e}")
        
        print("\n✅ Processing completed successfully!")
        
    except KeyboardInterrupt:
        print("\n⏹️  Processing interrupted by user")
        sys.exit(0)
        
    except Exception as e:
        print(f"\n❌ Processing failed: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


@cli.command()
@click.argument('repo_path', type=click.Path(exists=True, path_type=Path), required=False)
@click.option('--config', '-c', type=click.Path(exists=True, path_type=Path), 
              help='Configuration file path (default: config.yaml)')
@click.option('--force', is_flag=True,
              help='Force reprocessing of all files')
@click.option('--verbose', '-v', is_flag=True,
              help='Show detailed processing information')
def sync(repo_path: Optional[Path], config: Optional[Path], force: bool, verbose: bool):
    """
    Sync documents from a git repository, processing only new or changed files.
    
    This is a convenience command that automatically detects git repositories
    and processes only files that have changed since they were last processed.
    
    Examples:
    
    \b
        # Auto-detect git repository in current directory
        python cli.py sync
        
        # Sync specific repository
        python cli.py sync /path/to/docs
        
        # Force reprocess all files
        python cli.py sync --force
        
        # Show detailed processing information
        python cli.py sync --verbose
    """
    
    print("🔮 PrismWeave Document Sync")
    print("=" * 40)
    
    # Determine repository path
    if repo_path is None:
        # Try to auto-detect git repository
        current_path = Path.cwd()
        
        # Check if current directory is a git repository
        if (current_path / '.git').exists():
            repo_path = current_path
            if verbose:
                print(f"📁 Auto-detected git repository: {repo_path}")
        else:
            # Look for common document paths
            possible_paths = [
                current_path / 'PrismWeaveDocs',
                current_path.parent / 'PrismWeaveDocs',
                current_path / 'documents',
                current_path / 'docs'
            ]
            
            for path in possible_paths:
                if path.exists() and (path / '.git').exists():
                    repo_path = path
                    if verbose:
                        print(f"📁 Found git repository: {repo_path}")
                    break
            
            if repo_path is None:
                print("❌ No git repository found.")
                print("\n💡 Please specify a repository path or run from a git repository:")
                print("   python cli.py sync /path/to/your/docs")
                print("   OR cd into a git repository and run: python cli.py sync")
                sys.exit(1)
    
    # Validate that it's actually a git repository
    if not (repo_path / '.git').exists():
        print(f"❌ Path is not a git repository: {repo_path}")
        print("\n💡 Make sure you specify a path containing a .git folder")
        sys.exit(1)
    
    print(f"📂 Repository: {repo_path}")
    
    # Load configuration
    try:
        if config:
            config_obj = Config.from_file(config)
        else:
            # Try default config file
            default_config = Path(__file__).parent / "config.yaml"
            if default_config.exists():
                config_obj = Config.from_file(default_config)
            else:
                config_obj = Config()
        
        validation_issues = config_obj.validate()
        if validation_issues:
            print("❌ Configuration issues:")
            for issue in validation_issues:
                print(f"   - {issue}")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        sys.exit(1)
    
    # Check if Ollama is available
    print("🔍 Checking Ollama availability...")
    if not check_ollama_connection(config_obj):
        print(f"❌ Cannot connect to Ollama at {config_obj.ollama_host}")
        print("\n💡 Make sure Ollama is running:")
        print("   ollama serve")
        print(f"   ollama pull {config_obj.embedding_model}")
        sys.exit(1)
    
    if verbose:
        print("✅ Ollama is running")
    
    # Initialize git tracker and pull latest changes
    git_tracker: Optional[GitTracker] = None
    try:
        git_tracker = GitTracker(repo_path)
        if verbose:
            print("📝 Initialized git tracking for repository")
            summary = git_tracker.get_processing_summary()
            print(f"📊 Processing state: {summary['processed_files']} processed, {summary['unprocessed_files']} unprocessed")

        try:
            if verbose:
                print("🔁 Pulling latest changes from remote...")
            git_tracker.pull_latest()
            if verbose:
                print("   ✅ Repository up to date")
        except Exception as e:
            print(f"⚠️  Warning: Failed to pull latest changes: {e}")

        if verbose:
            print()

    except Exception as e:
        print(f"⚠️  Could not initialize git tracking: {e}")
        if not force:
            print("   Falling back to full processing mode")
        git_tracker = None
    
    # Run incremental processing
    mode = "force" if force else "incremental"
    print(f"🔄 Starting sync (mode: {mode})")
    print()
    
    try:
        success = process_directory(
            repo_path, 
            config_obj, 
            git_tracker=git_tracker,
            verbose=verbose, 
            incremental=not force, 
            force=force
        )
        
        if not success:
            sys.exit(1)
        
        if git_tracker:
            try:
                git_tracker.commit_processing_state()
                if verbose:
                    print("📝 Committed processing state")
            except Exception as e:
                print(f"⚠️  Warning: Failed to commit processing state: {e}")

        print("\n✅ Sync completed successfully!")
        
    except KeyboardInterrupt:
        print("\n⏹️  Sync interrupted by user")
        sys.exit(0)
        
    except Exception as e:
        print(f"\n❌ Sync failed: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


@cli.command('list')
@click.option('--config', '-c', type=click.Path(exists=True, path_type=Path), 
              help='Configuration file path (default: config.yaml)')
@click.option('--max', '-m', 'max_documents', type=int, default=50,
              help='Maximum number of files to show (or chunks in verbose mode, default: 50)')
@click.option('--verbose', '-v', is_flag=True,
              help='Show detailed document information')
@click.option('--source-files', '-s', is_flag=True,
              help='Show unique source files only')
def list_docs(config: Optional[Path], max_documents: int, verbose: bool, source_files: bool):
    """
    List documents stored in the ChromaDB collection.
    
    Examples:
    
    \b
        # List first 50 files (default)
        python cli.py list
        
        # List first 10 files
        python cli.py list --max 10
        
        # Show detailed information for first 5 chunks
        python cli.py list --max 5 --verbose
        
        # Show only unique source files
        python cli.py list --source-files
    """
    
    print("🔮 PrismWeave Document List")
    print("=" * 40)
    
    # Load configuration
    try:
        if config:
            config_obj = Config.from_file(config)
        else:
            # Try default config file
            default_config = Path(__file__).parent / "config.yaml"
            if default_config.exists():
                config_obj = Config.from_file(default_config)
            else:
                config_obj = Config()
        
        validation_issues = config_obj.validate()
        if validation_issues:
            print("❌ Configuration issues:")
            for issue in validation_issues:
                print(f"   - {issue}")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        sys.exit(1)
    
    # Initialize embedding store
    store = EmbeddingStore(config_obj)
    
    try:
        if source_files:
            # List unique source files
            print("📂 Unique source files in collection:")
            files = store.get_unique_source_files()
            
            if not files:
                print("   No source files found in collection")
                return
            
            # Apply max limit to source files too
            files_to_show = files[:max_documents] if max_documents else files
            
            for i, file_path in enumerate(files_to_show, 1):
                print(f"   {i:3d}. {Path(file_path).name}")
                if verbose:
                    print(f"        📁 Full path: {file_path}")
                
            print(f"\n📊 Showing {len(files_to_show)} of {len(files)} unique source files")
            
        else:
            # List documents
            if verbose:
                print(f"📄 Document chunks in collection (max: {max_documents}):")
            else:
                print(f"📄 Source files in collection (max: {max_documents}):")
            print()
            
            documents = store.list_documents(max_documents)
            
            if not documents:
                print("   No documents found in collection")
                verification = store.verify_embeddings()
                print(f"\n🔍 Collection info: {verification}")
                return
            
            if not verbose:
                # Compact mode - get all documents first to properly group by files
                all_documents = store.list_documents(None)  # Get all documents
                
                if not all_documents:
                    print("   No documents found in collection")
                    verification = store.verify_embeddings()
                    print(f"\n🔍 Collection info: {verification}")
                    return
                
                # Group by source file
                source_groups = {}
                for doc in all_documents:
                    source_file = doc['metadata'].get('source_file', 'Unknown')
                    if source_file not in source_groups:
                        source_groups[source_file] = []
                    source_groups[source_file].append(doc)
                
                # Limit the number of files shown, not chunks
                files_to_show = list(source_groups.items())[:max_documents]
                
                for i, (source_file, docs) in enumerate(files_to_show, 1):
                    file_name = Path(source_file).name if source_file != 'Unknown' else 'Unknown'
                    print(f"   {i:3d}. {file_name}")
                    print(f"        📄 Chunks: {len(docs)}")
                    
                    # Show tags from first chunk if available
                    if docs and 'tags' in docs[0]['metadata']:
                        tags = docs[0]['metadata']['tags']
                        print(f"        🏷️  Tags: {tags}")
                    
                    total_chars = sum(doc['content_length'] for doc in docs)
                    print(f"        📏 Total content: {total_chars:,} characters")
                    print()
                
                files_shown = len(files_to_show)
                total_files = len(source_groups)
                total_chunks = sum(len(docs) for docs in source_groups.values())
                
                print(f"📊 Summary: {files_shown} files shown")
                if files_shown < total_files:
                    print(f"   (Total in collection: {total_files} files, {total_chunks:,} chunks)")
                else:
                    print(f"   (Total in collection: {total_files} files, {total_chunks:,} chunks)")
                
            else:
                # Verbose mode - show individual chunks (documents already limited)
                for i, doc in enumerate(documents, 1):
                    print(f"   {i:3d}. Chunk ID: {doc['id']}")
                    
                    metadata = doc['metadata']
                    source_file = metadata.get('source_file', 'Unknown')
                    file_name = Path(source_file).name if source_file != 'Unknown' else 'Unknown'
                    print(f"        📁 File: {file_name}")
                    
                    if 'chunk_index' in metadata:
                        chunk_info = f"{metadata['chunk_index'] + 1}/{metadata.get('total_chunks', '?')}"
                        print(f"        🔢 Chunk: {chunk_info}")
                    
                    print(f"        📄 Length: {doc['content_length']} characters")
                    
                    if 'tags' in metadata:
                        print(f"        🏷️  Tags: {metadata['tags']}")
                    
                    print(f"        📝 Preview: {doc['content_preview']}")
                    print()
                
                print(f"📊 Showing {len(documents)} chunks")
                
                # Show total collection size
                total_count = store.get_document_count()
                if len(documents) < total_count:
                    print(f"   (Total in collection: {total_count:,} chunks)")
            
    except Exception as e:
        print(f"❌ Error listing documents: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


@cli.command()
@click.option('--config', '-c', type=click.Path(exists=True, path_type=Path), 
              help='Configuration file path (default: config.yaml)')
def count(config: Optional[Path]):
    """
    Show the total count of documents in the ChromaDB collection.
    
    Examples:
    
    \b
        # Show document count
        python cli.py count
    """
    
    print("🔮 PrismWeave Document Count")
    print("=" * 40)
    
    # Load configuration
    try:
        if config:
            config_obj = Config.from_file(config)
        else:
            # Try default config file
            default_config = Path(__file__).parent / "config.yaml"
            if default_config.exists():
                config_obj = Config.from_file(default_config)
            else:
                config_obj = Config()
        
        validation_issues = config_obj.validate()
        if validation_issues:
            print("❌ Configuration issues:")
            for issue in validation_issues:
                print(f"   - {issue}")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        sys.exit(1)
    
    # Initialize embedding store
    store = EmbeddingStore(config_obj)
    
    try:
        # Get counts
        total_documents = store.get_document_count()
        unique_sources = len(store.get_unique_source_files())
        
        print(f"📊 Collection Statistics:")
        print(f"   📄 Total document chunks: {total_documents:,}")
        print(f"   📁 Unique source files: {unique_sources:,}")
        
        if total_documents > 0:
            avg_chunks_per_file = total_documents / unique_sources if unique_sources > 0 else 0
            print(f"   📈 Average chunks per file: {avg_chunks_per_file:.1f}")
        
        # Get verification info
        verification = store.verify_embeddings()
        print(f"   🗄️  Collection name: {verification.get('collection_name', 'Unknown')}")
        print(f"   💾 Storage path: {verification.get('persist_directory', 'Unknown')}")
        
    except Exception as e:
        print(f"❌ Error getting document count: {e}")
        sys.exit(1)


@cli.command()
@click.argument('query')
@click.option('--config', '-c', type=click.Path(exists=True, path_type=Path), 
              help='Configuration file path (default: config.yaml)')
@click.option('--max', '-m', 'max_results', type=int, default=10,
              help='Maximum number of results to return (default: 10)')
@click.option('--threshold', '-t', type=float, default=0.0,
              help='Minimum similarity threshold (0.0-1.0, default: 0.0)')
@click.option('--verbose', '-v', is_flag=True,
              help='Show detailed search results')
@click.option('--filter-type', type=str,
              help='Filter results by file type (e.g., md, txt, pdf)')
def search(query: str, config: Optional[Path], max_results: int, threshold: float, verbose: bool, filter_type: Optional[str]):
    """
    Search documents using semantic similarity.
    
    Examples:
    
    \b
        # Basic search
        python cli.py search "machine learning concepts"
        
        # Search with more results
        python cli.py search "Python programming" --max 20
        
        # Search with similarity threshold
        python cli.py search "neural networks" --threshold 0.7
        
        # Filter by file type
        python cli.py search "documentation" --filter-type md
        
        # Verbose output with full content
        python cli.py search "API design" --verbose
    """
    
    if RICH_AVAILABLE:
        console.print(Panel("🔍 PrismWeave Semantic Search", style="bold cyan"))
    else:
        print("🔍 PrismWeave Semantic Search")
        print("=" * 40)
    
    # Load configuration
    try:
        if config:
            config_obj = Config.from_file(config)
        else:
            default_config = Path(__file__).parent / "config.yaml"
            if default_config.exists():
                config_obj = Config.from_file(default_config)
            else:
                config_obj = Config()
        
        validation_issues = config_obj.validate()
        if validation_issues:
            print("❌ Configuration issues:")
            for issue in validation_issues:
                print(f"   - {issue}")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        sys.exit(1)
    
    # Initialize embedding store
    store = EmbeddingStore(config_obj)
    
    try:
        # Perform search
        if RICH_AVAILABLE:
            with console.status(f"[bold green]Searching for: {query}..."):
                results = store.search_similar(query, k=max_results)
        else:
            print(f"\n🔎 Searching for: {query}")
            results = store.search_similar(query, k=max_results)
        
        if not results:
            print("\n❌ No results found")
            return
        
        # Filter by file type if specified
        if filter_type:
            filter_ext = f".{filter_type.lstrip('.')}"  # Ensure dot prefix
            filtered_results = []
            for doc in results:
                source_file = doc.metadata.get('source_file', '')
                if Path(source_file).suffix == filter_ext:
                    filtered_results.append(doc)
            results = filtered_results
            
            if not results:
                print(f"\n❌ No results found with file type: {filter_type}")
                return
        
        # Display results
        if RICH_AVAILABLE:
            console.print(f"\n[bold green]Found {len(results)} results[/bold green]\n")
            
            for i, doc in enumerate(results, 1):
                source_file = doc.metadata.get('source_file', 'Unknown')
                file_name = Path(source_file).name if source_file != 'Unknown' else 'Unknown'
                
                # Create result panel
                panel_title = f"Result {i}: {file_name}"
                
                content_lines = []
                content_lines.append(f"[cyan]📁 File:[/cyan] {file_name}")
                
                if 'chunk_index' in doc.metadata and 'total_chunks' in doc.metadata:
                    chunk_info = f"{doc.metadata['chunk_index'] + 1}/{doc.metadata['total_chunks']}"
                    content_lines.append(f"[cyan]🔢 Chunk:[/cyan] {chunk_info}")
                
                if 'tags' in doc.metadata:
                    content_lines.append(f"[cyan]🏷️  Tags:[/cyan] {doc.metadata['tags']}")
                
                # Content preview
                preview_length = 500 if verbose else 200
                content_preview = doc.page_content[:preview_length]
                if len(doc.page_content) > preview_length:
                    content_preview += "..."
                content_lines.append(f"\n[yellow]📝 Content:[/yellow]\n{content_preview}")
                
                panel_content = "\n".join(content_lines)
                console.print(Panel(panel_content, title=panel_title, border_style="green"))
        else:
            # Simple text output
            print(f"\n✅ Found {len(results)} results\n")
            
            for i, doc in enumerate(results, 1):
                source_file = doc.metadata.get('source_file', 'Unknown')
                file_name = Path(source_file).name if source_file != 'Unknown' else 'Unknown'
                
                print(f"{i}. {file_name}")
                print(f"   📁 File: {file_name}")
                
                if 'chunk_index' in doc.metadata and 'total_chunks' in doc.metadata:
                    chunk_info = f"{doc.metadata['chunk_index'] + 1}/{doc.metadata['total_chunks']}"
                    print(f"   🔢 Chunk: {chunk_info}")
                
                if 'tags' in doc.metadata:
                    print(f"   🏷️  Tags: {doc.metadata['tags']}")
                
                # Content preview
                preview_length = 500 if verbose else 200
                content_preview = doc.page_content[:preview_length]
                if len(doc.page_content) > preview_length:
                    content_preview += "..."
                print(f"   📝 Content: {content_preview}")
                print()
        
    except Exception as e:
        print(f"❌ Search failed: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


@cli.command()
@click.option('--config', '-c', type=click.Path(exists=True, path_type=Path), 
              help='Configuration file path (default: config.yaml)')
@click.option('--detailed', '-d', is_flag=True,
              help='Show detailed analytics')
def stats(config: Optional[Path], detailed: bool):
    """
    Show collection statistics and analytics.
    
    Examples:
    
    \b
        # Basic statistics
        python cli.py stats
        
        # Detailed analytics
        python cli.py stats --detailed
    """
    
    if RICH_AVAILABLE:
        console.print(Panel("📊 PrismWeave Collection Statistics", style="bold cyan"))
    else:
        print("📊 PrismWeave Collection Statistics")
        print("=" * 40)
    
    # Load configuration
    try:
        if config:
            config_obj = Config.from_file(config)
        else:
            default_config = Path(__file__).parent / "config.yaml"
            if default_config.exists():
                config_obj = Config.from_file(default_config)
            else:
                config_obj = Config()
        
        validation_issues = config_obj.validate()
        if validation_issues:
            print("❌ Configuration issues:")
            for issue in validation_issues:
                print(f"   - {issue}")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        sys.exit(1)
    
    # Initialize embedding store
    store = EmbeddingStore(config_obj)
    
    try:
        # Get basic counts
        total_chunks = store.get_document_count()
        source_files = store.get_unique_source_files()
        total_files = len(source_files)
        
        if total_chunks == 0:
            print("\n❌ No documents in collection")
            return
        
        # Calculate statistics
        avg_chunks_per_file = total_chunks / total_files if total_files > 0 else 0
        
        # Get all documents for detailed analysis
        all_docs = store.list_documents(None) if detailed else []
        
        # File type distribution
        file_types = {}
        total_content_length = 0
        tag_frequency = {}
        
        if detailed:
            for doc in all_docs:
                source_file = doc['metadata'].get('source_file', '')
                if source_file:
                    ext = Path(source_file).suffix or 'no extension'
                    file_types[ext] = file_types.get(ext, 0) + 1
                
                total_content_length += doc['content_length']
                
                # Tag frequency
                tags_str = doc['metadata'].get('tags', '')
                if tags_str:
                    tags = [t.strip() for t in tags_str.split(',')]
                    for tag in tags:
                        if tag:
                            tag_frequency[tag] = tag_frequency.get(tag, 0) + 1
        
        # Display statistics
        if RICH_AVAILABLE:
            # Basic statistics table
            stats_table = Table(title="Collection Overview", show_header=True)
            stats_table.add_column("Metric", style="cyan")
            stats_table.add_column("Value", style="green")
            
            stats_table.add_row("📄 Total Chunks", f"{total_chunks:,}")
            stats_table.add_row("📁 Source Files", f"{total_files:,}")
            stats_table.add_row("📈 Avg Chunks/File", f"{avg_chunks_per_file:.1f}")
            
            if detailed and total_content_length > 0:
                stats_table.add_row("📏 Total Content", f"{total_content_length:,} chars")
                avg_content_per_chunk = total_content_length / total_chunks
                stats_table.add_row("📊 Avg Chunk Size", f"{avg_content_per_chunk:.0f} chars")
            
            console.print("\n")
            console.print(stats_table)
            
            if detailed and file_types:
                # File type distribution table
                console.print("\n")
                type_table = Table(title="File Type Distribution", show_header=True)
                type_table.add_column("Extension", style="cyan")
                type_table.add_column("Count", style="green")
                type_table.add_column("Percentage", style="yellow")
                
                for ext, count in sorted(file_types.items(), key=lambda x: x[1], reverse=True):
                    percentage = (count / total_chunks) * 100
                    type_table.add_row(ext, str(count), f"{percentage:.1f}%")
                
                console.print(type_table)
            
            if detailed and tag_frequency:
                # Top tags table
                console.print("\n")
                tag_table = Table(title="Top 10 Tags", show_header=True)
                tag_table.add_column("Tag", style="cyan")
                tag_table.add_column("Frequency", style="green")
                
                sorted_tags = sorted(tag_frequency.items(), key=lambda x: x[1], reverse=True)[:10]
                for tag, freq in sorted_tags:
                    tag_table.add_row(tag, str(freq))
                
                console.print(tag_table)
        else:
            # Simple text output
            print(f"\n📊 Collection Overview:")
            print(f"   📄 Total chunks: {total_chunks:,}")
            print(f"   📁 Source files: {total_files:,}")
            print(f"   📈 Average chunks per file: {avg_chunks_per_file:.1f}")
            
            if detailed and total_content_length > 0:
                print(f"   📏 Total content: {total_content_length:,} characters")
                avg_content_per_chunk = total_content_length / total_chunks
                print(f"   📊 Average chunk size: {avg_content_per_chunk:.0f} characters")
            
            if detailed and file_types:
                print(f"\n📑 File Type Distribution:")
                for ext, count in sorted(file_types.items(), key=lambda x: x[1], reverse=True):
                    percentage = (count / total_chunks) * 100
                    print(f"   {ext}: {count} ({percentage:.1f}%)")
            
            if detailed and tag_frequency:
                print(f"\n🏷️  Top 10 Tags:")
                sorted_tags = sorted(tag_frequency.items(), key=lambda x: x[1], reverse=True)[:10]
                for tag, freq in sorted_tags:
                    print(f"   {tag}: {freq}")
        
        # Collection info
        verification = store.verify_embeddings()
        if RICH_AVAILABLE:
            console.print(f"\n[dim]Collection: {verification.get('collection_name', 'Unknown')}[/dim]")
            console.print(f"[dim]Storage: {verification.get('persist_directory', 'Unknown')}[/dim]")
        else:
            print(f"\nCollection: {verification.get('collection_name', 'Unknown')}")
            print(f"Storage: {verification.get('persist_directory', 'Unknown')}")
        
    except Exception as e:
        print(f"❌ Failed to generate statistics: {e}")
        if detailed:
            import traceback
            traceback.print_exc()
        sys.exit(1)


@cli.command()
@click.argument('output_file', type=click.Path(path_type=Path))
@click.option('--config', '-c', type=click.Path(exists=True, path_type=Path), 
              help='Configuration file path (default: config.yaml)')
@click.option('--format', '-f', type=click.Choice(['json', 'csv']), default='json',
              help='Export format (default: json)')
@click.option('--filter-type', type=str,
              help='Filter by file type (e.g., md, txt, pdf)')
@click.option('--include-content', is_flag=True,
              help='Include full content in export (JSON only)')
@click.option('--max', '-m', 'max_docs', type=int,
              help='Maximum number of documents to export')
def export(output_file: Path, config: Optional[Path], format: str, filter_type: Optional[str], 
           include_content: bool, max_docs: Optional[int]):
    """
    Export documents and metadata to JSON or CSV.
    
    Examples:
    
    \b
        # Export all documents to JSON
        python cli.py export documents.json
        
        # Export to CSV
        python cli.py export documents.csv --format csv
        
        # Export with full content
        python cli.py export full_export.json --include-content
        
        # Export only markdown files
        python cli.py export markdown_only.json --filter-type md
        
        # Export limited number of documents
        python cli.py export sample.json --max 100
    """
    
    if RICH_AVAILABLE:
        console.print(Panel("💾 PrismWeave Document Export", style="bold cyan"))
    else:
        print("💾 PrismWeave Document Export")
        print("=" * 40)
    
    # Load configuration
    try:
        if config:
            config_obj = Config.from_file(config)
        else:
            default_config = Path(__file__).parent / "config.yaml"
            if default_config.exists():
                config_obj = Config.from_file(default_config)
            else:
                config_obj = Config()
        
        validation_issues = config_obj.validate()
        if validation_issues:
            print("❌ Configuration issues:")
            for issue in validation_issues:
                print(f"   - {issue}")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        sys.exit(1)
    
    # Initialize embedding store
    store = EmbeddingStore(config_obj)
    
    try:
        # Get documents
        print("\n📥 Retrieving documents...")
        documents = store.list_documents(max_docs)
        
        if not documents:
            print("❌ No documents to export")
            return
        
        # Filter by file type if specified
        if filter_type:
            filter_ext = f".{filter_type.lstrip('.')}"  # Ensure dot prefix
            filtered_docs = []
            for doc in documents:
                source_file = doc['metadata'].get('source_file', '')
                if Path(source_file).suffix == filter_ext:
                    filtered_docs.append(doc)
            documents = filtered_docs
            
            if not documents:
                print(f"❌ No documents found with file type: {filter_type}")
                return
            
            print(f"🔍 Filtered to {len(documents)} documents with type: {filter_type}")
        
        # Prepare export data
        export_data = {
            'export_date': datetime.now().isoformat(),
            'total_documents': len(documents),
            'collection_name': config_obj.collection_name,
            'documents': []
        }
        
        for doc in documents:
            doc_export = {
                'id': doc['id'],
                'source_file': doc['metadata'].get('source_file', 'Unknown'),
                'chunk_index': doc['metadata'].get('chunk_index'),
                'total_chunks': doc['metadata'].get('total_chunks'),
                'tags': doc['metadata'].get('tags', ''),
                'content_length': doc['content_length'],
            }
            
            if include_content and format == 'json':
                # Include full content for JSON export
                collection = store.vector_store._collection
                full_doc = collection.get(ids=[doc['id']], include=['documents'])
                if full_doc['documents']:
                    doc_export['content'] = full_doc['documents'][0]
            else:
                doc_export['content_preview'] = doc['content_preview']
            
            export_data['documents'].append(doc_export)
        
        # Export based on format
        if format == 'json':
            print(f"\n💾 Exporting to JSON: {output_file}")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        elif format == 'csv':
            print(f"\n💾 Exporting to CSV: {output_file}")
            import csv
            
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['id', 'source_file', 'chunk_index', 'total_chunks', 'tags', 
                             'content_length', 'content_preview']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                
                writer.writeheader()
                for doc in export_data['documents']:
                    # Flatten the document for CSV
                    csv_row = {
                        'id': doc['id'],
                        'source_file': doc.get('source_file', ''),
                        'chunk_index': doc.get('chunk_index', ''),
                        'total_chunks': doc.get('total_chunks', ''),
                        'tags': doc.get('tags', ''),
                        'content_length': doc.get('content_length', 0),
                        'content_preview': doc.get('content_preview', '')
                    }
                    writer.writerow(csv_row)
        
        print(f"✅ Exported {len(documents)} documents to {output_file}")
        print(f"   File size: {output_file.stat().st_size / 1024:.1f} KB")
        
    except Exception as e:
        print(f"❌ Export failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
