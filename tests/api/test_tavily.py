#!/usr/bin/env python3
"""Test Tavily API directly"""

import os
import httpx
import asyncio


async def test_tavily():
    """Test Tavily API with current key"""
    api_key = "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"  # Use the working key
    print(f"API Key: {api_key[:10]}..." if api_key else "NOT SET")

    if not api_key:
        print("❌ No API key found")
        return

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "https://api.tavily.com/search",
                json={"query": "bitcoin", "max_results": 1},
                headers={"Authorization": f"Bearer {api_key}"},
            )

            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:200]}...")

            if response.status_code == 200:
                print("✅ Tavily API working")
            elif response.status_code == 401:
                print("❌ Tavily API key invalid or expired")
            else:
                print(f"⚠️ Unexpected status: {response.status_code}")

        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(test_tavily())
