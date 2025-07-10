"""
Enhanced document processor with LangChain text splitters
Provides intelligent chunking strategies for different content types
"""

import os
import asyncio
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass, asdict
import logging
import re
import hashlib

# LangChain text splitters
try:
    from langchain_text_splitters import (
        RecursiveCharacterTextSplitter,
        PythonCodeTextSplitter,
        MarkdownTextSplitter,
        TokenTextSplitter,
        TextSplitter
    )
    from langchain_core.documents import Document
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    # Fallback classes
    class Document:
        def __init__(self, page_content: str, metadata: Dict[str, Any] = None):
            self.page_content = page_content
            self.metadata = metadata or {}

    class TextSplitter:
        def split_text(self, text: str) -> List[str]:
            return [text]

# Standard dependencies
try:
    import frontmatter
    import markdown
    from bs4 import BeautifulSoup
    import nltk
    import textstat
    from langdetect import detect
except ImportError:
    frontmatter = None
    markdown = None
    BeautifulSoup = None
    nltk = None
    textstat = None
    detect = None

from ..models.ollama_client import OllamaClient
from ..utils.config_simplified import get_config

logger = logging.getLogger(__name__)

@dataclass
class DocumentAnalysis:
    """Results of document analysis"""
    summary: str
    tags: List[str]
    category: str
    word_count: int
    reading_time: int
    language: str
    readability_score: float
    key_topics: List[str]
    confidence: float

@dataclass
class ChunkMetadata:
    """Enhanced metadata for document chunks"""
    source_file: str
    chunk_index: int
    total_chunks: int
    chunk_size: int
    file_type: str
    section_title: Optional[str] = None
    parent_section: Optional[str] = None
    hierarchy_level: int = 0
    is_code_block: bool = False
    programming_language: Optional[str] = None
    estimated_reading_time: int = 0
    word_count: int = 0
    quality_score: float = 0.0

@dataclass
class ProcessedDocument:
    """Enhanced document with intelligent chunks"""
    file_path: str
    content: str
    chunks: List[Document]
    metadata: Dict[str, Any]
    processing_stats: Dict[str, Any]

class LangChainDocumentProcessor:
    """Enhanced document processor using LangChain text splitters"""

    def __init__(self, config=None):
        self.config = config or get_config()
        self.ollama_client = OllamaClient(
            host=self.config.ollama.host,
            timeout=self.config.ollama.timeout
        )

        # Initialize text splitters
        self._init_splitters()

        # Processing statistics
        self.stats = {
            "total_documents": 0,
            "total_chunks": 0,
            "average_chunks_per_doc": 0.0,
            "processing_time": 0.0,
            "langchain_enabled": LANGCHAIN_AVAILABLE
        }

    def _init_splitters(self):
        """Initialize LangChain text splitters"""
        if not LANGCHAIN_AVAILABLE:
            logger.warning("LangChain not available, using basic text splitting")
            self.splitters = {}
            return

        # Get chunking configuration
        chunk_config = getattr(self.config, 'chunking', {})
        default_chunk_size = chunk_config.get('default_chunk_size', 1000)
        default_overlap = chunk_config.get('default_overlap', 200)

        self.splitters = {
            # Python code splitter
            '.py': PythonCodeTextSplitter(
                chunk_size=chunk_config.get('python_chunk_size', 1500),
                chunk_overlap=chunk_config.get('python_overlap', 200),
                length_function=len
            ),

            # JavaScript/TypeScript splitter (using RecursiveCharacterTextSplitter with JS separators)
            '.js': RecursiveCharacterTextSplitter(
                chunk_size=chunk_config.get('javascript_chunk_size', 1200),
                chunk_overlap=chunk_config.get('javascript_overlap', 150),
                separators=["\nfunction ", "\nclass ", "\nconst ", "\nlet ", "\nvar ", "\n\n", "\n", " ", ""],
                length_function=len
            ),
            '.ts': RecursiveCharacterTextSplitter(
                chunk_size=chunk_config.get('typescript_chunk_size', 1200),
                chunk_overlap=chunk_config.get('typescript_overlap', 150),
                separators=["\nfunction ", "\nclass ", "\nconst ", "\nlet ", "\nvar ", "\ninterface ", "\ntype ", "\n\n", "\n", " ", ""],
                length_function=len
            ),

            # Markdown splitter
            '.md': MarkdownTextSplitter(
                chunk_size=chunk_config.get('markdown_chunk_size', 1000),
                chunk_overlap=chunk_config.get('markdown_overlap', 100)
            ),

            # Default recursive splitter for other content
            'default': RecursiveCharacterTextSplitter(
                chunk_size=default_chunk_size,
                chunk_overlap=default_overlap,
                separators=["\n\n", "\n", " ", ""],
                length_function=len,
                is_separator_regex=False,
            )
        }

        logger.info(f"Initialized {len(self.splitters)} LangChain text splitters")

    def get_splitter_for_file(self, file_path: Path) -> TextSplitter:
        """Get appropriate text splitter for file type"""
        if not LANGCHAIN_AVAILABLE:
            return TextSplitter()

        file_extension = file_path.suffix.lower()
        return self.splitters.get(file_extension, self.splitters['default'])

    def detect_content_type(self, content: str, file_path: Path) -> str:
        """Detect content type for better processing"""
        file_ext = file_path.suffix.lower()

        # File extension based detection
        if file_ext in ['.py']:
            return 'python_code'
        elif file_ext in ['.js', '.ts', '.jsx', '.tsx']:
            return 'javascript_code'
        elif file_ext in ['.md', '.markdown']:
            return 'markdown'
        elif file_ext in ['.txt']:
            return 'plain_text'
        elif file_ext in ['.json']:
            return 'json'
        elif file_ext in ['.yaml', '.yml']:
            return 'yaml'

        # Content-based detection
        if content.strip().startswith('```') or 'def ' in content or 'class ' in content:
            return 'code_mixed'
        elif content.count('#') > content.count('\n') * 0.1:  # Many headers
            return 'markdown'
        else:
            return 'plain_text'

    def extract_hierarchical_metadata(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Extract hierarchical structure from document"""
        metadata = {
            'file_path': str(file_path),
            'file_name': file_path.name,
            'file_type': file_path.suffix.lower(),
            'content_type': self.detect_content_type(content, file_path),
            'headers': [],
            'code_blocks': [],
            'sections': []
        }

        # Extract markdown headers
        if metadata['content_type'] in ['markdown', 'code_mixed']:
            headers = re.findall(r'^(#{1,6})\s+(.+)$', content, re.MULTILINE)
            metadata['headers'] = [
                {'level': len(level), 'title': title.strip(), 'line': 0}
                for level, title in headers
            ]

        # Extract code blocks
        code_blocks = re.findall(r'```(\w+)?\n(.*?)\n```', content, re.DOTALL)
        metadata['code_blocks'] = [
            {'language': lang or 'unknown', 'content': code[:100] + '...' if len(code) > 100 else code}
            for lang, code in code_blocks
        ]

        return metadata

    def enhance_chunk_metadata(self, chunk: str, chunk_index: int, total_chunks: int,
                             file_metadata: Dict[str, Any]) -> ChunkMetadata:
        """Create enhanced metadata for a chunk"""
        words = len(chunk.split())

        # Detect if chunk contains code
        is_code = bool(re.search(r'(def |class |function |import |from |#include)', chunk))

        # Extract programming language if it's code
        prog_lang = None
        if is_code:
            if 'python' in file_metadata.get('content_type', ''):
                prog_lang = 'python'
            elif 'javascript' in file_metadata.get('content_type', ''):
                prog_lang = 'javascript'

        # Find section context
        section_title = None
        for header in file_metadata.get('headers', []):
            if header['title'].lower() in chunk.lower():
                section_title = header['title']
                break

        return ChunkMetadata(
            source_file=file_metadata['file_path'],
            chunk_index=chunk_index,
            total_chunks=total_chunks,
            chunk_size=len(chunk),
            file_type=file_metadata['file_type'],
            section_title=section_title,
            hierarchy_level=1,  # Could be enhanced to detect actual level
            is_code_block=is_code,
            programming_language=prog_lang,
            estimated_reading_time=max(1, words // 200),  # ~200 words per minute
            word_count=words,
            quality_score=self._assess_chunk_quality(chunk)
        )

    def _assess_chunk_quality(self, chunk: str) -> float:
        """Assess the quality of a chunk for embedding"""
        if len(chunk.strip()) < 50:
            return 0.1

        words = chunk.split()
        if len(words) < 10:
            return 0.3

        # Check for code vs text balance
        code_indicators = len(re.findall(r'[{}();]', chunk))
        text_length = len(chunk)
        code_ratio = code_indicators / max(text_length / 100, 1)

        if code_ratio > 5:  # Mostly code
            return 0.9
        elif code_ratio < 0.5:  # Mostly text
            return 0.8
        else:  # Mixed content
            return 0.95

    async def process_document(self, file_path: Path, force_reprocess: bool = False) -> Optional[ProcessedDocument]:
        """Process document with enhanced chunking"""
        start_time = time.time()

        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            if not content.strip():
                logger.warning(f"Empty file: {file_path}")
                return None

            # Extract file metadata
            file_metadata = self.extract_hierarchical_metadata(content, file_path)

            # Get appropriate splitter
            splitter = self.get_splitter_for_file(file_path)

            # Split content into chunks
            if LANGCHAIN_AVAILABLE and hasattr(splitter, 'split_text'):
                chunk_texts = splitter.split_text(content)
            else:
                # Fallback to basic chunking
                chunk_texts = self._basic_chunk_text(content)

            # Create enhanced chunks with metadata
            chunks = []
            for i, chunk_text in enumerate(chunk_texts):
                if not chunk_text.strip():
                    continue

                # Create chunk metadata
                chunk_metadata = self.enhance_chunk_metadata(
                    chunk_text, i, len(chunk_texts), file_metadata
                )

                # Create LangChain Document
                doc = Document(
                    page_content=chunk_text,
                    metadata=asdict(chunk_metadata)
                )
                chunks.append(doc)

            # Processing statistics
            processing_time = time.time() - start_time
            processing_stats = {
                'processing_time': processing_time,
                'chunk_count': len(chunks),
                'total_length': len(content),
                'average_chunk_size': sum(len(chunk.page_content) for chunk in chunks) / len(chunks) if chunks else 0,
                'splitter_type': type(splitter).__name__,
                'langchain_enabled': LANGCHAIN_AVAILABLE
            }

            # Update global statistics
            self.stats['total_documents'] += 1
            self.stats['total_chunks'] += len(chunks)
            self.stats['processing_time'] += processing_time
            self.stats['average_chunks_per_doc'] = self.stats['total_chunks'] / self.stats['total_documents']

            logger.info(f"Processed {file_path.name}: {len(chunks)} chunks in {processing_time:.2f}s")

            return ProcessedDocument(
                file_path=str(file_path),
                content=content,
                chunks=chunks,
                metadata=file_metadata,
                processing_stats=processing_stats
            )

        except Exception as e:
            logger.error(f"Failed to process document {file_path}: {e}")
            return None

    def _basic_chunk_text(self, content: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Fallback basic text chunking when LangChain is not available"""
        if len(content) <= chunk_size:
            return [content]

        chunks = []
        start = 0

        while start < len(content):
            end = min(start + chunk_size, len(content))
            chunk = content[start:end]

            # Try to break at sentence boundary
            if end < len(content):
                last_period = chunk.rfind('.')
                last_newline = chunk.rfind('\n')
                break_point = max(last_period, last_newline)

                if break_point > start + chunk_size // 2:
                    chunk = content[start:start + break_point + 1]
                    end = start + break_point + 1

            chunks.append(chunk.strip())
            start = end - overlap

            if start >= len(content):
                break

        return [chunk for chunk in chunks if chunk.strip()]

    async def batch_process_documents(self, file_paths: List[Path],
                                    max_concurrent: int = None) -> List[ProcessedDocument]:
        """Process multiple documents concurrently"""
        max_concurrent = max_concurrent or getattr(self.config.processing, 'max_concurrent', 3)

        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_with_semaphore(file_path):
            async with semaphore:
                return await self.process_document(file_path)

        # Process documents concurrently
        tasks = [process_with_semaphore(fp) for fp in file_paths]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out None results and exceptions
        processed_docs = []
        for result in results:
            if isinstance(result, ProcessedDocument):
                processed_docs.append(result)
            elif isinstance(result, Exception):
                logger.error(f"Document processing failed: {result}")

        logger.info(f"Batch processed {len(processed_docs)}/{len(file_paths)} documents successfully")
        return processed_docs

    def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics"""
        return {
            **self.stats,
            'splitter_types': list(self.splitters.keys()) if LANGCHAIN_AVAILABLE else ['basic'],
            'supported_file_types': ['.py', '.js', '.ts', '.md', '.txt', '.json', '.yaml']
        }

    async def __aenter__(self):
        """Async context manager entry"""
        await self.ollama_client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.ollama_client.__aexit__(exc_type, exc_val, exc_tb)

    async def process_file(self, file_path: Path) -> Tuple[DocumentAnalysis, Dict[str, Any]]:
        """Process a file and return analysis with metadata"""
        logger.info(f"Processing file with LangChain: {file_path}")

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Read file content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            raise IOError(f"Failed to read file {file_path}: {e}")

        # Basic file metadata
        file_metadata = {
            'filename': file_path.name,
            'filepath': str(file_path),
            'file_size': file_path.stat().st_size,
            'modified_time': time.time()
        }

        # Process with LangChain splitters
        chunks = await self.process_content(content, file_path.suffix)

        # Basic analysis (simplified for now)
        word_count = len(content.split())
        reading_time = max(1, word_count // 200)

        # Create DocumentAnalysis object
        analysis = DocumentAnalysis(
            summary=f"Processed with LangChain - {len(chunks)} chunks generated",
            tags=["langchain", "processed"],
            category="document",
            word_count=word_count,
            reading_time=reading_time,
            language="en",
            readability_score=50.0,
            key_topics=["langchain", "text-splitting"],
            confidence=0.8
        )

        return analysis, file_metadata

    async def process_content(self, content: str, file_extension: str = None) -> List[str]:
        """Process content with appropriate LangChain splitter"""
        if not LANGCHAIN_AVAILABLE:
            # Fallback to simple splitting
            return [content[i:i+1000] for i in range(0, len(content), 800)]

        # Get appropriate splitter
        if file_extension and file_extension in self.splitters:
            splitter = self.splitters[file_extension]
        else:
            splitter = self.splitters['default']

        # Split the content
        try:
            chunks = splitter.split_text(content)
            return [chunk.strip() for chunk in chunks if chunk.strip()]
        except Exception as e:
            logger.warning(f"LangChain splitting failed: {e}, falling back to simple splitting")
            return [content[i:i+1000] for i in range(0, len(content), 800)]
