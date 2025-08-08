#!/usr/bin/env python3
"""Debug LiveCoinWatch API response structure"""

import asyncio
import os
import httpx
import json

async def debug_livecoinwatch_response():
    """Debug the LiveCoinWatch API response structure"""
    api_key = "474dbae9-72de-4691-81bc-430db59ed5e3"
    
    print("🔍 Debugging LiveCoinWatch API response structure...")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                'https://api.livecoinwatch.com/coins/single',
                headers={'x-api-key': api_key},
                json={
                    'currency': 'USD',
                    'code': 'BTC',
                    'meta': True
                }
            )
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ API Response Structure:")
                print(json.dumps(data, indent=2))
                
                # Check for symbol/code fields
                print(f"\n🔍 Symbol fields:")
                print(f"  'code': {data.get('code', 'NOT FOUND')}")
                print(f"  'symbol': {data.get('symbol', 'NOT FOUND')}")
                print(f"  'name': {data.get('name', 'NOT FOUND')}")
                
            else:
                print(f"❌ API failed: {response.status_code}")
                print(f"Response: {response.text}")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(debug_livecoinwatch_response())
