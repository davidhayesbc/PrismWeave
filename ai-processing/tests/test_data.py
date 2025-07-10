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

And some JavaScript:

```javascript
function greet(name) {
    console.log(`Hello, ${name}!`);
}
```

## Lists

### Ordered List
1. First item
2. Second item
3. Third item

### Unordered List
- Item A
- Item B
- Item C

## Links and Images

[PrismWeave](https://github.com/davidhayesbc/PrismWeave)

![Sample Image](https://example.com/image.png)

## Tables

| Name | Age | City |
|------|-----|------|
| Alice | 30 | New York |
| Bob | 25 | Los Angeles |

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
import sys
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class DocumentProcessor:
    \"\"\"Process documents for PrismWeave\"\"\"
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self._cache = {}
    
    def process_file(self, file_path: str) -> Dict[str, Any]:
        \"\"\"Process a single file\"\"\"
        logger.info(f"Processing file: {file_path}")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            result = self._analyze_content(content)
            self._cache[file_path] = result
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to process {file_path}: {e}")
            raise
    
    def _analyze_content(self, content: str) -> Dict[str, Any]:
        \"\"\"Analyze content and extract metadata\"\"\"
        lines = content.split('\\n')
        word_count = len(content.split())
        
        return {
            'line_count': len(lines),
            'word_count': word_count,
            'char_count': len(content),
            'estimated_reading_time': max(1, word_count // 200)
        }
    
    def batch_process(self, file_paths: List[str]) -> List[Dict[str, Any]]:
        \"\"\"Process multiple files\"\"\"
        results = []
        
        for file_path in file_paths:
            try:
                result = self.process_file(file_path)
                results.append(result)
            except Exception as e:
                logger.warning(f"Skipping {file_path}: {e}")
                continue
        
        return results
    
    def get_cache_stats(self) -> Dict[str, int]:
        \"\"\"Get cache statistics\"\"\"
        return {
            'cached_files': len(self._cache),
            'total_cache_size': sum(
                result['char_count'] for result in self._cache.values()
            )
        }

def main():
    \"\"\"Main function for CLI usage\"\"\"
    import argparse
    
    parser = argparse.ArgumentParser(description='Process documents')
    parser.add_argument('files', nargs='+', help='Files to process')
    parser.add_argument('--config', help='Configuration file')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.basicConfig(level=logging.INFO)
    
    config = {}
    if args.config:
        import json
        with open(args.config, 'r') as f:
            config = json.load(f)
    
    processor = DocumentProcessor(config)
    results = processor.batch_process(args.files)
    
    for i, result in enumerate(results):
        print(f"File {i+1}: {result}")

if __name__ == "__main__":
    main()
"""
    },
    
    "javascript_code": {
        "filename": "sample.js",
        "content": """/**
 * Sample JavaScript file for testing code processing
 * PrismWeave Document Management System
 */

class DocumentManager {
    constructor(config = {}) {
        this.config = {
            maxFileSize: 10 * 1024 * 1024, // 10MB
            allowedTypes: ['md', 'txt', 'js', 'py'],
            processingTimeout: 30000,
            ...config
        };
        this.cache = new Map();
        this.processing = new Set();
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
        
        if (this.processing.has(file.name)) {
            throw new Error(`File already being processed: ${file.name}`);
        }
        
        this.processing.add(file.name);
        
        try {
            const content = await this.readFile(file);
            const analysis = this.analyzeContent(content);
            const metadata = this.extractMetadata(file, content);
            
            const result = {
                file: file.name,
                size: file.size,
                content: content,
                analysis: analysis,
                metadata: metadata,
                processedAt: new Date().toISOString()
            };
            
            this.cache.set(file.name, result);
            return result;
            
        } finally {
            this.processing.delete(file.name);
        }
    }
    
    /**
     * Validate file type and size
     * @param {File} file - File to validate
     * @returns {boolean} Whether file is valid
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
     * @param {File} file - File to read
     * @returns {Promise<string>} File content
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
     * @param {string} content - Document content
     * @returns {Object} Content analysis
     */
    analyzeContent(content) {
        const lines = content.split('\\n');
        const words = content.split(/\\s+/).filter(word => word.length > 0);
        const characters = content.length;
        
        // Simple sentiment analysis
        const positiveWords = ['good', 'great', 'excellent', 'amazing', 'wonderful'];
        const negativeWords = ['bad', 'terrible', 'awful', 'horrible', 'worst'];
        
        const positiveCount = positiveWords.reduce((count, word) => 
            count + (content.toLowerCase().match(new RegExp(word, 'g')) || []).length, 0);
        const negativeCount = negativeWords.reduce((count, word) => 
            count + (content.toLowerCase().match(new RegExp(word, 'g')) || []).length, 0);
        
        return {
            lineCount: lines.length,
            wordCount: words.length,
            characterCount: characters,
            averageWordsPerLine: Math.round(words.length / lines.length),
            estimatedReadingTime: Math.ceil(words.length / 200), // 200 WPM
            sentiment: {
                positive: positiveCount,
                negative: negativeCount,
                score: positiveCount - negativeCount
            }
        };
    }
    
    /**
     * Extract metadata from file and content
     * @param {File} file - Original file
     * @param {string} content - File content
     * @returns {Object} Extracted metadata
     */
    extractMetadata(file, content) {
        const metadata = {
            filename: file.name,
            fileSize: file.size,
            fileType: file.type,
            lastModified: new Date(file.lastModified).toISOString(),
            encoding: 'utf-8'
        };
        
        // Extract title from content (first line or first header)
        const lines = content.split('\\n');
        const firstLine = lines[0]?.trim();
        
        if (firstLine?.startsWith('#')) {
            metadata.title = firstLine.replace(/^#+\\s*/, '');
        } else if (firstLine) {
            metadata.title = firstLine.substring(0, 100); // First 100 chars
        }
        
        // Extract headers (markdown style)
        const headers = [];
        lines.forEach((line, index) => {
            const match = line.match(/^(#+)\\s*(.+)$/);
            if (match) {
                headers.push({
                    level: match[1].length,
                    text: match[2],
                    line: index + 1
                });
            }
        });
        
        metadata.headers = headers;
        
        // Extract links
        const linkRegex = /\\[([^\\]]+)\\]\\(([^)]+)\\)/g;
        const links = [];
        let match;
        
        while ((match = linkRegex.exec(content)) !== null) {
            links.push({
                text: match[1],
                url: match[2]
            });
        }
        
        metadata.links = links;
        
        return metadata;
    }
    
    /**
     * Get processing statistics
     * @returns {Object} Processing stats
     */
    getStats() {
        return {
            cachedDocuments: this.cache.size,
            processingDocuments: this.processing.size,
            totalCacheSize: Array.from(this.cache.values())
                .reduce((total, doc) => total + doc.size, 0)
        };
    }
    
    /**
     * Clear cache
     */
    clearCache() {
        this.cache.clear();
    }
}

// Utility functions
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Export for Node.js
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        DocumentManager,
        formatFileSize,
        debounce
    };
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

# Performance test data
PERFORMANCE_TEST_DATA = {
    "large_markdown": {
        "filename": "large.md",
        "content": """# Large Test Document

This is a large document for performance testing.

""" + "## Section {i}\\n\\nContent for section {i}. " * 1000 + """

## Conclusion

This document contains many sections for testing performance.
"""
    },
    
    "massive_code": {
        "filename": "massive.py",
        "content": """#!/usr/bin/env python3
# Large Python file for performance testing

""" + """
def function_{i}():
    \"\"\"Function number {i}\"\"\"
    return {i}

class Class{i}:
    \"\"\"Class number {i}\"\"\"
    def __init__(self):
        self.value = {i}
    
    def method(self):
        return self.value * 2

""".replace("{i}", "1") * 500
    }
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
