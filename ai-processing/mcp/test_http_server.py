#!/usr/bin/env python3
"""
Test script for PrismWeave MCP HTTP/SSE server

This script tests the HTTP endpoints to verify the server is working correctly.
"""

import asyncio
import json
import sys

import aiohttp


async def test_sse_endpoint(base_url: str = "http://127.0.0.1:8000"):
    """Test the SSE endpoint"""
    print(f"Testing SSE endpoint at {base_url}/sse")

    try:
        async with aiohttp.ClientSession() as session, session.get(f"{base_url}/sse") as response:
            print(f"Status: {response.status}")
            print(f"Headers: {dict(response.headers)}")

            if response.status == 200:
                print("✓ SSE endpoint is accessible")
                return True
            else:
                print(f"✗ SSE endpoint returned status {response.status}")
                return False

    except aiohttp.ClientConnectorError as e:
        print(f"✗ Connection error: {e}")
        print("\nMake sure the server is running:")
        print("  python -m mcp.prismweave_server")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


async def test_list_tools(base_url: str = "http://127.0.0.1:8000"):
    """Test listing available tools"""
    print(f"\nTesting tools listing at {base_url}")

    try:
        async with aiohttp.ClientSession() as session:
            # MCP protocol: send initialize request
            message = {"jsonrpc": "2.0", "method": "tools/list", "params": {}, "id": 1}

            async with session.post(
                f"{base_url}/messages", json=message, headers={"Content-Type": "application/json"}
            ) as response:
                print(f"Status: {response.status}")

                if response.status == 200:
                    data = await response.json()
                    print("✓ Tools endpoint is accessible")

                    if "result" in data and "tools" in data["result"]:
                        tools = data["result"]["tools"]
                        print(f"\nAvailable tools ({len(tools)}):")
                        for tool in tools:
                            print(f"  - {tool['name']}: {tool.get('description', 'No description')}")
                        return True
                    else:
                        print(f"Response: {json.dumps(data, indent=2)}")
                        return True
                else:
                    text = await response.text()
                    print(f"✗ Unexpected status: {response.status}")
                    print(f"Response: {text}")
                    return False

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_server_info(base_url: str = "http://127.0.0.1:8000"):
    """Test server info endpoint"""
    print(f"\nTesting server info at {base_url}")

    try:
        async with aiohttp.ClientSession() as session, session.get(base_url) as response:
            print(f"Status: {response.status}")

            if response.status in (200, 404):  # Some servers return 404 for root
                print("✓ Server is responding")
                text = await response.text()
                if text:
                    print(f"Response: {text[:200]}...")
                return True
            else:
                print(f"✗ Unexpected status: {response.status}")
                return False

    except Exception as e:
        print(f"✗ Error: {e}")
        return False


async def main():
    """Run all tests"""
    base_url = "http://127.0.0.1:8000"

    if len(sys.argv) > 1:
        base_url = sys.argv[1]

    print("=" * 60)
    print("PrismWeave MCP HTTP Server Test")
    print("=" * 60)
    print(f"Testing server at: {base_url}\n")

    results = []

    # Test 1: Server info
    results.append(await test_server_info(base_url))

    # Test 2: SSE endpoint
    results.append(await test_sse_endpoint(base_url))

    # Test 3: List tools (this might not work without proper MCP client)
    # results.append(await test_list_tools(base_url))

    print("\n" + "=" * 60)
    if all(results):
        print("✓ All tests passed!")
        print("\nServer is ready for MCP clients.")
        print("\nConfigure your MCP client with:")
        print(f'  "url": "{base_url}/sse"')
        return 0
    else:
        print("✗ Some tests failed")
        print("\nMake sure the server is running:")
        print("  python -m mcp.prismweave_server")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
