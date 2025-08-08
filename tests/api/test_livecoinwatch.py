#!/usr/bin/env python3
"""Test LiveCoinWatch API directly"""

import asyncio
import os
import httpx

async def test_livecoinwatch():
    """Test LiveCoinWatch API"""
    api_key = os.getenv('LIVECOINWATCH_API_KEY')
    
    print(f"API Key: {api_key[:15]}..." if api_key else "NOT SET")
    
    if not api_key:
        print("❌ No API key found")
        return
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                'https://api.livecoinwatch.com/coins/single',
                headers={'x-api-key': api_key},
                json={
                    'currency': 'USD',
                    'code': 'BTC',
                    'meta': False
                }
            )
            
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ LiveCoinWatch API working!")
                print(f"BTC Price: ${data.get('rate', 'N/A')}")
            else:
                print(f"❌ LiveCoinWatch API failed: {response.status_code}")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_livecoinwatch())
