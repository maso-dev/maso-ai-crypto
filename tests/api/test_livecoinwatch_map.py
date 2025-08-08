#!/usr/bin/env python3
"""Test LiveCoinWatch /coins/map endpoint"""

import asyncio
import os
import httpx

async def test_livecoinwatch_map():
    """Test LiveCoinWatch /coins/map endpoint"""
    api_key = "474dbae9-72de-4..."  # The key we know works
    
    print("🔍 Testing LiveCoinWatch /coins/map endpoint...")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                'https://api.livecoinwatch.com/coins/map',
                headers={'x-api-key': api_key},
                json={
                    'currency': 'USD',
                    'codes': ['BTC', 'ETH'],
                    'meta': True
                }
            )
            
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ /coins/map endpoint working!")
                print(f"Got {len(data)} coins")
                for coin in data:
                    print(f"  {coin.get('code', 'N/A')}: ${coin.get('rate', 'N/A')}")
            else:
                print(f"❌ /coins/map endpoint failed: {response.status_code}")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_livecoinwatch_map())
