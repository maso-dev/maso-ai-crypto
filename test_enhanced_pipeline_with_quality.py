#!/usr/bin/env python3
"""
Test Enhanced News Pipeline with Data Quality Filtering
"""

import asyncio
import logging
from utils.enhanced_news_pipeline import EnhancedNewsPipeline, get_enhanced_crypto_news

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_enhanced_pipeline_with_quality():
    """Test the enhanced news pipeline with data quality filtering."""
    
    print("🧪 Testing Enhanced News Pipeline with Data Quality Filtering...")
    print("=" * 80)
    
    # Create pipeline instance
    pipeline = EnhancedNewsPipeline()
    
    # Test with crypto symbols
    symbols = ["BTC", "ETH", "SOL"]
    
    try:
        # Process news with quality filtering
        result = await pipeline.process_crypto_news(
            symbols=symbols,
            hours_back=24,
            enable_enrichment=True,
            max_articles=20
        )
        
        if result["success"]:
            print("\n✅ News processing completed successfully!")
            
            # Display results
            articles = result["articles"]
            metadata = result["metadata"]
            quality_metadata = result.get("quality_metadata", {})
            processing_info = result["processing_info"]
            
            print(f"\n📊 Processing Results:")
            print(f"   Articles processed: {len(articles)}")
            print(f"   Symbols searched: {', '.join(processing_info['symbols_searched'])}")
            print(f"   Time range: {processing_info['hours_back']} hours back")
            print(f"   Enrichment enabled: {processing_info['enrichment_enabled']}")
            print(f"   Quality filtering enabled: {processing_info['quality_filtering_enabled']}")
            print(f"   LangSmith enabled: {processing_info['langsmith_enabled']}")
            
            # Quality filtering results
            if quality_metadata.get("quality_filtering_enabled"):
                print(f"\n🔍 Quality Filtering Results:")
                print(f"   Articles before filtering: {quality_metadata['articles_before_filtering']}")
                print(f"   Articles after filtering: {quality_metadata['articles_after_filtering']}")
                print(f"   Approval rate: {quality_metadata['approval_rate']:.1%}")
                print(f"   Rejected articles: {quality_metadata['rejected_count']}")
            
            # Metadata analysis
            if metadata:
                print(f"\n📈 Metadata Analysis:")
                print(f"   Total articles: {metadata.get('total_articles', 0)}")
                print(f"   Unique sources: {metadata.get('unique_sources', 0)}")
                print(f"   Top sources: {', '.join(metadata.get('sources', [])[:5])}")
                
                enrichment_stats = metadata.get('enrichment_stats', {})
                if enrichment_stats:
                    print(f"   Enriched articles: {enrichment_stats.get('enriched_count', 0)}")
                    print(f"   Average sentiment: {enrichment_stats.get('avg_sentiment', 0):.2f}")
                    print(f"   Average trust: {enrichment_stats.get('avg_trust', 0):.2f}")
                    print(f"   Top categories: {', '.join(enrichment_stats.get('top_categories', [])[:3])}")
            
            # Display sample articles
            if articles:
                print(f"\n📰 Sample Articles:")
                for i, article in enumerate(articles[:3], 1):
                    title = article.get('title', 'No title')
                    source = article.get('source', {}).get('name', 'Unknown source')
                    print(f"   {i}. {title[:60]}... (Source: {source})")
                    
                    # Show enrichment data if available
                    if 'enrichment' in article:
                        enrichment = article['enrichment']
                        sentiment = enrichment.get('sentiment', 'N/A')
                        trust = enrichment.get('trust', 'N/A')
                        print(f"      Sentiment: {sentiment}, Trust: {trust}")
            
            print(f"\n⏰ Processing completed at: {processing_info['processing_time']}")
            
        else:
            print(f"\n❌ News processing failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()

async def test_convenience_function():
    """Test the convenience function."""
    
    print("\n" + "=" * 80)
    print("🧪 Testing Convenience Function...")
    
    try:
        result = await get_enhanced_crypto_news(
            symbols=["BTC", "ETH"],
            hours_back=12,
            enable_enrichment=True
        )
        
        if result["success"]:
            print("✅ Convenience function test passed!")
            print(f"   Articles returned: {len(result['articles'])}")
            print(f"   Quality filtering: {result['processing_info']['quality_filtering_enabled']}")
        else:
            print(f"❌ Convenience function failed: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ Convenience function test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_enhanced_pipeline_with_quality())
    asyncio.run(test_convenience_function()) 
