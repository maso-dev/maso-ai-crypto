#!/usr/bin/env python3
"""Test NewsAPI directly"""

import asyncio
import os
import httpx

async def test_newsapi():
    """Test NewsAPI"""
    api_key = os.getenv('NEWSAPI_KEY')
    
    print(f"API Key: {api_key[:15]}..." if api_key else "NOT SET")
    
    if not api_key:
        print("❌ No API key found")
        return
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                'https://newsapi.org/v2/everything',
                params={
                    'q': 'bitcoin',
                    'apiKey': api_key,
                    'pageSize': 1,
                    'sortBy': 'publishedAt'
                }
            )
            
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ NewsAPI working!")
                print(f"Total results: {data.get('totalResults', 'N/A')}")
                if data.get('articles'):
                    article = data['articles'][0]
                    print(f"First article: {article.get('title', 'N/A')}")
            else:
                print(f"❌ NewsAPI failed: {response.status_code}")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_newsapi())
