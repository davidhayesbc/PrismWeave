#!/usr/bin/env python3
"""
Quick validation script for PrismWeave AI Processing setup
Tests core functionality with your existing document collection
"""

import sys
import asyncio
from pathlib import Path
import yaml

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

async def test_configuration():
    """Test configuration loading"""
    print("🔧 Testing configuration...")
    try:
        from src.utils.config import get_config
        config = get_config()
        print(f"   ✅ Configuration loaded")
        print(f"   📁 Documents path: {config.integration.documents_path}")
        print(f"   🤖 Analysis model: {config.ollama.models.analysis}")
        return True
    except Exception as e:
        print(f"   ❌ Configuration error: {e}")
        return False

async def test_ollama_connection():
    """Test Ollama client connection"""
    print("🤖 Testing Ollama connection...")
    try:
        from src.models.ollama_client import OllamaClient
        from src.utils.config import get_config
        
        config = get_config()
        client = OllamaClient(config.ollama)
        
        # Test connection
        health = await client.health_check()
        if health:
            print("   ✅ Ollama server is healthy")
            
            # Test model availability
            models = await client.list_models()
            if models:
                print(f"   📋 Available models: {', '.join(models[:3])}")
            else:
                print("   ⚠️  No models available")
            
            return True
        else:
            print("   ❌ Ollama server not responding")
            return False
            
    except Exception as e:
        print(f"   ❌ Ollama connection error: {e}")
        return False

async def test_document_discovery():
    """Test document discovery in PrismWeaveDocs"""
    print("📚 Testing document discovery...")
    try:
        from src.utils.config import get_config
        
        config = get_config()
        docs_path = Path(config.integration.documents_path)
        
        if not docs_path.exists():
            print(f"   ❌ Documents path not found: {docs_path}")
            return False
        
        # Find markdown files
        md_files = list(docs_path.rglob("*.md"))
        if not md_files:
            print(f"   ❌ No markdown files found in {docs_path}")
            return False
        
        print(f"   ✅ Found {len(md_files)} markdown files")
        
        # Test a few files for frontmatter
        valid_docs = 0
        for md_file in md_files[:5]:  # Test first 5 files
            try:
                content = md_file.read_text(encoding='utf-8')
                if content.startswith('---'):
                    # Extract frontmatter
                    end_pos = content.find('---', 3)
                    if end_pos > 0:
                        frontmatter = content[3:end_pos].strip()
                        yaml.safe_load(frontmatter)
                        valid_docs += 1
            except Exception:
                continue
        
        print(f"   📋 Found {valid_docs} documents with valid frontmatter")
        return True
        
    except Exception as e:
        print(f"   ❌ Document discovery error: {e}")
        return False

async def test_processing_pipeline():
    """Test basic document processing"""
    print("⚙️ Testing processing pipeline...")
    try:
        from src.processors.document_processor import DocumentProcessor
        from src.models.ollama_client import OllamaClient
        from src.utils.config import get_config
        
        config = get_config()
        client = OllamaClient(config.ollama)
        processor = DocumentProcessor(client, config.processing)
        
        # Find a test document
        docs_path = Path(config.integration.documents_path)
        md_files = list(docs_path.rglob("*.md"))
        
        if not md_files:
            print("   ⚠️  No documents available for testing")
            return False
        
        test_doc = md_files[0]
        print(f"   📄 Testing with: {test_doc.name}")
        
        # Test metadata extraction only (skip AI for now)
        result = await processor.extract_metadata(test_doc)
        if result:
            print(f"   ✅ Metadata extracted: {result.get('title', 'No title')}")
            return True
        else:
            print("   ❌ Failed to extract metadata")
            return False
            
    except Exception as e:
        print(f"   ❌ Processing pipeline error: {e}")
        return False

async def test_search_engine():
    """Test search engine initialization"""
    print("🔍 Testing search engine...")
    try:
        from src.search.semantic_search import SemanticSearch
        from src.utils.config import get_config
        
        config = get_config()
        search = SemanticSearch(config.search)
        
        # Test initialization
        await search.initialize()
        print("   ✅ Search engine initialized")
        
        # Test vector database connection
        if hasattr(search, '_vector_store') and search._vector_store:
            print("   ✅ Vector database connected")
        else:
            print("   ⚠️  Vector database not connected (in-memory mode)")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Search engine error: {e}")
        return False

async def main():
    """Run all validation tests"""
    print("🌟 PrismWeave AI Processing Validation")
    print("=" * 50)
    
    tests = [
        ("Configuration", test_configuration),
        ("Ollama Connection", test_ollama_connection),
        ("Document Discovery", test_document_discovery),
        ("Processing Pipeline", test_processing_pipeline),
        ("Search Engine", test_search_engine),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"   💥 Test crashed: {e}")
            results.append((test_name, False))
        print()
    
    # Summary
    print("📊 Test Results:")
    print("-" * 30)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:8} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All tests passed! Your setup is ready.")
        print("\n📋 Next steps:")
        print("   python cli/prismweave.py process")
        print("   python cli/prismweave.py search \"your query\"")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
        print("\n🔧 Common fixes:")
        print("   - Ensure Ollama is running: ollama serve")
        print("   - Install missing dependencies: pip install -r requirements.txt")
        print("   - Check paths in config.yaml")
    
    return passed == len(results)

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
