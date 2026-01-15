"""
Document Manager for MCP Server

Handles document CRUD operations (Create, Read, Update, Delete) for the PrismWeave
document management system. Works with both captured documents and generated content.
"""

from datetime import datetime
from pathlib import Path
from typing import Optional

from prismweave_mcp.schemas.responses import (
    Document,
    DocumentMetadata,
)
from prismweave_mcp.utils.document_utils import (
    calculate_reading_time,
    count_words,
    generate_document_id,
    generate_filename,
    generate_frontmatter,
    normalize_tags,
    parse_frontmatter,
    safe_parse_datetime,
    validate_markdown,
)
from prismweave_mcp.utils.path_utils import (
    ensure_directory_exists,
    get_document_category,
    get_documents_root,
    get_relative_path,
    is_generated_document,
    list_markdown_files,
    resolve_document_path,
    validate_path_safety,
)
from src.core.config import Config
from src.core.embedding_store import EmbeddingStore


class DocumentManager:
    """Manage document CRUD operations"""

    def __init__(self, config: Config, embedding_store: Optional[EmbeddingStore] = None):
        """
        Initialize Document Manager

        Args:
            config: Application configuration
            embedding_store: Optional EmbeddingStore for efficient ID lookups
        """
        self.config = config
        self.docs_root = get_documents_root(config.mcp.paths.documents_root)
        self.embedding_store = embedding_store

    def get_document_by_id(self, document_id: str) -> Optional[Document]:
        """
        Get a document by its unique ID

        Args:
            document_id: Unique document identifier

        Returns:
            Document if found, None otherwise
        """
        # Get path from embedding store for efficiency
        if self.embedding_store:
            source_file = self._get_path_from_embedding_store(document_id)
            if source_file:
                doc_path = Path(source_file)
                if doc_path.exists() and validate_path_safety(doc_path, self.docs_root):
                    # Read and parse the document
                    file_content = doc_path.read_text(encoding="utf-8")
                    metadata, content = parse_frontmatter(file_content)
                    if metadata.get("id") == document_id or metadata.get("document_id") == document_id:
                        return self._build_document(doc_path, metadata, content)

        return None

    def _get_path_from_embedding_store(self, document_id: str) -> Optional[str]:
        """
        Get document path from embedding store by ID

        Args:
            document_id: Document ID to look up

        Returns:
            Path to the document file if found, None otherwise
        """
        try:
            if self.embedding_store and hasattr(self.embedding_store, "document_store"):
                # Get all documents and filter in memory
                # This is efficient enough for document lookup since we only need metadata
                all_docs = self.embedding_store.document_store.filter_documents()
                for doc in all_docs:
                    if doc.meta.get("id") == document_id:
                        return doc.meta.get("source_file")
        except Exception:
            pass

        return None

    def get_document_by_path(self, path: str) -> Optional[Document]:
        """
        Get a document by its file path

        Args:
            path: Relative or absolute file path

        Returns:
            Document if found, None otherwise

        Raises:
            ValueError: If path is unsafe or outside documents root
        """
        # First validate path safety before resolving
        # For absolute paths, check if they would be outside docs_root
        path_obj = Path(path)
        if path_obj.is_absolute():
            # Check if path is outside docs_root
            try:
                path_obj.relative_to(self.docs_root)
            except ValueError:
                raise ValueError(f"Path is not safe or outside documents root: {path}") from None
        elif ".." in str(path) or path.startswith("/"):
            # Detect path traversal attempts in relative paths
            # Try to resolve it to check safety
            test_path = (self.docs_root / path).resolve()
            try:
                test_path.relative_to(self.docs_root.resolve())
            except ValueError:
                raise ValueError(f"Path is not safe or outside documents root: {path}") from None

        # Resolve the path
        doc_path = resolve_document_path(path, self.docs_root)

        if doc_path is None:
            return None

        # Validate path safety (raises ValueError if unsafe)
        try:
            validate_path_safety(doc_path, self.docs_root)
        except ValueError as e:
            raise ValueError(f"Path is not safe or outside documents root: {path}") from e

        # Check if file exists
        if not doc_path.exists():
            return None

        # Parse and return document
        try:
            # Read file content
            file_content = doc_path.read_text(encoding="utf-8")
            # Parse frontmatter
            metadata, content = parse_frontmatter(file_content)
            return self._build_document(doc_path, metadata, content)
        except Exception as e:
            raise ValueError(f"Failed to parse document: {e}") from e

    def list_documents(
        self,
        category: Optional[str] = None,
        generated_only: bool = False,
        captured_only: bool = False,
        tags: Optional[list[str]] = None,
        sort_by: str = "created_date",
        sort_order: str = "desc",
        limit: Optional[int] = None,
    ) -> tuple[list[DocumentMetadata], int]:
        """
        List documents with filtering and sorting using ChromaDB

        Only returns documents that have been indexed in ChromaDB with embeddings.
        Documents without embeddings will not be included in results.

        Args:
            category: Filter by category (e.g., "tech", "general")
            generated_only: Only include generated documents
            captured_only: Only include captured documents
            tags: Filter by tags (documents must have all specified tags)
            sort_by: Field to sort by (created_date, modified_date, title, word_count)
            sort_order: Sort order (asc or desc)
            limit: Maximum number of results

        Returns:
            Tuple of (list of document metadata, total count before limit)
        """
        # Get all document chunks from ChromaDB
        if self.embedding_store is not None and hasattr(self.embedding_store, "document_store"):
            all_chunks = self.embedding_store.document_store.filter_documents()
        else:
            all_chunks = []

        # Track which files are in ChromaDB for efficient lookup
        chromadb_files = {}
        for chunk in all_chunks:
            source_file = chunk.meta.get("source_file")
            if source_file and source_file not in chromadb_files:
                chromadb_files[source_file] = chunk

        # Get all markdown files from disk to ensure completeness
        all_disk_files = list_markdown_files(self.docs_root)

        # Build document metadata list with filtering
        documents = []
        for doc_path in all_disk_files:
            try:
                # Verify file is safe
                validate_path_safety(doc_path, self.docs_root)

                # Apply generated/captured filters early
                is_generated = is_generated_document(doc_path, self.docs_root)
                if generated_only and not is_generated:
                    continue
                if captured_only and is_generated:
                    continue

                # Apply category filter early
                if category:
                    doc_category = get_document_category(doc_path, self.docs_root)
                    if doc_category != category:
                        continue

                # Read file for metadata and content
                file_content = doc_path.read_text(encoding="utf-8")
                metadata, content = parse_frontmatter(file_content)

                # Apply tag filter
                if tags:
                    doc_tags = metadata.get("tags", [])
                    if isinstance(doc_tags, str):
                        doc_tags = [t.strip() for t in doc_tags.split(",") if t.strip()]
                    if not all(tag in doc_tags for tag in tags):
                        continue

                # Build metadata object
                doc_metadata = self._build_document_metadata(doc_path, metadata, content)
                documents.append(doc_metadata)

            except Exception:
                # Skip files that can't be parsed
                continue

        # Sort documents
        reverse = sort_order == "desc"
        if sort_by in ("created_date", "created_at"):
            documents.sort(key=lambda d: d.created_at or datetime.min, reverse=reverse)
        elif sort_by in ("modified_date", "modified_at"):
            documents.sort(key=lambda d: d.modified_at or datetime.min, reverse=reverse)
        elif sort_by == "title":
            documents.sort(key=lambda d: d.title.lower(), reverse=reverse)
        elif sort_by == "word_count":
            documents.sort(key=lambda d: d.word_count or 0, reverse=reverse)

        total_count = len(documents)

        # Apply limit
        if limit is not None and limit > 0:
            documents = documents[:limit]

        return documents, total_count

    def create_document(
        self,
        title: str,
        content: str,
        tags: Optional[list[str]] = None,
        category: Optional[str] = None,
        metadata: Optional[dict] = None,
        custom_filename: Optional[str] = None,
    ) -> tuple[Document, Path]:
        """
        Create a new document in the generated/ folder

        Args:
            title: Document title
            content: Document content (markdown)
            tags: List of tags
            category: Document category (creates subdirectory in generated/)
            metadata: Additional metadata dictionary
            custom_filename: Custom filename (if not provided, generated from title)

        Returns:
            Tuple of (created Document object, file path)

        Raises:
            ValueError: If validation fails or file already exists
        """
        # Validate markdown content
        is_valid, error = validate_markdown(content)
        if not is_valid:
            raise ValueError(f"Invalid markdown content: {error}")

        # Determine target directory
        generated_dir = self.docs_root / self.config.mcp.paths.generated_dir
        target_dir = generated_dir / category if category else generated_dir

        # Ensure directory exists
        ensure_directory_exists(target_dir)

        # Generate filename
        if custom_filename:
            filename = custom_filename
            if not filename.endswith(".md"):
                filename += ".md"
        else:
            filename = generate_filename(title)

        file_path = target_dir / filename

        # Check if file already exists
        if file_path.exists():
            raise ValueError(f"Document already exists: {filename}")

        # Generate document ID
        doc_id = generate_document_id()

        # Build complete metadata
        full_metadata = {
            "id": doc_id,
            "title": title,
            "created_date": datetime.now().isoformat(),
            "modified_date": datetime.now().isoformat(),
            "tags": tags or [],
            "category": category or self.config.mcp.creation.default_category,
            "generated": True,
            "word_count": count_words(content),
        }

        # Add custom metadata
        if metadata:
            full_metadata.update(metadata)

        # Generate frontmatter and combine with content
        frontmatter_text = generate_frontmatter(full_metadata)
        full_content = f"{frontmatter_text}\n{content}"

        # Write file
        try:
            file_path.write_text(full_content, encoding="utf-8")
        except Exception as e:
            raise ValueError(f"Failed to write document: {e}") from e

        # Build and return document object
        document = self._build_document(file_path, full_metadata, content)

        return document, file_path

    def update_document(
        self,
        document_id: Optional[str] = None,
        path: Optional[str] = None,
        content: Optional[str] = None,
        title: Optional[str] = None,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict] = None,
        merge_metadata: bool = True,
    ) -> tuple[Document, Path]:
        """
        Update an existing document (generated documents only)

        Args:
            document_id: Document ID to update
            path: Path to document to update
            content: New content (if provided)
            title: New title (if provided)
            tags: New tags (if provided)
            metadata: Metadata updates
            merge_metadata: If True, merge with existing metadata; if False, replace

        Returns:
            Tuple of (updated Document object, file path)

        Raises:
            ValueError: If document not found, not generated, or validation fails
        """
        # Find the document
        if document_id:
            doc_path = None
            all_docs = list_markdown_files(self.docs_root)
            for candidate_path in all_docs:
                try:
                    # Read and check for duplicate ID
                    candidate_content = candidate_path.read_text(encoding="utf-8")
                    meta, _ = parse_frontmatter(candidate_content)
                    if meta.get("id") == document_id or meta.get("document_id") == document_id:
                        doc_path = candidate_path
                        break
                except Exception:
                    continue

            if doc_path is None:
                raise ValueError(f"Document not found with ID: {document_id}")

        elif path:
            doc_path = resolve_document_path(path, self.docs_root)
            if doc_path is None:
                raise ValueError(f"Document not found at path: {path}")
        else:
            raise ValueError("Must provide either document_id or path")

        # Validate path safety (raises ValueError if unsafe)
        try:
            validate_path_safety(doc_path, self.docs_root)
        except ValueError as e:
            raise ValueError(f"Path is not safe or outside documents root: {doc_path}") from e

        # Verify document is generated (only generated documents can be updated)
        if not is_generated_document(doc_path, self.docs_root):
            raise ValueError("Can only update generated documents. Captured documents are read-only.")

        # Parse existing document
        file_content = doc_path.read_text(encoding="utf-8")
        existing_metadata, existing_content = parse_frontmatter(file_content)

        # Prepare updates
        new_content = content if content is not None else existing_content
        new_metadata = dict(existing_metadata) if merge_metadata else {}

        # Update title if provided
        if title is not None:
            new_metadata["title"] = title

        # Update tags if provided
        if tags is not None:
            new_metadata["tags"] = tags

        # Update custom metadata
        if metadata:
            if merge_metadata:
                new_metadata.update(metadata)
            else:
                new_metadata = metadata

        # Update modified date
        new_metadata["modified_date"] = datetime.now().isoformat()

        # Update word count if content changed
        if content is not None:
            new_metadata["word_count"] = count_words(new_content)

        # Validate markdown if content changed
        if content is not None:
            is_valid, error = validate_markdown(new_content)
            if not is_valid:
                raise ValueError(f"Invalid markdown content: {error}")

        # Generate new frontmatter and combine with content
        frontmatter_text = generate_frontmatter(new_metadata)
        full_content = f"{frontmatter_text}\n{new_content}"

        # Write updated file
        try:
            doc_path.write_text(full_content, encoding="utf-8")
        except Exception as e:
            raise ValueError(f"Failed to update document: {e}") from e

        # Build and return updated document object
        document = self._build_document(doc_path, new_metadata, new_content)

        return document, doc_path

    def get_document_metadata(
        self, document_id: Optional[str] = None, path: Optional[str] = None
    ) -> Optional[DocumentMetadata]:
        """
        Get document metadata without full content

        Args:
            document_id: Document ID
            path: Document path

        Returns:
            DocumentMetadata if found, None otherwise
        """
        if document_id:
            doc = self.get_document_by_id(document_id)
        elif path:
            doc = self.get_document_by_path(path)
        else:
            raise ValueError("Must provide either document_id or path")

        if doc is None:
            return None

        return doc.metadata

    def _build_document(self, file_path: Path, metadata: dict, content: str) -> Document:
        """Build a Document object from file data"""
        doc_metadata = self._build_document_metadata(file_path, metadata, content)

        # Get relative path from documents root
        rel_path = get_relative_path(file_path, self.docs_root)

        return Document(
            id=metadata.get("id") or metadata.get("document_id", generate_document_id()),
            path=rel_path,
            content=content,
            metadata=doc_metadata,
        )

    def _build_document_metadata(self, file_path: Path, metadata: dict, content: str) -> DocumentMetadata:
        """Build DocumentMetadata from file data"""
        # Get file stats
        file_stat = file_path.stat()

        # Parse dates using utility function
        created_at = safe_parse_datetime(metadata.get("created_at") or metadata.get("created_date"))
        modified_at = safe_parse_datetime(metadata.get("modified_at") or metadata.get("modified_date"))

        # Fallback to file system modified time if no metadata
        if modified_at is None:
            modified_at = datetime.fromtimestamp(file_stat.st_mtime)

        # Get tags and normalize them
        tags = normalize_tags(metadata.get("tags", []))

        # Get category from path or metadata
        category = get_document_category(file_path, self.docs_root)
        if not category:
            category = metadata.get("category", self.config.mcp.creation.default_category)

        # Collect additional metadata fields not in the standard schema
        additional = {}
        excluded_keys = {
            "title",
            "tags",
            "category",
            "created_at",
            "created_date",
            "modified_at",
            "modified_date",
            "word_count",
            "reading_time",
            "source_url",
            "author",
            "id",
            "document_id",
            "generated",
        }
        for key, value in metadata.items():
            if key not in excluded_keys:
                additional[key] = value

        document_id = metadata.get("id") or metadata.get("document_id")
        if document_id:
            additional["id"] = document_id

        # Store relative path for downstream consumers that need it
        try:
            rel_path = get_relative_path(file_path, self.docs_root)
            additional["path"] = str(rel_path)
        except Exception:
            # Fallback: use absolute path if relative resolution fails
            additional["path"] = str(file_path)

        return DocumentMetadata(
            title=metadata.get("title", file_path.stem),
            created_at=created_at,
            modified_at=modified_at,
            tags=tags,
            category=category,
            word_count=metadata.get("word_count") or count_words(content),
            reading_time=metadata.get("reading_time") or calculate_reading_time(content),
            source_url=metadata.get("url") or metadata.get("source_url"),
            author=metadata.get("author"),
            additional=additional if additional else None,
        )
