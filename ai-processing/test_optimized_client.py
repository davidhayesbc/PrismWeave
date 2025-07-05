#!/usr/bin/env python3
"""
Memory-optimized fix for PrismWeave OllamaClient 
Addresses the memory usage and hanging issues with phi3:mini processing
"""

import asyncio
import time
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
import logging

# Reduce logging verbosity to prevent memory bloat
logging.getLogger().setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# Import the original classes we need
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.models.ollama_client import GenerationResult, ModelInfo

class OptimizedOllamaClient:
    """Memory-optimized Ollama client to fix hanging and memory issues"""
    
    def __init__(self, host: str = "http://localhost:11434", timeout: int = 30):
        self.host = host.rstrip('/')
        self.timeout = timeout
        self._session: Optional = None
        
        # Reduce memory footprint - don't cache models unnecessarily
        self._available_models: Dict[str, bool] = {}  # Just track existence, not full info
        
        # Import aiohttp only when needed
        self._aiohttp = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit with proper cleanup"""
        await self.close()
    
    async def _get_aiohttp(self):
        """Lazy import aiohttp to reduce memory"""
        if self._aiohttp is None:
            import aiohttp
            self._aiohttp = aiohttp
        return self._aiohttp
    
    async def _ensure_session(self):
        """Create session with proper timeout and memory settings"""
        if self._session is None:
            aiohttp = await self._get_aiohttp()
            
            # Optimize timeout and connection settings for memory
            timeout = aiohttp.ClientTimeout(
                total=self.timeout,
                connect=10,      # Quick connection timeout
                sock_read=self.timeout  # But allow longer for generation
            )
            
            # Create session with memory-optimized settings
            connector = aiohttp.TCPConnector(
                limit=1,           # Limit concurrent connections
                limit_per_host=1,  # One connection per host
                ttl_dns_cache=300, # 5 minutes DNS cache
                use_dns_cache=True
            )
            
            self._session = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector
            )
    
    async def close(self):
        """Close session and clean up memory"""
        if self._session:
            await self._session.close()
            self._session = None
        
        # Clear cached data
        self._available_models.clear()
    
    async def is_available(self) -> bool:
        """Quick availability check with minimal memory usage"""
        try:
            await self._ensure_session()
            
            async with self._session.get(f"{self.host}/api/tags") as response:
                return response.status == 200
        except:
            return False
    
    async def model_exists(self, model_name: str) -> bool:
        """Memory-efficient model existence check"""
        # Check cache first
        if model_name in self._available_models:
            return self._available_models[model_name]
        
        try:
            await self._ensure_session()
            
            async with self._session.get(f"{self.host}/api/tags") as response:
                if response.status == 200:
                    data = await response.json()
                    models = data.get('models', [])
                    
                    # Cache only what we need
                    for model in models:
                        name = model.get('name', '')
                        self._available_models[name] = True
                    
                    # Check both exact name and base name
                    model_base = model_name.split(':')[0]
                    exists = any(
                        name == model_name or name.startswith(f"{model_base}:")
                        for name in self._available_models.keys()
                    )
                    
                    self._available_models[model_name] = exists
                    return exists
        except:
            pass
        
        self._available_models[model_name] = False
        return False
    
    async def generate(
        self,
        model: str,
        prompt: str,
        system: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> GenerationResult:
        """Memory-optimized generation with proper error handling"""
        
        # Apply memory-optimized defaults
        if options is None:
            options = {}
        
        # Set memory-optimized options for phi3:mini
        optimized_options = {
            "num_ctx": 2048,        # Reasonable context window
            "num_predict": 200,     # Limit prediction length
            "temperature": 0.1,     # Reduce randomness
            "top_p": 0.9,          # Nucleus sampling
            "repeat_penalty": 1.1,  # Prevent loops
            "stop": ["\n\n\n"]     # Stop on multiple newlines
        }
        
        # Merge with user options, user options take precedence
        optimized_options.update(options)
        
        # Ensure model exists
        if not await self.model_exists(model):
            raise Exception(f"Model {model} not available")
        
        # Build minimal payload
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": optimized_options
        }
        
        if system:
            payload["system"] = system
        
        try:
            await self._ensure_session()
            
            async with self._session.post(f"{self.host}/api/generate", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Create result with minimal memory footprint
                    result = GenerationResult(
                        response=data.get('response', ''),
                        model=data.get('model', model),
                        created_at=data.get('created_at', ''),
                        done=data.get('done', True),
                        total_duration=data.get('total_duration', 0),
                        eval_count=data.get('eval_count', 0)
                    )
                    
                    return result
                else:
                    error_text = await response.text()
                    raise Exception(f"Generation failed: {response.status} - {error_text}")
        
        except Exception as e:
            raise Exception(f"Generation error: {e}")

async def test_optimized_client():
    """Test the optimized client with the problematic document"""
    print("🔧 Testing Optimized OllamaClient")
    print("=" * 50)
    
    # Read the problematic document
    doc_path = Path("d:/source/PrismWeaveDocs/documents/tech/2025-06-22-building-industrial-strength-software-without-unit.md")
    
    if not doc_path.exists():
        print(f"❌ Test document not found: {doc_path}")
        return
    
    with open(doc_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"📄 Document size: {len(content)} characters")
    
    async with OptimizedOllamaClient() as client:
        # Test availability
        print("📋 Checking Ollama availability...")
        available = await client.is_available()
        print(f"   Available: {available}")
        
        if not available:
            print("❌ Ollama not available")
            return
        
        # Test model existence
        print("📋 Checking phi3:mini availability...")
        model_exists = await client.model_exists("phi3:mini")
        print(f"   phi3:mini available: {model_exists}")
        
        if not model_exists:
            print("❌ phi3:mini not available")
            return
        
        # Test summary generation (the problematic case)
        print("\n🧪 Testing document summary generation...")
        
        # Truncate content to avoid overwhelming the model
        content_sample = content[:3000]  # First 3000 characters
        
        system_prompt = "You are a document summarization expert. Create a concise, informative summary."
        user_prompt = f"Summarize this document in 2-3 sentences:\n\n{content_sample}"
        
        print(f"   Content sample size: {len(content_sample)} characters")
        print(f"   Prompt size: {len(user_prompt)} characters")
        
        start_time = time.time()
        try:
            result = await asyncio.wait_for(
                client.generate(
                    model="phi3:mini",
                    prompt=user_prompt,
                    system=system_prompt
                ),
                timeout=60.0  # 60 second timeout
            )
            
            end_time = time.time()
            print(f"   ✅ SUCCESS in {end_time - start_time:.2f}s")
            print(f"   Summary: '{result.response}'")
            print(f"   Response length: {len(result.response)} characters")
            
        except asyncio.TimeoutError:
            print("   ❌ TIMEOUT - Still hanging with optimized client")
        except Exception as e:
            print(f"   ❌ ERROR: {e}")

async def test_multiple_documents():
    """Test processing multiple documents to check for memory leaks"""
    print("\n🔧 Testing Multiple Document Processing")
    print("=" * 50)
    
    docs_path = Path("d:/source/PrismWeaveDocs/documents")
    md_files = list(docs_path.rglob("*.md"))[:3]  # Test first 3 files
    
    print(f"📄 Testing {len(md_files)} documents")
    
    async with OptimizedOllamaClient() as client:
        for i, doc_path in enumerate(md_files, 1):
            print(f"\n📄 Processing document {i}: {doc_path.name}")
            
            try:
                with open(doc_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Use first 1000 characters for quick processing
                content_sample = content[:1000]
                
                start_time = time.time()
                result = await asyncio.wait_for(
                    client.generate(
                        model="phi3:mini",
                        prompt=f"Summarize in one sentence: {content_sample}",
                        options={"num_predict": 50}  # Short summary
                    ),
                    timeout=30.0
                )
                
                end_time = time.time()
                print(f"   ✅ Processed in {end_time - start_time:.2f}s")
                print(f"   Summary: '{result.response[:100]}...'")
                
            except Exception as e:
                print(f"   ❌ Failed: {e}")

async def main():
    """Main test function"""
    print("🚀 PrismWeave Ollama Client Optimization Test")
    print("=" * 60)
    
    # Test optimized client
    await test_optimized_client()
    
    # Test multiple documents
    await test_multiple_documents()
    
    print("\n✅ Optimization tests complete")
    print("\n💡 Next steps:")
    print("1. If optimized client works: Replace the original OllamaClient")
    print("2. If still hanging: Issue may be with phi3:mini model itself")
    print("3. Consider using a different model like qwen2.5-coder or phi4-mini")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
