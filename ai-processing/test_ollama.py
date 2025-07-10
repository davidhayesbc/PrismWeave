#!/usr/bin/env python3

import asyncio
import aiohttp
import ollama

async def test_direct_api():
    print("Testing direct HTTP API...")
    async with aiohttp.ClientSession() as session:
        async with session.get('http://localhost:11434/api/tags') as response:
            data = await response.json()
            models = data.get('models', [])
            print(f'Found {len(models)} models via direct API:')
            for model in models[:3]:  # Show first 3
                print(f'  - {model["name"]}')
            
            # Check if our model is there
            model_names = [m["name"] for m in models]
            if "nomic-embed-text:latest" in model_names:
                print("✓ nomic-embed-text:latest found in direct API")
            else:
                print("✗ nomic-embed-text:latest NOT found in direct API")

def test_sync_client():
    print("\nTesting ollama sync client...")
    try:
        client = ollama.Client(host='http://localhost:11434')
        models = client.list()
        print(f"Sync client response type: {type(models)}")
        print(f"Sync client response: {models}")
        if isinstance(models, dict) and 'models' in models:
            model_list = models['models']
            print(f'Found {len(model_list)} models via sync client')
            for model in model_list[:3]:
                print(f'  - {model.get("name", "NO_NAME")}')
        else:
            print("Unexpected response format from sync client")
    except Exception as e:
        print(f"Sync client error: {e}")

async def test_async_client():
    print("\nTesting ollama async client...")
    try:
        client = ollama.AsyncClient(host='http://localhost:11434')
        models = await client.list()
        print(f"Async client response type: {type(models)}")
        print(f"Async client response: {models}")
        if isinstance(models, dict) and 'models' in models:
            model_list = models['models']
            print(f'Found {len(model_list)} models via async client')
            for model in model_list[:3]:
                print(f'  - {model.get("name", "NO_NAME")}')
        else:
            print("Unexpected response format from async client")
    except Exception as e:
        print(f"Async client error: {e}")

async def main():
    await test_direct_api()
    test_sync_client()
    await test_async_client()

if __name__ == "__main__":
    asyncio.run(main())
