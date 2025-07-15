#!/usr/bin/env python3
"""
PrismWeave Document Processing CLI

Process documents and generate embeddings using LangChain and Ollama.
Supports markdown, PDF, DOCX, HTML, and text files.
"""

import sys
import click
from pathlib import Path
from typing import Optional

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


@click.command()
@click.argument('path', type=click.Path(exists=True, path_type=Path))
@click.option('--config', '-c', type=click.Path(exists=True, path_type=Path), 
              help='Configuration file path (default: config.yaml)')
@click.option('--verbose', '-v', is_flag=True, 
              help='Show detailed output and metadata')
@click.option('--verify', is_flag=True, 
              help='Verify embeddings storage after processing')
@click.option('--clear', is_flag=True, 
              help='Clear existing embeddings before processing')
def main(path: Path, config: Optional[Path], verbose: bool, verify: bool, clear: bool):
    """
    Process documents and generate embeddings using LangChain and Ollama.
    
    PATH can be either a single file or a directory.
    
    Examples:
    
    \b
        # Process a single file
        python cli.py document.md
        
        # Process all files in a directory
        python cli.py ../PrismWeaveDocs/documents
        
        # Process with verbose output
        python cli.py document.md --verbose
        
        # Clear existing embeddings and reprocess
        python cli.py ../docs --clear --verify
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


if __name__ == "__main__":
    main()
