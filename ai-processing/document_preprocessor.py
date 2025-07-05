#!/usr/bin/env python3
"""
Production Fix: Content Preprocessor for PrismWeave
Addresses the document complexity issues that cause timeouts with phi3:mini
"""

import re
import hashlib
from typing import Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class ProcessingMetrics:
    """Metrics for document processing"""
    original_size: int
    processed_size: int
    code_blocks_removed: int
    complexity_score: float
    estimated_tokens: int
    processing_time_estimate: float

class DocumentPreprocessor:
    """
    Preprocesses documents to make them more suitable for LLM processing
    Especially important for phi3:mini which struggles with complex formatting
    """
    
    def __init__(self, max_chars: int = 4000, max_tokens: int = 1000):
        self.max_chars = max_chars
        self.max_tokens = max_tokens
        
        # Patterns that cause issues with phi3:mini
        self.problematic_patterns = [
            r'```[^`]*```',           # Code blocks
            r'`{4,}',                 # Nested backticks
            r'\n\s*\n\s*\n',         # Multiple consecutive newlines
            r'\[([^\]]{100,})\]',     # Very long link text
            r'#+\s+.{100,}',          # Very long headers
        ]
    
    def analyze_complexity(self, content: str) -> ProcessingMetrics:
        """Analyze document complexity to predict processing difficulty"""
        
        # Count problematic elements
        code_blocks = len(re.findall(r'```[^`]*```', content))
        nested_backticks = len(re.findall(r'`{3,}', content))
        long_lines = len([line for line in content.split('\n') if len(line) > 200])
        special_chars = len(re.findall(r'[^\x00-\x7F]', content))
        
        # Calculate complexity score (0-10, where 10 is very complex)
        complexity_score = min(10, (
            code_blocks * 0.5 +           # Code blocks add complexity
            nested_backticks * 0.3 +      # Nested backticks
            long_lines * 0.2 +             # Long lines
            special_chars * 0.01 +         # Special characters
            len(content) / 2000            # Size factor
        ))
        
        # Estimate tokens (rough approximation: 4 chars per token)
        estimated_tokens = len(content) // 4
        
        # Estimate processing time based on complexity and size
        base_time = len(content) / 200  # Base: 200 chars per second
        complexity_multiplier = 1 + (complexity_score / 5)  # More complex = slower
        processing_time_estimate = base_time * complexity_multiplier
        
        return ProcessingMetrics(
            original_size=len(content),
            processed_size=len(content),  # Will be updated after processing
            code_blocks_removed=0,
            complexity_score=complexity_score,
            estimated_tokens=estimated_tokens,
            processing_time_estimate=processing_time_estimate
        )
    
    def should_preprocess(self, content: str) -> bool:
        """Determine if content needs preprocessing"""
        metrics = self.analyze_complexity(content)
        
        return (
            metrics.original_size > self.max_chars or
            metrics.estimated_tokens > self.max_tokens or
            metrics.complexity_score > 6.0
        )
    
    def preprocess_for_phi3_mini(self, content: str, preserve_meaning: bool = True) -> Tuple[str, ProcessingMetrics]:
        """
        Preprocess content specifically for phi3:mini compatibility
        
        Args:
            content: Original document content
            preserve_meaning: If True, replace code blocks with summaries instead of removing
            
        Returns:
            Tuple of (processed_content, metrics)
        """
        
        metrics = self.analyze_complexity(content)
        processed = content
        code_blocks_removed = 0
        
        if not self.should_preprocess(content):
            return processed, metrics
        
        # Step 1: Handle code blocks (biggest issue for phi3:mini)
        if preserve_meaning:
            # Replace code blocks with simplified descriptions
            def replace_code_block(match):
                nonlocal code_blocks_removed
                code_blocks_removed += 1
                code_content = match.group(0)
                
                # Try to identify the language
                lang_match = re.match(r'```(\w+)', code_content)
                language = lang_match.group(1) if lang_match else "code"
                
                # Count lines to give size indication
                lines = code_content.count('\n')
                
                return f"[{language.upper()} CODE BLOCK: {lines} lines]"
        else:
            # Simply remove code blocks
            processed = re.sub(r'```[^`]*```', '[CODE BLOCK REMOVED]', processed)
            code_blocks_removed = len(re.findall(r'```[^`]*```', content))
        
        if preserve_meaning:
            processed = re.sub(r'```[^`]*```', replace_code_block, processed)
        
        # Step 2: Clean up excessive whitespace
        processed = re.sub(r'\n\s*\n\s*\n+', '\n\n', processed)
        
        # Step 3: Simplify very long headers
        processed = re.sub(r'(#+\s+)(.{80})(.{20,})', r'\1\2...', processed)
        
        # Step 4: Truncate very long link texts
        processed = re.sub(r'\[([^\]]{80})([^\]]{20,})\]', r'[\1...] ', processed)
        
        # Step 5: If still too long, intelligently truncate
        if len(processed) > self.max_chars:
            processed = self._intelligent_truncate(processed, self.max_chars)
        
        # Update metrics
        metrics.processed_size = len(processed)
        metrics.code_blocks_removed = code_blocks_removed
        metrics.estimated_tokens = len(processed) // 4
        
        # Recalculate complexity for processed content
        new_complexity = self.analyze_complexity(processed)
        metrics.complexity_score = new_complexity.complexity_score
        metrics.processing_time_estimate = new_complexity.processing_time_estimate
        
        return processed, metrics
    
    def _intelligent_truncate(self, content: str, max_length: int) -> str:
        """Intelligently truncate content at natural break points"""
        
        if len(content) <= max_length:
            return content
        
        # Try to truncate at paragraph boundaries
        paragraphs = content.split('\n\n')
        truncated = ""
        
        for paragraph in paragraphs:
            if len(truncated) + len(paragraph) + 2 <= max_length:
                truncated += paragraph + '\n\n'
            else:
                break
        
        # If that doesn't work, truncate at sentence boundaries
        if not truncated.strip():
            sentences = content.split('. ')
            truncated = ""
            
            for sentence in sentences:
                if len(truncated) + len(sentence) + 2 <= max_length:
                    truncated += sentence + '. '
                else:
                    break
        
        # Last resort: hard truncate with ellipsis
        if not truncated.strip():
            truncated = content[:max_length - 3] + "..."
        
        return truncated.strip()
    
    def create_processing_summary(self, content: str, metrics: ProcessingMetrics) -> str:
        """Create a summary of what processing was done"""
        
        summary_parts = []
        
        if metrics.code_blocks_removed > 0:
            summary_parts.append(f"Removed {metrics.code_blocks_removed} code blocks")
        
        if metrics.processed_size < metrics.original_size:
            reduction = metrics.original_size - metrics.processed_size
            percentage = (reduction / metrics.original_size) * 100
            summary_parts.append(f"Reduced size by {reduction} chars ({percentage:.1f}%)")
        
        summary_parts.append(f"Complexity score: {metrics.complexity_score:.1f}/10")
        summary_parts.append(f"Estimated processing time: {metrics.processing_time_estimate:.1f}s")
        
        return "; ".join(summary_parts)

# Integration function for PrismWeave
def preprocess_document_for_ai(content: str, model_name: str = "phi3:mini") -> Tuple[str, str]:
    """
    Main integration function for PrismWeave
    
    Args:
        content: Original document content
        model_name: Name of the model that will process the content
        
    Returns:
        Tuple of (processed_content, processing_summary)
    """
    
    preprocessor = DocumentPreprocessor()
    
    # Adjust settings based on model
    if "phi3" in model_name.lower():
        # phi3:mini needs more aggressive preprocessing
        preprocessor.max_chars = 3000
        preprocessor.max_tokens = 800
    elif "qwen" in model_name.lower():
        # Qwen models can handle more complexity
        preprocessor.max_chars = 6000
        preprocessor.max_tokens = 1500
    else:
        # Conservative defaults for unknown models
        preprocessor.max_chars = 4000
        preprocessor.max_tokens = 1000
    
    # Check if preprocessing is needed
    if not preprocessor.should_preprocess(content):
        return content, "No preprocessing needed"
    
    # Preprocess the content
    processed_content, metrics = preprocessor.preprocess_for_phi3_mini(content)
    summary = preprocessor.create_processing_summary(content, metrics)
    
    return processed_content, summary

# Test the preprocessor
async def test_preprocessor():
    """Test the preprocessor with the problematic document"""
    print("🔧 Testing Document Preprocessor")
    print("=" * 50)
    
    from pathlib import Path
    doc_path = Path("d:/source/PrismWeaveDocs/documents/tech/2025-06-22-building-industrial-strength-software-without-unit.md")
    
    with open(doc_path, 'r', encoding='utf-8') as f:
        original_content = f.read()
    
    print(f"📄 Original document: {len(original_content)} characters")
    
    # Test preprocessing
    processed_content, summary = preprocess_document_for_ai(original_content, "phi3:mini")
    
    print(f"📄 Processed document: {len(processed_content)} characters")
    print(f"📊 Processing summary: {summary}")
    
    # Test with optimized client
    from test_optimized_client import OptimizedOllamaClient
    
    async with OptimizedOllamaClient() as client:
        print(f"\n🧪 Testing processed content with phi3:mini...")
        
        try:
            import time
            start_time = time.time()
            
            result = await asyncio.wait_for(
                client.generate(
                    model="phi3:mini",
                    prompt=f"Summarize this document in 2-3 sentences:\n\n{processed_content}",
                    system="You are a document summarization expert."
                ),
                timeout=45.0
            )
            
            end_time = time.time()
            print(f"   ✅ SUCCESS in {end_time - start_time:.2f}s")
            print(f"   Summary: '{result.response}'")
            
        except Exception as e:
            print(f"   ❌ ERROR: {e}")

if __name__ == "__main__":
    import asyncio
    try:
        asyncio.run(test_preprocessor())
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
