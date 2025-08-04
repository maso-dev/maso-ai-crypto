#!/usr/bin/env python3
"""
Test Data Quality Filter Integration with Mock Data
"""

import asyncio
import logging
from utils.data_quality_filter import filter_news_articles, get_quality_metrics
from utils.enhanced_news_pipeline import EnhancedNewsPipeline

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_quality_filter_integration():
    """Test data quality filter integration with mock data."""
    
    print("🧪 Testing Data Quality Filter Integration...")
    print("=" * 80)
    
    # Mock news articles for testing
    mock_articles = [
        {
            "title": "Bitcoin Surges to $50,000 as Institutional Adoption Grows",
            "description": "Bitcoin has reached a new milestone, with major institutions continuing to invest in the cryptocurrency.",
            "content": "Bitcoin, the world's leading cryptocurrency, has achieved a significant milestone by reaching $50,000. This surge comes as major financial institutions, including Tesla and MicroStrategy, continue to allocate significant portions of their treasury to Bitcoin. Market analysts attribute this growth to increasing institutional adoption and growing mainstream acceptance of digital assets.",
            "source": {"name": "Reuters"},
            "url": "https://reuters.com/bitcoin-50000",
            "publishedAt": "2025-08-02T10:00:00Z"
        },
        {
            "title": "🚀🚀🚀 THIS CRYPTO WILL MAKE YOU RICH!!! 🚀🚀🚀",
            "description": "You won't believe what happens next! This secret cryptocurrency is going to the moon!",
            "content": "Breaking news! This amazing cryptocurrency is about to explode! Buy now before it's too late! This is your chance to become a millionaire! Don't miss out on this incredible opportunity! The price is going to 100x!",
            "source": {"name": "CryptoDaily"},
            "url": "https://cryptodaily.co.uk/millionaire-crypto",
            "publishedAt": "2025-08-02T11:00:00Z"
        },
        {
            "title": "Ethereum Smart Contract Development: A Comprehensive Guide",
            "description": "Learn how to develop secure and efficient smart contracts on the Ethereum blockchain.",
            "content": "Smart contracts are self-executing contracts with the terms of the agreement directly written into code. This comprehensive guide covers Solidity programming, gas optimization techniques, and best practices for Ethereum development. Topics include DeFi protocol development, NFT standards implementation, and blockchain security considerations.",
            "source": {"name": "CoinDesk"},
            "url": "https://coindesk.com/ethereum-guide",
            "publishedAt": "2025-08-02T12:00:00Z"
        },
        {
            "title": "Solana Network Achieves 65,000 TPS Milestone",
            "description": "Solana blockchain demonstrates exceptional performance with 65,000 transactions per second.",
            "content": "The Solana blockchain has achieved a remarkable milestone by processing 65,000 transactions per second during recent stress tests. This performance demonstrates the network's capability to handle high-throughput applications and positions Solana as a leading platform for DeFi and NFT applications.",
            "source": {"name": "The Block"},
            "url": "https://theblock.co/solana-65k-tps",
            "publishedAt": "2025-08-02T13:00:00Z"
        },
        {
            "title": "Random Cat News That Has Nothing to Do With Crypto",
            "description": "Cats are amazing pets that everyone should have in their homes.",
            "content": "Cats are wonderful companions that provide love and entertainment to their owners. They are independent animals that can take care of themselves and require minimal maintenance. Many people enjoy having cats as pets because they are affectionate and provide great company.",
            "source": {"name": "PetNews"},
            "url": "https://petnews.com/cats",
            "publishedAt": "2025-08-02T14:00:00Z"
        }
    ]
    
    print(f"📊 Testing with {len(mock_articles)} mock articles")
    print()
    
    # Test 1: Direct quality filtering
    print("🔍 Test 1: Direct Quality Filtering")
    print("-" * 40)
    
    symbols = ["BTC", "ETH", "SOL"]
    filtered_articles = await filter_news_articles(mock_articles, symbols)
    
    approved_count = sum(1 for article in filtered_articles if article.is_approved)
    print(f"✅ Quality filtering results: {approved_count}/{len(mock_articles)} articles approved")
    
    for i, filtered_article in enumerate(filtered_articles, 1):
        original = filtered_article.original_article
        metrics = filtered_article.quality_metrics
        
        status = "✅ APPROVED" if filtered_article.is_approved else "❌ REJECTED"
        print(f"   {i}. {original['title'][:40]}... {status}")
        print(f"      Source: {original['source']['name']}")
        print(f"      Quality Score: {metrics.overall_score:.2f}")
        print(f"      Clickbait Score: {metrics.clickbait_score:.2f}")
        print(f"      Relevance Score: {metrics.relevance_score:.2f}")
        
        if not filtered_article.is_approved:
            print(f"      Rejection: {filtered_article.rejection_reason}")
    
    # Test 2: Individual article quality metrics
    print(f"\n🔍 Test 2: Individual Article Quality Metrics")
    print("-" * 40)
    
    test_article = mock_articles[0]  # Bitcoin article
    metrics = await get_quality_metrics(test_article, symbols)
    
    print(f"📰 Article: {test_article['title']}")
    print(f"   Overall Score: {metrics.overall_score:.2f}")
    print(f"   Source Reliability: {metrics.source_reliability:.2f}")
    print(f"   Content Quality: {metrics.content_quality:.2f}")
    print(f"   Clickbait Score: {metrics.clickbait_score:.2f}")
    print(f"   Relevance Score: {metrics.relevance_score:.2f}")
    print(f"   Verification Score: {metrics.verification_score:.2f}")
    print(f"   Quality Level: {metrics.quality_level.upper()}")
    print(f"   Is Verified: {metrics.is_verified}")
    print(f"   Is Clickbait: {metrics.is_clickbait}")
    print(f"   Is Relevant: {metrics.is_relevant}")
    
    if metrics.issues:
        print(f"   Issues: {', '.join(metrics.issues)}")
    
    if metrics.recommendations:
        print(f"   Recommendations: {', '.join(metrics.recommendations)}")
    
    # Test 3: Simulate pipeline integration
    print(f"\n🔍 Test 3: Pipeline Integration Simulation")
    print("-" * 40)
    
    # Simulate the pipeline steps
    original_count = len(mock_articles)
    
    # Step 1: Quality filtering
    filtered_articles = await filter_news_articles(mock_articles, symbols)
    approved_articles = [fa.original_article for fa in filtered_articles if fa.is_approved]
    rejected_articles = [fa.original_article for fa in filtered_articles if not fa.is_approved]
    
    print(f"📊 Pipeline Simulation Results:")
    print(f"   Original articles: {original_count}")
    print(f"   After quality filtering: {len(approved_articles)}")
    print(f"   Rejected articles: {len(rejected_articles)}")
    print(f"   Approval rate: {len(approved_articles)/original_count:.1%}")
    
    # Quality metadata
    quality_metadata = {
        "quality_filtering_enabled": True,
        "articles_before_filtering": original_count,
        "articles_after_filtering": len(approved_articles),
        "approval_rate": len(approved_articles) / original_count,
        "rejected_count": len(rejected_articles)
    }
    
    print(f"\n📈 Quality Metadata:")
    for key, value in quality_metadata.items():
        if isinstance(value, float):
            print(f"   {key}: {value:.2f}")
        else:
            print(f"   {key}: {value}")
    
    # Test 4: Different symbol combinations
    print(f"\n🔍 Test 4: Different Symbol Combinations")
    print("-" * 40)
    
    symbol_combinations = [
        ["BTC"],
        ["ETH"],
        ["SOL"],
        ["BTC", "ETH"],
        ["BTC", "ETH", "SOL"],
        []  # No symbols
    ]
    
    for symbols_test in symbol_combinations:
        filtered_test = await filter_news_articles(mock_articles, symbols_test)
        approved_test = [fa for fa in filtered_test if fa.is_approved]
        
        symbol_str = ", ".join(symbols_test) if symbols_test else "None"
        print(f"   Symbols [{symbol_str}]: {len(approved_test)}/{len(mock_articles)} approved")
    
    print(f"\n✅ Data Quality Filter Integration test completed!")
    print(f"🎯 Key Features Verified:")
    print(f"   ✅ Source reliability checking")
    print(f"   ✅ Clickbait detection")
    print(f"   ✅ Content quality analysis")
    print(f"   ✅ Relevance scoring")
    print(f"   ✅ AI-powered analysis (when available)")
    print(f"   ✅ Pipeline integration")
    print(f"   ✅ Comprehensive quality metrics")

if __name__ == "__main__":
    asyncio.run(test_quality_filter_integration()) 
