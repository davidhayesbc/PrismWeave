"""
Simple tests for PrismWeave core functionality
"""

import pytest
from pathlib import Path
import tempfile
import os

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from src.core.config import Config, load_config
from src.core.document_processor import DocumentProcessor


class TestConfig:
    """Test configuration loading and validation"""
    
    def test_default_config(self):
        """Test default configuration creation"""
        config = Config()
        assert config.ollama_host == "http://localhost:11434"
        assert config.chunk_size == 1000
        assert config.embedding_model == "nomic-embed-text:latest"
    
    def test_config_validation(self):
        """Test configuration validation"""
        # Valid config
        config = Config()
        issues = config.validate()
        assert len(issues) == 0
        
        # Invalid config - empty model
        config.embedding_model = ""
        issues = config.validate()
        assert len(issues) > 0
        assert any("embedding model" in issue.lower() for issue in issues)
    
    def test_load_config_no_file(self):
        """Test loading config when file doesn't exist"""
        config = load_config(Path("nonexistent.yaml"))
        assert isinstance(config, Config)
        assert config.chunk_size == 1000  # Should use defaults


class TestDocumentProcessor:
    """Test document processing functionality"""
    
    def test_processor_initialization(self):
        """Test processor can be initialized"""
        config = Config()
        processor = DocumentProcessor(config)
        assert processor.config == config
        assert processor.text_splitter is not None
    
    def test_supported_file_types(self):
        """Test that processor recognizes supported file types"""
        config = Config()
        processor = DocumentProcessor(config)
        
        supported_extensions = {'.md', '.txt', '.pdf', '.docx', '.html', '.htm'}
        for ext in supported_extensions:
            assert ext in processor.loaders
    
    def test_markdown_with_frontmatter(self):
        """Test processing markdown file with frontmatter"""
        config = Config()
        processor = DocumentProcessor(config)
        
        # Create temporary markdown file with frontmatter
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("""---
title: Test Document
author: Test Author
tags: [test, document]
---

# Test Document

This is a test document with some content.

## Section 1

Some more content here.
""")
            temp_file = Path(f.name)
        
        try:
            # Process the document
            chunks = processor.process_document(temp_file)
            
            # Verify results
            assert len(chunks) > 0
            
            # Check that frontmatter metadata is preserved
            first_chunk = chunks[0]
            assert first_chunk.metadata['title'] == 'Test Document'
            assert first_chunk.metadata['author'] == 'Test Author'
            assert 'tags' in first_chunk.metadata
            
            # Check file metadata
            assert first_chunk.metadata['file_name'] == temp_file.name
            assert first_chunk.metadata['file_extension'] == '.md'
            
        finally:
            # Clean up
            os.unlink(temp_file)
    
    def test_process_nonexistent_file(self):
        """Test processing nonexistent file raises error"""
        config = Config()
        processor = DocumentProcessor(config)
        
        with pytest.raises(FileNotFoundError):
            processor.process_document(Path("nonexistent.md"))
    
    def test_process_unsupported_file_type(self):
        """Test processing unsupported file type raises error"""
        config = Config()
        processor = DocumentProcessor(config)
        
        # Create temporary file with unsupported extension
        with tempfile.NamedTemporaryFile(suffix='.xyz', delete=False) as f:
            temp_file = Path(f.name)
        
        try:
            with pytest.raises(ValueError, match="Unsupported file type"):
                processor.process_document(temp_file)
        finally:
            os.unlink(temp_file)


if __name__ == "__main__":
    pytest.main([__file__])
