#!/usr/bin/env python3
"""Test different Tavily API formats"""

import os
import httpx
import asyncio


async def test_tavily_formats():
    """Test different Tavily API formats"""
    api_key = "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"

    print("🔍 Testing Tavily API formats...")

    # Test 1: POST with api-key header
    print("\n1. POST with api-key header:")
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.tavily.com/search",
            json={"query": "bitcoin", "max_results": 1},
            headers={"api-key": api_key},
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:100]}...")

    # Test 2: GET with api_key parameter
    print("\n2. GET with api_key parameter:")
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.tavily.com/search",
            params={"query": "bitcoin", "api_key": api_key, "max_results": 1},
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:100]}...")

    # Test 3: POST with Authorization header
    print("\n3. POST with Authorization header:")
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.tavily.com/search",
            json={"query": "bitcoin", "max_results": 1},
            headers={"Authorization": f"Bearer {api_key}"},
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:100]}...")


if __name__ == "__main__":
    asyncio.run(test_tavily_formats())
