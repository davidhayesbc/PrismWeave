#!/usr/bin/env python3
"""Query local prismweave MCP SearchTools for a given query string.

This script invokes the SearchTools directly (bypassing the HTTP/SSE layer)
so it can run a quick semantic search from the repository environment.
"""
import asyncio
import json
import sys

from prismweave_mcp.tools.search import SearchTools
from prismweave_mcp.schemas.requests import SearchDocumentsRequest
from src.core.config import load_config


async def main(query: str):
    config = load_config()
    st = SearchTools(config)
    await st.initialize()

    req = SearchDocumentsRequest(query=query, max_results=50)
    result = await st.search_documents(req)

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: query_mcp_search.py <query>")
        sys.exit(2)

    q = " ".join(sys.argv[1:])
    asyncio.run(main(q))
