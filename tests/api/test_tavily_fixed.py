#!/usr/bin/env python3
"""Test the fixed Tavily client"""

import asyncio
import os


async def test_tavily_client():
    """Test the fixed Tavily client"""
    os.environ["TAVILY_API_KEY"] = "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"

    from utils.tavily_search import TavilySearchClient

    client = TavilySearchClient()
    print(f"Client initialized: {client.api_key[:15] if client.api_key else 'None'}...")

    try:
        result = await client.search_news("bitcoin", 1)
        print(f"✅ Success! Found {len(result.results)} results")
        if result.results:
            print(f"First result: {result.results[0].title}")
            print(f"URL: {result.results[0].url}")
        else:
            print("No results found")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(test_tavily_client())
