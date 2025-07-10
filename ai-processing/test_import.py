#!/usr/bin/env python3
"""
Test script to verify imports work correctly
"""
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

print(f"Python path: {sys.path[:3]}")
print(f"Looking for modules in: {src_path}")

try:
    # Test direct import
    sys.path.insert(0, str(src_path / "processors"))
    import langchain_document_processor
    print("✅ Direct import successful")
    
    # Test class import
    from langchain_document_processor import LangChainDocumentProcessor
    print("✅ Class import successful")
    
    # Test instantiation
    processor = LangChainDocumentProcessor()
    print("✅ Processor instantiation successful")
    
except Exception as e:
    print(f"❌ Import failed: {e}")
    import traceback
    traceback.print_exc()
