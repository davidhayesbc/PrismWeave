#!/usr/bin/env python3
"""
Debug script to isolate the specific issue with the problematic document
"""

import asyncio
import time
import re
from pathlib import Path

# Import our optimized client
from test_optimized_client import OptimizedOllamaClient

async def analyze_document_content():
    """Analyze the problematic document to find what's causing issues"""
    
    doc_path = Path("d:/source/PrismWeaveDocs/documents/tech/2025-06-22-building-industrial-strength-software-without-unit.md")
    
    with open(doc_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("🔍 Document Analysis")
    print("=" * 50)
    print(f"Total size: {len(content)} characters")
    print(f"Total lines: {content.count(chr(10))} lines")
    
    # Analyze specific content patterns
    code_blocks = re.findall(r'```[^`]*```', content)
    print(f"Code blocks: {len(code_blocks)}")
    
    # Find nested backticks
    nested_backticks = re.findall(r'`{3,}', content)
    print(f"Nested backticks (3+): {len(nested_backticks)}")
    
    # Find markdown complexity
    headers = re.findall(r'^#+ ', content, re.MULTILINE)
    print(f"Headers: {len(headers)}")
    
    links = re.findall(r'\[([^\]]+)\]\([^)]+\)', content)
    print(f"Links: {len(links)}")
    
    # Look for special characters that might cause parsing issues
    special_chars = len(re.findall(r'[^\x00-\x7F]', content))
    print(f"Non-ASCII characters: {special_chars}")
    
    # Test different portions of the document
    await test_document_portions(content)

async def test_document_portions(content: str):
    """Test different portions of the document to isolate the issue"""
    print("\n🧪 Testing Document Portions")
    print("=" * 50)
    
    async with OptimizedOllamaClient() as client:
        
        # Test 1: Just the frontmatter
        frontmatter_end = content.find('---', 3) + 3
        frontmatter = content[:frontmatter_end]
        
        await test_content_portion(client, "Frontmatter only", frontmatter)
        
        # Test 2: First 500 characters
        await test_content_portion(client, "First 500 chars", content[:500])
        
        # Test 3: First 1000 characters  
        await test_content_portion(client, "First 1000 chars", content[:1000])
        
        # Test 4: First 2000 characters
        await test_content_portion(client, "First 2000 chars", content[:2000])
        
        # Test 5: Content without code blocks
        no_code_blocks = re.sub(r'```[^`]*```', '[CODE BLOCK REMOVED]', content)
        await test_content_portion(client, "No code blocks", no_code_blocks[:2000])
        
        # Test 6: Just the problematic section (around line 100)
        lines = content.split('\n')
        problem_section = '\n'.join(lines[80:120])
        await test_content_portion(client, "Lines 80-120", problem_section)

async def test_content_portion(client, description: str, content_portion: str):
    """Test a specific portion of content"""
    print(f"\n📄 Testing: {description}")
    print(f"   Size: {len(content_portion)} characters")
    
    # Use a very simple prompt to minimize complexity
    prompt = f"What is this text about? Answer in one sentence:\n\n{content_portion}"
    
    try:
        start_time = time.time()
        
        result = await asyncio.wait_for(
            client.generate(
                model="phi3:mini",
                prompt=prompt,
                options={
                    "num_predict": 50,    # Very short response
                    "temperature": 0.1,   # Low temperature
                    "num_ctx": 1024       # Smaller context
                }
            ),
            timeout=30.0  # 30 second timeout
        )
        
        end_time = time.time()
        print(f"   ✅ SUCCESS in {end_time - start_time:.2f}s")
        print(f"   Response: '{result.response[:100]}...'")
        
    except asyncio.TimeoutError:
        print(f"   ❌ TIMEOUT after 30 seconds")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")

async def test_different_models():
    """Test with different models to see if issue is phi3:mini specific"""
    print("\n🧪 Testing Different Models")
    print("=" * 50)
    
    doc_path = Path("d:/source/PrismWeaveDocs/documents/tech/2025-06-22-building-industrial-strength-software-without-unit.md")
    
    with open(doc_path, 'r', encoding='utf-8') as f:
        content = f.read()[:2000]  # First 2000 characters
    
    # Models to test (you may need to adjust based on what you have installed)
    models_to_test = [
        "phi3:mini",
        "qwen2.5:1.5b",
        "llama3.2:1b",
        "gemma2:2b"
    ]
    
    prompt = f"Summarize this in one sentence: {content}"
    
    async with OptimizedOllamaClient() as client:
        for model in models_to_test:
            print(f"\n🤖 Testing model: {model}")
            
            # Check if model exists
            if not await client.model_exists(model):
                print(f"   ⚠️ Model {model} not available")
                continue
            
            try:
                start_time = time.time()
                
                result = await asyncio.wait_for(
                    client.generate(
                        model=model,
                        prompt=prompt,
                        options={"num_predict": 50}
                    ),
                    timeout=45.0
                )
                
                end_time = time.time()
                print(f"   ✅ SUCCESS in {end_time - start_time:.2f}s")
                print(f"   Response: '{result.response[:80]}...'")
                
            except asyncio.TimeoutError:
                print(f"   ❌ TIMEOUT after 45 seconds")
            except Exception as e:
                print(f"   ❌ ERROR: {e}")

async def main():
    """Main analysis function"""
    print("🚀 Debug Document Issue Analysis")
    print("=" * 60)
    
    # Analyze document content
    await analyze_document_content()
    
    # Test different models
    await test_different_models()
    
    print("\n💡 Analysis complete!")
    print("\nRecommendations:")
    print("1. If small portions work but large ones don't: Document size/complexity issue")
    print("2. If no code blocks version works: Code block parsing issue") 
    print("3. If other models work: phi3:mini specific issue")
    print("4. If nothing works: Fundamental Ollama/network issue")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️ Analysis interrupted by user")
    except Exception as e:
        print(f"\n❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
