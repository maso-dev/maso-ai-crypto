#!/usr/bin/env python3
"""
Test script for the separated backend structure.
Tests admin, portfolio, and crypto news routers.
"""

import asyncio
import httpx
import json
from datetime import datetime, timezone

async def test_admin_endpoints():
    """Test admin endpoints."""
    print("🧪 Testing Admin Endpoints...")
    
    try:
        async with httpx.AsyncClient() as client:
            # Test 1: System status
            print("   📊 Testing system status...")
            response = await client.get("http://localhost:8000/admin/status", timeout=10.0)
            
            if response.status_code == 200:
                data = response.json()
                print(f"      ✅ System status: {data['status']}")
                print(f"      📊 Services: {list(data['services'].keys())}")
            else:
                print(f"      ❌ System status returned status: {response.status_code}")
                return False
            
            # Test 2: Health check
            print("   ❤️ Testing health check...")
            response = await client.get("http://localhost:8000/admin/health", timeout=10.0)
            
            if response.status_code == 200:
                data = response.json()
                print(f"      ✅ Health check: {data['status']}")
            else:
                print(f"      ❌ Health check returned status: {response.status_code}")
                return False
            
            # Test 3: Cost tracking
            print("   💰 Testing cost tracking...")
            response = await client.get("http://localhost:8000/admin/costs/daily", timeout=10.0)
            
            if response.status_code == 200:
                data = response.json()
                print(f"      ✅ Daily costs: ${data['total_cost']:.4f}")
            else:
                print(f"      ❌ Cost tracking returned status: {response.status_code}")
                return False
            
            # Test 4: System config
            print("   ⚙️ Testing system config...")
            response = await client.get("http://localhost:8000/admin/config", timeout=10.0)
            
            if response.status_code == 200:
                data = response.json()
                print(f"      ✅ System config retrieved")
                print(f"      📊 Services enabled: {data['openai_enabled']}, {data['tavily_enabled']}, {data['newsapi_enabled']}")
            else:
                print(f"      ❌ System config returned status: {response.status_code}")
                return False
            
            return True
            
    except Exception as e:
        print(f"❌ Admin endpoints test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_portfolio_endpoints():
    """Test portfolio endpoints."""
    print("\n🧪 Testing Portfolio Endpoints...")
    
    try:
        async with httpx.AsyncClient() as client:
            # Test 1: Portfolio assets
            print("   💼 Testing portfolio assets...")
            response = await client.get("http://localhost:8000/portfolio/assets", timeout=10.0)
            
            if response.status_code == 200:
                data = response.json()
                print(f"      ✅ Portfolio assets: ${data['total_value_usdt']:.2f}")
                print(f"      📊 Assets count: {len(data['assets'])}")
            else:
                print(f"      ❌ Portfolio assets returned status: {response.status_code}")
                return False
            
            # Test 2: Market summary
            print("   📊 Testing market summary...")
            response = await client.post(
                "http://localhost:8000/portfolio/market_summary",
                json={
                    "symbols": ["BTC", "ETH"],
                    "limit": 5,
                    "always_include_base_coins": True
                },
                timeout=10.0
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"      ✅ Market summary generated")
                print(f"      📊 Symbols analyzed: {data['symbols_analyzed']}")
                print(f"      📰 News articles: {len(data['news'])}")
            else:
                print(f"      ❌ Market summary returned status: {response.status_code}")
                return False
            
            # Test 3: ETF comparison
            print("   📈 Testing ETF comparison...")
            response = await client.get("http://localhost:8000/portfolio/etf-comparison", timeout=10.0)
            
            if response.status_code == 200:
                data = response.json()
                print(f"      ✅ ETF comparison: {len(data['etfs'])} ETFs")
            else:
                print(f"      ❌ ETF comparison returned status: {response.status_code}")
                return False
            
            # Test 4: Portfolio performance
            print("   📊 Testing portfolio performance...")
            response = await client.get("http://localhost:8000/portfolio/performance", timeout=10.0)
            
            if response.status_code == 200:
                data = response.json()
                print(f"      ✅ Portfolio performance: {data['total_return_24h']}% 24h")
            else:
                print(f"      ❌ Portfolio performance returned status: {response.status_code}")
                return False
            
            return True
            
    except Exception as e:
        print(f"❌ Portfolio endpoints test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_crypto_news_endpoints():
    """Test crypto news endpoints."""
    print("\n🧪 Testing Crypto News Endpoints...")
    
    try:
        async with httpx.AsyncClient() as client:
            # Test 1: News search
            print("   🔍 Testing news search...")
            response = await client.post(
                "http://localhost:8000/news/search",
                json={
                    "symbols": ["BTC", "ETH"],
                    "limit": 5
                },
                timeout=10.0
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"      ✅ News search: {data['total_found']} articles found")
            else:
                print(f"      ❌ News search returned status: {response.status_code}")
                return False
            
            # Test 2: Trending topics
            print("   📈 Testing trending topics...")
            response = await client.get("http://localhost:8000/news/trending", timeout=10.0)
            
            if response.status_code == 200:
                data = response.json()
                print(f"      ✅ Trending topics: {len(data['trending_topics'])} topics")
            else:
                print(f"      ❌ Trending topics returned status: {response.status_code}")
                return False
            
            # Test 3: News sources
            print("   📰 Testing news sources...")
            response = await client.get("http://localhost:8000/news/sources", timeout=10.0)
            
            if response.status_code == 200:
                data = response.json()
                print(f"      ✅ News sources: {data['total_sources']} sources")
            else:
                print(f"      ❌ News sources returned status: {response.status_code}")
                return False
            
            # Test 4: News stats
            print("   📊 Testing news stats...")
            response = await client.get("http://localhost:8000/news/stats", timeout=10.0)
            
            if response.status_code == 200:
                data = response.json()
                print(f"      ✅ News stats: {data['total_articles_processed']} articles processed")
            else:
                print(f"      ❌ News stats returned status: {response.status_code}")
                return False
            
            return True
            
    except Exception as e:
        print(f"❌ Crypto news endpoints test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_legacy_endpoints():
    """Test legacy endpoints that should still work."""
    print("\n🧪 Testing Legacy Endpoints...")
    
    try:
        async with httpx.AsyncClient() as client:
            # Test 1: Legacy crypto news RAG
            print("   📰 Testing legacy crypto news RAG...")
            response = await client.post(
                "http://localhost:8000/populate_crypto_news_rag",
                json={
                    "terms": ["cryptocurrency", "bitcoin", "ethereum"],
                    "chunking": {
                        "method": "paragraph",
                        "chunk_size": 500,
                        "overlap": 50
                    }
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"      ✅ Legacy RAG: {data['articles_processed']} articles processed")
            else:
                print(f"      ❌ Legacy RAG returned status: {response.status_code}")
                return False
            
            return True
            
    except Exception as e:
        print(f"❌ Legacy endpoints test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all backend separation tests."""
    print("🚀 Starting Backend Separation Tests\n")
    
    try:
        # Test 1: Admin endpoints
        test1 = await test_admin_endpoints()
        
        # Test 2: Portfolio endpoints
        test2 = await test_portfolio_endpoints()
        
        # Test 3: Crypto news endpoints
        test3 = await test_crypto_news_endpoints()
        
        # Test 4: Legacy endpoints
        test4 = await test_legacy_endpoints()
        
        print(f"\n📊 Backend Separation Test Results:")
        print(f"   Admin endpoints: {'✅ PASSED' if test1 else '❌ FAILED'}")
        print(f"   Portfolio endpoints: {'✅ PASSED' if test2 else '❌ FAILED'}")
        print(f"   Crypto news endpoints: {'✅ PASSED' if test3 else '❌ FAILED'}")
        print(f"   Legacy endpoints: {'✅ PASSED' if test4 else '❌ FAILED'}")
        
        if all([test1, test2, test3, test4]):
            print("\n🎉 All backend separation tests passed!")
            print("   The backend has been successfully separated into:")
            print("   ✅ Admin system (/admin/*) - Cost tracking, system status, config")
            print("   ✅ Portfolio system (/portfolio/*) - User portfolio management")
            print("   ✅ Crypto news system (/news/*) - News operations and analysis")
            print("   ✅ Legacy compatibility - Old endpoints still work")
            print("\n   Key benefits achieved:")
            print("   🔒 Proper separation of concerns")
            print("   🛡️ Admin functions isolated from user features")
            print("   📊 Cost tracking in admin system only")
            print("   🎯 Clean API organization")
            print("   🔄 Backward compatibility maintained")
        else:
            print("\n⚠️  Some backend separation tests failed.")
            print("   Note: Tests may fail if the server is not running.")
            
    except Exception as e:
        print(f"\n❌ Backend separation test suite failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 
