#!/usr/bin/env python3
"""
Test script to generate LangSmith traces
Shows the actual LangChain pipeline in action.
"""

import os
import asyncio
from datetime import datetime

# Set up LangSmith
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "masonic-brain"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_ORGANIZATION"] = "703f12b7-8da7-455d-9870-c0dd95d12d7d"


async def test_langsmith_pipeline():
    """Test the LangChain pipeline with LangSmith tracing."""
    print("🧠 Testing LangChain Pipeline with LangSmith Tracing")
    print("=" * 60)
    print("📊 Check https://smith.langchain.com for traces")
    print("   Organization: 703f12b7-8da7-455d-9870-c0dd95d12d7d")
    print("   Project: masonic-brain")
    print()

    try:
        from utils.enhanced_news_pipeline import get_enhanced_crypto_news

        # Test 1: News processing with enrichment
        print("🔄 Test 1: Processing news with AI enrichment...")
        result = await get_enhanced_crypto_news(
            symbols=["Bitcoin", "Ethereum"], hours_back=6, enable_enrichment=True
        )

        print(f"   ✅ Processed {len(result.get('articles', []))} articles")
        print(f"   📊 Metadata: {result.get('metadata', {})}")

        # Test 2: Direct enrichment chain
        print("\n🔄 Test 2: Testing enrichment chain directly...")
        from utils.enrichment import get_enrichment_chain

        chain = get_enrichment_chain()
        if chain:
            test_article = {
                "title": "Bitcoin reaches new all-time high",
                "content": "Bitcoin has achieved a new all-time high, surpassing previous records and showing strong institutional adoption.",
                "source_name": "CryptoTest",
                "published_at": "2024-01-15T14:00:00Z",
            }

            print("   Running enrichment with LangSmith tracing...")
            enrichment_result = chain.invoke(test_article)

            print(f"   ✅ Enrichment result:")
            print(f"      Sentiment: {enrichment_result.get('sentiment', 'N/A')}")
            print(f"      Trust: {enrichment_result.get('trust', 'N/A')}")
            print(f"      Categories: {enrichment_result.get('categories', [])}")
            print(
                f"      Macro Category: {enrichment_result.get('macro_category', 'N/A')}"
            )

        # Test 3: Multiple operations to generate more traces
        print("\n🔄 Test 3: Generating multiple traces...")
        for i in range(3):
            test_articles = [
                {
                    "title": f"Test article {i+1}: Ethereum upgrade",
                    "content": f"This is test article {i+1} about Ethereum upgrades and improvements.",
                    "source_name": "TestSource",
                    "published_at": "2024-01-15T14:00:00Z",
                }
            ]

            from utils.enrichment import enrich_news_articles

            enriched = await enrich_news_articles(test_articles)
            print(f"   ✅ Generated trace {i+1}")

        print("\n🎉 LangSmith tracing tests completed!")
        print("\n📊 To view your pipeline:")
        print("   1. Go to https://smith.langchain.com")
        print("   2. Select your organization: 703f12b7-8da7-455d-9870-c0dd95d12d7d")
        print("   3. Click on 'masonic-brain' project")
        print("   4. View traces with tags: ['enrichment', 'news', 'crypto']")
        print("   5. Click on any trace to see the detailed pipeline")

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


if __name__ == "__main__":
    asyncio.run(test_langsmith_pipeline())
