#!/usr/bin/env python3
"""
Minimal phi3:mini timeout investigation
"""

import asyncio
import aiohttp
import time
import json

async def test_phi3_mini_minimal():
    """Test phi3:mini with absolute minimal request"""
    
    print("🔬 Minimal phi3:mini Timeout Investigation")
    print("=" * 50)
    
    # Test different payload sizes
    test_cases = [
        ("Tiny", "Hi"),
        ("Small", "What is 2+2?"),
        ("Medium", "Explain what machine learning is in one sentence."),
        ("Large", "What is artificial intelligence?" * 10),
        ("Code", "```python\nprint('hello')\n```"),
        ("Markdown", "# Header\n\nSome **bold** text with `code`.")
    ]
    
    timeout = aiohttp.ClientTimeout(total=60, sock_read=60)
    connector = aiohttp.TCPConnector(limit=1)
    
    async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
        
        for test_name, prompt in test_cases:
            print(f"\n🧪 Test: {test_name}")
            print(f"   Prompt: '{prompt[:50]}{'...' if len(prompt) > 50 else ''}'")
            
            payload = {
                "model": "phi3:mini",
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": 20,    # Very short response
                    "temperature": 0.1,
                    "num_ctx": 512       # Small context
                }
            }
            
            try:
                start_time = time.time()
                
                async with session.post("http://localhost:11434/api/generate", json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        end_time = time.time()
                        
                        print(f"   ✅ SUCCESS in {end_time - start_time:.2f}s")
                        print(f"   Response: '{data.get('response', '')[:80]}...'")
                    else:
                        error_text = await response.text()
                        print(f"   ❌ HTTP {response.status}: {error_text[:100]}")
                        
            except asyncio.TimeoutError:
                print(f"   ❌ TIMEOUT after 60 seconds")
            except Exception as e:
                print(f"   ❌ ERROR: {e}")

async def check_ollama_status():
    """Check Ollama service status"""
    print("\n🔍 Checking Ollama Status")
    print("=" * 30)
    
    timeout = aiohttp.ClientTimeout(total=10)
    
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            # Check if Ollama is running
            async with session.get("http://localhost:11434/api/tags") as response:
                if response.status == 200:
                    data = await response.json()
                    models = data.get('models', [])
                    print(f"✅ Ollama is running with {len(models)} models")
                    
                    # Check if phi3:mini is available
                    phi3_models = [m for m in models if 'phi3' in m.get('name', '')]
                    if phi3_models:
                        print(f"✅ phi3 models available: {[m['name'] for m in phi3_models]}")
                    else:
                        print("❌ No phi3 models found")
                        
                else:
                    print(f"❌ Ollama responded with status {response.status}")
    except Exception as e:
        print(f"❌ Ollama check failed: {e}")

async def test_other_models():
    """Test if other models work to isolate if it's phi3:mini specific"""
    print("\n🧪 Testing Other Models")
    print("=" * 30)
    
    # Get available models first
    timeout = aiohttp.ClientTimeout(total=30)
    
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get("http://localhost:11434/api/tags") as response:
                if response.status == 200:
                    data = await response.json()
                    models = [m['name'] for m in data.get('models', [])]
                    print(f"Available models: {models}")
                    
                    # Test each model with a simple prompt
                    simple_prompt = "What is 1+1?"
                    
                    for model_name in models[:3]:  # Test first 3 models
                        print(f"\n🤖 Testing {model_name}...")
                        
                        payload = {
                            "model": model_name,
                            "prompt": simple_prompt,
                            "stream": False,
                            "options": {"num_predict": 10}
                        }
                        
                        try:
                            start_time = time.time()
                            
                            async with session.post("http://localhost:11434/api/generate", json=payload) as response:
                                if response.status == 200:
                                    result = await response.json()
                                    end_time = time.time()
                                    print(f"   ✅ SUCCESS in {end_time - start_time:.2f}s")
                                    print(f"   Response: '{result.get('response', '')}'")
                                else:
                                    error_text = await response.text()
                                    print(f"   ❌ HTTP {response.status}: {error_text[:100]}")
                                    
                        except Exception as e:
                            print(f"   ❌ ERROR: {e}")
                            
    except Exception as e:
        print(f"❌ Model testing failed: {e}")

async def main():
    """Main investigation"""
    
    # Check Ollama status
    await check_ollama_status()
    
    # Test other models first
    await test_other_models()
    
    # Test phi3:mini specifically
    await test_phi3_mini_minimal()
    
    print("\n💡 Investigation Summary:")
    print("1. If other models work but phi3:mini doesn't: phi3:mini specific issue")
    print("2. If all models timeout: Ollama service issue")
    print("3. If only larger prompts timeout: Context/complexity issue")
    print("4. Consider restarting Ollama service or trying a different model")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️ Investigation interrupted")
    except Exception as e:
        print(f"\n❌ Investigation failed: {e}")
        import traceback
        traceback.print_exc()
