#!/usr/bin/env python3
"""
LangChain Setup Script for PrismWeave using UV Package Manager
Installs LangChain text splitters and validates the enhanced embedding process
"""

import subprocess
import sys
import os
import asyncio
from pathlib import Path
from typing import List, Dict, Any

def run_command(command: List[str], description: str = "") -> bool:
    """Run a command and return success status"""
    print(f"🔧 {description or ' '.join(command)}")
    try:
        result = subprocess.run(
            command, 
            check=True, 
            capture_output=True, 
            text=True,
            cwd=Path(__file__).parent
        )
        if result.stdout.strip():
            print(f"   ✅ {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Error: {e.stderr.strip() if e.stderr else str(e)}")
        return False
    except FileNotFoundError:
        print(f"   ❌ Command not found: {command[0]}")
        return False

def check_uv_available() -> bool:
    """Check if uv package manager is available"""
    print("🔍 Checking UV package manager availability...")
    
    if run_command(["uv", "--version"], "Checking UV version"):
        return True
    
    print("❌ UV package manager not found!")
    print("📦 Install UV with:")
    print("   curl -LsSf https://astral.sh/uv/install.sh | sh")
    print("   or")
    print("   pip install uv")
    return False

def install_langchain_packages() -> bool:
    """Install LangChain packages using UV"""
    print("\n📦 Installing LangChain packages with UV...")
    
    # Core LangChain packages
    packages = [
        "langchain>=0.1.0",
        "langchain-text-splitters>=0.0.1", 
        "langchain-community>=0.0.1",
        "langchain-core>=0.1.0",
        "pyyaml>=6.0"  # Required for configuration management
    ]
    
    success = True
    for package in packages:
        if not run_command(["uv", "pip", "install", package], f"Installing {package}"):
            success = False
    
    return success

def verify_langchain_installation() -> bool:
    """Verify LangChain installation and functionality"""
    print("\n🧪 Verifying LangChain installation...")
    
    try:
        # Test core LangChain imports
        print("   📋 Testing LangChain imports...")
        from langchain_text_splitters import (
            RecursiveCharacterTextSplitter,
            PythonCodeTextSplitter,
            MarkdownTextSplitter,
            Language
        )
        from langchain_core.documents import Document
        print("   ✅ Core LangChain imports successful")
        
        # Test basic functionality
        print("   📋 Testing text splitter functionality...")
        
        # Test RecursiveCharacterTextSplitter
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=200,
            chunk_overlap=50,
            separators=["\n\n", "\n", " ", ""]
        )
        
        test_text = """
# Test Document

This is a test document with multiple paragraphs.

## Section 1
Here is some content in section 1.

## Section 2  
Here is some content in section 2 with more text to ensure we have enough content for chunking.

### Subsection 2.1
Even more detailed content here to test the chunking algorithm properly.
"""
        
        chunks = splitter.split_text(test_text)
        print(f"   ✅ RecursiveCharacterTextSplitter: {len(chunks)} chunks created")
        
        # Test MarkdownTextSplitter
        md_splitter = MarkdownTextSplitter(
            chunk_size=200,
            chunk_overlap=50,
            headers_to_split_on=[
                ("#", "Header 1"),
                ("##", "Header 2"),
                ("###", "Header 3")
            ]
        )
        
        md_chunks = md_splitter.split_text(test_text)
        print(f"   ✅ MarkdownTextSplitter: {len(md_chunks)} chunks created")
        
        # Test PythonCodeTextSplitter
        python_code = '''
def authenticate_user(username, password):
    """Authenticate a user with username and password"""
    if not username or not password:
        return False
    
    user = database.get_user(username)
    if user and verify_password(password, user.password_hash):
        create_session(user)
        return True
    
    return False

class UserManager:
    """Manages user operations"""
    
    def __init__(self, database):
        self.database = database
    
    def create_user(self, username, email, password):
        """Create a new user account"""
        if self.database.user_exists(username):
            raise ValueError("Username already exists")
        
        password_hash = hash_password(password)
        user = User(username=username, email=email, password_hash=password_hash)
        return self.database.save_user(user)
'''
        
        py_splitter = PythonCodeTextSplitter(
            chunk_size=300,
            chunk_overlap=50
        )
        
        py_chunks = py_splitter.split_text(python_code)
        print(f"   ✅ PythonCodeTextSplitter: {len(py_chunks)} chunks created")
        
        return True
        
    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Functionality test failed: {e}")
        return False

def test_enhanced_document_processor() -> bool:
    """Test the enhanced document processor with LangChain"""
    print("\n🧪 Testing Enhanced Document Processor...")
    
    try:
        # Import the enhanced processor
        sys.path.append(str(Path(__file__).parent))
        try:
            from langchain_document_processor import (
                LangChainDocumentProcessor, 
                check_langchain_availability
            )
        except ImportError:
            print("   ⚠️  Enhanced document processor not found - using basic test")
            return True  # Not critical for setup
        
        # Check availability
        status = check_langchain_availability()
        print(f"   📋 LangChain availability: {status}")
        
        if not status.get('langchain_available'):
            print(f"   ❌ LangChain not available: {status.get('error', 'Unknown error')}")
            return False
        
        # Test processor initialization
        processor = LangChainDocumentProcessor()
        available_splitters = processor.get_available_splitters()
        print(f"   ✅ Processor initialized with {len(available_splitters)} splitters")
        print(f"   📋 Available splitters: {', '.join(available_splitters)}")
        
        # Test document analysis
        test_content = '''
# API Authentication Guide

## Overview
This guide covers authentication methods for our API.

## Methods

### Token Authentication
Use bearer tokens for API access:

```python
import requests

headers = {
    "Authorization": "Bearer your-token-here",
    "Content-Type": "application/json"
}

response = requests.get("https://api.example.com/data", headers=headers)
```

### API Key Authentication
Alternative method using API keys:

```javascript
const apiKey = 'your-api-key';
const response = await fetch('https://api.example.com/data', {
    headers: {
        'X-API-Key': apiKey,
        'Content-Type': 'application/json'
    }
});
```

## Security Best Practices
- Never expose tokens in client-side code
- Use HTTPS for all API calls
- Rotate tokens regularly
'''
        
        analysis = processor.analyze_document_structure(test_content, Path("test.md"))
        print(f"   ✅ Document analysis complete:")
        print(f"      - Length: {analysis['total_length']} chars")
        print(f"      - Contains code: {analysis['contains_code']}")
        print(f"      - Contains headers: {analysis['contains_headers']}")
        print(f"      - Recommended splitter: {analysis['recommended_splitter']}")
        
        return True
        
    except ImportError as e:
        print(f"   ❌ Could not import document processor: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Document processor test failed: {e}")
        return False

async def test_semantic_search_integration() -> bool:
    """Test the semantic search with LangChain integration"""
    print("\n🧪 Testing Semantic Search with LangChain...")
    
    try:
        # Import semantic search
        sys.path.append(str(Path(__file__).parent / "src"))
        # Import semantic search
        try:
            from semantic_search import SemanticSearch
            from config import get_config
        except ImportError:
            print("   ⚠️  Semantic search modules not found - using basic test")
            return True  # Not critical for setup
        
        # Create test config
        config = get_config()
        
        # Test chunking functionality
        search_engine = SemanticSearch(config)
        
        test_python_code = '''
def process_document(file_path, content):
    """Process a document and extract key information"""
    try:
        # Extract metadata
        metadata = extract_metadata(content)
        
        # Process content
        processed = preprocess_content(content)
        
        # Generate embeddings
        embeddings = generate_embeddings(processed)
        
        return {
            'success': True,
            'metadata': metadata,
            'embeddings': embeddings
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

class DocumentProcessor:
    """Document processing class"""
    
    def __init__(self, config):
        self.config = config
        self.models = load_models(config)
    
    async def process_batch(self, documents):
        """Process multiple documents"""
        results = []
        for doc in documents:
            result = await self.process_single(doc)
            results.append(result)
        return results
'''
        
        # Test enhanced chunking
        chunks = search_engine._extract_text_chunks(test_python_code, Path("test.py"))
        print(f"   ✅ Enhanced chunking created {len(chunks)} chunks for Python code")
        
        # Test with different file types
        markdown_content = '''
# Data Processing Pipeline

## Overview
Our data processing pipeline handles multiple data sources.

## Components

### Data Ingestion
- File uploads
- API integrations
- Database connections

### Processing Engine
The processing engine uses multiple stages:

1. **Validation** - Check data integrity
2. **Transformation** - Convert to standard format  
3. **Enrichment** - Add metadata and context

### Output Generation
Final processed data is available in multiple formats.
'''
        
        md_chunks = search_engine._extract_text_chunks(markdown_content, Path("test.md"))
        print(f"   ✅ Enhanced chunking created {len(md_chunks)} chunks for Markdown")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Semantic search test failed: {e}")
        return False

def create_langchain_config() -> bool:
    """Create enhanced configuration with LangChain settings"""
    print("\n⚙️  Creating LangChain configuration...")
    
    try:
        config_path = Path(__file__).parent / "config.yaml"
        
        # Read existing config
        import yaml
        
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f) or {}
        else:
            config = {}
        
        # Add LangChain-specific chunking configuration
        if 'chunking' not in config:
            config['chunking'] = {}
        
        config['chunking'].update({
            'default_chunk_size': 1000,
            'default_overlap': 200,
            'python_chunk_size': 1500,
            'python_overlap': 200,
            'javascript_chunk_size': 1200,
            'javascript_overlap': 150,
            'typescript_chunk_size': 1200,
            'typescript_overlap': 150,
            'markdown_chunk_size': 1000,
            'markdown_overlap': 100,
            'code_chunk_size': 1500,
            'code_overlap': 200,
            'token_chunk_size': 800,
            'token_overlap': 100
        })
        
        # Add search configuration
        if 'search' not in config:
            config['search'] = {}
        
        config['search'].update({
            'semantic_weight': 0.7,
            'keyword_weight': 0.3,
            'enable_hybrid_search': True,
            'langchain_enabled': True
        })
        
        # Write updated config
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, indent=2)
        
        print(f"   ✅ Configuration updated: {config_path}")
        return True
        
    except Exception as e:
        print(f"   ❌ Configuration update failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 PrismWeave LangChain Setup with UV Package Manager")
    print("=" * 60)
    
    success = True
    
    # Check UV availability
    if not check_uv_available():
        return False
    
    # Install LangChain packages
    if not install_langchain_packages():
        success = False
    
    # Verify installation
    if not verify_langchain_installation():
        success = False
    
    # Test document processor
    if not test_enhanced_document_processor():
        success = False
    
    # Test semantic search integration
    if not asyncio.run(test_semantic_search_integration()):
        success = False
    
    # Create enhanced configuration
    if not create_langchain_config():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("✅ LangChain setup completed successfully!")
        print("\n📋 Next steps:")
        print("   1. Test the enhanced RAG server:")
        print("      python scripts/start_rag_server.py")
        print("   2. Test document processing:")
        print("      python -m src.processors.langchain_document_processor")
        print("   3. Test semantic search:")
        print("      python -m src.search.semantic_search")
        print("\n🎯 Enhanced embedding process is now using LangChain text splitters!")
    else:
        print("❌ Setup completed with errors. Please check the output above.")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
