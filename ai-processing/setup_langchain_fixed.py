#!/usr/bin/env python3
"""
Simplified PrismWeave LangChain Setup with UV Package Manager
Fixed import issues and streamlined installation process
"""

import subprocess
import sys
from pathlib import Path

def run_command(cmd: list, description: str) -> bool:
    """Run a command and return success status"""
    try:
        print(f"🔧 {description}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return True
        else:
            print(f"   ❌ Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"   ❌ Error running command: {e}")
        return False

def check_uv_availability() -> bool:
    """Check if UV package manager is available"""
    print("🔍 Checking UV package manager availability...")
    if run_command(["uv", "--version"], "Checking UV version"):
        return True
    else:
        print("❌ UV package manager not found. Please install UV first:")
        print("   Visit: https://github.com/astral-sh/uv")
        return False

def install_packages() -> bool:
    """Install required packages using UV"""
    print("\\n📦 Installing packages with UV...")
    
    packages = [
        "langchain>=0.3.0",
        "langchain-text-splitters>=0.3.0", 
        "langchain-community>=0.3.0",
        "langchain-core>=0.3.0",
        "pyyaml>=6.0"
    ]
    
    success = True
    for package in packages:
        if not run_command(["uv", "pip", "install", package], f"Installing {package}"):
            success = False
    
    return success

def test_langchain_basic() -> bool:
    """Test basic LangChain functionality"""
    print("\\n🧪 Testing LangChain installation...")
    
    try:
        print("   📋 Testing imports...")
        
        # Test imports with the correct module paths
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        from langchain_core.documents import Document
        print("   ✅ Core imports successful")
        
        # Test basic functionality
        print("   📋 Testing text splitter...")
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=100,
            chunk_overlap=20,
            separators=["\\n\\n", "\\n", " ", ""]
        )
        
        test_text = "This is a test document. It has multiple sentences. Let's see how it splits into chunks."
        chunks = splitter.split_text(test_text)
        print(f"   ✅ Text splitting successful: {len(chunks)} chunks created")
        
        # Test document creation
        print("   📋 Testing document creation...")
        doc = Document(page_content="Test content", metadata={"source": "test"})
        print("   ✅ Document creation successful")
        
        return True
        
    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        print("   💡 Try reinstalling: uv pip install --force-reinstall langchain langchain-text-splitters")
        return False
    except Exception as e:
        print(f"   ❌ Functionality error: {e}")
        return False

def test_code_splitters() -> bool:
    """Test code-specific splitters"""
    print("\\n🧪 Testing code-specific splitters...")
    
    try:
        from langchain_text_splitters import PythonCodeTextSplitter, MarkdownTextSplitter
        
        # Test Python splitter
        python_code = '''
def hello_world():
    """Say hello to the world"""
    print("Hello, World!")

class Greeter:
    def __init__(self, name):
        self.name = name
    
    def greet(self):
        return f"Hello, {self.name}!"
'''
        
        py_splitter = PythonCodeTextSplitter(chunk_size=200, chunk_overlap=50)
        py_chunks = py_splitter.split_text(python_code)
        print(f"   ✅ Python splitter: {len(py_chunks)} chunks")
        
        # Test Markdown splitter
        markdown_content = '''
# Main Title

## Section 1
This is section 1 content.

### Subsection 1.1
Some subsection content.

## Section 2
This is section 2 content.
'''
        
        md_splitter = MarkdownTextSplitter(chunk_size=200, chunk_overlap=50)
        md_chunks = md_splitter.split_text(markdown_content)
        print(f"   ✅ Markdown splitter: {len(md_chunks)} chunks")
        
        return True
        
    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def update_requirements() -> bool:
    """Update requirements.txt with LangChain packages"""
    print("\\n📝 Updating requirements.txt...")
    
    try:
        requirements_file = Path(__file__).parent / "requirements.txt"
        
        # Read existing requirements
        if requirements_file.exists():
            with open(requirements_file, 'r', encoding='utf-8') as f:
                existing = f.read()
        else:
            existing = ""
        
        # LangChain packages to add
        langchain_packages = [
            "# LangChain packages for enhanced embedding",
            "langchain>=0.3.0",
            "langchain-text-splitters>=0.3.0",
            "langchain-community>=0.3.0", 
            "langchain-core>=0.3.0",
            "pyyaml>=6.0"
        ]
        
        # Check if LangChain is already in requirements
        if "langchain" not in existing:
            with open(requirements_file, 'a', encoding='utf-8') as f:
                f.write("\\n\\n")
                f.write("\\n".join(langchain_packages))
                f.write("\\n")
            print("   ✅ Requirements.txt updated with LangChain packages")
        else:
            print("   ✅ LangChain packages already in requirements.txt")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error updating requirements: {e}")
        return False

def create_basic_config() -> bool:
    """Create basic configuration for LangChain"""
    print("\\n⚙️  Creating basic configuration...")
    
    try:
        config_content = '''# LangChain Enhanced RAG Configuration

langchain:
  enabled: true
  
  # Text splitter settings
  splitters:
    python:
      chunk_size: 1500
      chunk_overlap: 200
    
    markdown:
      chunk_size: 1000
      chunk_overlap: 100
      headers_to_split_on:
        - ["#", "Header 1"]
        - ["##", "Header 2"] 
        - ["###", "Header 3"]
    
    default:
      chunk_size: 1000
      chunk_overlap: 200
      separators: ["\\\\n\\\\n", "\\\\n", " ", ""]

  # Quality assessment
  quality:
    min_chunk_size: 50
    max_chunk_size: 2000
    quality_threshold: 0.5

# RAG settings
rag:
  use_langchain_processing: true
  fallback_to_basic: true
  enable_metadata_enrichment: true
'''
        
        config_file = Path(__file__).parent / "langchain_config.yaml"
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(config_content)
        
        print(f"   ✅ Configuration created: {config_file}")
        return True
        
    except Exception as e:
        print(f"   ❌ Error creating config: {e}")
        return False

def show_next_steps():
    """Show next steps to the user"""
    print("\\n" + "="*60)
    print("✅ LangChain setup completed successfully!")
    print("\\n🎯 Next Steps:")
    print("   1. Test the enhanced embedding process:")
    print("      python validate_langchain_embedding.py")
    print("\\n   2. Start the enhanced RAG server:")
    print("      python rag_server.py")
    print("\\n   3. Test with your documents:")
    print("      # Your RAG server now uses intelligent chunking!")
    print("\\n📚 Key Features Now Available:")
    print("   • Code-aware chunking (Python, JS, TS)")
    print("   • Header-aware Markdown processing")
    print("   • Intelligent boundary detection")
    print("   • Enhanced metadata extraction")
    print("   • Quality-based chunk assessment")
    
    config_file = Path(__file__).parent / "langchain_config.yaml"
    if config_file.exists():
        print(f"\\n⚙️  Configuration file: {config_file}")
    print("\\n" + "="*60)

def main():
    """Main setup function"""
    print("🚀 PrismWeave LangChain Setup (Simplified)")
    print("="*60)
    
    # Check UV availability
    if not check_uv_availability():
        sys.exit(1)
    
    # Install packages
    if not install_packages():
        print("❌ Package installation failed")
        sys.exit(1)
    
    # Test basic functionality
    if not test_langchain_basic():
        print("❌ Basic LangChain test failed")
        sys.exit(1)
    
    # Test code splitters
    if not test_code_splitters():
        print("⚠️  Code splitters test failed, but continuing...")
    
    # Update requirements
    if not update_requirements():
        print("⚠️  Requirements update failed, but continuing...")
    
    # Create configuration
    if not create_basic_config():
        print("⚠️  Configuration creation failed, but continuing...")
    
    # Show next steps
    show_next_steps()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\\n❌ Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\\n❌ Setup failed with error: {e}")
        sys.exit(1)
