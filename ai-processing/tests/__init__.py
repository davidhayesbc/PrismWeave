"""
Test suite for PrismWeave AI Processing module
Comprehensive tests for all components including models, processors, and utilities
"""

# Test configuration and utilities
import pytest
from pathlib import Path
import tempfile
import shutil
from typing import Dict, Any

def get_test_data_dir() -> Path:
    """Get the test data directory"""
    return Path(__file__).parent / "data"

def create_temp_config(config_data: Dict[str, Any]) -> Path:
    """Create a temporary config file for testing"""
    import yaml
    temp_dir = Path(tempfile.mkdtemp())
    config_path = temp_dir / "test_config.yaml"
    
    with open(config_path, 'w') as f:
        yaml.safe_dump(config_data, f)
    
    return config_path

def cleanup_temp_dir(temp_path: Path):
    """Clean up temporary directory"""
    if temp_path.exists():
        shutil.rmtree(temp_path)

# Common test fixtures that can be imported by other test modules
TEST_CONFIG = {
    'ollama': {
        'host': 'http://localhost:11434',
        'timeout': 30,
        'models': {
            'large': 'llama3.1:8b',
            'medium': 'phi3:mini',
            'small': 'phi3:mini',
            'embedding': 'nomic-embed-text'
        }
    },
    'processing': {
        'max_concurrent': 2,
        'chunk_size': 500,
        'chunk_overlap': 50,
        'min_chunk_size': 100,
        'summary_timeout': 60,
        'tagging_timeout': 30,
        'min_word_count': 10,
        'max_word_count': 10000
    },
    'vector': {
        'collection_name': 'test_documents',
        'persist_directory': './test_chroma_db',
        'max_results': 5,
        'similarity_threshold': 0.6
    },
    'log_level': 'DEBUG'
}

# Sample content for testing
SAMPLE_MARKDOWN = """# Test Document

This is a test document for the PrismWeave AI processing system.

## Overview

The document contains multiple sections to test various processing capabilities:

- Text analysis
- Chunking strategies
- Metadata extraction

## Code Examples

Here's some Python code:

```python
def hello_world():
    print("Hello, PrismWeave!")
    return True
```

## Conclusion

This document serves as a comprehensive test case for document processing.
"""

SAMPLE_PYTHON_CODE = """#!/usr/bin/env python3
\"\"\"
Sample Python module for testing code processing
\"\"\"

import os
import sys
from typing import List, Dict, Any

class TestClass:
    \"\"\"A test class for demonstration\"\"\"
    
    def __init__(self, name: str):
        self.name = name
        self._private_value = 0
    
    def get_name(self) -> str:
        \"\"\"Get the name\"\"\"
        return self.name
    
    def process_data(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        \"\"\"Process some data\"\"\"
        result = {}
        for item in data:
            if 'key' in item:
                result[item['key']] = item.get('value', None)
        return result

def main():
    \"\"\"Main function\"\"\"
    test_obj = TestClass("TestInstance")
    print(f"Created: {test_obj.get_name()}")
    
    sample_data = [
        {'key': 'item1', 'value': 'value1'},
        {'key': 'item2', 'value': 'value2'}
    ]
    
    result = test_obj.process_data(sample_data)
    print(f"Processed: {result}")

if __name__ == "__main__":
    main()
"""

SAMPLE_JAVASCRIPT = """/**
 * Sample JavaScript file for testing code processing
 */

class Calculator {
    constructor() {
        this.memory = 0;
    }
    
    add(a, b) {
        const result = a + b;
        this.memory = result;
        return result;
    }
    
    subtract(a, b) {
        const result = a - b;
        this.memory = result;
        return result;
    }
    
    getMemory() {
        return this.memory;
    }
    
    clear() {
        this.memory = 0;
    }
}

function calculateSum(numbers) {
    return numbers.reduce((sum, num) => sum + num, 0);
}

function processData(data) {
    const calculator = new Calculator();
    const results = [];
    
    for (const item of data) {
        if (item.operation === 'add') {
            results.push(calculator.add(item.a, item.b));
        } else if (item.operation === 'subtract') {
            results.push(calculator.subtract(item.a, item.b));
        }
    }
    
    return {
        results: results,
        finalMemory: calculator.getMemory()
    };
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { Calculator, calculateSum, processData };
}
"""
