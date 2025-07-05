#!/usr/bin/env python3
"""
Debug script to identify memory usage issues in PrismWeave AI processing
"""

import asyncio
import sys
import time
import gc
import tracemalloc
from pathlib import Path
import logging

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.processors.document_processor import DocumentProcessor
from src.models.ollama_client import OllamaClient
from src.utils.config import get_config

# Enable memory profiling
tracemalloc.start()

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def memory_profile_ollama():
    """Profile memory usage of basic Ollama operations"""
    print("🔍 Testing Ollama Client Memory Usage...")
    
    try:
        # Memory snapshot before
        snapshot1 = tracemalloc.take_snapshot()
        
        async with OllamaClient() as client:
            print("📋 Checking Ollama availability...")
            is_available = await client.is_available()
            print(f"   Available: {is_available}")
            
            if is_available:
                print("📋 Listing models...")
                models = await client.list_models()
                print(f"   Found {len(models)} models")
                
                # Memory snapshot after basic operations
                snapshot2 = tracemalloc.take_snapshot()
                top_stats = snapshot2.compare_to(snapshot1, 'lineno')
                
                print("\n📊 Memory usage after basic operations:")
                for stat in top_stats[:5]:
                    print(f"   {stat}")
                
                # Test small generation
                if models:
                    model_name = "phi3:mini"  # The problematic model
                    if await client.model_exists(model_name):
                        print(f"\n🧪 Testing generation with {model_name}...")
                        
                        # Very simple test
                        simple_prompt = "Say hello in one word."
                        print(f"   Prompt: '{simple_prompt}'")
                        
                        start_time = time.time()
                        try:
                            result = await asyncio.wait_for(
                                client.generate(
                                    model=model_name,
                                    prompt=simple_prompt,
                                    options={"num_predict": 10}  # Limit output
                                ),
                                timeout=30.0  # 30 second timeout
                            )
                            
                            end_time = time.time()
                            print(f"   ✅ Generated: '{result.response}' in {end_time - start_time:.2f}s")
                            
                            # Memory snapshot after generation
                            snapshot3 = tracemalloc.take_snapshot()
                            top_stats = snapshot3.compare_to(snapshot2, 'lineno')
                            
                            print("\n📊 Memory usage after generation:")
                            for stat in top_stats[:5]:
                                print(f"   {stat}")
                                
                        except asyncio.TimeoutError:
                            print("   ❌ Generation timed out after 30 seconds")
                        except Exception as e:
                            print(f"   ❌ Generation failed: {e}")
                            
                    else:
                        print(f"   ⚠️ Model {model_name} not available")
    
    except Exception as e:
        print(f"❌ Ollama profiling failed: {e}")
        traceback.print_exc()

async def memory_profile_document_processing():
    """Profile memory usage of document processing"""
    print("\n🔍 Testing Document Processing Memory Usage...")
    
    # Test document path
    doc_path = Path("d:/source/PrismWeaveDocs/documents/tech/2025-06-22-building-industrial-strength-software-without-unit.md")
    
    if not doc_path.exists():
        print(f"❌ Test document not found: {doc_path}")
        return
    
    try:
        # Memory snapshot before
        snapshot1 = tracemalloc.take_snapshot()
        
        async with DocumentProcessor() as processor:
            print("📋 Checking processor health...")
            health = await processor.health_check()
            print(f"   Ollama available: {health['ollama_available']}")
            print(f"   Models: {health.get('models_available', [])}")
            
            if not health['ollama_available']:
                print("⚠️ Ollama not available, skipping document processing")
                return
            
            # Memory snapshot after initialization
            snapshot2 = tracemalloc.take_snapshot()
            top_stats = snapshot2.compare_to(snapshot1, 'lineno')
            
            print("\n📊 Memory usage after processor initialization:")
            for stat in top_stats[:3]:
                print(f"   {stat}")
            
            print(f"\n🧪 Processing document: {doc_path.name}")
            start_time = time.time()
            
            try:
                result = await asyncio.wait_for(
                    processor.process_document(doc_path),
                    timeout=60.0  # 60 second timeout
                )
                
                end_time = time.time()
                
                if result.success:
                    print(f"   ✅ Processing completed in {end_time - start_time:.2f}s")
                    print(f"   Category: {result.suggested_category}")
                    print(f"   Quality: {result.quality_score:.2f}")
                    print(f"   Tags: {result.suggested_tags[:3]}")
                else:
                    print(f"   ❌ Processing failed: {result.error}")
                
                # Memory snapshot after processing
                snapshot3 = tracemalloc.take_snapshot()
                top_stats = snapshot3.compare_to(snapshot2, 'lineno')
                
                print("\n📊 Memory usage after document processing:")
                for stat in top_stats[:5]:
                    print(f"   {stat}")
                    
            except asyncio.TimeoutError:
                print("   ❌ Document processing timed out after 60 seconds")
            except Exception as e:
                print(f"   ❌ Document processing failed: {e}")
                traceback.print_exc()
    
    except Exception as e:
        print(f"❌ Document processing profiling failed: {e}")
        traceback.print_exc()

async def test_model_options():
    """Test different model options to reduce memory usage"""
    print("\n🔍 Testing Model Options for Memory Optimization...")
    
    try:
        async with OllamaClient() as client:
            model_name = "phi3:mini"
            
            if not await client.model_exists(model_name):
                print(f"❌ Model {model_name} not available")
                return
            
            # Test with memory-optimized options
            memory_options = {
                "num_ctx": 512,        # Reduce context window
                "num_predict": 50,     # Limit prediction length
                "temperature": 0.1,    # Reduce randomness
                "top_p": 0.9,         # Nucleus sampling
                "repeat_penalty": 1.1  # Prevent repetition
            }
            
            test_prompt = "Summarize in one sentence: This is a test document about software testing."
            
            print(f"🧪 Testing with memory-optimized options...")
            print(f"   Options: {memory_options}")
            
            start_time = time.time()
            snapshot1 = tracemalloc.take_snapshot()
            
            try:
                result = await asyncio.wait_for(
                    client.generate(
                        model=model_name,
                        prompt=test_prompt,
                        options=memory_options
                    ),
                    timeout=20.0
                )
                
                end_time = time.time()
                snapshot2 = tracemalloc.take_snapshot()
                
                print(f"   ✅ Generated in {end_time - start_time:.2f}s: '{result.response}'")
                
                # Check memory usage
                top_stats = snapshot2.compare_to(snapshot1, 'lineno')
                print("\n📊 Memory usage with optimized options:")
                for stat in top_stats[:3]:
                    print(f"   {stat}")
                    
            except asyncio.TimeoutError:
                print("   ❌ Generation with optimized options timed out")
            except Exception as e:
                print(f"   ❌ Generation with optimized options failed: {e}")
    
    except Exception as e:
        print(f"❌ Model options testing failed: {e}")

def check_system_resources():
    """Check available system resources"""
    print("🔍 Checking System Resources...")
    
    try:
        import psutil
        
        # Memory info
        memory = psutil.virtual_memory()
        print(f"   💾 Total Memory: {memory.total / 1024**3:.1f} GB")
        print(f"   💾 Available Memory: {memory.available / 1024**3:.1f} GB")
        print(f"   💾 Memory Usage: {memory.percent}%")
        
        # CPU info
        print(f"   🖥️  CPU Cores: {psutil.cpu_count()}")
        print(f"   🖥️  CPU Usage: {psutil.cpu_percent()}%")
        
        # Disk space for temp files
        disk = psutil.disk_usage('/')
        print(f"   💽 Disk Free: {disk.free / 1024**3:.1f} GB")
        
    except ImportError:
        print("   ⚠️ psutil not available, skipping system resource check")

async def main():
    """Main debugging function"""
    print("🚀 PrismWeave Memory Usage Debug")
    print("=" * 50)
    
    # Check system resources first
    check_system_resources()
    print()
    
    # Test Ollama client memory usage
    await memory_profile_ollama()
    
    # Force garbage collection
    gc.collect()
    print("\n🧹 Garbage collection completed")
    
    # Test model options
    await test_model_options()
    
    # Force garbage collection again
    gc.collect()
    print("\n🧹 Garbage collection completed")
    
    # Test document processing
    await memory_profile_document_processing()
    
    # Final memory snapshot
    final_snapshot = tracemalloc.take_snapshot()
    top_stats = final_snapshot.statistics('lineno')
    
    print("\n📊 Final Memory Usage (Top 10):")
    for i, stat in enumerate(top_stats[:10], 1):
        print(f"   {i}. {stat}")
    
    print("\n✅ Memory profiling complete")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️ Debug interrupted by user")
    except Exception as e:
        print(f"\n❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()
