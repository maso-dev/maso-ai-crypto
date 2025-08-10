#!/usr/bin/env python3
"""
Phase 3 News Integration Test
Tests the enhanced news endpoint with multi-source integration and quality filtering
"""

import asyncio
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.getcwd())


async def test_news_quality_filter():
    """Test the news quality filtering functionality."""
    print("🧪 Testing Phase 3 News Quality Filter...")

    try:
        from utils.data_quality_filter import DataQualityFilter

        quality_filter = DataQualityFilter()

        # Test high-quality article
        good_article = {
            "title": "Bitcoin Reaches New All-Time High as Institutional Adoption Grows",
            "content": "Bitcoin has reached a new all-time high of $50,000 as major institutions continue to adopt cryptocurrency. The price surge comes amid growing acceptance from traditional financial institutions and increased retail interest.",
            "source_url": "https://coindesk.com/bitcoin-news",
            "published_at": "2024-01-15T10:00:00Z",
            "source": "coindesk",
        }

        # Test low-quality article
        bad_article = {
            "title": "CLICK HERE TO WIN FREE BITCOIN!!!",
            "content": "You won't believe what happened next! Click here to get free Bitcoin instantly! This is too good to be true!",
            "source_url": "https://spam-site.com/free-bitcoin",
            "published_at": "2024-01-15T10:00:00Z",
            "source": "spam",
        }

        # Test quality filtering
        good_result = await quality_filter._filter_single_article(good_article)
        bad_result = await quality_filter._filter_single_article(bad_article)

        print(
            f"✅ Good article quality score: {good_result.quality_metrics.overall_score}"
        )
        print(
            f"✅ Bad article quality score: {bad_result.quality_metrics.overall_score}"
        )
        print(f"✅ Good article passed filter: {good_result.is_approved}")
        print(f"✅ Bad article passed filter: {bad_result.is_approved}")

        return True

    except Exception as e:
        print(f"❌ News quality filter test failed: {e}")
        return False


async def test_tavily_integration():
    """Test Tavily search integration."""
    print("🧪 Testing Tavily Integration...")

    try:
        from utils.tavily_search import TavilySearchClient

        client = TavilySearchClient()

        # Test news search
        response = await client.search_news(
            query="Bitcoin cryptocurrency", max_results=5, time_period="1d"
        )

        print(f"✅ Tavily search completed: {len(response.results)} results")
        print(f"✅ Search time: {response.search_time:.2f}s")

        if response.results:
            print(f"✅ First result: {response.results[0].title[:50]}...")

        return True

    except Exception as e:
        print(f"❌ Tavily integration test failed: {e}")
        return False


async def test_multi_source_news():
    """Test multi-source news integration."""
    print("🧪 Testing Multi-Source News Integration...")

    try:
        from utils.intelligent_news_cache import get_portfolio_news
        from utils.tavily_search import TavilySearchClient

        # Test NewsAPI (cached)
        news_data = await get_portfolio_news(
            include_alpha_portfolio=True,
            include_opportunity_tokens=True,
            include_personal_portfolio=True,
            hours_back=24,
        )

        print(
            f"✅ NewsAPI results: {len(news_data.get('news_by_category', {}))} categories"
        )

        # Test Tavily
        tavily_client = TavilySearchClient()
        tavily_response = await tavily_client.search_news(
            query="cryptocurrency market", max_results=5, time_period="1d"
        )

        print(f"✅ Tavily results: {len(tavily_response.results)} articles")

        # Test hybrid RAG
        from utils.hybrid_rag import HybridRAGSystem, HybridQuery, HybridQueryType

        hybrid_rag = HybridRAGSystem()
        hybrid_query = HybridQuery(
            query_text="crypto market news",
            query_type=HybridQueryType.SENTIMENT_ANALYSIS,
            symbols=["BTC", "ETH"],
            time_range_hours=24,
            limit=5,
        )

        hybrid_results = await hybrid_rag.hybrid_search(hybrid_query)
        print(f"✅ Hybrid RAG results: {len(hybrid_results)} articles")

        return True

    except Exception as e:
        print(f"❌ Multi-source news test failed: {e}")
        return False


async def test_news_endpoint():
    """Test the enhanced news endpoint."""
    print("🧪 Testing Enhanced News Endpoint...")

    try:
        # Import the function directly
        from main import get_enhanced_news

        # Test the endpoint
        result = await get_enhanced_news()

        print(f"✅ News endpoint status: {result.get('status')}")
        print(f"✅ Total articles: {result.get('total_articles')}")
        print(f"✅ Sources: {result.get('sources')}")
        print(f"✅ Phase: {result.get('phase')}")

        # Check quality metrics
        quality_metrics = result.get("quality_metrics", {})
        print(
            f"✅ Quality metrics: {quality_metrics.get('filtered_articles')} filtered, {quality_metrics.get('filtered_out')} filtered out"
        )
        print(
            f"✅ Average quality score: {quality_metrics.get('average_quality_score')}"
        )

        return True

    except Exception as e:
        print(f"❌ News endpoint test failed: {e}")
        return False


async def main():
    """Run all Phase 3 news tests."""
    print("🚀 PHASE 3 NEWS INTEGRATION TESTS")
    print("=" * 50)

    tests = [
        test_news_quality_filter,
        test_tavily_integration,
        test_multi_source_news,
        test_news_endpoint,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if await test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")

    print("=" * 50)
    print(f"📊 PHASE 3 NEWS TEST SUMMARY")
    print(f"Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")

    if passed == total:
        print("🎉 All Phase 3 news tests passed!")
        return 0
    else:
        print("⚠️  Some Phase 3 news tests failed.")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
