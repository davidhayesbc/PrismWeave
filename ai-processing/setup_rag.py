#!/usr/bin/env python3
"""
PrismWeave RAG Setup Script
Initialize and configure the RAG (Retrieval Augmented Generation) system
"""

import asyncio
import sys
from pathlib import Path
from typing import List
import json

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from src.processors.document_processor import DocumentProcessor
from src.search.semantic_search import SemanticSearch
from src.rag.rag_synthesizer import RAGSynthesizer
from src.models.ollama_client import OllamaClient
from src.utils.config import get_config

async def check_system_requirements():
    """Check if all system requirements are met"""
    print("🔍 Checking System Requirements...")
    
    config = get_config()
    issues = []
    
    # Check Ollama connection
    try:
        async with OllamaClient() as client:
            if await client.is_available():
                print("✅ Ollama server connection: OK")
            else:
                issues.append("❌ Ollama server not available at " + config.ollama.host)
    except Exception as e:
        issues.append(f"❌ Ollama connection failed: {str(e)}")
    
    # Check required models
    required_models = [
        config.get_model_config('large')['primary'],
        config.get_model_config('small')['primary'],
        config.get_model_config('embedding')['primary']
    ]
    
    async with OllamaClient() as client:
        for model in required_models:
            if await client.model_exists(model):
                print(f"✅ Model {model}: Available")
            else:
                issues.append(f"❌ Model {model}: Not found")
    
    # Check document directory
    docs_path = config.get_documents_path()
    if docs_path.exists():
        doc_count = len(list(docs_path.glob("**/*.md")))
        print(f"✅ Documents directory: {docs_path} ({doc_count} .md files)")
    else:
        issues.append(f"❌ Documents directory not found: {docs_path}")
    
    # Check vector database directory
    vector_db_path = Path(config.vector_db.chroma.persist_directory)
    vector_db_path.mkdir(parents=True, exist_ok=True)
    print(f"✅ Vector database directory: {vector_db_path}")
    
    return issues

async def pull_required_models():
    """Pull all required models if they don't exist"""
    print("\n📥 Checking and pulling required models...")
    
    config = get_config()
    models_to_pull = [
        config.get_model_config('large')['primary'],
        config.get_model_config('small')['primary'], 
        config.get_model_config('embedding')['primary']
    ]
    
    async with OllamaClient() as client:
        for model in models_to_pull:
            if not await client.model_exists(model):
                print(f"📥 Pulling model: {model}")
                success = await client.pull_model(model)
                if success:
                    print(f"✅ Successfully pulled: {model}")
                else:
                    print(f"❌ Failed to pull: {model}")
            else:
                print(f"✅ Model already available: {model}")

async def initialize_vector_database():
    """Initialize the vector database"""
    print("\n🗄️ Initializing Vector Database...")
    
    try:
        async with SemanticSearch() as search:
            health = await search.health_check()
            if health['vector_db_available']:
                print("✅ Vector database initialized successfully")
                print(f"📊 Indexed documents: {health.get('indexed_documents', 0)}")
            else:
                print("❌ Vector database initialization failed")
    except Exception as e:
        print(f"❌ Vector database error: {str(e)}")

async def process_sample_documents(max_docs: int = 10):
    """Process a sample of documents to test the system"""
    print(f"\n📝 Processing sample documents (max {max_docs})...")
    
    config = get_config()
    docs_path = config.get_documents_path()
    
    # Find sample documents
    sample_docs = list(docs_path.glob("**/*.md"))[:max_docs]
    
    if not sample_docs:
        print("❌ No markdown documents found to process")
        return
    
    try:
        async with DocumentProcessor() as processor:
            for i, doc_path in enumerate(sample_docs, 1):
                print(f"📄 Processing ({i}/{len(sample_docs)}): {doc_path.name}")
                result = await processor.process_document(doc_path)
                
                if result.success:
                    print(f"   ✅ Success - Quality: {result.quality_score:.1f}/10")
                else:
                    print(f"   ❌ Failed: {result.error}")
    
    except Exception as e:
        print(f"❌ Document processing error: {str(e)}")

async def test_rag_system():
    """Test the RAG system with sample queries"""
    print("\n🧠 Testing RAG System...")
    
    test_queries = [
        "What technologies are mentioned in the documents?",
        "Summarize the main topics covered",
        "What are the key insights from recent articles?"
    ]
    
    try:
        async with RAGSynthesizer() as rag:
            for i, query in enumerate(test_queries, 1):
                print(f"\n🤔 Test Query {i}: {query}")
                
                response = await rag.quick_answer(query)
                
                if response.sources:
                    print(f"✅ Generated answer using {len(response.sources)} sources")
                    print(f"📊 Confidence: {response.confidence_score:.2f}")
                    print(f"⏱️ Processing time: {response.processing_time:.2f}s")
                    
                    # Show brief answer
                    answer_preview = response.answer[:200] + "..." if len(response.answer) > 200 else response.answer
                    print(f"💡 Answer preview: {answer_preview}")
                else:
                    print("❌ No sources found for this query")
    
    except Exception as e:
        print(f"❌ RAG testing error: {str(e)}")

async def generate_setup_report():
    """Generate a comprehensive setup report"""
    print("\n📊 Generating Setup Report...")
    
    config = get_config()
    
    # Gather system information
    report = {
        "timestamp": "2025-07-04",
        "configuration": {
            "ollama_host": config.ollama.host,
            "documents_path": str(config.get_documents_path()),
            "vector_db_path": config.vector_db.chroma.persist_directory,
            "models": {
                "large": config.get_model_config('large')['primary'],
                "small": config.get_model_config('small')['primary'],
                "embedding": config.get_model_config('embedding')['primary']
            }
        },
        "system_status": {}
    }
    
    # Check system status
    try:
        async with DocumentProcessor() as processor:
            health = await processor.health_check()
            report["system_status"]["processor"] = health
        
        async with SemanticSearch() as search:
            health = await search.health_check()
            report["system_status"]["search"] = health
            
    except Exception as e:
        report["system_status"]["error"] = str(e)
    
    # Save report
    report_path = Path("../PrismWeaveDocs/.prismweave/setup_report.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"✅ Setup report saved to: {report_path}")
    return report

def print_usage_examples():
    """Print usage examples for the RAG system"""
    print("\n🚀 RAG System Usage Examples:")
    print("=" * 50)
    
    examples = [
        ("Basic Question", "python cli/prismweave.py ask 'What are the main concepts in machine learning?'"),
        ("Technical Query", "python cli/prismweave.py tech 'How do I implement authentication in TypeScript?' --technologies 'typescript,auth'"),
        ("Research Synthesis", "python cli/prismweave.py research 'artificial intelligence trends'"),
        ("Brief Answer", "python cli/prismweave.py ask 'What is RAG?' --style brief"),
        ("Category Filter", "python cli/prismweave.py ask 'Show me tutorials' --category tutorial"),
        ("JSON Output", "python cli/prismweave.py ask 'Explain vector databases' --format json"),
    ]
    
    for title, command in examples:
        print(f"\n{title}:")
        print(f"  {command}")
    
    print("\n📚 For more options, run: python cli/prismweave.py --help")

async def main():
    """Main setup process"""
    print("🔮 PrismWeave RAG System Setup")
    print("=" * 50)
    
    # Step 1: Check requirements
    issues = await check_system_requirements()
    if issues:
        print("\n❌ Setup Issues Found:")
        for issue in issues:
            print(f"  {issue}")
        
        if "Ollama" in str(issues):
            print("\n💡 To fix Ollama issues:")
            print("  1. Install Ollama: https://ollama.ai")
            print("  2. Start Ollama: ollama serve")
            print("  3. Re-run this setup script")
            return
    
    # Step 2: Pull required models
    await pull_required_models()
    
    # Step 3: Initialize vector database
    await initialize_vector_database()
    
    # Step 4: Process sample documents
    await process_sample_documents(max_docs=5)
    
    # Step 5: Test RAG system
    await test_rag_system()
    
    # Step 6: Generate report
    report = await generate_setup_report()
    
    # Step 7: Show usage examples
    print_usage_examples()
    
    print("\n🎉 RAG System Setup Complete!")
    print("Your PrismWeave RAG system is ready for intelligent document synthesis.")

if __name__ == "__main__":
    asyncio.run(main())
