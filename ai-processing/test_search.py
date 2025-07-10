#!/usr/bin/env python3
import asyncio
import sys
import logging
sys.path.append('src')
from src.search.semantic_search import SemanticSearch
from src.utils.config_simplified import get_config

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

async def test_search_with_known_content():
    config = get_config()
    async with SemanticSearch(config) as search:
        print("=== Testing Search Functionality ===")
        
        # First check if search engine is properly initialized
        print(f"Collection available: {search.collection is not None}")
        print(f"Ollama client available: {search.ollama_client is not None}")
        print(f"Embedding model: {search.embedding_model}")
        
        # Check if embedding model is available
        if search.ollama_client:
            model_exists = await search.ollama_client.model_exists(search.embedding_model)
            print(f"Embedding model '{search.embedding_model}' exists: {model_exists}")
        
        # Get a document to test with
        docs = await search.list_documents(limit=5)
        print(f"Found {len(docs)} documents in collection")
        
        if docs:
            doc = docs[0]
            content = doc.get('content_preview', '')
            print(f'\nTesting search with content from: {doc.get("id")}')
            print(f'Content preview: {content[:100]}...')
            
            if content:
                # Test with a simple query first
                simple_query = "Databricks"
                print(f'\nSimple search query: "{simple_query}"')
                
                try:
                    result = await search.search(simple_query, max_results=5)
                    print(f'Search returned {len(result.results)} results')
                    
                    if result.results:
                        for i, res in enumerate(result.results):
                            print(f'  {i+1}. {res.document_path} (score: {res.similarity_score:.3f})')
                    else:
                        print('No results found')
                        
                        # Try to check what went wrong
                        print("\nDebugging search process...")
                        
                        # Test embedding generation
                        embeddings = await search.ollama_client.embed(
                            model=search.embedding_model,
                            input_text=[simple_query]
                        )
                        print(f"Query embedding generated: {len(embeddings) > 0 and len(embeddings[0]) > 0}")
                        
                        if embeddings and len(embeddings[0]) > 0:
                            print(f"Embedding dimension: {len(embeddings[0])}")
                        
                except Exception as e:
                    print(f"Search failed with error: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print('No content to search with')
        else:
            print('No documents found to test with')

if __name__ == '__main__':
    asyncio.run(test_search_with_known_content())
