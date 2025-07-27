#!/usr/bin/env python3
"""
Test script for the optimized pipeline.
Tests summary-focused processing, metadata preparation, and vector/graph data generation.
"""

import asyncio
import json
from datetime import datetime, timedelta
from utils.optimized_pipeline import OptimizedNewsPipeline, run_optimized_pipeline

def create_test_articles():
    """Create test articles with temporal context."""
    now = datetime.utcnow()
    
    return [
        {
            "title": "Bitcoin ETF Approval Sends Markets Soaring",
            "content": "The SEC has officially approved Bitcoin ETFs, marking a historic moment for cryptocurrency adoption. Major financial institutions including BlackRock and Fidelity have already filed applications. Analysts predict this could bring billions in institutional investment to the crypto market.",
            "crypto_topic": "BTC",
            "source_name": "CoinDesk",
            "source_url": "https://example.com/bitcoin-etf",
            "published_at": (now - timedelta(hours=1)).isoformat() + "Z"
        },
        {
            "title": "Ethereum Layer 2 Solutions Gain Traction",
            "content": "Ethereum Layer 2 scaling solutions are seeing increased adoption as gas fees remain high. Polygon, Arbitrum, and Optimism are leading the charge with significant TVL growth. Developers are increasingly choosing L2s for their applications.",
            "crypto_topic": "ETH",
            "source_name": "Decrypt",
            "source_url": "https://example.com/ethereum-l2",
            "published_at": (now - timedelta(hours=6)).isoformat() + "Z"
        },
        {
            "title": "DeFi Protocol Exploits Continue to Rise",
            "content": "DeFi protocols continue to face security challenges with multiple high-profile exploits reported this month. Security experts recommend increased auditing and insurance coverage for DeFi projects.",
            "crypto_topic": "DEFI",
            "source_name": "The Block",
            "source_url": "https://example.com/defi-exploits",
            "published_at": (now - timedelta(days=2)).isoformat() + "Z"
        }
    ]

async def test_optimized_pipeline():
    """Test the complete optimized pipeline."""
    print("🧪 Testing Optimized Pipeline...")
    
    # Create test articles
    test_articles = create_test_articles()
    print(f"✅ Created {len(test_articles)} test articles")
    
    # Run the pipeline
    pipeline = OptimizedNewsPipeline()
    processed_articles = await pipeline.process_articles_batch(test_articles)
    
    # Validate results
    if len(processed_articles) != len(test_articles):
        print(f"❌ Expected {len(test_articles)} processed articles, got {len(processed_articles)}")
        return False
    
    print(f"✅ Successfully processed {len(processed_articles)} articles")
    
    # Validate structure of processed articles
    for i, article in enumerate(processed_articles):
        required_keys = ["vector_data", "graph_data", "metadata"]
        missing_keys = [key for key in required_keys if key not in article]
        
        if missing_keys:
            print(f"❌ Article {i+1} missing keys: {missing_keys}")
            return False
        
        # Validate vector data
        vector_data = article["vector_data"]
        vector_required = ["chunk_text", "vector", "sparse_vector", "title", "crypto_topic"]
        vector_missing = [key for key in vector_required if key not in vector_data]
        
        if vector_missing:
            print(f"❌ Article {i+1} vector data missing: {vector_missing}")
            return False
        
        # Validate graph data
        graph_data = article["graph_data"]
        graph_required = ["node_id", "node_type", "properties", "relationships"]
        graph_missing = [key for key in graph_required if key not in graph_data]
        
        if graph_missing:
            print(f"❌ Article {i+1} graph data missing: {graph_missing}")
            return False
    
    print("✅ All processed articles have correct structure")
    
    # Test data extraction
    vector_data_batch = pipeline.get_vector_data_batch(processed_articles)
    graph_data_batch = pipeline.get_graph_data_batch(processed_articles)
    
    if len(vector_data_batch) != len(processed_articles):
        print(f"❌ Vector data batch size mismatch: {len(vector_data_batch)} vs {len(processed_articles)}")
        return False
    
    if len(graph_data_batch) != len(processed_articles):
        print(f"❌ Graph data batch size mismatch: {len(graph_data_batch)} vs {len(processed_articles)}")
        return False
    
    print("✅ Data extraction working correctly")
    
    # Test summary generation
    summary = pipeline.get_processing_summary(processed_articles)
    
    required_summary_keys = ["total_processed", "breaking_news", "recent_news", "avg_sentiment"]
    summary_missing = [key for key in required_summary_keys if key not in summary]
    
    if summary_missing:
        print(f"❌ Summary missing keys: {summary_missing}")
        return False
    
    print(f"✅ Processing Summary:")
    print(f"   Total processed: {summary['total_processed']}")
    print(f"   Breaking news: {summary['breaking_news']}")
    print(f"   Recent news: {summary['recent_news']}")
    print(f"   Avg sentiment: {summary['avg_sentiment']}")
    
    return True

async def test_summary_focused_chunking():
    """Test summary-focused chunking specifically."""
    print("\n🧪 Testing Summary-Focused Chunking...")
    
    from utils.optimized_embedding import create_summary_focused_chunk
    
    # Test article
    test_article = {
        "title": "Bitcoin Reaches New All-Time High",
        "crypto_topic": "BTC",
        "source_name": "CoinDesk",
        "published_at": "2024-01-15T10:30:00Z",
        "categories": ["Bitcoin", "Price Action"],
        "market_impact": "high",
        "time_relevance": "breaking"
    }
    
    test_summary = "Bitcoin has reached a new all-time high of $50,000, driven by institutional adoption and ETF inflows."
    
    # Create summary-focused chunk
    chunk_data = create_summary_focused_chunk(test_article, test_summary)
    
    # Validate chunk structure
    required_chunk_keys = ["searchable_text", "metadata", "summary"]
    missing_keys = [key for key in required_chunk_keys if key not in chunk_data]
    
    if missing_keys:
        print(f"❌ Chunk missing keys: {missing_keys}")
        return False
    
    # Validate searchable text contains summary
    searchable_text = chunk_data["searchable_text"]
    if test_summary not in searchable_text:
        print("❌ Summary not found in searchable text")
        return False
    
    # Validate metadata structure
    metadata = chunk_data["metadata"]
    required_metadata = ["article_id", "title", "crypto_topic", "summary", "sentiment", "market_impact"]
    missing_metadata = [key for key in required_metadata if key not in metadata]
    
    if missing_metadata:
        print(f"❌ Metadata missing keys: {missing_metadata}")
        return False
    
    print("✅ Summary-focused chunking working correctly")
    print(f"   Searchable text length: {len(searchable_text)} characters")
    print(f"   Article ID: {metadata['article_id']}")
    print(f"   Market Impact: {metadata['market_impact']}")
    
    return True

async def test_convenience_function():
    """Test the convenience function."""
    print("\n🧪 Testing Convenience Function...")
    
    from utils.optimized_pipeline import run_optimized_pipeline
    
    # Create test articles
    test_articles = create_test_articles()
    
    # Run convenience function
    result = await run_optimized_pipeline(test_articles)
    
    # Validate result structure
    required_result_keys = ["processed_articles", "vector_data", "graph_data", "summary"]
    missing_keys = [key for key in required_result_keys if key not in result]
    
    if missing_keys:
        print(f"❌ Result missing keys: {missing_keys}")
        return False
    
    # Validate data consistency
    if len(result["processed_articles"]) != len(result["vector_data"]):
        print("❌ Processed articles and vector data count mismatch")
        return False
    
    if len(result["processed_articles"]) != len(result["graph_data"]):
        print("❌ Processed articles and graph data count mismatch")
        return False
    
    print("✅ Convenience function working correctly")
    print(f"   Processed: {len(result['processed_articles'])} articles")
    print(f"   Vector data: {len(result['vector_data'])} entries")
    print(f"   Graph data: {len(result['graph_data'])} entries")
    
    return True

async def main():
    """Run all tests."""
    print("🚀 Starting Optimized Pipeline Tests\n")
    
    try:
        # Run tests
        test1 = await test_optimized_pipeline()
        test2 = await test_summary_focused_chunking()
        test3 = await test_convenience_function()
        
        print(f"\n📊 Test Results:")
        print(f"   Optimized pipeline: {'✅ PASSED' if test1 else '❌ FAILED'}")
        print(f"   Summary chunking: {'✅ PASSED' if test2 else '❌ FAILED'}")
        print(f"   Convenience function: {'✅ PASSED' if test3 else '❌ FAILED'}")
        
        if all([test1, test2, test3]):
            print("\n🎉 All optimized pipeline tests passed!")
            print("   The pipeline is ready for integration.")
        else:
            print("\n⚠️  Some tests failed. Please check the implementation.")
            
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 
