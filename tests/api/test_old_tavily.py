#!/usr/bin/env python3
"""Test the old Tavily key with correct authentication"""

import asyncio
import httpx


async def test_old_tavily():
    """Test old Tavily key with Bearer auth"""
    # The old key from environment
    old_key = "tvly-dev-ilpEwz......"  # This is what we saw in env

    print("🔍 Testing old Tavily key with Bearer auth...")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.tavily.com/search",
            headers={"Authorization": f"Bearer {old_key}"},
            json={"query": "bitcoin", "max_results": 1},
        )

        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}...")

        if response.status_code == 200:
            print("✅ Old key works with Bearer auth!")
        else:
            print("❌ Old key still doesn't work")


if __name__ == "__main__":
    asyncio.run(test_old_tavily())
