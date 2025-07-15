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


def check_ollama_connection(config: Config) -> bool:
    """Check if Ollama is available and running"""
    try:
        import requests
        response = requests.get(f"{config.ollama_host}/api/tags", timeout=5)
        return response.status_code == 200
    except Exception:
        return False


def process_single_file(file_path: Path, config: Config, verbose: bool = False):
    """Process a single document file"""
    
    if verbose:
        print(f"🔮 Processing: {file_path}")
        print(f"🤖 Using model: {config.embedding_model}")
        print(f"💾 Storage: {config.chroma_db_path}")
        print()
    
    # Initialize components
    processor = DocumentProcessor(config)
    store = EmbeddingStore(config)
    
    try:
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


def process_directory(input_dir: Path, config: Config, verbose: bool = False):
    """Process all supported files in a directory"""
    
    # Supported file extensions
    supported_extensions = {'.md', '.txt', '.pdf', '.docx', '.html', '.htm'}
    
    # Find all supported files
    files_to_process = []
    for ext in supported_extensions:
        files_to_process.extend(list(input_dir.rglob(f"*{ext}")))
    
    if not files_to_process:
        print(f"❌ No supported files found in {input_dir}")
        print(f"   Supported extensions: {', '.join(supported_extensions)}")
        return False
    
    if verbose:
        print(f"📂 Found {len(files_to_process)} files to process")
        print()
    
    # Process files
    success_count = 0
    error_count = 0
    
    for file_path in files_to_process:
        try:
            if process_single_file(file_path, config, verbose=False):
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
def process(path: Path, config: Optional[Path], verbose: bool, verify: bool, clear: bool):
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
    """
    
    print("🔮 PrismWeave Document Processor")
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
        store = EmbeddingStore(config_obj)
        store.clear_collection()
        print("✅ Embeddings cleared")
        print()
    
    # Determine if path is file or directory and process accordingly
    try:
        if path.is_file():
            print(f"📄 Processing single file: {path}")
            print()
            success = process_single_file(path, config_obj, verbose=verbose)
            
        elif path.is_dir():
            print(f"📂 Processing directory: {path}")
            print()
            success = process_directory(path, config_obj, verbose=verbose)
            
        else:
            print(f"❌ Path is neither a file nor a directory: {path}")
            sys.exit(1)
        
        if not success:
            sys.exit(1)
        
        # Verify embeddings if requested
        if verify:
            print("\n🔍 Verifying embeddings storage...")
            store = EmbeddingStore(config_obj)
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
