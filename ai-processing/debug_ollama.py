#!/usr/bin/env python3
"""
Debug script to test Ollama client and investigate the 'done_reason' field issue
"""
import asyncio
import logging
import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from models.ollama_client import OllamaClient, GenerationResult

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def debug_models():
    """Debug the models that are causing issues"""
    problematic_models = [
        "qwen2.5:3b",
        "phi3:latest", 
        "phi3:mini",
        "mistral:latest",
        "qwen2.5-coder:latest"
    ]
    
    async with OllamaClient() as client:
        logger.info("=== Starting Ollama Debug Session ===")
        
        # Check if Ollama is available
        is_available = await client.is_available()
        logger.info(f"Ollama available: {is_available}")
        
        if not is_available:
            logger.error("Ollama is not available - exiting")
            return
        
        # List available models
        logger.info("=== Listing Available Models ===")
        models = await client.list_models()
        logger.info(f"Found {len(models)} models:")
        for model in models:
            logger.info(f"  - {model.name}")
        
        # Test each problematic model
        for model_name in problematic_models:
            logger.info(f"\n=== Testing Model: {model_name} ===")
            
            # Check if model exists
            exists = await client.model_exists(model_name)
            logger.info(f"Model {model_name} exists: {exists}")
            
            if not exists:
                logger.warning(f"Skipping {model_name} - not available")
                continue
            
            # Try a simple generation
            try:
                logger.info(f"Testing generation with {model_name}")
                result = await client.generate(
                    model=model_name,
                    prompt="Hello, please respond with just 'Hi there!'",
                    stream=False
                )
                
                logger.info(f"Generation successful for {model_name}")
                logger.info(f"Response: {result.response[:100]}...")
                logger.info(f"Model: {result.model}")
                logger.info(f"Done: {result.done}")
                logger.info(f"Done reason: {getattr(result, 'done_reason', 'NOT SET')}")
                
            except Exception as e:
                logger.error(f"Generation failed for {model_name}: {e}")
                logger.error(f"Exception type: {type(e).__name__}")
                
                # Try to get raw response data
                try:
                    logger.info("Attempting to get raw response data...")
                    # This is a hack to see the raw data
                    import ollama
                    response = ollama.generate(model=model_name, prompt="Test", stream=False)
                    logger.info(f"Raw Ollama response keys: {list(response.keys())}")
                    logger.info(f"Raw Ollama response: {json.dumps(response, indent=2, default=str)}")
                except Exception as raw_error:
                    logger.error(f"Failed to get raw response: {raw_error}")

async def test_generation_result_creation():
    """Test creating GenerationResult with various field combinations"""
    logger.info("\n=== Testing GenerationResult Creation ===")
    
    # Test data with done_reason field (newer Ollama versions)
    test_data_with_done_reason = {
        "model": "test:latest",
        "created_at": "2024-01-01T00:00:00Z",
        "response": "Test response",
        "done": True,
        "done_reason": "stop",
        "context": [1, 2, 3],
        "total_duration": 1000000,
        "load_duration": 500000,
        "prompt_eval_count": 10,
        "prompt_eval_duration": 200000,
        "eval_count": 5,
        "eval_duration": 300000
    }
    
    # Test data without done_reason field (older Ollama versions)
    test_data_without_done_reason = {
        "model": "test:latest",
        "created_at": "2024-01-01T00:00:00Z",
        "response": "Test response",
        "done": True,
        "total_duration": 1000000,
        "load_duration": 500000,
        "prompt_eval_count": 10,
        "prompt_eval_duration": 200000,
        "eval_count": 5,
        "eval_duration": 300000
    }
    
    # Test with minimal data
    test_data_minimal = {
        "model": "test:latest",
        "created_at": "2024-01-01T00:00:00Z",
        "response": "Test response",
        "done": True
    }
    
    test_cases = [
        ("With done_reason", test_data_with_done_reason),
        ("Without done_reason", test_data_without_done_reason),
        ("Minimal data", test_data_minimal)
    ]
    
    for test_name, test_data in test_cases:
        logger.info(f"\nTesting: {test_name}")
        logger.info(f"Test data keys: {list(test_data.keys())}")
        
        try:
            result = GenerationResult.from_dict(test_data)
            logger.info(f"✅ SUCCESS: Created GenerationResult")
            logger.info(f"   Model: {result.model}")
            logger.info(f"   Response length: {len(result.response)}")
            logger.info(f"   Done: {result.done}")
            logger.info(f"   Done reason: {getattr(result, 'done_reason', 'NOT SET')}")
        except Exception as e:
            logger.error(f"❌ FAILED: {e}")
            logger.error(f"   Exception type: {type(e).__name__}")

if __name__ == "__main__":
    # Test GenerationResult creation first
    asyncio.run(test_generation_result_creation())
    
    # Then test actual model interactions
    asyncio.run(debug_models())
