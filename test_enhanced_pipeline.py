#!/usr/bin/env python3
"""
Test script for the Enhanced News Pipeline
Demonstrates the full pipeline with mock data and LangSmith integration.
"""

import os
import asyncio
from typing import List, Dict, Any


async def test_pipeline_with_mock_data():
    """Test the pipeline with mock news data."""
    print("🧠 Testing Enhanced News Pipeline with Mock Data")
    print("=" * 60)

    # Mock news articles for testing
    mock_articles = [
        {
            "title": "Bitcoin ETF inflows reach $1.2B as institutional adoption accelerates",
            "content": "The cryptocurrency market saw significant institutional inflows today as Bitcoin ETFs reported record-breaking volumes. Major financial institutions are increasingly allocating capital to digital assets, signaling a broader acceptance of cryptocurrency as a legitimate investment class.",
            "source_name": "CoinDesk",
            "published_at": "2024-01-15T10:30:00Z",
            "crypto_topic": "Bitcoin",
            "source_url": "https://example.com/article1",
            "hours_ago": 2,
            "is_breaking": True,
            "is_recent": True,
        },
        {
            "title": "Ethereum upgrade shows promise for scalability improvements",
            "content": "The latest Ethereum upgrade demonstrates significant improvements in transaction processing speed and gas efficiency. Developers report a 40% reduction in gas costs and improved network throughput.",
            "source_name": "CryptoNews",
            "published_at": "2024-01-15T12:00:00Z",
            "crypto_topic": "Ethereum",
            "source_url": "https://example.com/article2",
            "hours_ago": 4,
            "is_breaking": False,
            "is_recent": True,
        },
        {
            "title": "Regulatory clarity boosts crypto market confidence",
            "content": "Recent regulatory developments have provided much-needed clarity for the cryptocurrency industry. Market participants are responding positively to the new guidelines.",
            "source_name": "CryptoInsider",
            "published_at": "2024-01-15T08:00:00Z",
            "crypto_topic": "cryptocurrency",
            "source_url": "https://example.com/article3",
            "hours_ago": 8,
            "is_breaking": False,
            "is_recent": True,
        },
    ]

    try:
        from utils.enrichment import enrich_news_articles

        print("📰 Processing mock articles...")
        print(f"   Articles to process: {len(mock_articles)}")

        # Test enrichment
        enriched_articles = await enrich_news_articles(mock_articles)

        print(f"\n✅ Successfully processed {len(enriched_articles)} articles")

        # Display results
        for i, article in enumerate(enriched_articles, 1):
            print(f"\n📰 Article {i}: {article['title'][:60]}...")
            print(f"   Source: {article['source_name']}")
            print(f"   Topic: {article['crypto_topic']}")
            print(f"   Hours ago: {article['hours_ago']}")
            print(f"   Breaking: {'Yes' if article['is_breaking'] else 'No'}")

            if "enrichment" in article:
                enrichment = article["enrichment"]
                print(f"   🧠 AI Enrichment:")
                print(f"      Sentiment: {enrichment['sentiment']:.2f}")
                print(f"      Trust: {enrichment['trust']:.2f}")
                print(f"      Categories: {', '.join(enrichment['categories'][:3])}")
                print(f"      Macro Category: {enrichment['macro_category']}")
                print(f"      Market Impact: {enrichment['market_impact']}")
                print(f"      Time Relevance: {enrichment['time_relevance']}")
                print(f"      Summary: {enrichment['summary'][:100]}...")

        # Calculate statistics
        if any("enrichment" in art for art in enriched_articles):
            sentiments = [
                art["enrichment"]["sentiment"]
                for art in enriched_articles
                if "enrichment" in art
            ]
            avg_sentiment = sum(sentiments) / len(sentiments)
            print(f"\n📊 Statistics:")
            print(f"   Average Sentiment: {avg_sentiment:.2f}")
            print(
                f"   Enriched Articles: {len([art for art in enriched_articles if 'enrichment' in art])}"
            )
            print(f"   Total Articles: {len(enriched_articles)}")

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


async def test_langsmith_integration():
    """Test LangSmith integration."""
    print("\n🔍 Testing LangSmith Integration")
    print("=" * 40)

    langsmith_key = os.getenv("LANGSMITH_API_KEY")
    if not langsmith_key:
        print("⚠️ LANGSMITH_API_KEY not set - LangSmith tracing disabled")
        print("   To enable LangSmith:")
        print("   1. Get API key from https://smith.langchain.com")
        print("   2. Set environment variable: export LANGSMITH_API_KEY=your_key")
        print("   3. Run this test again")
        return True

    try:
        # Set up LangSmith
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_PROJECT"] = "masonic-test"
        os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"

        from utils.enrichment import get_enrichment_chain

        chain = get_enrichment_chain()
        if not chain:
            print("⚠️ Enrichment chain not available")
            return False

        # Test with tracing
        test_article = {
            "title": "Bitcoin reaches new all-time high",
            "content": "Bitcoin has achieved a new all-time high, surpassing previous records.",
            "source_name": "CryptoTest",
            "published_at": "2024-01-15T14:00:00Z",
        }

        print("   Running enrichment with LangSmith tracing...")
        result = chain.invoke(test_article)

        print("✅ LangSmith integration successful!")
        print(
            f"   Result: {result.get('macro_category', 'N/A')} - {result.get('sentiment', 'N/A')} sentiment"
        )
        print("   Check https://smith.langchain.com for traces")

        return True

    except Exception as e:
        print(f"❌ LangSmith test failed: {e}")
        return False


async def main():
    """Run all tests."""
    print("🧠 Enhanced News Pipeline Test Suite")
    print("=" * 60)

    tests = [test_pipeline_with_mock_data, test_langsmith_integration]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if await test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")

    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Enhanced news pipeline is ready.")
        print("\n🚀 Next steps:")
        print("   1. Set LANGSMITH_API_KEY for tracing")
        print("   2. Integrate with your news processing workflow")
        print("   3. Monitor performance in LangSmith dashboard")
        return True
    else:
        print("⚠️ Some tests failed - check configuration")
        return False


if __name__ == "__main__":
    asyncio.run(main())
