#!/usr/bin/env python3
"""
PrismWeave Document Processing CLI

Process documents and generate embeddings using LangChain and Ollama.
Supports markdown, PDF, DOCX, HTML, and text files.
"""

import sys
import click
from pathlib import Path
from typing import Optional, List
import json

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))

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
    """Process all supported files in a directory"""
    
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
    
    # Process files
    success_count = 0
    error_count = 0
    skipped_count = 0
    
    for file_path in files_to_process:
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
    
    # Summary
    print(f"\n📊 Processing Summary:")
    print(f"   ✅ Successfully processed: {success_count} files")
    if error_count > 0:
        print(f"   ❌ Failed to process: {error_count} files")
    
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
    Process documents and generate embeddings using LangChain and Ollama.
    
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
    
    # Initialize git tracker for incremental processing
    git_tracker = None
    if incremental or repo_path:
        try:
            # Determine repository path
            if repo_path:
                repo_root = repo_path
            elif path.is_dir():
                # Try to find git repo from the path
                repo_root = path
                while repo_root != repo_root.parent:
                    if (repo_root / '.git').exists():
                        break
                    repo_root = repo_root.parent
                else:
                    raise ValueError("No git repository found")
            else:
                # For single file, find repo from parent directories
                repo_root = path.parent
                while repo_root != repo_root.parent:
                    if (repo_root / '.git').exists():
                        break
                    repo_root = repo_root.parent
                else:
                    raise ValueError("No git repository found")
            
            git_tracker = GitTracker(repo_root)
            
            if verbose:
                print(f"🔄 Git repository: {repo_root}")
                summary = git_tracker.get_processing_summary()
                print(f"📊 Processing state: {summary['processed_files']} processed, {summary['unprocessed_files']} unprocessed")
                print()
                
        except Exception as e:
            if incremental:
                print(f"❌ Failed to initialize git tracking: {e}")
                print("   Incremental processing requires a git repository")
                sys.exit(1)
            else:
                print(f"⚠️  Warning: Git tracking not available: {e}")
                git_tracker = None
    
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
    
    # Run incremental processing
    mode = "force" if force else "incremental"
    print(f"🔄 Starting sync (mode: {mode})")
    print()
    
    try:
        success = process_directory(
            repo_path, 
            config_obj, 
            git_tracker=None,  # Will be created automatically
            verbose=verbose, 
            incremental=not force, 
            force=force
        )
        
        if not success:
            sys.exit(1)
        
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


if __name__ == "__main__":
    main()
