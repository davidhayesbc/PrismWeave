#!/usr/bin/env python3
"""
Simple debug script to identify the memory/hanging issue in Ollama phi3:mini processing
"""

import asyncio
import sys
import time
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.models.ollama_client import OllamaClient

async def test_phi3_mini():
    """Test phi3:mini model with progressively complex requests"""
    print("🔍 Testing phi3:mini Memory/Hanging Issue")
    print("=" * 50)
    
    try:
        async with OllamaClient() as client:
            model_name = "phi3:mini"
            
            # Check if model exists
            print(f"📋 Checking if {model_name} is available...")
            model_available = await client.model_exists(model_name)
            print(f"   Available: {model_available}")
            
            if not model_available:
                print(f"❌ Model {model_name} not available. Please pull it first with: ollama pull {model_name}")
                return
            
            # Test 1: Minimal generation
            print(f"\n🧪 Test 1: Minimal generation")
            simple_options = {
                "num_predict": 5,      # Only generate 5 tokens
                "temperature": 0,      # Deterministic
                "num_ctx": 256,        # Small context
            }
            
            start_time = time.time()
            try:
                result = await asyncio.wait_for(
                    client.generate(
                        model=model_name,
                        prompt="Hello",
                        options=simple_options
                    ),
                    timeout=15.0  # 15 second timeout
                )
                end_time = time.time()
                print(f"   ✅ Success in {end_time - start_time:.2f}s: '{result.response}'")
                
            except asyncio.TimeoutError:
                print("   ❌ TIMEOUT after 15 seconds - This indicates the hanging issue!")
                return
            except Exception as e:
                print(f"   ❌ Error: {e}")
                return
            
            # Test 2: Slightly larger generation
            print(f"\n🧪 Test 2: Small text generation")
            small_options = {
                "num_predict": 20,     # 20 tokens
                "temperature": 0.1,
                "num_ctx": 512,        # Moderate context
            }
            
            start_time = time.time()
            try:
                result = await asyncio.wait_for(
                    client.generate(
                        model=model_name,
                        prompt="Write one sentence about testing software.",
                        options=small_options
                    ),
                    timeout=20.0
                )
                end_time = time.time()
                print(f"   ✅ Success in {end_time - start_time:.2f}s: '{result.response}'")
                
            except asyncio.TimeoutError:
                print("   ❌ TIMEOUT after 20 seconds")
                return
            except Exception as e:
                print(f"   ❌ Error: {e}")
                return
            
            # Test 3: Document summary (the problematic case)
            print(f"\n🧪 Test 3: Document summary (problematic case)")
            
            # Read the test document
            doc_path = Path("d:/source/PrismWeaveDocs/documents/tech/2025-06-22-building-industrial-strength-software-without-unit.md")
            
            if not doc_path.exists():
                print(f"   ❌ Test document not found: {doc_path}")
                return
            
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Truncate content to see if it's a content length issue
            content_truncated = content[:2000]  # First 2000 characters
            
            summary_options = {
                "num_predict": 100,    # Reasonable summary length
                "temperature": 0.1,
                "num_ctx": 2048,       # Larger context for document
            }
            
            system_prompt = "You are a document summarization expert. Create a concise, informative summary."
            user_prompt = f"Summarize this document in 2-3 sentences:\n\n{content_truncated}"
            
            print(f"   Document size: {len(content)} chars (using first {len(content_truncated)} chars)")
            print(f"   Prompt size: {len(user_prompt)} chars")
            
            start_time = time.time()
            try:
                result = await asyncio.wait_for(
                    client.generate(
                        model=model_name,
                        prompt=user_prompt,
                        system=system_prompt,
                        options=summary_options
                    ),
                    timeout=45.0  # 45 second timeout for longer task
                )
                end_time = time.time()
                print(f"   ✅ Success in {end_time - start_time:.2f}s")
                print(f"   Summary: '{result.response}'")
                
            except asyncio.TimeoutError:
                print("   ❌ TIMEOUT after 45 seconds - Document processing hangs!")
                print("   💡 This confirms the issue is with document processing")
                return
            except Exception as e:
                print(f"   ❌ Error: {e}")
                return
            
            print("\n✅ All tests passed! No hanging detected.")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

async def debug_ollama_directly():
    """Debug Ollama directly to see if it's a PrismWeave issue or Ollama issue"""
    print("\n🔍 Testing Ollama directly (bypassing PrismWeave client)")
    
    try:
        import ollama
        
        print("📋 Testing synchronous Ollama client...")
        
        # Test basic generation
        start_time = time.time()
        try:
            response = ollama.generate(
                model='phi3:mini',
                prompt='Hello, respond with just "Hi"',
                options={'num_predict': 5}
            )
            end_time = time.time()
            print(f"   ✅ Direct Ollama success in {end_time - start_time:.2f}s: '{response['response']}'")
            
        except Exception as e:
            print(f"   ❌ Direct Ollama failed: {e}")
            
    except ImportError:
        print("   ⚠️ Ollama module not available for direct testing")

async def main():
    """Main debug function"""
    await test_phi3_mini()
    await debug_ollama_directly()
    
    print("\n💡 Troubleshooting suggestions:")
    print("1. If Test 1 fails: Basic Ollama/phi3:mini issue")
    print("2. If Test 2 fails: Context/generation length issue")
    print("3. If Test 3 fails: Document processing causes memory/hanging")
    print("4. Check Ollama logs: ollama logs")
    print("5. Try different model: phi3:3.8b-mini-instruct-4k-fp16")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️ Debug interrupted by user")
    except Exception as e:
        print(f"\n❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()
