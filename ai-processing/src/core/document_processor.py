"""
Document processor using LangChain for text splitting and document loading
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
import frontmatter
from datetime import datetime

# LangChain imports
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    TextLoader,
    PyPDFLoader,
    Docx2txtLoader,
    BSHTMLLoader,
)
from langchain_core.documents import Document

from .config import Config
from .git_tracker import GitTracker


class DocumentProcessor:
    """Process documents and split them into chunks for embedding"""
    
    def __init__(self, config: Config, git_tracker: Optional[GitTracker] = None):
        self.config = config
        self.git_tracker = git_tracker
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        # Document loader mapping
        self.loaders = {
            '.md': self._load_markdown,
            '.txt': TextLoader,
            '.pdf': PyPDFLoader,
            '.docx': Docx2txtLoader,
            '.html': BSHTMLLoader,
            '.htm': BSHTMLLoader,
        }
    
    def process_document(self, file_path: Path) -> List[Document]:
        """
        Process a document file and return chunks as LangChain Documents
        
        Args:
            file_path: Path to the document file
            
        Returns:
            List of Document objects with content and metadata
        """
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_extension = file_path.suffix.lower()
        
        if file_extension not in self.loaders:
            raise ValueError(f"Unsupported file type: {file_extension}")
        
        # Load document based on file type
        if file_extension == '.md':
            documents = self._load_markdown(file_path)
        else:
            loader_class = self.loaders[file_extension]
            loader = loader_class(str(file_path))
            documents = loader.load()
        
        # Split documents into chunks
        chunks = []
        for doc in documents:
            doc_chunks = self.text_splitter.split_documents([doc])
            chunks.extend(doc_chunks)
        
        # Add file metadata to all chunks
        for i, chunk in enumerate(chunks):
            # Basic file metadata
            chunk.metadata.update({
                'file_path': str(file_path),
                'file_name': file_path.name,
                'file_extension': file_extension,
                'file_size': file_path.stat().st_size,
                'processed_at': datetime.now().isoformat(),
                'chunk_index': i,
                'total_chunks': len(chunks),
            })
            
            # Add git metadata if git_tracker is available
            if self.git_tracker:
                try:
                    last_commit = self.git_tracker.get_file_last_commit_hash(file_path)
                    content_hash = self.git_tracker.get_file_content_hash(file_path)
                    
                    chunk.metadata.update({
                        'git_commit_hash': last_commit,
                        'content_hash': content_hash,
                        'last_modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                    })
                except Exception as e:
                    # Don't fail processing if git operations fail
                    print(f"Warning: Failed to get git metadata for {file_path}: {e}")
        
        return chunks
    
    def _load_markdown(self, file_path: Path) -> List[Document]:
        """
        Load markdown file with frontmatter support
        
        Args:
            file_path: Path to markdown file
            
        Returns:
            List containing single Document with content and frontmatter metadata
        """
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)
            
            # Create document with content and metadata from frontmatter
            metadata = dict(post.metadata)
            metadata.update({
                'source': str(file_path),
                'title': post.metadata.get('title', file_path.stem),
            })
            
            document = Document(
                page_content=post.content,
                metadata=metadata
            )
            
            return [document]
            
        except Exception as e:
            # Fallback to regular text loading if frontmatter parsing fails
            print(f"Warning: Failed to parse frontmatter in {file_path}, treating as plain markdown: {e}")
            
            loader = TextLoader(str(file_path), encoding='utf-8')
            documents = loader.load()
            
            # Add basic metadata
            for doc in documents:
                doc.metadata.update({
                    'title': file_path.stem,
                    'source': str(file_path),
                })
            
            return documents
