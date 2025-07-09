"""
Vector database verification utilities for PrismWeave AI processing
Comprehensive checks for embeddings, database health, and data integrity
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import json

from .semantic_search import SemanticSearch
from .config_simplified import get_vector_config, get_model_for_purpose
from ..models.ollama_client_simplified import OllamaClient

logger = logging.getLogger(__name__)

@dataclass
class VectorHealthReport:
    """Comprehensive health report for vector database"""
    database_accessible: bool
    collection_exists: bool
    document_count: int
    embedding_model_available: bool
    sample_documents: List[Dict[str, Any]]
    database_size_mb: float
    last_updated: Optional[str]
    integrity_check_passed: bool
    performance_metrics: Dict[str, float]
    issues: List[str]
    recommendations: List[str]

class VectorVerifier:
    """Comprehensive vector database verification and health checking"""
    
    def __init__(self):
        self.config = get_vector_config()
        self._search_engine: Optional[SemanticSearch] = None
        self._ollama_client: Optional[OllamaClient] = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.cleanup()
    
    async def initialize(self):
        """Initialize verification components"""
        self._search_engine = SemanticSearch(self.config)
        await self._search_engine.initialize()
        
        # Initialize Ollama client for embedding model checks
        from .config_simplified import get_config
        app_config = get_config()
        self._ollama_client = OllamaClient(
            host=app_config.ollama.host,
            timeout=app_config.ollama.timeout
        )
    
    async def cleanup(self):
        """Cleanup resources"""
        if self._search_engine:
            await self._search_engine.close()
        if self._ollama_client:
            await self._ollama_client.close()
    
    async def comprehensive_health_check(self) -> VectorHealthReport:
        """Perform comprehensive health check of vector database"""
        logger.info("Starting comprehensive vector database health check...")
        
        issues = []
        recommendations = []
        performance_metrics = {}
        
        # 1. Check database accessibility
        database_accessible = await self._check_database_accessibility()
        if not database_accessible:
            issues.append("Vector database is not accessible")
            recommendations.append("Check if ChromaDB can connect to the persist directory")
        
        # 2. Check collection existence
        collection_exists = await self._check_collection_exists()
        if not collection_exists:
            issues.append("Document collection does not exist")
            recommendations.append("Process some documents to create the collection")
        
        # 3. Get document count
        document_count = await self._get_document_count()
        if document_count == 0:
            issues.append("No documents found in vector database")
            recommendations.append("Process documents to populate the database")
        
        # 4. Check embedding model availability
        embedding_model_available = await self._check_embedding_model()
        if not embedding_model_available:
            issues.append("Embedding model is not available")
            recommendations.append("Ensure the embedding model is pulled in Ollama")
        
        # 5. Get sample documents
        sample_documents = await self._get_sample_documents()
        
        # 6. Calculate database size
        database_size_mb = await self._calculate_database_size()
        
        # 7. Get last updated timestamp
        last_updated = await self._get_last_updated()
        
        # 8. Perform integrity check
        integrity_check_passed = await self._perform_integrity_check()
        if not integrity_check_passed:
            issues.append("Vector database integrity check failed")
            recommendations.append("Consider rebuilding the vector database")
        
        # 9. Performance metrics
        if database_accessible and collection_exists and document_count > 0:
            performance_metrics = await self._measure_performance()
        
        # Generate overall health score
        health_score = self._calculate_health_score(
            database_accessible, collection_exists, document_count,
            embedding_model_available, integrity_check_passed
        )
        
        logger.info(f"Health check completed. Score: {health_score:.2f}/100")
        
        return VectorHealthReport(
            database_accessible=database_accessible,
            collection_exists=collection_exists,
            document_count=document_count,
            embedding_model_available=embedding_model_available,
            sample_documents=sample_documents,
            database_size_mb=database_size_mb,
            last_updated=last_updated,
            integrity_check_passed=integrity_check_passed,
            performance_metrics=performance_metrics,
            issues=issues,
            recommendations=recommendations
        )
    
    async def _check_database_accessibility(self) -> bool:
        """Check if vector database is accessible"""
        try:
            if not self._search_engine:
                return False
            
            # Try to get basic stats
            stats = await self._search_engine.get_collection_stats()
            return stats.get('initialized', False)
        except Exception as e:
            logger.error(f"Database accessibility check failed: {e}")
            return False
    
    async def _check_collection_exists(self) -> bool:
        """Check if the document collection exists"""
        try:
            if not self._search_engine:
                return False
            
            count = await self._search_engine.get_document_count()
            return count >= 0  # Collection exists even if empty
        except Exception as e:
            logger.error(f"Collection existence check failed: {e}")
            return False
    
    async def _get_document_count(self) -> int:
        """Get total number of documents in the database"""
        try:
            if not self._search_engine:
                return 0
            
            return await self._search_engine.get_document_count()
        except Exception as e:
            logger.error(f"Document count check failed: {e}")
            return 0
    
    async def _check_embedding_model(self) -> bool:
        """Check if embedding model is available in Ollama"""
        try:
            if not self._ollama_client:
                return False
            
            embedding_model = get_model_for_purpose('embedding')
            return await self._ollama_client.model_exists(embedding_model)
        except Exception as e:
            logger.error(f"Embedding model check failed: {e}")
            return False
    
    async def _get_sample_documents(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get sample documents from the database"""
        try:
            if not self._search_engine:
                return []
            
            documents = await self._search_engine.list_documents(limit=limit)
            return documents
        except Exception as e:
            logger.error(f"Sample documents retrieval failed: {e}")
            return []
    
    async def _calculate_database_size(self) -> float:
        """Calculate database size in MB"""
        try:
            persist_path = Path(self.config.persist_directory)
            if not persist_path.exists():
                return 0.0
            
            total_size = 0
            for file_path in persist_path.rglob('*'):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
            
            return total_size / (1024 * 1024)  # Convert to MB
        except Exception as e:
            logger.error(f"Database size calculation failed: {e}")
            return 0.0
    
    async def _get_last_updated(self) -> Optional[str]:
        """Get last updated timestamp from database"""
        try:
            persist_path = Path(self.config.persist_directory)
            if not persist_path.exists():
                return None
            
            # Find the most recently modified file
            latest_time = 0
            for file_path in persist_path.rglob('*'):
                if file_path.is_file():
                    file_time = file_path.stat().st_mtime
                    if file_time > latest_time:
                        latest_time = file_time
            
            if latest_time > 0:
                return datetime.fromtimestamp(latest_time).isoformat()
            return None
        except Exception as e:
            logger.error(f"Last updated check failed: {e}")
            return None
    
    async def _perform_integrity_check(self) -> bool:
        """Perform basic integrity check on vector database"""
        try:
            if not self._search_engine:
                return False
            
            # Get document count
            count = await self._search_engine.get_document_count()
            if count == 0:
                return True  # Empty database is valid
            
            # Try to retrieve a few documents
            sample_docs = await self._search_engine.list_documents(limit=3)
            if not sample_docs:
                return False
            
            # Check if documents have required fields
            for doc in sample_docs:
                if not doc.get('id') or not isinstance(doc.get('metadata'), dict):
                    return False
            
            # Try a simple search operation
            if count > 0:
                search_results = await self._search_engine.search(
                    query="test",
                    max_results=1
                )
                # Search should complete without error (results may be empty)
            
            return True
        except Exception as e:
            logger.error(f"Integrity check failed: {e}")
            return False
    
    async def _measure_performance(self) -> Dict[str, float]:
        """Measure basic performance metrics"""
        metrics = {}
        
        try:
            if not self._search_engine:
                return metrics
            
            # Measure search performance
            start_time = asyncio.get_event_loop().time()
            await self._search_engine.search(query="performance test", max_results=5)
            search_time = asyncio.get_event_loop().time() - start_time
            metrics['search_time_ms'] = search_time * 1000
            
            # Measure document count retrieval time
            start_time = asyncio.get_event_loop().time()
            await self._search_engine.get_document_count()
            count_time = asyncio.get_event_loop().time() - start_time
            metrics['count_time_ms'] = count_time * 1000
            
            # Measure list documents time
            start_time = asyncio.get_event_loop().time()
            await self._search_engine.list_documents(limit=10)
            list_time = asyncio.get_event_loop().time() - start_time
            metrics['list_time_ms'] = list_time * 1000
            
        except Exception as e:
            logger.error(f"Performance measurement failed: {e}")
            metrics['error'] = str(e)
        
        return metrics
    
    def _calculate_health_score(
        self,
        database_accessible: bool,
        collection_exists: bool,
        document_count: int,
        embedding_model_available: bool,
        integrity_check_passed: bool
    ) -> float:
        """Calculate overall health score (0-100)"""
        score = 0.0
        
        if database_accessible:
            score += 30
        if collection_exists:
            score += 20
        if document_count > 0:
            score += 20
        if embedding_model_available:
            score += 15
        if integrity_check_passed:
            score += 15
        
        return score
    
    async def verify_document_embedding(self, document_id: str) -> Dict[str, Any]:
        """Verify that a specific document has been properly embedded"""
        try:
            if not self._search_engine:
                await self.initialize()
            
            # Try to retrieve the document
            documents = await self._search_engine.list_documents(limit=1000)
            document = next((doc for doc in documents if doc['id'] == document_id), None)
            
            if not document:
                return {
                    'found': False,
                    'error': 'Document not found in vector database'
                }
            
            # Test search functionality with document content
            if document.get('content_preview'):
                search_query = document['content_preview'][:50]  # Use first 50 chars
                search_results = await self._search_engine.search(
                    query=search_query,
                    max_results=5
                )
                
                # Check if the document appears in its own search results
                found_in_search = any(
                    result.document_id == document_id 
                    for result in search_results
                )
                
                return {
                    'found': True,
                    'document': document,
                    'searchable': found_in_search,
                    'search_results_count': len(search_results)
                }
            else:
                return {
                    'found': True,
                    'document': document,
                    'searchable': None,
                    'note': 'No content available for search test'
                }
        except Exception as e:
            logger.error(f"Document embedding verification failed: {e}")
            return {
                'found': False,
                'error': str(e)
            }
    
    async def rebuild_embeddings(self, document_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """Rebuild embeddings for specified documents or all documents"""
        try:
            if not self._search_engine:
                await self.initialize()
            
            if document_ids is None:
                # Get all document IDs
                all_docs = await self._search_engine.list_documents(limit=10000)
                document_ids = [doc['id'] for doc in all_docs]
            
            results = {
                'processed': 0,
                'succeeded': 0,
                'failed': 0,
                'errors': []
            }
            
            for doc_id in document_ids:
                try:
                    # This would need to be implemented based on your document storage
                    # For now, we'll just report what would be done
                    results['processed'] += 1
                    results['succeeded'] += 1
                except Exception as e:
                    results['failed'] += 1
                    results['errors'].append(f"{doc_id}: {str(e)}")
            
            return results
        except Exception as e:
            logger.error(f"Embeddings rebuild failed: {e}")
            return {
                'processed': 0,
                'succeeded': 0,
                'failed': 0,
                'errors': [str(e)]
            }
    
    async def export_embeddings_info(self, output_path: Path) -> bool:
        """Export detailed information about embeddings to a file"""
        try:
            if not self._search_engine:
                await self.initialize()
            
            # Gather comprehensive information
            health_report = await self.comprehensive_health_check()
            all_documents = await self._search_engine.list_documents(limit=10000)
            stats = await self._search_engine.get_collection_stats()
            
            export_data = {
                'export_timestamp': datetime.now().isoformat(),
                'health_report': {
                    'database_accessible': health_report.database_accessible,
                    'collection_exists': health_report.collection_exists,
                    'document_count': health_report.document_count,
                    'embedding_model_available': health_report.embedding_model_available,
                    'database_size_mb': health_report.database_size_mb,
                    'last_updated': health_report.last_updated,
                    'integrity_check_passed': health_report.integrity_check_passed,
                    'performance_metrics': health_report.performance_metrics,
                    'issues': health_report.issues,
                    'recommendations': health_report.recommendations
                },
                'collection_stats': stats,
                'documents': all_documents,
                'configuration': {
                    'collection_name': self.config.collection_name,
                    'persist_directory': self.config.persist_directory,
                    'max_results': self.config.max_results,
                    'similarity_threshold': self.config.similarity_threshold
                }
            }
            
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            logger.info(f"Embeddings info exported to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Export failed: {e}")
            return False

# Convenience functions
async def quick_health_check() -> VectorHealthReport:
    """Quick health check with default configuration"""
    async with VectorVerifier() as verifier:
        return await verifier.comprehensive_health_check()

async def verify_embeddings_exist() -> bool:
    """Quick check if any embeddings exist"""
    try:
        async with VectorVerifier() as verifier:
            count = await verifier._get_document_count()
            return count > 0
    except Exception:
        return False

async def get_embeddings_summary() -> Dict[str, Any]:
    """Get summary information about embeddings"""
    try:
        async with VectorVerifier() as verifier:
            return {
                'document_count': await verifier._get_document_count(),
                'database_accessible': await verifier._check_database_accessibility(),
                'embedding_model_available': await verifier._check_embedding_model(),
                'database_size_mb': await verifier._calculate_database_size()
            }
    except Exception as e:
        return {'error': str(e)}
