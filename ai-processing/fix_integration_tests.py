#!/usr/bin/env python3
"""
Script to fix all remaining API mismatches in integration tests
"""

import re
from pathlib import Path

def fix_integration_tests():
    test_file = Path("tests/test_integration.py")
    content = test_file.read_text(encoding='utf-8')
    
    # Fix constructor calls - remove ollama_client parameter
    content = re.sub(
        r'LangChainDocumentProcessor\(\s*config=integration_config,\s*ollama_client=mock_ollama_client\s*\)',
        'LangChainDocumentProcessor(\n            config=integration_config\n        )',
        content
    )
    
    # Fix process_document calls - use Path objects instead of strings
    content = re.sub(
        r'await processor\.process_document\(str\(([^)]+)\)\)',
        r'await processor.process_document(\1)',
        content
    )
    
    content = re.sub(
        r'processor\.process_document\(str\(([^)]+)\)\)',
        r'processor.process_document(\1)',
        content
    )
    
    # Fix literal string file paths to Path objects
    content = re.sub(
        r'await processor\.process_document\("([^"]+)"\)',
        r'await processor.process_document(Path("\1"))',
        content
    )
    
    # Fix chunk attribute access from .content to .page_content
    content = re.sub(
        r'chunk\.content',
        'chunk.page_content',
        content
    )
    
    # Fix metadata attribute access from dot notation to dictionary access
    content = re.sub(
        r'result\.metadata\.(\w+)',
        r"result.metadata['\1']",
        content
    )
    
    # Fix chunk_type references (these don't exist in LangChain Documents)
    content = re.sub(
        r'chunk\.chunk_type',
        'chunk.metadata.get("chunk_type", "unknown")',
        content
    )
    
    # Remove invalid ollama client call parameters
    content = re.sub(
        r'max_tokens=\d+,?\s*',
        '',
        content
    )
    
    content = re.sub(
        r'prompt="[^"]*",?\s*',
        '',
        content
    )
    
    # Fix embed call parameters
    content = re.sub(
        r'embed\(\s*model=([^,]+),\s*\)',
        r'embed(\1, input_text="Test text for embedding")',
        content
    )
    
    # Write the fixed content back
    test_file.write_text(content, encoding='utf-8')
    print("Fixed integration tests API mismatches")

if __name__ == "__main__":
    fix_integration_tests()
