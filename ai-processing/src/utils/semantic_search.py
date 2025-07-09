"""
Simplified semantic search utility for PrismWeave AI processing
Clean vector database interface without complex fallback mechanisms
"""

import asyncio
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import json
from dataclasses import dataclass

import chromadb
from chromadb.config import Settings

from .config_simplified import VectorConfig
from ..models.ollama_client_simplified import OllamaClient

logger = logging.getLogger(__name__)

@dataclass
class SearchResult:
    """Search result with metadata"""
    content: str
    metadata: Dict[str, Any]
    similarity: float
    document_id: str

class SemanticSearch:
    """Simplified semantic search using ChromaDB"""
    
    def __init__(self, config: VectorConfig):
        self.config = config
        self._client: Optional[chromadb.Client] = None
        self._collection: Optional[chromadb.Collection] = None
        self._embedding_client: Optional[OllamaClient] = None
    
    async def initialize(self):
        """Initialize the vector database and embedding client"""
        logger.info(f"Initializing semantic search with collection: {self.config.collection_name}")
        
        # Initialize ChromaDB client
        self._client = chromadb.PersistentClient(
            path=self.config.persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        try:
            self._collection = self._client.get_collection(
                name=self.config.collection_name
            )
            logger.info(f"Found existing collection with {self._collection.count()} documents")
        except Exception:
            logger.info("Creating new collection")
            self._collection = self._client.create_collection(
                name=self.config.collection_name,
                metadata={"description": "PrismWeave document embeddings"}
            )
        
        # Initialize embedding client
        self._embedding_client = OllamaClient()
    
    async def close(self):
        """Close the embedding client"""
        if self._embedding_client:
            await self._embedding_client.close()
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
    
    async def add_document(
        self,
        document_id: str,
        content: str,
        metadata: Dict[str, Any]
    ) -> bool:
        """Add a document to the search index"""
        if not self._collection or not self._embedding_client:
            await self.initialize()
        
        try:
            logger.debug(f"Adding document: {document_id}")
            
            # Generate embedding
            from .config_simplified import get_model_for_purpose
            embedding_model = get_model_for_purpose('embedding')
            
            embeddings = await self._embedding_client.embed(
                model=embedding_model,
                input_text=content
            )
            
            if not embeddings:
                logger.error(f"Failed to generate embedding for {document_id}")
                return False
            
            # Extract embedding from nested format: [[embedding]] -> [embedding]
            embedding = embeddings[0]
            if isinstance(embedding[0], list):
                embedding = embedding[0]
            
            # Convert datetime objects to strings for ChromaDB compatibility
            clean_metadata = {}
            for key, value in metadata.items():
                if hasattr(value, 'isoformat'):  # datetime objects
                    clean_metadata[key] = value.isoformat()
                elif isinstance(value, (str, int, float, bool)) or value is None:
                    clean_metadata[key] = value
                else:
                    # Convert other types to string
                    clean_metadata[key] = str(value)
            
            # Add to collection
            self._collection.add(
                ids=[document_id],
                embeddings=[embedding],
                documents=[content],
                metadatas=[clean_metadata]
            )
            
            logger.info(f"Successfully added document: {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add document {document_id}: {e}")
            return False
    
    async def search(
        self,
        query: str,
        max_results: Optional[int] = None,
        similarity_threshold: Optional[float] = None
    ) -> List[SearchResult]:
        """Search for documents similar to the query"""
        if not self._collection or not self._embedding_client:
            await self.initialize()
        
        max_results = max_results or self.config.max_results
        similarity_threshold = similarity_threshold or self.config.similarity_threshold
        
        try:
            logger.debug(f"Searching for: {query}")
            
            # Generate query embedding
            from .config_simplified import get_model_for_purpose
            embedding_model = get_model_for_purpose('embedding')
            
            query_embeddings = await self._embedding_client.embed(
                model=embedding_model,
                input_text=query
            )
            
            if not query_embeddings:
                logger.error("Failed to generate query embedding")
                return []
            
            # Handle nested embedding format from Ollama API
            query_embedding = query_embeddings[0]
            if isinstance(query_embedding, list) and len(query_embedding) == 1 and isinstance(query_embedding[0], list):
                # Handle nested format: [[[embedding]]] -> [embedding]
                query_embedding = query_embedding[0]
            
            # Search collection
            results = self._collection.query(
                query_embeddings=[query_embedding],
                n_results=max_results
            )
            
            # Process results
            search_results = []
            
            if results['ids'] and results['ids'][0]:
                for i, doc_id in enumerate(results['ids'][0]):
                    distance = results['distances'][0][i]
                    similarity = 1.0 - distance  # Convert distance to similarity
                    
                    if similarity >= similarity_threshold:
                        result = SearchResult(
                            content=results['documents'][0][i],
                            metadata=results['metadatas'][0][i] or {},
                            similarity=similarity,
                            document_id=doc_id
                        )
                        search_results.append(result)
            
            logger.info(f"Found {len(search_results)} results above threshold {similarity_threshold}")
            return search_results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    async def update_document(
        self,
        document_id: str,
        content: str,
        metadata: Dict[str, Any]
    ) -> bool:
        """Update an existing document in the search index"""
        if not self._collection:
            await self.initialize()
        
        try:
            # Delete existing document
            await self.delete_document(document_id)
            
            # Add updated document
            return await self.add_document(document_id, content, metadata)
            
        except Exception as e:
            logger.error(f"Failed to update document {document_id}: {e}")
            return False
    
    async def delete_document(self, document_id: str) -> bool:
        """Delete a document from the search index"""
        if not self._collection:
            await self.initialize()
        
        try:
            self._collection.delete(ids=[document_id])
            logger.info(f"Deleted document: {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete document {document_id}: {e}")
            return False
    
    async def get_document_count(self) -> int:
        """Get the total number of documents in the index"""
        if not self._collection:
            await self.initialize()
        
        try:
            return self._collection.count()
        except Exception as e:
            logger.error(f"Failed to get document count: {e}")
            return 0
    
    async def list_documents(self, limit: int = 100) -> List[Dict[str, Any]]:
        """List documents in the index"""
        if not self._collection:
            await self.initialize()
        
        try:
            results = self._collection.get(limit=limit)
            
            documents = []
            if results['ids']:
                for i, doc_id in enumerate(results['ids']):
                    doc = {
                        'id': doc_id,
                        'metadata': results['metadatas'][i] if results['metadatas'] else {},
                        'content_preview': (results['documents'][i][:100] + "...") if results['documents'] else ""
                    }
                    documents.append(doc)
            
            return documents
            
        except Exception as e:
            logger.error(f"Failed to list documents: {e}")
            return []
    
    async def clear_collection(self) -> bool:
        """Clear all documents from the collection"""
        if not self._collection:
            await self.initialize()
        
        try:
            # Delete the collection and recreate it
            self._client.delete_collection(name=self.config.collection_name)
            self._collection = self._client.create_collection(
                name=self.config.collection_name,
                metadata={"description": "PrismWeave document embeddings"}
            )
            
            logger.info("Collection cleared successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear collection: {e}")
            return False
    
    async def export_documents(self, output_path: Path) -> bool:
        """Export all documents to a JSON file"""
        try:
            documents = await self.list_documents(limit=10000)  # Get all documents
            
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(documents, f, indent=2, default=str)
            
            logger.info(f"Exported {len(documents)} documents to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export documents: {e}")
            return False
    
    async def import_documents(self, input_path: Path) -> int:
        """Import documents from a JSON file"""
        if not input_path.exists():
            logger.error(f"Import file not found: {input_path}")
            return 0
        
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                documents = json.load(f)
            
            imported_count = 0
            
            for doc in documents:
                success = await self.add_document(
                    document_id=doc['id'],
                    content=doc.get('content', ''),
                    metadata=doc.get('metadata', {})
                )
                
                if success:
                    imported_count += 1
            
            logger.info(f"Imported {imported_count}/{len(documents)} documents")
            return imported_count
            
        except Exception as e:
            logger.error(f"Failed to import documents: {e}")
            return 0
    
    async def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection"""
        stats = {
            'document_count': 0,
            'collection_name': self.config.collection_name,
            'persist_directory': self.config.persist_directory,
            'embedding_model': '',
            'initialized': self._collection is not None
        }
        
        try:
            if self._collection:
                stats['document_count'] = await self.get_document_count()
            
            from .config_simplified import get_model_for_purpose
            stats['embedding_model'] = get_model_for_purpose('embedding')
            
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            stats['error'] = str(e)
        
        return stats

# Convenience functions
async def quick_search(query: str, max_results: int = 5) -> List[SearchResult]:
    """Quick search with default configuration"""
    from .config_simplified import get_vector_config
    
    config = get_vector_config()
    async with SemanticSearch(config) as search:
        return await search.search(query, max_results)

async def quick_add_document(document_id: str, content: str, metadata: Dict[str, Any]) -> bool:
    """Quick document addition with default configuration"""
    from .config_simplified import get_vector_config
    
    config = get_vector_config()
    async with SemanticSearch(config) as search:
        return await search.add_document(document_id, content, metadata)
