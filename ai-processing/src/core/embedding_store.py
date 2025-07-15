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


class EmbeddingStore:
    """Store and retrieve document embeddings using ChromaDB via LangChain"""
    
    def __init__(self, config: Config):
        self.config = config
        
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
