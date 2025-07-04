#!/usr/bin/env python3
"""
Debug script to test specific models and their response structures
"""

import asyncio
import json
import logging
from pathlib import Path
import sys

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from models.ollama_client import OllamaClient

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

PROBLEMATIC_MODELS = [
    "qwen3:latest",
    "phi4-reasoning:latest", 
    "phi4-mini-reasoning:3.8b",
    "mistral:latest",
    "qwen2.5-coder:latest"
]

async def debug_all_models():
    """Debug all problematic models"""
    async with OllamaClient() as client:
        print("🔍 Starting model debugging session...")
        
        # First, check which models are actually available
        print("\n📋 Checking available models...")
        models = await client.list_models()
        available_model_names = [model.name for model in models]
        print(f"Available models: {available_model_names}")
        
        results = {}
        
        for model_name in PROBLEMATIC_MODELS:
            print(f"\n🤖 Testing model: {model_name}")
            print("=" * 50)
            
            # Check if model exists
            exists = await client.model_exists(model_name)
            print(f"Model exists: {exists}")
            
            if not exists:
                # Check if any similar models exist
                model_base = model_name.split(':')[0]
                similar = [name for name in available_model_names if name.startswith(model_base)]
                if similar:
                    print(f"Similar models found: {similar}")
                    # Test the first similar model
                    model_name = similar[0]
                    print(f"Testing similar model: {model_name}")
                else:
                    print(f"❌ No similar models found for {model_name}")
                    continue
            
            try:
                # Debug the response structure
                debug_info = await client.debug_model_response(model_name)
                results[model_name] = debug_info
                
                print(f"📊 Debug Results for {model_name}:")
                print(f"  Response keys: {debug_info['response_keys']}")
                print(f"  Response types: {debug_info['response_types']}")
                
                if debug_info.get('raw_response'):
                    raw = debug_info['raw_response']
                    print(f"  Raw response sample:")
                    for key, value in raw.items():
                        if isinstance(value, str) and len(value) > 100:
                            print(f"    {key}: {type(value).__name__} (length: {len(value)})")
                        else:
                            print(f"    {key}: {value}")
                
                gen_result = debug_info.get('generation_result', {})
                if gen_result.get('success'):
                    print(f"  ✅ GenerationResult parsing: SUCCESS")
                    print(f"  Response length: {gen_result.get('response_length', 'unknown')}")
                else:
                    print(f"  ❌ GenerationResult parsing: FAILED")
                    print(f"  Parse error: {gen_result.get('parse_error', 'unknown')}")
                
                if debug_info.get('error'):
                    print(f"  ❌ Error: {debug_info['error']}")
                    
            except Exception as e:
                print(f"  💥 Exception during debug: {e}")
                results[model_name] = {"error": str(e)}
        
        # Save results to file
        results_file = Path(__file__).parent / "debug_results.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n💾 Debug results saved to: {results_file}")
        
        # Summary
        print(f"\n📈 Summary:")
        successful = sum(1 for r in results.values() if r.get('generation_result', {}).get('success'))
        total = len(results)
        print(f"  Successful models: {successful}/{total}")
        
        if successful < total:
            print(f"  Failed models:")
            for model, result in results.items():
                if not result.get('generation_result', {}).get('success'):
                    error = result.get('generation_result', {}).get('parse_error') or result.get('error', 'unknown')
                    print(f"    - {model}: {error}")

if __name__ == "__main__":
    asyncio.run(debug_all_models())
