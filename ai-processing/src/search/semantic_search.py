"""
Semantic search engine for PrismWeave documents
Provides vector-based search, hybrid search, and document recommendations
"""

import asyncio
import time
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass, asdict
import logging
import pickle
import hashlib

try:
    import numpy as np
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.feature_extraction.text import TfidfVectorizer
    import chromadb
    from chromadb.config import Settings
except ImportError:
    # Handle missing dependencies gracefully
    np = None
    cosine_similarity = None
    TfidfVectorizer = None
    chromadb = None
    Settings = None

from ..models.ollama_client_simplified import OllamaClient
from ..utils.config_simplified import get_config

logger = logging.getLogger(__name__)

@dataclass
class SearchResult:
    """Single search result"""
    document_path: str
    title: str
    similarity_score: float
    snippet: str
    metadata: Dict[str, Any]
    rank: int = 0

@dataclass 
class SearchResponse:
    """Complete search response"""
    query: str
    results: List[SearchResult]
    total_results: int
    search_time: float
    search_type: str = "semantic"
    
class SemanticSearch:
    """Main semantic search engine"""
    
    def __init__(self, config=None):
        # Always work with full config object
        if config is None:
            self.full_config = get_config()
        elif hasattr(config, 'ollama'):
            # Full config object
            self.full_config = config
        else:
            # Vector config only - load full config
            self.full_config = get_config()
        
        # Store references to sub-configs for convenience
        self.config = self.full_config.vector
        self.processing_config = self.full_config.processing
        self.ollama_config = self.full_config.ollama
        
        # Initialize Ollama client with full config
        self.ollama_client = OllamaClient(
            host=self.ollama_config.host,
            timeout=self.ollama_config.timeout
        )
        
        # Vector database setup
        self.chroma_client = None
        self.collection = None
        self.embedding_model = None
        self.tfidf_vectorizer = None
        
        # Document index
        self.document_index: Dict[str, Dict[str, Any]] = {}
        self.embeddings_cache: Dict[str, List[float]] = {}
        
        # Search statistics
        self.stats = {
            "total_searches": 0,
            "average_search_time": 0.0,
            "total_search_time": 0.0,
            "indexed_documents": 0
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.cleanup()
    
    async def initialize(self) -> bool:
        """Initialize the search engine"""
        try:
            # Initialize Ollama client
            await self.ollama_client.__aenter__()
            
            # Set up embedding model from ollama config
            self.embedding_model = self.ollama_config.models.get('embedding', 'nomic-embed-text')
            
            # Initialize vector database
            if self.config.persist_directory:
                await self._init_chroma()
            else:
                logger.info("Using in-memory vector storage")
            
            # Initialize TF-IDF for hybrid search
            if TfidfVectorizer:
                self.tfidf_vectorizer = TfidfVectorizer(
                    max_features=5000,
                    stop_words='english',
                    ngram_range=(1, 2)
                )
            
            logger.info("Semantic search engine initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize search engine: {e}")
            return False
    
    async def _init_chroma(self):
        """Initialize Chroma vector database"""
        if not chromadb:
            logger.warning("ChromaDB not available, using in-memory storage")
            return
        
        try:
            persist_dir = Path(self.config.persist_directory)
            persist_dir.mkdir(parents=True, exist_ok=True)
            
            self.chroma_client = chromadb.PersistentClient(
                path=str(persist_dir),
                settings=Settings(anonymized_telemetry=False)
            )
            
            collection_name = self.config.collection_name
            self.collection = self.chroma_client.get_or_create_collection(
                name=collection_name,
                metadata={"description": "PrismWeave document embeddings"}
            )
            
            logger.info(f"ChromaDB initialized with collection: {collection_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            self.chroma_client = None
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.ollama_client:
            await self.ollama_client.__aexit__(None, None, None)
    
    def _generate_document_id(self, file_path: str) -> str:
        """Generate unique document ID"""
        return hashlib.md5(file_path.encode()).hexdigest()
    
    def _extract_text_chunks(self, content: str, file_path: Optional[Path] = None, 
                            chunk_size: int = None, overlap: int = None) -> List[str]:
        """Extract text chunks for embedding using enhanced LangChain splitters"""
        try:
            # Import LangChain document processor
            from ..processors.langchain_document_processor import LangChainDocumentProcessor
            
            # Create processor instance with full config
            processor = LangChainDocumentProcessor(self.full_config)
            
            # Use the enhanced document processor directly with content
            if file_path:
                # Get the appropriate splitter for the file type
                splitter = processor.get_splitter_for_file(file_path)
                
                if hasattr(splitter, 'split_text'):
                    chunks = splitter.split_text(content)
                    logger.debug(f"Used {type(splitter).__name__} for {file_path.suffix} file: {len(chunks)} chunks")
                    return [chunk.strip() for chunk in chunks if chunk.strip()]
            
            # Fallback to content-based detection for appropriate splitter
            content_type = processor.detect_content_type(content, file_path or Path("temp.txt"))
            
            # Get splitter based on content type
            splitter_map = {
                'python_code': processor.splitters.get('.py'),
                'javascript_code': processor.splitters.get('.js'),
                'markdown': processor.splitters.get('.md'),
                'code_mixed': processor.splitters.get('.py'),  # Use Python splitter for mixed code
                'default': processor.splitters.get('default')
            }
            
            splitter = splitter_map.get(content_type, processor.splitters.get('default'))
            
            if splitter and hasattr(splitter, 'split_text'):
                chunks = splitter.split_text(content)
                logger.debug(f"Used {type(splitter).__name__} for {content_type} content: {len(chunks)} chunks")
                return [chunk.strip() for chunk in chunks if chunk.strip()]
            
            # Final fallback to basic RecursiveCharacterTextSplitter
            try:
                from langchain_text_splitters import RecursiveCharacterTextSplitter
                
                chunk_size = chunk_size or self.processing_config.chunk_size
                overlap = overlap or self.processing_config.chunk_overlap
                
                splitter = RecursiveCharacterTextSplitter(
                    chunk_size=chunk_size,
                    chunk_overlap=overlap,
                    separators=["\n\n", "\n", " ", ""],
                    length_function=len,
                    is_separator_regex=False,
                )
                
                chunks = splitter.split_text(content)
                logger.debug(f"Used fallback RecursiveCharacterTextSplitter: {len(chunks)} chunks")
                return [chunk.strip() for chunk in chunks if chunk.strip()]
            except ImportError:
                logger.warning("LangChain text splitters not available, using basic chunking")
                return self._enhanced_basic_chunking(content, file_path, chunk_size, overlap)
            
        except ImportError as e:
            logger.warning(f"LangChain not available ({e}), using enhanced basic chunking")
            return self._enhanced_basic_chunking(content, file_path, chunk_size, overlap)
        except Exception as e:
            logger.error(f"Error in LangChain chunking ({e}), falling back to basic chunking")
            return self._enhanced_basic_chunking(content, file_path, chunk_size, overlap)
    
    def _enhanced_basic_chunking(self, content: str, file_path: Optional[Path] = None,
                                chunk_size: int = None, overlap: int = None) -> List[str]:
        """Enhanced basic text chunking with file-type awareness"""
        chunk_size = chunk_size or self.processing_config.chunk_size
        overlap = overlap or self.processing_config.chunk_overlap
        
        if len(content) <= chunk_size:
            return [content]
        
        # Determine content type for smarter splitting
        file_ext = file_path.suffix.lower() if file_path else '.txt'
        
        # File-type specific separators for better chunking
        if file_ext in ['.py']:
            # Python files - respect function, class, and import boundaries
            separators = [
                '\nclass ',           # Class definitions
                '\ndef ',             # Function definitions
                '\nasync def ',       # Async function definitions
                '\nfrom ',            # Import statements
                '\nimport ',          # Import statements
                '\n\n',               # Double newlines (paragraphs)
                '\n    def ',         # Indented methods
                '\n    async def ',   # Indented async methods
                '\n',                 # Single newlines
                ' ',                  # Spaces
                ''                    # Character-level fallback
            ]
        elif file_ext in ['.js', '.ts', '.jsx', '.tsx']:
            # JavaScript/TypeScript files
            separators = [
                '\nclass ',           # Class definitions
                '\nfunction ',        # Function definitions
                '\nconst ',           # Const declarations
                '\nlet ',             # Let declarations
                '\nvar ',             # Var declarations
                '\nimport ',          # ES6 imports
                '\nexport ',          # ES6 exports
                '\n\n',               # Double newlines
                '\n',                 # Single newlines
                ' ',                  # Spaces
                ''                    # Character-level fallback
            ]
        elif file_ext in ['.md', '.markdown']:
            # Markdown files - respect header boundaries
            separators = [
                '\n# ',               # H1 headers
                '\n## ',              # H2 headers
                '\n### ',             # H3 headers
                '\n#### ',            # H4 headers
                '\n##### ',           # H5 headers
                '\n###### ',          # H6 headers
                '\n\n',               # Double newlines (paragraphs)
                '\n',                 # Single newlines
                '. ',                 # Sentence boundaries
                ' ',                  # Spaces
                ''                    # Character-level fallback
            ]
        elif file_ext in ['.json']:
            # JSON files - respect object boundaries
            separators = [
                '\n  },\n',           # End of nested objects
                '\n},\n',             # End of main objects
                '\n[\n',              # Array starts
                '\n],\n',             # Array ends
                '\n\n',               # Double newlines
                '\n',                 # Single newlines
                ' ',                  # Spaces
                ''                    # Character-level fallback
            ]
        elif file_ext in ['.yaml', '.yml']:
            # YAML files - respect key boundaries
            separators = [
                '\n---\n',            # Document separators
                '\n- ',               # List items
                '\n  ',               # Indented content
                '\n\n',               # Double newlines
                '\n',                 # Single newlines
                ' ',                  # Spaces
                ''                    # Character-level fallback
            ]
        else:
            # Default text splitting with smart boundaries
            separators = [
                '\n\n',               # Paragraph breaks
                '\n',                 # Line breaks
                '. ',                 # Sentence boundaries
                '! ',                 # Exclamation sentence boundaries
                '? ',                 # Question sentence boundaries
                ' ',                  # Word boundaries
                ''                    # Character-level fallback
            ]
        
        # Split using prioritized separators
        chunks = []
        start = 0
        
        while start < len(content):
            end = min(start + chunk_size, len(content))
            chunk = content[start:end]
            
            # Try to break at appropriate boundaries
            if end < len(content):
                best_break = -1
                best_separator = ""
                
                # Try separators in order of preference
                for separator in separators:
                    if not separator:  # Character-level fallback
                        break
                    
                    break_point = chunk.rfind(separator)
                    if break_point > start + chunk_size // 3:  # At least 1/3 into chunk
                        best_break = break_point + len(separator)
                        best_separator = separator
                        break
                
                if best_break > -1:
                    chunk = content[start:start + best_break]
                    end = start + best_break
                    logger.debug(f"Split at '{best_separator.strip() or 'char-level'}' boundary")
            
            chunk_text = chunk.strip()
            if chunk_text:
                chunks.append(chunk_text)
            
            start = end - overlap
            
            if start >= len(content):
                break
        
        logger.debug(f"Enhanced basic chunking for {file_ext} created {len(chunks)} chunks")
        return [chunk for chunk in chunks if chunk.strip()]
    
    def _basic_chunk_text(self, content: str, chunk_size: int = None, overlap: int = None) -> List[str]:
        """Fallback basic text chunking when LangChain is not available"""
        chunk_size = chunk_size or self.processing_config.chunk_size
        overlap = overlap or self.processing_config.chunk_overlap
        
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
    
    async def index_document(self, file_path: Path, content: str, metadata: Dict[str, Any]) -> bool:
        """Index a document for search"""
        try:
            doc_id = self._generate_document_id(str(file_path))
            
            # Extract text chunks using LangChain-enhanced chunking
            chunks = self._extract_text_chunks(content, file_path)
            if not chunks:
                logger.warning(f"No content chunks extracted from {file_path}")
                return False
            
            # Generate embeddings
            embeddings = await self.ollama_client.embed(
                model=self.embedding_model,
                input_text=chunks
            )
            
            if not embeddings:
                logger.error(f"Failed to generate embeddings for {file_path}")
                return False
            
            # Store in vector database
            if self.collection:
                # ChromaDB storage
                chunk_ids = [f"{doc_id}_{i}" for i in range(len(chunks))]
                
                # Clean metadata to ensure ChromaDB compatibility (only str, int, float, bool, None)
                clean_metadata = {}
                for key, value in metadata.items():
                    if isinstance(value, (str, int, float, bool)) or value is None:
                        clean_metadata[key] = value
                    elif isinstance(value, list):
                        # Convert lists to comma-separated strings
                        clean_metadata[key] = ", ".join(str(item) for item in value)
                    else:
                        # Convert other types to string
                        clean_metadata[key] = str(value)
                
                chunk_metadatas = [
                    {
                        **clean_metadata,
                        "chunk_index": i,
                        "chunk_text": chunks[i][:200] + "..." if len(chunks[i]) > 200 else chunks[i],
                        "document_path": str(file_path),
                        "file_type": file_path.suffix.lower(),
                        "chunk_size": len(chunks[i]),
                        "total_chunks": len(chunks)
                    }
                    for i in range(len(chunks))
                ]
                
                self.collection.add(
                    embeddings=embeddings,
                    documents=chunks,
                    metadatas=chunk_metadatas,
                    ids=chunk_ids
                )
            else:
                # In-memory storage
                self.embeddings_cache[doc_id] = {
                    "embeddings": embeddings,
                    "chunks": chunks,
                    "metadata": metadata,
                    "file_path": str(file_path)
                }
            
            # Update document index
            self.document_index[doc_id] = {
                "file_path": str(file_path),
                "title": metadata.get("title", file_path.stem),
                "metadata": metadata,
                "chunk_count": len(chunks),
                "indexed_at": time.time(),
                "file_type": file_path.suffix.lower()
            }
            
            self.stats["indexed_documents"] += 1
            logger.info(f"Successfully indexed document with LangChain chunking: {file_path} ({len(chunks)} chunks)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to index document {file_path}: {e}")
            return False
    
    async def search(
        self,
        query: str,
        max_results: int = None,
        similarity_threshold: float = None,
        search_type: str = "semantic"
    ) -> SearchResponse:
        """Perform semantic search"""
        start_time = time.time()
        
        max_results = max_results or self.config.max_results
        similarity_threshold = similarity_threshold or self.config.similarity_threshold
        
        try:
            if search_type == "semantic":
                results = await self._semantic_search(query, max_results, similarity_threshold)
            elif search_type == "hybrid":
                results = await self._hybrid_search(query, max_results, similarity_threshold)
            else:
                results = await self._keyword_search(query, max_results)
            
            search_time = time.time() - start_time
            
            # Update statistics
            self.stats["total_searches"] += 1
            self.stats["total_search_time"] += search_time
            self.stats["average_search_time"] = (
                self.stats["total_search_time"] / self.stats["total_searches"]
            )
            
            return SearchResponse(
                query=query,
                results=results,
                total_results=len(results),
                search_time=search_time,
                search_type=search_type
            )
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return SearchResponse(
                query=query,
                results=[],
                total_results=0,
                search_time=time.time() - start_time,
                search_type=search_type
            )
    
    async def _semantic_search(
        self,
        query: str,
        max_results: int,
        similarity_threshold: float
    ) -> List[SearchResult]:
        """Pure semantic search using embeddings"""
        try:
            # Generate query embedding
            query_embeddings = await self.ollama_client.embed(
                model=self.embedding_model,
                input_text=[query]
            )
            
            if not query_embeddings:
                return []
            
            query_embedding = query_embeddings[0]
            results = []
            
            if self.collection:
                # ChromaDB search
                search_results = self.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=max_results,
                    include=['documents', 'metadatas', 'distances']
                )
                
                if search_results['documents']:
                    for i, (doc, metadata, distance) in enumerate(zip(
                        search_results['documents'][0],
                        search_results['metadatas'][0],
                        search_results['distances'][0]
                    )):
                        similarity = 1 - distance  # Convert distance to similarity
                        if similarity >= similarity_threshold:
                            results.append(SearchResult(
                                document_path=metadata['document_path'],
                                title=metadata.get('title', 'Untitled'),
                                similarity_score=similarity,
                                snippet=metadata.get('chunk_text', doc[:200]),
                                metadata=metadata,
                                rank=i + 1
                            ))
            
            else:
                # In-memory search
                if not np or not cosine_similarity:
                    logger.warning("NumPy/scikit-learn not available for in-memory search")
                    return []
                
                for doc_id, doc_data in self.embeddings_cache.items():
                    doc_embeddings = doc_data["embeddings"]
                    
                    for i, embedding in enumerate(doc_embeddings):
                        similarity = cosine_similarity([query_embedding], [embedding])[0][0]
                        
                        if similarity >= similarity_threshold:
                            chunk_text = doc_data["chunks"][i]
                            results.append(SearchResult(
                                document_path=doc_data["file_path"],
                                title=doc_data["metadata"].get("title", "Untitled"),
                                similarity_score=similarity,
                                snippet=chunk_text[:200] + "..." if len(chunk_text) > 200 else chunk_text,
                                metadata=doc_data["metadata"],
                                rank=0
                            ))
            
            # Sort by similarity score
            results.sort(key=lambda x: x.similarity_score, reverse=True)
            
            # Update ranks
            for i, result in enumerate(results):
                result.rank = i + 1
            
            return results[:max_results]
            
        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            return []
    
    async def _hybrid_search(
        self,
        query: str,
        max_results: int,
        similarity_threshold: float
    ) -> List[SearchResult]:
        """Hybrid search combining semantic and keyword search"""
        try:
            # Get semantic results
            semantic_results = await self._semantic_search(query, max_results * 2, similarity_threshold * 0.8)
            
            # Get keyword results (placeholder - would need full-text index)
            keyword_results = await self._keyword_search(query, max_results)
            
            # Combine and re-rank results
            # Use default weights since SearchConfig is not used in simplified config
            semantic_weight = 0.7
            keyword_weight = 0.3
            
            combined_results = {}
            
            # Add semantic results
            for result in semantic_results:
                key = result.document_path
                combined_results[key] = result
                result.similarity_score *= semantic_weight
            
            # Add keyword results
            for result in keyword_results:
                key = result.document_path
                if key in combined_results:
                    # Combine scores
                    combined_results[key].similarity_score += result.similarity_score * keyword_weight
                else:
                    result.similarity_score *= keyword_weight
                    combined_results[key] = result
            
            # Sort by combined score
            final_results = list(combined_results.values())
            final_results.sort(key=lambda x: x.similarity_score, reverse=True)
            
            # Update ranks
            for i, result in enumerate(final_results):
                result.rank = i + 1
            
            return final_results[:max_results]
            
        except Exception as e:
            logger.error(f"Hybrid search failed: {e}")
            return await self._semantic_search(query, max_results, similarity_threshold)
    
    async def _keyword_search(self, query: str, max_results: int) -> List[SearchResult]:
        """Simple keyword-based search (placeholder implementation)"""
        results = []
        query_words = query.lower().split()
        
        for doc_id, doc_info in self.document_index.items():
            # Simple keyword matching in title and metadata
            title = doc_info.get("title", "").lower()
            metadata_text = " ".join(str(v) for v in doc_info.get("metadata", {}).values()).lower()
            
            score = 0.0
            for word in query_words:
                if word in title:
                    score += 2.0  # Higher weight for title matches
                if word in metadata_text:
                    score += 1.0
            
            if score > 0:
                results.append(SearchResult(
                    document_path=doc_info["file_path"],
                    title=doc_info["title"],
                    similarity_score=score / len(query_words),  # Normalize score
                    snippet=f"Keyword matches in {doc_info['title']}",
                    metadata=doc_info["metadata"],
                    rank=0
                ))
        
        # Sort by score
        results.sort(key=lambda x: x.similarity_score, reverse=True)
        
        # Update ranks
        for i, result in enumerate(results):
            result.rank = i + 1
        
        return results[:max_results]
    
    async def find_similar_documents(
        self,
        document_path: str,
        max_results: int = 5
    ) -> List[SearchResult]:
        """Find documents similar to the given document"""
        try:
            doc_id = self._generate_document_id(document_path)
            
            if doc_id not in self.document_index:
                logger.warning(f"Document not found in index: {document_path}")
                return []
            
            # Use document title as query for now
            # In a full implementation, we'd use the document's own embedding
            doc_title = self.document_index[doc_id]["title"]
            
            results = await self._semantic_search(doc_title, max_results + 1, 0.5)
            
            # Remove the source document from results
            filtered_results = [r for r in results if r.document_path != document_path]
            
            return filtered_results[:max_results]
            
        except Exception as e:
            logger.error(f"Failed to find similar documents: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get search engine statistics"""
        stats = self.stats.copy()
        stats["document_index_size"] = len(self.document_index)
        stats["embeddings_cache_size"] = len(self.embeddings_cache)
        
        if self.collection:
            try:
                stats["chroma_collection_count"] = self.collection.count()
            except:
                stats["chroma_collection_count"] = 0
        
        return stats
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on search components"""
        health = {
            "search_engine_ready": True,
            "ollama_available": False,
            "embedding_model_ready": False,
            "vector_db_ready": False,
            "indexed_documents": len(self.document_index),
            "statistics": self.get_statistics()
        }
        
        try:
            # Check Ollama availability
            health["ollama_available"] = await self.ollama_client.is_available()
            
            # Check embedding model
            if health["ollama_available"]:
                health["embedding_model_ready"] = await self.ollama_client.model_exists(self.embedding_model)
            
            # Check vector database
            if self.collection:
                try:
                    health["vector_db_ready"] = True
                    health["vector_db_count"] = self.collection.count()
                except:
                    health["vector_db_ready"] = False
            elif self.embeddings_cache:
                health["vector_db_ready"] = True
        
        except Exception as e:
            health["error"] = str(e)
            health["search_engine_ready"] = False
        
        return health

    # Compatibility methods for CLI
    async def add_document(self, document_id: str, content: str, metadata: Dict[str, Any]) -> bool:
        """Add document to search index (compatibility method)"""
        return await self.index_document(Path(document_id), content, metadata)

    async def close(self):
        """Close search engine (compatibility method)"""
        await self.cleanup()

# Convenience functions
async def quick_search(query: str, max_results: int = 10) -> List[SearchResult]:
    """Quick search with automatic search engine management"""
    async with SemanticSearch() as search_engine:
        response = await search_engine.search(query, max_results)
        return response.results
