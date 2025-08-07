#!/usr/bin/env python3
"""
Test script for Data Quality Filter
"""

import asyncio
import logging
from utils.data_quality_filter import (
    filter_news_articles,
    get_quality_metrics,
    data_quality_filter,
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_data_quality_filter():
    """Test the data quality filter with sample articles."""

    # Sample articles for testing
    test_articles = [
        {
            "title": "Bitcoin Reaches New All-Time High of $50,000",
            "description": "Bitcoin has achieved a new milestone, reaching $50,000 for the first time in its history.",
            "content": "Bitcoin, the world's leading cryptocurrency, has reached a new all-time high of $50,000. This milestone represents a significant achievement for the digital asset, which has seen remarkable growth over the past year. Market analysts attribute this surge to increased institutional adoption and growing mainstream acceptance of cryptocurrencies.",
            "source": {"name": "Reuters"},
            "url": "https://reuters.com/bitcoin-50000",
        },
        {
            "title": "🚀🚀🚀 THIS CRYPTO WILL MAKE YOU A MILLIONAIRE!!! 🚀🚀🚀",
            "description": "You won't believe what happens next! This secret cryptocurrency is going to the moon!",
            "content": "Breaking news! This amazing cryptocurrency is about to explode! Buy now before it's too late! This is your chance to become a millionaire! Don't miss out on this incredible opportunity!",
            "source": {"name": "CryptoDaily"},
            "url": "https://cryptodaily.co.uk/millionaire-crypto",
        },
        {
            "title": "Ethereum Smart Contract Development Guide",
            "description": "A comprehensive guide to developing smart contracts on the Ethereum blockchain.",
            "content": "Smart contracts are self-executing contracts with the terms of the agreement directly written into code. This guide covers Solidity programming, gas optimization, and best practices for Ethereum development. Learn about DeFi protocols, NFT standards, and blockchain security.",
            "source": {"name": "CoinDesk"},
            "url": "https://coindesk.com/ethereum-guide",
        },
        {
            "title": "Random News About Cats",
            "description": "Cats are amazing pets that everyone should have.",
            "content": "Cats are wonderful companions that provide love and entertainment. They are independent animals that can take care of themselves. Many people enjoy having cats as pets because they are low maintenance and very affectionate.",
            "source": {"name": "PetNews"},
            "url": "https://petnews.com/cats",
        },
    ]

    print("🧪 Testing Data Quality Filter...")
    print(f"📊 Testing with {len(test_articles)} sample articles")
    print()

    # Test filtering
    symbols = ["BTC", "ETH"]
    filtered_articles = await filter_news_articles(test_articles, symbols)

    print("📋 Filtering Results:")
    print("=" * 80)

    for i, filtered_article in enumerate(filtered_articles, 1):
        original = filtered_article.original_article
        metrics = filtered_article.quality_metrics

        print(f"\n📰 Article {i}: {original['title'][:50]}...")
        print(f"   Source: {original['source']['name']}")
        print(
            f"   Status: {'✅ APPROVED' if filtered_article.is_approved else '❌ REJECTED'}"
        )

        if not filtered_article.is_approved:
            print(f"   Rejection Reason: {filtered_article.rejection_reason}")

        print(f"   Quality Metrics:")
        print(f"     Overall Score: {metrics.overall_score:.2f}")
        print(f"     Source Reliability: {metrics.source_reliability:.2f}")
        print(f"     Content Quality: {metrics.content_quality:.2f}")
        print(f"     Clickbait Score: {metrics.clickbait_score:.2f}")
        print(f"     Relevance Score: {metrics.relevance_score:.2f}")
        print(f"     Verification Score: {metrics.verification_score:.2f}")
        print(f"     Quality Level: {metrics.quality_level.upper()}")

        if metrics.issues:
            print(f"     Issues: {', '.join(metrics.issues)}")

        if metrics.recommendations:
            print(f"     Recommendations: {', '.join(metrics.recommendations)}")

    # Summary
    approved_count = sum(1 for article in filtered_articles if article.is_approved)
    total_count = len(filtered_articles)

    print("\n" + "=" * 80)
    print(f"📊 SUMMARY: {approved_count}/{total_count} articles approved")
    print(f"🎯 Approval Rate: {(approved_count/total_count)*100:.1f}%")

    # Test individual article quality metrics
    print("\n🔍 Testing Individual Article Quality Metrics...")
    test_article = test_articles[0]  # Bitcoin article
    metrics = await get_quality_metrics(test_article, symbols)

    print(f"📰 Article: {test_article['title']}")
    print(f"   Overall Score: {metrics.overall_score:.2f}")
    print(f"   Is Verified: {metrics.is_verified}")
    print(f"   Is Clickbait: {metrics.is_clickbait}")
    print(f"   Is Relevant: {metrics.is_relevant}")

    print("\n✅ Data Quality Filter test completed!")


if __name__ == "__main__":
    asyncio.run(test_data_quality_filter())
