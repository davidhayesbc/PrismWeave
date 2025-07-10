"""
Tests for LangChain document processor
"""

import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from typing import List, Dict, Any
import time

# Import test utilities
import sys
import os
from pathlib import Path

# Add src to Python path 
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Import the actual modules directly
sys.path.insert(0, str(src_path / "processors"))
from langchain_document_processor import (
    LangChainDocumentProcessor,
    DocumentAnalysis,
    ChunkMetadata, 
    ProcessedDocument
)

# Import test data
SAMPLE_MARKDOWN = """# Test Document

This is a test document for testing purposes.

## Section 1

Content for section 1.

## Section 2

Content for section 2 with more content.
"""

SAMPLE_PYTHON_CODE = '''
def hello_world():
    """A simple hello world function"""
    print("Hello, World!")
    return True

class TestClass:
    """A test class"""
    def __init__(self):
        self.value = 42
    
    def get_value(self):
        return self.value
'''

SAMPLE_JAVASCRIPT = '''
function helloWorld() {
    console.log("Hello, World!");
    return true;
}

class TestClass {
    constructor() {
        this.value = 42;
    }
    
    getValue() {
        return this.value;
    }
}
'''


class TestChunkMetadata:
    """Test suite for ChunkMetadata dataclass"""

    def test_init(self):
        """Test ChunkMetadata initialization"""
        metadata = ChunkMetadata(
            source_file="/test/file.py",
            chunk_index=0,
            total_chunks=5,
            chunk_size=1000,
            file_type=".py"
        )
        
        assert metadata.source_file == "/test/file.py"
        assert metadata.chunk_index == 0
        assert metadata.total_chunks == 5
        assert metadata.chunk_size == 1000
        assert metadata.file_type == ".py"
        assert metadata.section_title is None
        assert metadata.is_code_block is False
        assert metadata.quality_score == 0.0

    def test_init_with_optional_fields(self):
        """Test ChunkMetadata with optional fields"""
        metadata = ChunkMetadata(
            source_file="/test/file.md",
            chunk_index=2,
            total_chunks=10,
            chunk_size=800,
            file_type=".md",
            section_title="Introduction",
            parent_section="Getting Started",
            hierarchy_level=2,
            is_code_block=True,
            programming_language="python",
            estimated_reading_time=3,
            word_count=150,
            quality_score=0.9
        )
        
        assert metadata.section_title == "Introduction"
        assert metadata.parent_section == "Getting Started"
        assert metadata.hierarchy_level == 2
        assert metadata.is_code_block is True
        assert metadata.programming_language == "python"
        assert metadata.estimated_reading_time == 3
        assert metadata.word_count == 150
        assert metadata.quality_score == 0.9


class TestDocumentAnalysis:
    """Test suite for DocumentAnalysis dataclass"""

    def test_init(self):
        """Test DocumentAnalysis initialization"""
        analysis = DocumentAnalysis(
            summary="Test document summary",
            tags=["test", "document"],
            category="technical",
            word_count=500,
            reading_time=3,
            language="en",
            readability_score=75.0,
            key_topics=["testing", "documentation"],
            confidence=0.85
        )
        
        assert analysis.summary == "Test document summary"
        assert analysis.tags == ["test", "document"]
        assert analysis.category == "technical"
        assert analysis.word_count == 500
        assert analysis.reading_time == 3
        assert analysis.language == "en"
        assert analysis.readability_score == 75.0
        assert analysis.key_topics == ["testing", "documentation"]
        assert analysis.confidence == 0.85


class TestProcessedDocument:
    """Test suite for ProcessedDocument dataclass"""

    def test_init(self):
        """Test ProcessedDocument initialization"""
        # Mock Document objects
        mock_chunk1 = Mock()
        mock_chunk1.page_content = "First chunk content"
        mock_chunk1.metadata = {"chunk_index": 0}
        
        mock_chunk2 = Mock()
        mock_chunk2.page_content = "Second chunk content"
        mock_chunk2.metadata = {"chunk_index": 1}
        
        chunks = [mock_chunk1, mock_chunk2]
        
        metadata = {
            "file_path": "/test/document.md",
            "file_name": "document.md",
            "content_type": "markdown"
        }
        
        stats = {
            "processing_time": 2.5,
            "chunk_count": 2,
            "total_length": 1000
        }
        
        doc = ProcessedDocument(
            file_path="/test/document.md",
            content="Original document content",
            chunks=chunks,
            metadata=metadata,
            processing_stats=stats
        )
        
        assert doc.file_path == "/test/document.md"
        assert doc.content == "Original document content"
        assert len(doc.chunks) == 2
        assert doc.metadata["content_type"] == "markdown"
        assert doc.processing_stats["chunk_count"] == 2


class TestLangChainDocumentProcessor:
    """Test suite for LangChainDocumentProcessor"""

    @pytest.fixture
    def mock_config(self):
        """Mock configuration for testing"""
        config = Mock()
        
        # Mock ollama config
        config.ollama.host = "http://localhost:11434"
        config.ollama.timeout = 30
        
        # Mock chunking config
        config.chunking = {
            'default_chunk_size': 1000,
            'default_overlap': 200,
            'python_chunk_size': 1500,
            'python_overlap': 200,
            'javascript_chunk_size': 1200,
            'javascript_overlap': 150,
            'markdown_chunk_size': 1000,
            'markdown_overlap': 100
        }
        
        # Mock processing config
        config.processing.max_concurrent = 3
        
        return config

    @pytest.fixture
    def mock_processor(self, mock_config):
        """Create mock processor"""
        with patch('processors.langchain_document_processor.get_config', return_value=mock_config):
            with patch('processors.langchain_document_processor.OllamaClient') as mock_client_class:
                mock_client = Mock()
                mock_client_class.return_value = mock_client
                
                processor = LangChainDocumentProcessor(mock_config)
                return processor

    @pytest.fixture
    def temp_test_file(self):
        """Create temporary test file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(SAMPLE_MARKDOWN)
            temp_path = Path(f.name)
        
        yield temp_path
        
        # Cleanup
        if temp_path.exists():
            temp_path.unlink()

    def test_init_with_config(self, mock_config):
        """Test processor initialization with config"""
        with patch('processors.langchain_document_processor.OllamaClient') as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            
            processor = LangChainDocumentProcessor(mock_config)
            
            assert processor.config is mock_config
            assert processor.stats["langchain_enabled"] is True
            assert processor.stats["total_documents"] == 0
            assert processor.stats["total_chunks"] == 0

    def test_init_without_langchain(self, mock_config):
        """Test processor initialization without LangChain"""
        with patch('processors.langchain_document_processor.LANGCHAIN_AVAILABLE', False):
            processor = LangChainDocumentProcessor(mock_config)
            
            assert processor.splitters == {}
            assert processor.stats["langchain_enabled"] is False

    def test_detect_content_type_python(self, mock_processor):
        """Test content type detection for Python files"""
        python_file = Path("test.py")
        
        content_type = mock_processor.detect_content_type(SAMPLE_PYTHON_CODE, python_file)
        assert content_type == "python_code"

    def test_detect_content_type_javascript(self, mock_processor):
        """Test content type detection for JavaScript files"""
        js_file = Path("test.js")
        
        content_type = mock_processor.detect_content_type(SAMPLE_JAVASCRIPT, js_file)
        assert content_type == "javascript_code"

    def test_detect_content_type_markdown(self, mock_processor):
        """Test content type detection for Markdown files"""
        md_file = Path("test.md")
        
        content_type = mock_processor.detect_content_type(SAMPLE_MARKDOWN, md_file)
        assert content_type == "markdown"

    def test_detect_content_type_content_based(self, mock_processor):
        """Test content-based type detection"""
        txt_file = Path("test.txt")
        
        # Code-like content
        code_content = "def hello():\n    print('hello')\nclass TestClass:\n    pass"
        content_type = mock_processor.detect_content_type(code_content, txt_file)
        assert content_type == "code_mixed"
        
        # Markdown-like content
        markdown_content = "# Header\n## Subheader\n### Another header\nContent"
        content_type = mock_processor.detect_content_type(markdown_content, txt_file)
        assert content_type == "markdown"
        
        # Plain text
        plain_content = "This is just plain text without special formatting."
        content_type = mock_processor.detect_content_type(plain_content, txt_file)
        assert content_type == "plain_text"

    def test_extract_hierarchical_metadata_markdown(self, mock_processor):
        """Test metadata extraction from markdown"""
        md_file = Path("test.md")
        
        metadata = mock_processor.extract_hierarchical_metadata(SAMPLE_MARKDOWN, md_file)
        
        assert metadata["file_path"] == str(md_file)
        assert metadata["file_name"] == "test.md"
        assert metadata["file_type"] == ".md"
        assert metadata["content_type"] == "markdown"
        assert len(metadata["headers"]) > 0
        assert any(header["title"] == "Test Document" for header in metadata["headers"])

    def test_extract_hierarchical_metadata_python(self, mock_processor):
        """Test metadata extraction from Python code"""
        py_file = Path("test.py")
        
        metadata = mock_processor.extract_hierarchical_metadata(SAMPLE_PYTHON_CODE, py_file)
        
        assert metadata["file_type"] == ".py"
        assert metadata["content_type"] == "python_code"
        assert len(metadata["code_blocks"]) == 0  # No markdown code blocks in raw Python

    def test_enhance_chunk_metadata(self, mock_processor):
        """Test chunk metadata enhancement"""
        chunk_text = "def test_function():\n    return True"
        file_metadata = {
            "file_path": "/test/file.py",
            "file_type": ".py",
            "content_type": "python_code",
            "headers": []
        }
        
        metadata = mock_processor.enhance_chunk_metadata(
            chunk_text, 0, 5, file_metadata
        )
        
        assert metadata.source_file == "/test/file.py"
        assert metadata.chunk_index == 0
        assert metadata.total_chunks == 5
        assert metadata.file_type == ".py"
        assert metadata.is_code_block is True
        assert metadata.programming_language == "python"
        assert metadata.word_count > 0
        assert metadata.quality_score > 0

    def test_assess_chunk_quality_short_chunk(self, mock_processor):
        """Test quality assessment for short chunk"""
        short_chunk = "short"
        quality = mock_processor._assess_chunk_quality(short_chunk)
        assert quality == 0.1

    def test_assess_chunk_quality_minimal_words(self, mock_processor):
        """Test quality assessment for chunk with few words"""
        minimal_chunk = "just a few words here"
        quality = mock_processor._assess_chunk_quality(minimal_chunk)
        assert quality == 0.3

    def test_assess_chunk_quality_code_chunk(self, mock_processor):
        """Test quality assessment for code chunk"""
        code_chunk = "function test() { console.log('hello'); return true; }"
        quality = mock_processor._assess_chunk_quality(code_chunk)
        assert quality == 0.9

    def test_assess_chunk_quality_text_chunk(self, mock_processor):
        """Test quality assessment for text chunk"""
        text_chunk = "This is a regular text chunk with normal content and no special code symbols."
        quality = mock_processor._assess_chunk_quality(text_chunk)
        assert quality == 0.8

    def test_basic_chunk_text(self, mock_processor):
        """Test basic text chunking fallback"""
        content = "This is a test content. " * 100  # Long content
        
        chunks = mock_processor._basic_chunk_text(content, chunk_size=100, overlap=20)
        
        assert len(chunks) > 1
        assert all(len(chunk) <= 120 for chunk in chunks)  # chunk_size + some buffer
        assert all(chunk.strip() for chunk in chunks)  # No empty chunks

    def test_basic_chunk_text_short_content(self, mock_processor):
        """Test basic chunking with short content"""
        content = "Short content"
        
        chunks = mock_processor._basic_chunk_text(content, chunk_size=1000)
        
        assert len(chunks) == 1
        assert chunks[0] == content

    def test_basic_chunk_text_sentence_boundary(self, mock_processor):
        """Test basic chunking respects sentence boundaries"""
        content = "First sentence. Second sentence. Third sentence. " * 20
        
        chunks = mock_processor._basic_chunk_text(content, chunk_size=100, overlap=10)
        
        # Should break at periods when possible
        assert len(chunks) > 1
        assert any("." in chunk for chunk in chunks)

    @pytest.mark.asyncio
    async def test_process_document_success(self, mock_processor, temp_test_file):
        """Test successful document processing"""
        # Mock the splitter
        mock_splitter = Mock()
        mock_splitter.split_text.return_value = ["Chunk 1", "Chunk 2", "Chunk 3"]
        
        with patch.object(mock_processor, 'get_splitter_for_file', return_value=mock_splitter):
            result = await mock_processor.process_document(temp_test_file)
        
        assert result is not None
        assert isinstance(result, ProcessedDocument)
        assert result.file_path == str(temp_test_file)
        assert len(result.chunks) == 3
        assert result.processing_stats["chunk_count"] == 3
        assert result.processing_stats["processing_time"] > 0

    @pytest.mark.asyncio
    async def test_process_document_empty_file(self, mock_processor):
        """Test processing empty file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("")  # Empty file
            empty_file = Path(f.name)
        
        try:
            result = await mock_processor.process_document(empty_file)
            assert result is None
        finally:
            empty_file.unlink()

    @pytest.mark.asyncio
    async def test_process_document_nonexistent_file(self, mock_processor):
        """Test processing nonexistent file"""
        nonexistent_file = Path("/nonexistent/file.txt")
        
        result = await mock_processor.process_document(nonexistent_file)
        assert result is None

    @pytest.mark.asyncio
    async def test_process_document_without_langchain(self, mock_config):
        """Test document processing without LangChain available"""
        with patch('processors.langchain_document_processor.LANGCHAIN_AVAILABLE', False):
            with patch('processors.langchain_document_processor.OllamaClient'):
                processor = LangChainDocumentProcessor(mock_config)
                
                with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
                    f.write(SAMPLE_MARKDOWN)
                    test_file = Path(f.name)
                
                try:
                    result = await processor.process_document(test_file)
                    
                    assert result is not None
                    assert len(result.chunks) > 0
                    # Should use basic chunking
                    assert result.processing_stats["splitter_type"] == "TextSplitter"
                    assert result.processing_stats["langchain_enabled"] is False
                finally:
                    test_file.unlink()

    @pytest.mark.asyncio
    async def test_batch_process_documents(self, mock_processor):
        """Test batch document processing"""
        # Create multiple temp files
        temp_files = []
        try:
            for i in range(3):
                with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
                    f.write(f"# Document {i}\n\nContent for document {i}")
                    temp_files.append(Path(f.name))
            
            # Mock the single document processing
            async def mock_process_doc(file_path):
                # Simulate successful processing
                return ProcessedDocument(
                    file_path=str(file_path),
                    content="test content",
                    chunks=[],
                    metadata={},
                    processing_stats={"chunk_count": 1}
                )
            
            with patch.object(mock_processor, 'process_document', side_effect=mock_process_doc):
                results = await mock_processor.batch_process_documents(temp_files, max_concurrent=2)
            
            assert len(results) == 3
            assert all(isinstance(result, ProcessedDocument) for result in results)
            
        finally:
            # Cleanup
            for temp_file in temp_files:
                if temp_file.exists():
                    temp_file.unlink()

    @pytest.mark.asyncio
    async def test_batch_process_with_errors(self, mock_processor):
        """Test batch processing with some errors"""
        temp_files = []
        try:
            for i in range(2):
                with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
                    f.write(f"Document {i}")
                    temp_files.append(Path(f.name))
            
            # Mock processing with one success and one error
            async def mock_process_doc(file_path):
                if "0" in str(file_path):
                    raise Exception("Processing failed")
                return ProcessedDocument(
                    file_path=str(file_path),
                    content="content",
                    chunks=[],
                    metadata={},
                    processing_stats={}
                )
            
            with patch.object(mock_processor, 'process_document', side_effect=mock_process_doc):
                results = await mock_processor.batch_process_documents(temp_files)
            
            # Should only return successful results
            assert len(results) == 1
            
        finally:
            for temp_file in temp_files:
                if temp_file.exists():
                    temp_file.unlink()

    def test_get_processing_stats(self, mock_processor):
        """Test getting processing statistics"""
        # Set some stats
        mock_processor.stats["total_documents"] = 5
        mock_processor.stats["total_chunks"] = 25
        mock_processor.stats["processing_time"] = 10.5
        
        stats = mock_processor.get_processing_stats()
        
        assert stats["total_documents"] == 5
        assert stats["total_chunks"] == 25
        assert stats["processing_time"] == 10.5
        assert stats["average_chunks_per_doc"] == 5.0
        assert "supported_file_types" in stats

    @pytest.mark.asyncio
    async def test_context_manager(self, mock_processor):
        """Test async context manager functionality"""
        mock_processor.ollama_client.__aenter__ = AsyncMock()
        mock_processor.ollama_client.__aexit__ = AsyncMock()
        
        async with mock_processor as processor:
            assert processor is mock_processor
        
        mock_processor.ollama_client.__aenter__.assert_called_once()
        mock_processor.ollama_client.__aexit__.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_file_compatibility(self, mock_processor, temp_test_file):
        """Test process_file method for backward compatibility"""
        analysis, metadata = await mock_processor.process_file(temp_test_file)
        
        assert isinstance(analysis, DocumentAnalysis)
        assert analysis.word_count > 0
        assert analysis.reading_time > 0
        assert isinstance(metadata, dict)
        assert metadata["filename"] == temp_test_file.name

    @pytest.mark.asyncio
    async def test_process_file_nonexistent(self, mock_processor):
        """Test process_file with nonexistent file"""
        nonexistent_file = Path("/nonexistent/file.txt")
        
        with pytest.raises(FileNotFoundError):
            await mock_processor.process_file(nonexistent_file)

    @pytest.mark.asyncio
    async def test_process_content(self, mock_processor):
        """Test content processing"""
        content = SAMPLE_MARKDOWN
        
        # Mock splitter
        mock_splitter = Mock()
        mock_splitter.split_text.return_value = ["Chunk 1", "Chunk 2"]
        mock_processor.splitters = {".md": mock_splitter, "default": mock_splitter}
        
        chunks = await mock_processor.process_content(content, ".md")
        
        assert len(chunks) == 2
        assert chunks[0] == "Chunk 1"
        assert chunks[1] == "Chunk 2"

    @pytest.mark.asyncio
    async def test_process_content_fallback(self, mock_processor):
        """Test content processing with splitter failure"""
        content = SAMPLE_MARKDOWN
        
        # Mock splitter that raises exception
        mock_splitter = Mock()
        mock_splitter.split_text.side_effect = Exception("Splitter failed")
        mock_processor.splitters = {"default": mock_splitter}
        
        chunks = await mock_processor.process_content(content)
        
        # Should fall back to basic chunking
        assert len(chunks) > 0
        assert all(isinstance(chunk, str) for chunk in chunks)

    def test_get_splitter_for_file_python(self, mock_processor):
        """Test getting splitter for Python file"""
        py_file = Path("test.py")
        
        # Mock splitters
        python_splitter = Mock()
        default_splitter = Mock()
        mock_processor.splitters = {".py": python_splitter, "default": default_splitter}
        
        splitter = mock_processor.get_splitter_for_file(py_file)
        assert splitter is python_splitter

    def test_get_splitter_for_file_unknown(self, mock_processor):
        """Test getting splitter for unknown file type"""
        unknown_file = Path("test.xyz")
        
        # Mock splitters
        default_splitter = Mock()
        mock_processor.splitters = {"default": default_splitter}
        
        splitter = mock_processor.get_splitter_for_file(unknown_file)
        assert splitter is default_splitter

    def test_get_splitter_for_file_no_langchain(self, mock_config):
        """Test getting splitter when LangChain is not available"""
        with patch('processors.langchain_document_processor.LANGCHAIN_AVAILABLE', False):
            with patch('processors.langchain_document_processor.OllamaClient'):
                processor = LangChainDocumentProcessor(mock_config)
                
                py_file = Path("test.py")
                splitter = processor.get_splitter_for_file(py_file)
                
                # Should return basic TextSplitter
                assert splitter.__class__.__name__ == "TextSplitter"


# Performance and stress tests
@pytest.mark.slow
class TestLangChainDocumentProcessorPerformance:
    """Performance tests for document processor"""

    @pytest.fixture
    def large_content(self):
        """Generate large content for performance testing"""
        return SAMPLE_MARKDOWN * 100  # Large document

    @pytest.mark.asyncio
    async def test_large_document_processing(self, mock_processor, large_content):
        """Test processing large documents"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(large_content)
            large_file = Path(f.name)
        
        try:
            start_time = time.time()
            result = await mock_processor.process_document(large_file)
            processing_time = time.time() - start_time
            
            assert result is not None
            assert processing_time < 10.0  # Should process within 10 seconds
            assert len(result.chunks) > 10  # Should create multiple chunks
            
        finally:
            large_file.unlink()

    @pytest.mark.asyncio
    async def test_concurrent_processing_performance(self, mock_processor):
        """Test concurrent processing performance"""
        # Create multiple files
        temp_files = []
        try:
            for i in range(10):
                with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
                    f.write(f"# Document {i}\n" + SAMPLE_MARKDOWN)
                    temp_files.append(Path(f.name))
            
            start_time = time.time()
            results = await mock_processor.batch_process_documents(temp_files, max_concurrent=3)
            total_time = time.time() - start_time
            
            assert len(results) == 10
            assert total_time < 30.0  # Should complete within 30 seconds
            
        finally:
            for temp_file in temp_files:
                if temp_file.exists():
                    temp_file.unlink()


if __name__ == "__main__":
    pytest.main([__file__])
