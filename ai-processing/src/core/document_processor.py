"""
Document processor using Haystack for text splitting and document conversion
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import frontmatter

# Haystack imports
from haystack import Document
from haystack.components.converters import (
    HTMLToDocument,
    PyPDFToDocument,
    TextFileToDocument,
)
from haystack.components.preprocessors import DocumentSplitter

try:
    from haystack.components.converters import DocxToDocument  # type: ignore

    _DOCX_AVAILABLE = True
except ImportError:  # pragma: no cover - optional dependency
    DocxToDocument = None  # type: ignore
    _DOCX_AVAILABLE = False

from .config import Config
from .git_tracker import GitTracker


class DocumentProcessor:
    """Process documents and split them into chunks for embedding"""

    def __init__(self, config: Config, git_tracker: Optional[GitTracker] = None):
        self.config = config
        self.git_tracker = git_tracker

        # Initialize text splitter using Haystack's DocumentSplitter
        self.text_splitter = DocumentSplitter(
            split_by="word",
            split_length=config.chunk_size // 5,  # Approximate words from characters
            split_overlap=config.chunk_overlap // 5,
        )

        # Document converter mapping for Haystack
        self.converters = {
            ".md": self._load_markdown,
            ".txt": TextFileToDocument(),
            ".pdf": PyPDFToDocument(),
            ".html": HTMLToDocument(),
            ".htm": HTMLToDocument(),
        }

        if _DOCX_AVAILABLE:
            try:
                self.converters[".docx"] = DocxToDocument()
            except Exception as exc:  # pragma: no cover - optional dependency runtime check
                # Provide graceful degradation if python-docx or other deps are missing
                print(f"Warning: Docx support unavailable ({exc})")

        # Backward compatibility for older interfaces that referenced loaders directly
        self.loaders = self.converters

    def process_document(self, file_path: Path) -> List[Document]:
        """
        Process a document file and return chunks as Haystack Documents

        Args:
            file_path: Path to the document file

        Returns:
            List of Document objects with content and metadata
        """

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        file_extension = file_path.suffix.lower()

        if file_extension not in self.converters:
            raise ValueError(f"Unsupported file type: {file_extension}")

        # Load document based on file type
        if file_extension == ".md":
            documents = self._load_markdown(file_path)
        else:
            converter = self.converters[file_extension]
            result = converter.run(sources=[file_path])
            documents = result.get("documents", [])

        # Ensure metadata alias is available on all base documents
        documents = [self._ensure_metadata_alias(doc) for doc in documents]

        # Split documents into chunks
        chunks = []
        for doc in documents:
            split_result = self.text_splitter.run(documents=[doc])
            doc_chunks = split_result.get("documents", [])
            chunks.extend(self._ensure_metadata_alias(chunk) for chunk in doc_chunks)

        # Add file metadata to all chunks
        for i, chunk in enumerate(chunks):
            # Basic file metadata
            chunk.meta.update(
                {
                    "file_path": str(file_path),
                    "file_name": file_path.name,
                    "file_extension": file_extension,
                    "file_size": file_path.stat().st_size,
                    "processed_at": datetime.now().isoformat(),
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                }
            )

            # Add git metadata if git_tracker is available
            if self.git_tracker:
                try:
                    last_commit = self.git_tracker.get_file_last_commit_hash(file_path)
                    content_hash = self.git_tracker.get_file_content_hash(file_path)

                    chunk.meta.update(
                        {
                            "git_commit_hash": last_commit,
                            "content_hash": content_hash,
                            "last_modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                        }
                    )
                except Exception as e:
                    # Don't fail processing if git operations fail
                    print(f"Warning: Failed to get git metadata for {file_path}: {e}")

            # Keep metadata alias in sync after updates
            self._ensure_metadata_alias(chunk)

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
            with open(file_path, "r", encoding="utf-8") as f:
                post = frontmatter.load(f)

            # Create Haystack document with content and metadata from frontmatter
            metadata = dict(post.metadata)
            metadata.update(
                {
                    "source": str(file_path),
                    "title": post.metadata.get("title", file_path.stem),
                }
            )

            document = Document(content=post.content, meta=metadata)

            return [self._ensure_metadata_alias(document)]

        except Exception as e:
            # Fallback to regular text loading if frontmatter parsing fails
            print(f"Warning: Failed to parse frontmatter in {file_path}, treating as plain markdown: {e}")

            converter = TextFileToDocument()
            result = converter.run(sources=[file_path])
            documents = result.get("documents", [])

            # Add basic metadata
            for doc in documents:
                doc.meta.update(
                    {
                        "title": file_path.stem,
                        "source": str(file_path),
                    }
                )
                self._ensure_metadata_alias(doc)

            return documents

    @staticmethod
    def _ensure_metadata_alias(document: Document) -> Document:
        """Ensure Document exposes a metadata attribute mirroring meta for backward compatibility."""

        # Avoid clobbering existing attributes while keeping alias in sync
        setattr(document, "metadata", document.meta)
        return document
