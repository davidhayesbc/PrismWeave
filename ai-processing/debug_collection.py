#!/usr/bin/env python3
import asyncio
import sys
sys.path.append('src')
from src.search.semantic_search import SemanticSearch
from src.utils.config_simplified import get_config
import hashlib

async def check_collection():
    config = get_config()
    async with SemanticSearch(config) as search:
        count = await search.get_document_count()
        print(f'Total documents in collection: {count}')
        
        # Look for README.md specifically
        readme_hash = hashlib.md5('README.md'.encode()).hexdigest()
        print(f'\nLooking for README.md with hash: {readme_hash}')
        
        if count > 0:
            docs = await search.list_documents(limit=100)
            
            # Find README entries
            readme_docs = [d for d in docs if readme_hash in d.get('id', '')]
            print(f'\nFound {len(readme_docs)} README.md entries:')
            for doc in readme_docs:
                doc_id = doc.get('id', 'none')
                print(f'  ID: {doc_id}')
                metadata = doc.get('metadata', {})
                document_path = metadata.get('document_path', 'none')
                print(f'  Document path: {document_path}')
                content = doc.get('content_preview', '')
                print(f'  Content: {content[:100]}...')
                print()
            
            if not readme_docs:
                print('No README.md entries found!')
                print('\nAll document IDs (first 10):')
                for i, doc in enumerate(docs[:10]):
                    doc_id = doc.get('id', 'none')
                    print(f'{i+1}. {doc_id}')

if __name__ == '__main__':
    asyncio.run(check_collection())
