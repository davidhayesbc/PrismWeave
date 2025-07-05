#!/usr/bin/env python3
"""
Test the fixed PrismWeave configuration with the problematic document
"""

import asyncio
import time
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path.cwd() / 'src'))

async def test_fixed_processing():
    """Test document processing with the fixed configuration"""
    
    print("🧪 Testing Fixed PrismWeave Document Processing")
    print("=" * 55)
    
    try:
        # Import PrismWeave components
        from src.processors.document_processor import DocumentProcessor
        from src.utils.config import Config
        
        # Load configuration
        config = Config()
        print(f"✅ Configuration loaded")
        print(f"   max_content_length: {config.processing.max_content_length}")
        print(f"   timeout: {getattr(config.processing, 'timeout', 'default')}")
        
        # Initialize processor
        processor = DocumentProcessor(config)
        print(f"✅ Document processor initialized")
        
        # Test with the problematic document
        doc_path = Path("d:/source/PrismWeaveDocs/documents/tech/2025-06-22-building-industrial-strength-software-without-unit.md")
        
        if not doc_path.exists():
            print(f"❌ Test document not found: {doc_path}")
            return
            
        print(f"📄 Testing with: {doc_path.name}")
        
        # Read document
        with open(doc_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"📊 Original document size: {len(content)} characters")
        
        # The new config should automatically truncate to 3000 characters
        max_length = config.processing.max_content_length
        if len(content) > max_length:
            print(f"📊 Will be truncated to: {max_length} characters")
        
        # Test summary generation
        print(f"\n🔍 Testing summary generation...")
        start_time = time.time()
        
        try:
            summary = await asyncio.wait_for(
                processor._generate_summary(content, "Building Industrial Strength Software without Unit Tests"),
                timeout=60.0  # 60 second timeout
            )
            
            end_time = time.time()
            
            if summary:
                print(f"✅ SUCCESS in {end_time - start_time:.2f}s")
                print(f"📝 Summary: '{summary}'")
                print(f"📊 Summary length: {len(summary)} characters")
            else:
                print(f"⚠️ Generated empty summary in {end_time - start_time:.2f}s")
                
        except asyncio.TimeoutError:
            print(f"❌ TIMEOUT after 60 seconds")
        except Exception as e:
            print(f"❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            
        # Test tag generation
        print(f"\n🏷️ Testing tag generation...")
        start_time = time.time()
        
        try:
            tags = await asyncio.wait_for(
                processor._suggest_tags(content, "Building Industrial Strength Software without Unit Tests", []),
                timeout=60.0
            )
            
            end_time = time.time()
            
            if tags:
                print(f"✅ SUCCESS in {end_time - start_time:.2f}s")
                print(f"🏷️ Tags: {tags}")
            else:
                print(f"⚠️ Generated no tags in {end_time - start_time:.2f}s")
                
        except asyncio.TimeoutError:
            print(f"❌ TIMEOUT after 60 seconds")
        except Exception as e:
            print(f"❌ ERROR: {e}")
            
    except ImportError as e:
        print(f"❌ Could not import PrismWeave components: {e}")
        print("   Make sure all dependencies are installed with 'uv pip install -r requirements.txt'")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

async def test_model_availability():
    """Test if phi3:mini is available and working"""
    print("\n🔍 Testing Model Availability")
    print("=" * 35)
    
    try:
        from src.models.ollama_client import OllamaClient
        from src.utils.config import Config
        
        config = Config()
        client = OllamaClient(config)
        
        # Test phi3:mini availability
        print("📋 Checking phi3:mini availability...")
        available = await client.is_available()
        print(f"   Ollama service: {'✅ Available' if available else '❌ Not available'}")
        
        if available:
            phi3_exists = await client.model_exists("phi3:mini")
            print(f"   phi3:mini model: {'✅ Available' if phi3_exists else '❌ Not available'}")
            
            if phi3_exists:
                # Test a simple generation
                print("🧪 Testing simple generation...")
                start_time = time.time()
                
                result = await asyncio.wait_for(
                    client.generate(
                        model="phi3:mini",
                        prompt="What is 2+2?",
                        system="You are a helpful assistant."
                    ),
                    timeout=30.0
                )
                
                end_time = time.time()
                print(f"   ✅ Simple test: {end_time - start_time:.2f}s")
                print(f"   Response: '{result.response[:50]}...'")
        
        await client.close()
        
    except Exception as e:
        print(f"❌ Model test failed: {e}")

async def main():
    """Main test function"""
    print("🚀 PrismWeave Fix Verification Test")
    print("=" * 60)
    
    # Test model availability first
    await test_model_availability()
    
    # Test fixed processing
    await test_fixed_processing()
    
    print("\n💡 Test Summary:")
    print("✅ If both tests pass: The configuration fix resolved the issue")
    print("⚠️ If still timing out: Try switching to mistral:latest model")
    print("❌ If failing to import: Install dependencies with 'uv pip install -r requirements.txt'")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
