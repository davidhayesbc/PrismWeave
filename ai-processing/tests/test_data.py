"""
Test data and fixtures for PrismWeave AI processing tests
"""

# Create test data directory and sample files
TEST_DATA_DIR = "test_data"

# Sample documents for testing
SAMPLE_DOCUMENTS = {
    "simple_markdown": {
        "filename": "simple.md",
        "content": """# Simple Document

This is a simple markdown document for testing.

## Section 1

Content in section 1.

## Section 2

Content in section 2.
"""
    },
    
    "complex_markdown": {
        "filename": "complex.md", 
        "content": """# Complex Document

This document contains various markdown elements.

## Code Examples

Here's some Python code:

```python
def hello_world():
    print("Hello, PrismWeave!")
    return True
```

## Lists

### Ordered List
1. First item
2. Second item

### Unordered List
- Item A
- Item B

## Links and Images

[PrismWeave](https://github.com/davidhayesbc/PrismWeave)

## Tables

| Name | Age |
|------|-----|
| Alice | 30 |
| Bob | 25 |

## Conclusion

This document demonstrates various markdown features.
"""
    },
    
    "python_code": {
        "filename": "sample.py",
        "content": """#!/usr/bin/env python3
\"\"\"
Sample Python module for testing code processing
\"\"\"

import os
from typing import List, Dict, Any

class DocumentProcessor:
    \"\"\"Process documents for PrismWeave\"\"\"
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self._cache = {}
    
    def process_file(self, file_path: str) -> Dict[str, Any]:
        \"\"\"Process a single file\"\"\"
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        result = self._analyze_content(content)
        self._cache[file_path] = result
        return result
    
    def _analyze_content(self, content: str) -> Dict[str, Any]:
        \"\"\"Analyze content and extract metadata\"\"\"
        lines = content.split('\\n')
        word_count = len(content.split())
        
        return {
            'line_count': len(lines),
            'word_count': word_count,
            'char_count': len(content)
        }

def main():
    \"\"\"Main function for CLI usage\"\"\"
    config = {}
    processor = DocumentProcessor(config)
    print("DocumentProcessor initialized")

if __name__ == "__main__":
    main()
"""
    },
    
    "javascript_code": {
        "filename": "sample.js",
        "content": """/**
 * Sample JavaScript file for testing code processing
 */

class DocumentManager {
    constructor(config = {}) {
        this.config = {
            maxFileSize: 10 * 1024 * 1024, // 10MB
            allowedTypes: ['md', 'txt', 'js', 'py'],
            ...config
        };
        this.cache = new Map();
    }
    
    /**
     * Process a document file
     * @param {File} file - The file to process
     * @returns {Promise<Object>} Processing result
     */
    async processDocument(file) {
        if (!this.isValidFile(file)) {
            throw new Error(`Invalid file: ${file.name}`);
        }
        
        const content = await this.readFile(file);
        const analysis = this.analyzeContent(content);
        
        const result = {
            file: file.name,
            size: file.size,
            content: content,
            analysis: analysis,
            processedAt: new Date().toISOString()
        };
        
        this.cache.set(file.name, result);
        return result;
    }
    
    /**
     * Validate file type and size
     */
    isValidFile(file) {
        if (file.size > this.config.maxFileSize) {
            return false;
        }
        
        const extension = file.name.split('.').pop().toLowerCase();
        return this.config.allowedTypes.includes(extension);
    }
    
    /**
     * Read file content
     */
    async readFile(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => resolve(reader.result);
            reader.onerror = () => reject(new Error('Failed to read file'));
            reader.readAsText(file);
        });
    }
    
    /**
     * Analyze document content
     */
    analyzeContent(content) {
        const lines = content.split('\\n');
        const words = content.split(/\\s+/).filter(word => word.length > 0);
        
        return {
            lineCount: lines.length,
            wordCount: words.length,
            characterCount: content.length
        };
    }
}

// Export for Node.js
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { DocumentManager };
}
"""
    },
    
    "json_config": {
        "filename": "config.json",
        "content": """{
  "ollama": {
    "host": "http://localhost:11434",
    "timeout": 60,
    "models": {
      "large": "llama3.1:8b",
      "medium": "phi3:mini",
      "small": "phi3:mini",
      "embedding": "nomic-embed-text"
    }
  },
  "processing": {
    "max_concurrent": 3,
    "chunk_size": 1000,
    "chunk_overlap": 200,
    "min_chunk_size": 100,
    "summary_timeout": 120,
    "tagging_timeout": 60,
    "categorization_timeout": 30,
    "min_word_count": 50,
    "max_word_count": 50000,
    "max_summary_length": 500,
    "max_tags": 10
  },
  "vector": {
    "collection_name": "documents",
    "persist_directory": "./chroma_db",
    "embedding_function": "sentence-transformers",
    "max_results": 10,
    "similarity_threshold": 0.7
  },
  "log_level": "INFO",
  "log_file": null
}"""
    },
    
    "yaml_config": {
        "filename": "config.yaml",
        "content": """# PrismWeave AI Processing Configuration

ollama:
  host: http://localhost:11434
  timeout: 60
  models:
    large: llama3.1:8b
    medium: phi3:mini
    small: phi3:mini
    embedding: nomic-embed-text

processing:
  max_concurrent: 3
  chunk_size: 1000
  chunk_overlap: 200
  min_chunk_size: 100
  summary_timeout: 120
  tagging_timeout: 60
  categorization_timeout: 30
  min_word_count: 50
  max_word_count: 50000
  max_summary_length: 500
  max_tags: 10

vector:
  collection_name: documents
  persist_directory: ./chroma_db
  embedding_function: sentence-transformers
  max_results: 10
  similarity_threshold: 0.7

log_level: INFO
log_file: null
"""
    }
}

# Error test cases
ERROR_TEST_CASES = {
    "invalid_encoding": {
        "filename": "invalid.txt",
        "content": b"\\xff\\xfe\\x00Invalid encoding content"
    },
    
    "binary_file": {
        "filename": "binary.bin",
        "content": b"\\x00\\x01\\x02\\x03\\x04\\x05\\x06\\x07\\x08\\x09"
    },
    
    "empty_file": {
        "filename": "empty.txt",
        "content": ""
    },
    
    "very_long_line": {
        "filename": "long_line.txt", 
        "content": "A" * 10000 + "\\nNormal line\\n" + "B" * 10000
    }
}

# Performance test data (disabled for faster tests)
# Uncomment and modify for performance testing when needed
PERFORMANCE_TEST_DATA = {
    # "large_markdown": {
    #     "filename": "large.md", 
    #     "content": "# Large Test Document\n\nSmall test content for performance.\n"
    # },
    # 
    # "massive_code": {
    #     "filename": "massive.py",
    #     "content": "# Small test file\nprint('test')\n"
    # }
}

def create_test_files():
    """Create test files in test_data directory"""
    import os
    from pathlib import Path
    
    test_dir = Path(TEST_DATA_DIR)
    test_dir.mkdir(exist_ok=True)
    
    # Create regular test files
    for doc_id, doc_data in SAMPLE_DOCUMENTS.items():
        file_path = test_dir / doc_data["filename"]
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(doc_data["content"])
    
    # Create error test files
    for error_id, error_data in ERROR_TEST_CASES.items():
        file_path = test_dir / error_data["filename"]
        if isinstance(error_data["content"], bytes):
            with open(file_path, 'wb') as f:
                f.write(error_data["content"])
        else:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(error_data["content"])
    
    print(f"Created test files in {test_dir}")

def cleanup_test_files():
    """Remove test files"""
    import shutil
    from pathlib import Path
    
    test_dir = Path(TEST_DATA_DIR)
    if test_dir.exists():
        shutil.rmtree(test_dir)
        print(f"Cleaned up {test_dir}")

if __name__ == "__main__":
    create_test_files()
