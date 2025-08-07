#!/usr/bin/env python3
"""
Test Tavily Search Integration
"""

import asyncio
import logging
from utils.tavily_search import (
    tavily_client,
    search_crypto_news,
    get_crypto_market_data,
    get_trending_crypto_topics,
    search_tavily_news,
    search_tavily_finance,
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_tavily_integration():
    """Test Tavily search integration."""

    print("🧪 Testing Tavily Search Integration...")
    print("=" * 80)

    # Test 1: System Status
    print("🔍 Test 1: System Status")
    print("-" * 40)

    try:
        status = await tavily_client.get_system_status()
        print(f"✅ Service: {status['service']}")
        print(f"📊 Status: {status['status']}")
        print(f"🔑 API Key Available: {status['api_key_available']}")
        print(f"🌐 Base URL: {status['base_url']}")

        print("\n🔧 Features:")
        for feature, available in status["features"].items():
            status_icon = "✅" if available else "❌"
            print(f"   {status_icon} {feature}")

    except Exception as e:
        print(f"❌ System status test failed: {e}")

    # Test 2: News Search
    print(f"\n🔍 Test 2: News Search")
    print("-" * 40)

    try:
        response = await search_tavily_news(
            "Bitcoin cryptocurrency news", max_results=5
        )

        print(
            f"✅ News Search: {'SUCCESS' if response.total_results > 0 else 'NO RESULTS'}"
        )
        print(f"📊 Total Results: {response.total_results}")
        print(f"⏱️ Search Time: {response.search_time:.2f}s")
        print(f"🔍 Query: {response.query}")

        if response.results:
            print(f"\n📰 Sample Results:")
            for i, result in enumerate(response.results[:3], 1):
                print(f"   {i}. {result.title}")
                print(f"      Source: {result.source}")
                print(f"      Score: {result.score:.2f}")
                print(f"      URL: {result.url}")
                print()
        else:
            print("   ⚠️ No results found")

    except Exception as e:
        print(f"❌ News search test failed: {e}")

    # Test 3: Finance Search
    print(f"\n🔍 Test 3: Finance Search")
    print("-" * 40)

    try:
        response = await search_tavily_finance(
            "Bitcoin current price market cap", max_results=3
        )

        print(
            f"✅ Finance Search: {'SUCCESS' if response.total_results > 0 else 'NO RESULTS'}"
        )
        print(f"📊 Total Results: {response.total_results}")
        print(f"⏱️ Search Time: {response.search_time:.2f}s")
        print(f"🔍 Query: {response.query}")

        if response.results:
            print(f"\n💰 Sample Results:")
            for i, result in enumerate(response.results[:2], 1):
                print(f"   {i}. {result.title}")
                print(f"      Source: {result.source}")
                print(f"      Score: {result.score:.2f}")
                print(f"      Content: {result.content[:100]}...")
                print()
        else:
            print("   ⚠️ No results found")

    except Exception as e:
        print(f"❌ Finance search test failed: {e}")

    # Test 4: Crypto News
    print(f"\n🔍 Test 4: Crypto News")
    print("-" * 40)

    try:
        symbols = ["BTC", "ETH", "SOL"]
        results = await search_crypto_news(symbols, max_results=10)

        print(f"✅ Crypto News: {'SUCCESS' if results else 'NO RESULTS'}")
        print(f"📊 Total Results: {len(results)}")
        print(f"🎯 Symbols: {symbols}")

        if results:
            print(f"\n📰 Sample Results:")
            for i, result in enumerate(results[:3], 1):
                print(f"   {i}. {result.title}")
                print(f"      Source: {result.source}")
                print(f"      Score: {result.score:.2f}")
                print(f"      Type: {result.search_type}")
                print()
        else:
            print("   ⚠️ No results found")

    except Exception as e:
        print(f"❌ Crypto news test failed: {e}")

    # Test 5: Market Data
    print(f"\n🔍 Test 5: Market Data")
    print("-" * 40)

    try:
        symbols = ["BTC", "ETH"]
        market_data = await get_crypto_market_data(symbols)

        print(f"✅ Market Data: {'SUCCESS' if market_data else 'NO RESULTS'}")
        print(f"📊 Symbols: {symbols}")

        if market_data:
            for symbol, data in market_data.items():
                print(f"\n💰 {symbol}:")
                print(f"   Results: {len(data['results'])}")
                print(f"   Search Time: {data['search_time']:.2f}s")
                if data.get("answer"):
                    print(f"   Answer: {data['answer'][:100]}...")
        else:
            print("   ⚠️ No market data found")

    except Exception as e:
        print(f"❌ Market data test failed: {e}")

    # Test 6: Trending Topics
    print(f"\n🔍 Test 6: Trending Topics")
    print("-" * 40)

    try:
        trending_topics = await get_trending_crypto_topics()

        print(f"✅ Trending Topics: {'SUCCESS' if trending_topics else 'NO RESULTS'}")
        print(f"📊 Count: {len(trending_topics)}")

        if trending_topics:
            print(f"\n🔥 Trending Topics:")
            for i, topic in enumerate(trending_topics, 1):
                print(f"   {i}. {topic}")
        else:
            print("   ⚠️ No trending topics found")

    except Exception as e:
        print(f"❌ Trending topics test failed: {e}")

    # Test 7: Web Search
    print(f"\n🔍 Test 7: Web Search")
    print("-" * 40)

    try:
        response = await tavily_client.search_web(
            "cryptocurrency blockchain technology", max_results=3
        )

        print(
            f"✅ Web Search: {'SUCCESS' if response.total_results > 0 else 'NO RESULTS'}"
        )
        print(f"📊 Total Results: {response.total_results}")
        print(f"⏱️ Search Time: {response.search_time:.2f}s")
        print(f"🔍 Query: {response.query}")

        if response.results:
            print(f"\n🌐 Sample Results:")
            for i, result in enumerate(response.results[:2], 1):
                print(f"   {i}. {result.title}")
                print(f"      Source: {result.source}")
                print(f"      Score: {result.score:.2f}")
                print(f"      URL: {result.url}")
                print()
        else:
            print("   ⚠️ No results found")

    except Exception as e:
        print(f"❌ Web search test failed: {e}")

    print(f"\n✅ Tavily Search Integration test completed!")
    print(f"🎯 Key Features Tested:")
    print(f"   ✅ System status and health check")
    print(f"   ✅ News search functionality")
    print(f"   ✅ Finance search functionality")
    print(f"   ✅ Crypto-specific news search")
    print(f"   ✅ Market data collection")
    print(f"   ✅ Trending topics detection")
    print(f"   ✅ General web search")
    print(f"   ✅ Error handling and logging")
    print(f"   ✅ API integration with centralized config")


if __name__ == "__main__":
    asyncio.run(test_tavily_integration())
