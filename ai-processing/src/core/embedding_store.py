"""
Embedding store using Haystack's ChromaDB integration
"""

import uuid
from collections.abc import Sequence
from pathlib import Path
from typing import Any, Dict, List, Optional

# Haystack imports
from haystack import Document
from haystack_integrations.components.embedders.ollama import OllamaDocumentEmbedder, OllamaTextEmbedder
from haystack_integrations.components.retrievers.chroma import ChromaEmbeddingRetriever
from haystack_integrations.document_stores.chroma import ChromaDocumentStore

from .config import Config
from .git_tracker import GitTracker


class EmbeddingStore:
    """Store and retrieve document embeddings using ChromaDB via Haystack"""

    def __init__(self, config: Config, git_tracker: Optional[GitTracker] = None):
        self.config = config
        self.git_tracker = git_tracker

        # Initialize Haystack ChromaDB document store
        self.persist_directory = Path(config.chroma_db_path)
        self.persist_directory.mkdir(parents=True, exist_ok=True)

        self.document_store = ChromaDocumentStore(
            collection_name=config.collection_name,
            persist_path=str(self.persist_directory),
        )

        # Initialize Ollama embedders for Haystack
        self.document_embedder = OllamaDocumentEmbedder(url=config.ollama_host, model=config.embedding_model)

        self.text_embedder = OllamaTextEmbedder(url=config.ollama_host, model=config.embedding_model)

        # Initialize retriever for semantic search
        self.retriever = ChromaEmbeddingRetriever(document_store=self.document_store)

    def _clean_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Clean metadata to ensure ChromaDB compatibility.

        ChromaDB supports: str, int, float, bool, and in some versions lists/dicts.
        For consistency in downstream filtering, lists are normalized to
        comma-separated strings.
        """
        cleaned = {}
        for key, value in metadata.items():
            if value is None:
                continue
            elif isinstance(value, (str, int, float, bool)):
                cleaned[key] = value
            elif isinstance(value, list):
                # Normalize lists to comma-separated strings
                try:
                    cleaned[key] = ", ".join(str(item) for item in value)
                except (TypeError, ValueError):
                    cleaned[key] = str(value)
            elif isinstance(value, dict):
                cleaned[key] = str(value)
            else:
                # Convert other types to string
                cleaned[key] = str(value)
        return cleaned

    def add_document(self, file_path: Path, chunks: List[Document]) -> None:
        """
        Add document chunks to the document store with embeddings

        Args:
            file_path: Path to the original document file
            chunks: List of Document chunks to add
        """

        if not chunks:
            print(f"No chunks to add for {file_path}")
            return

        # Clean and prepare metadata for all chunks
        for i, chunk in enumerate(chunks):
            # Clean the metadata to ensure ChromaDB compatibility
            cleaned_metadata = self._clean_metadata(chunk.meta)

            # Add additional metadata
            cleaned_metadata.update(
                {
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "chunk_id": f"{file_path.stem}_{i}_{uuid.uuid4().hex[:8]}",
                    "source_file": str(file_path),
                }
            )

            # Update the chunk with cleaned metadata
            chunk.meta = cleaned_metadata

        try:
            # Generate embeddings for chunks
            embedded_result = self.document_embedder.run(documents=chunks)
            embedded_documents = embedded_result.get("documents", chunks)

            # Write documents to store
            self.document_store.write_documents(embedded_documents)
            print(f"Added {len(chunks)} chunks from {file_path.name}")

            # Mark file as processed in git tracker if available
            if self.git_tracker:
                try:
                    self.git_tracker.mark_file_processed(file_path)
                    print(f"Marked {file_path.name} as processed in git tracker")
                except (OSError, ValueError) as e:
                    print(f"Warning: Failed to mark file as processed in git tracker: {e}")

        except (ConnectionError, TimeoutError) as e:
            raise RuntimeError(f"Failed to connect to embedding service for {file_path}: {e}") from e
        except (ValueError, KeyError) as e:
            raise RuntimeError(f"Invalid document data for {file_path}: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Failed to add chunks for {file_path}: {e}") from e

    def search_similar(self, query: str, k: int = 5) -> List[Document]:
        """
        Search for similar documents

        Args:
            query: Search query
            k: Number of results to return

        Returns:
            List of similar Documents
        """

        try:
            # Embed the query text
            query_result = self.text_embedder.run(text=query)
            query_embedding = query_result.get("embedding")

            # Retrieve similar documents
            retrieval_result = self.retriever.run(query_embedding=query_embedding, top_k=k)

            return retrieval_result.get("documents", [])

        except Exception as e:
            print(f"Search failed: {e}")
            return []

    def search_similar_with_scores(self, query: str, k: int = 5) -> List[tuple[Document, float]]:
        """
        Search for similar documents with relevance scores

        Args:
            query: Search query
            k: Number of results to return

        Returns:
            List of tuples (Document, score) where higher score means more similar
        """

        try:
            # Embed the query text
            query_result = self.text_embedder.run(text=query)
            query_embedding = query_result.get("embedding")

            # Retrieve similar documents with scores
            # Note: Haystack ChromaEmbeddingRetriever returns documents with scores as doc.score attribute
            retrieval_result = self.retriever.run(query_embedding=query_embedding, top_k=k)

            documents = retrieval_result.get("documents", [])
            # ChromaDB returns squared L2 distance (lower is more similar)
            # Typical range: 0-1000+ for 768-dimensional vectors
            # Convert to similarity score (0-1 range, higher is better)
            results = []
            for doc in documents:
                distance = doc.score if hasattr(doc, "score") else 1000.0
                # Convert distance to similarity using exponential decay
                # This maps small distances (good matches) to scores near 1.0
                # and large distances to scores near 0.0
                similarity = 1.0 - min(distance / 1000.0, 1.0)  # Normalize to 0-1 range
                results.append((doc, similarity))
            return results

        except Exception as e:
            print(f"Search with scores failed: {e}")
            return []

    def verify_embeddings(self) -> Dict[str, Any]:
        """
        Verify that embeddings are stored correctly

        Returns:
            Dictionary with verification results
        """

        try:
            # Get document count
            count = self.document_store.count_documents()

            # Try a simple search to verify functionality
            if count > 0:
                test_results = self.search_similar("test", k=1)
                search_works = len(test_results) > 0
            else:
                search_works = None

            return {
                "status": "success",
                "document_count": count,
                "search_functional": search_works,
                "collection_name": self.config.collection_name,
                "persist_directory": str(self.persist_directory),
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "document_count": 0,
                "search_functional": False,
            }

    def clear_collection(self) -> None:
        """Clear all documents from the collection"""

        try:
            # Get all document IDs and delete them
            all_docs = self.document_store.filter_documents()

            if all_docs:
                doc_ids = [doc.id for doc in all_docs if doc.id]
                if doc_ids:
                    self.document_store.delete_documents(doc_ids)

            print("Collection cleared successfully")

        except Exception as e:
            print(f"Failed to clear collection: {e}")

    def get_document_count(self) -> int:
        """Get the number of documents in the collection"""

        try:
            return self.document_store.count_documents()
        except Exception:
            return 0

    def list_documents(self, max_documents: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        List documents in the collection with their metadata

        Args:
            max_documents: Maximum number of documents to return (None for all)

        Returns:
            List of document metadata dictionaries
        """

        try:
            # Get documents from the store
            all_docs = self.document_store.filter_documents()

            # Limit if requested
            if max_documents:
                all_docs = all_docs[:max_documents]

            documents = []
            for doc in all_docs:
                doc_info = {
                    "id": doc.id,
                    "metadata": doc.meta,
                    "content_preview": doc.content[:200] + "..." if len(doc.content) > 200 else doc.content,
                    "content_length": len(doc.content),
                }
                documents.append(doc_info)

            return documents

        except Exception as e:
            print(f"Failed to list documents: {e}")
            return []

    def remove_file_documents(self, file_path: Path) -> bool:
        """
        Remove all document chunks for a specific file from the document store

        Args:
            file_path: Path to the file whose chunks should be removed

        Returns:
            True if documents were found and removed
        """
        try:
            # Find all chunks for this file
            filters = {"field": "meta.source_file", "operator": "==", "value": str(file_path)}
            matching_docs = self.document_store.filter_documents(filters=filters)

            if matching_docs:
                # Delete the chunks
                doc_ids = [doc.id for doc in matching_docs if doc.id]
                if doc_ids:
                    self.document_store.delete_documents(doc_ids)
                    print(f"Removed {len(doc_ids)} chunks for {file_path.name}")
                    return True
            else:
                print(f"No existing chunks found for {file_path.name}")
                return False

        except Exception as e:
            print(f"Warning: Failed to remove existing chunks for {file_path}: {e}")
            return False

    def get_file_document_count(self, file_path: Path) -> int:
        """
        Get the number of document chunks for a specific file

        Args:
            file_path: Path to the file

        Returns:
            Number of chunks for this file
        """
        try:
            filters = {"field": "meta.source_file", "operator": "==", "value": str(file_path)}
            matching_docs = self.document_store.filter_documents(filters=filters)
            return len(matching_docs)
        except Exception:
            return 0

    def get_unique_source_files(self) -> List[str]:
        """
        Get a list of unique source files in the collection

        Returns:
            List of unique source file paths
        """

        try:
            # Get all documents
            all_docs = self.document_store.filter_documents()

            source_files = set()
            for doc in all_docs:
                if "source_file" in doc.meta:
                    source_files.add(doc.meta["source_file"])

            return sorted(list(source_files))

        except Exception as e:
            print(f"Failed to get source files: {e}")
            return []

    def get_article_embedding(self, file_path: Path) -> Optional[List[float]]:
        """Compute a representative embedding for an article by averaging its chunks.

        This keeps the primary storage at chunk level while still providing a
        stable article-level vector for visualization and coarse search.
        """

        try:
            filters = {"field": "meta.source_file", "operator": "==", "value": str(file_path)}
            docs = self.document_store.filter_documents(filters=filters)
        except Exception:
            return None

        vectors: List[Sequence[float]] = []
        for doc in docs:
            embedding = getattr(doc, "embedding", None)
            if isinstance(embedding, list) and embedding:
                vectors.append(embedding)

        if not vectors:
            return None

        dim = len(vectors[0])
        sums = [0.0] * dim
        for vec in vectors:
            if len(vec) != dim:
                continue
            for i, value in enumerate(vec):
                sums[i] += float(value)

        count = float(len(vectors))
        return [s / count for s in sums]
