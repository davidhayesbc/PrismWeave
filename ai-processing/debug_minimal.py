#!/usr/bin/env python3
"""
Minimal debug script to test phi3:mini memory/hanging issue
Bypasses all PrismWeave dependencies to isolate the Ollama issue
"""

import asyncio
import time

async def test_with_aiohttp():
    """Test Ollama directly with aiohttp"""
    print("🔍 Testing Ollama with aiohttp (raw HTTP)")
    
    try:
        import aiohttp
        import json
        
        timeout = aiohttp.ClientTimeout(total=30)
        
        async with aiohttp.ClientSession(timeout=timeout) as session:
            # Check if Ollama is available
            print("📋 Checking Ollama server...")
            try:
                async with session.get("http://localhost:11434/api/tags") as response:
                    if response.status == 200:
                        data = await response.json()
                        models = [model['name'] for model in data.get('models', [])]
                        print(f"   ✅ Ollama available, models: {models}")
                        
                        if 'phi3:mini' not in models:
                            print("   ❌ phi3:mini not found. Please run: ollama pull phi3:mini")
                            return
                    else:
                        print(f"   ❌ Ollama not available (status: {response.status})")
                        return
            except Exception as e:
                print(f"   ❌ Ollama check failed: {e}")
                return
            
            # Test 1: Minimal generation
            print("\n🧪 Test 1: Minimal generation (5 tokens)")
            payload = {
                "model": "phi3:mini",
                "prompt": "Hello",
                "stream": False,
                "options": {
                    "num_predict": 5,
                    "temperature": 0,
                    "num_ctx": 256
                }
            }
            
            start_time = time.time()
            try:
                async with session.post("http://localhost:11434/api/generate", json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        end_time = time.time()
                        print(f"   ✅ Success in {end_time - start_time:.2f}s: '{result.get('response', '')}'")
                    else:
                        error_text = await response.text()
                        print(f"   ❌ HTTP Error {response.status}: {error_text}")
                        return
            except asyncio.TimeoutError:
                print("   ❌ TIMEOUT - This indicates the hanging issue!")
                return
            except Exception as e:
                print(f"   ❌ Error: {e}")
                return
            
            # Test 2: Document summary (the problematic case)
            print("\n🧪 Test 2: Document summary with limited content")
            
            # Read a small portion of the document
            test_content = """
            # Testing Software
            
            I don't know about you, but testing isn't my favourite part of software development.
            It's usually the last thing standing between me and shipping a shiny new feature.
            Testing can be challenging but is important for software quality.
            """
            
            summary_payload = {
                "model": "phi3:mini",
                "prompt": f"Summarize this text in one sentence:\n\n{test_content}",
                "stream": False,
                "options": {
                    "num_predict": 50,
                    "temperature": 0.1,
                    "num_ctx": 1024
                }
            }
            
            start_time = time.time()
            try:
                async with session.post("http://localhost:11434/api/generate", json=summary_payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        end_time = time.time()
                        print(f"   ✅ Success in {end_time - start_time:.2f}s")
                        print(f"   Summary: '{result.get('response', '')}'")
                    else:
                        error_text = await response.text()
                        print(f"   ❌ HTTP Error {response.status}: {error_text}")
                        return
            except asyncio.TimeoutError:
                print("   ❌ TIMEOUT - Document processing causes hanging!")
                return
            except Exception as e:
                print(f"   ❌ Error: {e}")
                return
            
            print("\n✅ Both tests passed - no hanging detected with aiohttp")
    
    except ImportError:
        print("❌ aiohttp not available")

async def test_with_ollama_library():
    """Test with the ollama Python library"""
    print("\n🔍 Testing with ollama Python library")
    
    try:
        import ollama
        
        # Test async client
        print("📋 Testing async ollama client...")
        
        async_client = ollama.AsyncClient()
        
        # Test 1: Simple generation
        print("\n🧪 Test 1: Simple generation")
        start_time = time.time()
        try:
            response = await asyncio.wait_for(
                async_client.generate(
                    model='phi3:mini',
                    prompt='Hello',
                    options={'num_predict': 5}
                ),
                timeout=15.0
            )
            end_time = time.time()
            print(f"   ✅ Success in {end_time - start_time:.2f}s: '{response['response']}'")
            
        except asyncio.TimeoutError:
            print("   ❌ TIMEOUT with ollama async client")
            return
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return
        
        # Test 2: Document-like content
        print("\n🧪 Test 2: Document-like content")
        
        test_doc = """
        # Building Industrial Strength Software without Unit Tests
        
        I don't know about you, but testing isn't my favourite part of software development.
        It's usually the last thing standing between me and shipping a shiny new feature, 
        and writing tests is often an annoying process with a lot of boilerplate.
        """
        
        start_time = time.time()
        try:
            response = await asyncio.wait_for(
                async_client.generate(
                    model='phi3:mini',
                    prompt=f'Summarize this in one sentence: {test_doc}',
                    options={'num_predict': 30, 'temperature': 0.1}
                ),
                timeout=30.0
            )
            end_time = time.time()
            print(f"   ✅ Success in {end_time - start_time:.2f}s")
            print(f"   Summary: '{response['response']}'")
            
        except asyncio.TimeoutError:
            print("   ❌ TIMEOUT with ollama async client on document content")
            return
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return
        
        print("\n✅ Ollama library tests passed")
    
    except ImportError:
        print("❌ ollama library not available")

def test_sync_ollama():
    """Test synchronous ollama (non-async)"""
    print("\n🔍 Testing synchronous ollama client")
    
    try:
        import ollama
        
        client = ollama.Client()
        
        # Test simple generation
        print("🧪 Synchronous generation test")
        start_time = time.time()
        try:
            response = client.generate(
                model='phi3:mini',
                prompt='Hello world',
                options={'num_predict': 10, 'temperature': 0}
            )
            end_time = time.time()
            print(f"   ✅ Sync success in {end_time - start_time:.2f}s: '{response['response']}'")
            
        except Exception as e:
            print(f"   ❌ Sync error: {e}")
        
    except ImportError:
        print("❌ ollama library not available for sync test")

async def main():
    """Main debug function"""
    print("🚀 Minimal Ollama phi3:mini Debug")
    print("=" * 50)
    
    # Test synchronous first (simpler)
    test_sync_ollama()
    
    # Test with aiohttp (raw HTTP)
    await test_with_aiohttp()
    
    # Test with ollama library
    await test_with_ollama_library()
    
    print("\n💡 Diagnosis:")
    print("- If all tests pass: Issue is in PrismWeave code")
    print("- If tests timeout: Issue is with phi3:mini model or Ollama setup")
    print("- If sync works but async fails: Async handling issue")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Tests failed: {e}")
        import traceback
        traceback.print_exc()
