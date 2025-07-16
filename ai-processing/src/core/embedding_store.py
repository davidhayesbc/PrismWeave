"""
Embedding store using LangChain's ChromaDB integration
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
import uuid

# LangChain imports
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

from .config import Config
from .git_tracker import GitTracker


class EmbeddingStore:
    """Store and retrieve document embeddings using ChromaDB via LangChain"""
    
    def __init__(self, config: Config, git_tracker: Optional[GitTracker] = None):
        self.config = config
        self.git_tracker = git_tracker
        
        # Initialize Ollama embeddings
        self.embeddings = OllamaEmbeddings(
            base_url=config.ollama_host,
            model=config.embedding_model
        )
        
        # Initialize ChromaDB
        self.persist_directory = Path(config.chroma_db_path)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        self.vector_store = Chroma(
            collection_name=config.collection_name,
            embedding_function=self.embeddings,
            persist_directory=str(self.persist_directory)
        )
    
    def _clean_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Clean metadata to ensure ChromaDB compatibility"""
        cleaned = {}
        for key, value in metadata.items():
            if value is None:
                continue
            elif isinstance(value, (str, int, float, bool)):
                cleaned[key] = value
            elif isinstance(value, list):
                # Convert lists to comma-separated strings
                cleaned[key] = ", ".join(str(item) for item in value)
            else:
                # Convert other types to string
                cleaned[key] = str(value)
        return cleaned

    def add_document(self, file_path: Path, chunks: List[Document]) -> None:
        """
        Add document chunks to the vector store
        
        Args:
            file_path: Path to the original document file
            chunks: List of Document chunks to add
        """
        
        if not chunks:
            print(f"No chunks to add for {file_path}")
            return
        
        # Generate unique IDs for each chunk
        chunk_ids = []
        for i, chunk in enumerate(chunks):
            # Create a unique ID based on file path and chunk index
            chunk_id = f"{file_path.stem}_{i}_{uuid.uuid4().hex[:8]}"
            chunk_ids.append(chunk_id)
            
            # Clean the metadata to ensure ChromaDB compatibility
            cleaned_metadata = self._clean_metadata(chunk.metadata)
            
            # Add additional metadata
            cleaned_metadata.update({
                'chunk_index': i,
                'total_chunks': len(chunks),
                'chunk_id': chunk_id,
                'source_file': str(file_path),
            })
            
            # Update the chunk with cleaned metadata
            chunk.metadata = cleaned_metadata
        
        try:
            # Add chunks to vector store
            self.vector_store.add_documents(chunks, ids=chunk_ids)
            print(f"Added {len(chunks)} chunks from {file_path.name}")
            
            # Mark file as processed in git tracker if available
            if self.git_tracker:
                try:
                    self.git_tracker.mark_file_processed(file_path)
                    print(f"Marked {file_path.name} as processed in git tracker")
                except Exception as e:
                    print(f"Warning: Failed to mark file as processed in git tracker: {e}")
            
        except Exception as e:
            raise Exception(f"Failed to add chunks for {file_path}: {e}")
    
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
            results = self.vector_store.similarity_search(query, k=k)
            return results
            
        except Exception as e:
            print(f"Search failed: {e}")
            return []
    
    def verify_embeddings(self) -> Dict[str, Any]:
        """
        Verify that embeddings are stored correctly
        
        Returns:
            Dictionary with verification results
        """
        
        try:
            # Get collection info
            collection = self.vector_store._collection
            count = collection.count()
            
            # Try a simple similarity search to verify functionality
            if count > 0:
                test_results = self.vector_store.similarity_search("test", k=1)
                search_works = len(test_results) > 0
            else:
                search_works = None
            
            return {
                'status': 'success',
                'document_count': count,
                'search_functional': search_works,
                'collection_name': self.config.collection_name,
                'persist_directory': str(self.persist_directory),
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'document_count': 0,
                'search_functional': False,
            }
    
    def clear_collection(self) -> None:
        """Clear all documents from the collection"""
        
        try:
            # Delete the collection and recreate it
            self.vector_store.delete_collection()
            
            # Recreate the vector store
            self.vector_store = Chroma(
                collection_name=self.config.collection_name,
                embedding_function=self.embeddings,
                persist_directory=str(self.persist_directory)
            )
            
            print("Collection cleared successfully")
            
        except Exception as e:
            print(f"Failed to clear collection: {e}")
    
    def get_document_count(self) -> int:
        """Get the number of documents in the collection"""
        
        try:
            return self.vector_store._collection.count()
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
            collection = self.vector_store._collection
            
            # Get all document IDs and metadata
            # ChromaDB get() without specifying ids returns all documents
            if max_documents:
                result = collection.get(limit=max_documents, include=['metadatas', 'documents'])
            else:
                result = collection.get(include=['metadatas', 'documents'])
            
            documents = []
            for i, (doc_id, metadata, content) in enumerate(zip(
                result['ids'], 
                result['metadatas'], 
                result['documents']
            )):
                doc_info = {
                    'id': doc_id,
                    'metadata': metadata,
                    'content_preview': content[:200] + '...' if len(content) > 200 else content,
                    'content_length': len(content)
                }
                documents.append(doc_info)
            
            return documents
            
        except Exception as e:
            print(f"Failed to list documents: {e}")
            return []
    
    def remove_file_documents(self, file_path: Path) -> bool:
        """
        Remove all document chunks for a specific file from the vector store
        
        Args:
            file_path: Path to the file whose chunks should be removed
            
        Returns:
            True if documents were found and removed
        """
        try:
            collection = self.vector_store._collection
            
            # Find all chunks for this file
            result = collection.get(
                where={"source_file": str(file_path)},
                include=['ids']
            )
            
            if result['ids']:
                # Delete the chunks
                collection.delete(ids=result['ids'])
                print(f"Removed {len(result['ids'])} chunks for {file_path.name}")
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
            collection = self.vector_store._collection
            result = collection.get(
                where={"source_file": str(file_path)},
                include=['ids']
            )
            return len(result['ids'])
        except Exception:
            return 0
    
    def get_unique_source_files(self) -> List[str]:
        """
        Get a list of unique source files in the collection
        
        Returns:
            List of unique source file paths
        """
        
        try:
            collection = self.vector_store._collection
            result = collection.get(include=['metadatas'])
            
            source_files = set()
            for metadata in result['metadatas']:
                if 'source_file' in metadata:
                    source_files.add(metadata['source_file'])
            
            return sorted(list(source_files))
            
        except Exception as e:
            print(f"Failed to get source files: {e}")
            return []
