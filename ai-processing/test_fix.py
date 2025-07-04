#!/usr/bin/env python3
"""
Test script to verify the GenerationResult fix for done_reason error
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.models.ollama_client import OllamaClient

async def test_generation():
    """Test generation with different models to verify fix"""
    client = OllamaClient()
    
    try:
        print("🔍 Testing Ollama connection...")
        is_available = await client.is_available()
        print(f"✅ Ollama available: {is_available}")
        
        if not is_available:
            print("❌ Ollama server not available")
            return
        
        print("\n📋 Listing available models...")
        models = await client.list_models()
        model_names = [m.name for m in models]
        print(f"Available models: {model_names}")
        
        # Test with a working model first
        test_models = ['phi3:mini', 'qwen2.5-coder:latest']
        
        for model_name in test_models:
            if model_name in model_names:
                print(f"\n🧪 Testing {model_name}...")
                try:
                    result = await client.generate(
                        model=model_name,
                        prompt="Hello! Please respond with just 'Success' to test the API."
                    )
                    print(f"✅ {model_name} generation successful!")
                    print(f"   Response: {result.response.strip()}")
                    print(f"   Model: {result.model}")
                    print(f"   Done: {result.done}")
                    
                    # Check if done_reason is handled properly
                    done_reason = getattr(result, 'done_reason', None)
                    print(f"   Done reason: {done_reason}")
                    
                    print(f"   Processing time: {result.total_duration / 1_000_000:.2f}ms")
                    
                except Exception as e:
                    print(f"❌ {model_name} generation failed: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print(f"⚠️  {model_name} not available, skipping...")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await client.close()

if __name__ == "__main__":
    print("🚀 Testing GenerationResult fix for done_reason error")
    print("=" * 60)
    asyncio.run(test_generation())
    print("=" * 60)
    print("✅ Test completed!")
