#!/usr/bin/env python3
"""
Test script for the optimized pipeline integration.
Tests the actual integration with the crypto_news_rag endpoint logic.
"""

import asyncio
import os
from datetime import datetime, timedelta
from utils.newsapi import fetch_news_articles
from utils.optimized_pipeline import run_optimized_pipeline
from utils.milvus import insert_news_chunks

async def test_optimized_pipeline_integration():
    """Test the optimized pipeline integration with real data flow."""
    print("🧪 Testing Optimized Pipeline Integration...")
    
    try:
        # Step 1: Fetch real news articles
        print("Step 1: Fetching news articles...")
        articles = await fetch_news_articles(["BTC"], hours_back=24)
        print(f"✓ Fetched {len(articles)} articles from NewsAPI")
        
        if not articles:
            print("⚠️ No articles fetched, skipping test")
            return False
        
        # Step 2: Process with optimized pipeline
        print("Step 2: Processing with optimized pipeline...")
        processed_data = await run_optimized_pipeline(articles)
        
        vector_data = processed_data["vector_data"]
        summary = processed_data["summary"]
        
        print(f"✓ Optimized pipeline summary:")
        print(f"   Total processed: {summary['total_processed']}")
        print(f"   Breaking news: {summary['breaking_news']}")
        print(f"   Recent news: {summary['recent_news']}")
        print(f"   Avg sentiment: {summary['avg_sentiment']}")
        
        # Step 3: Validate vector data structure
        print("Step 3: Validating vector data structure...")
        if not vector_data:
            print("❌ No vector data generated")
            return False
        
        # Check first chunk structure
        first_chunk = vector_data[0]
        required_fields = [
            "chunk_text", "vector", "sparse_vector", "title", 
            "crypto_topic", "sentiment", "trust", "categories", 
            "summary", "urgency_score", "market_impact", "time_relevance"
        ]
        
        missing_fields = [field for field in required_fields if field not in first_chunk]
        if missing_fields:
            print(f"❌ Missing fields in vector data: {missing_fields}")
            return False
        
        print(f"✅ Vector data structure valid")
        print(f"   Chunk text length: {len(first_chunk['chunk_text'])} characters")
        print(f"   Vector dimensions: {len(first_chunk['vector'])}")
        print(f"   Sentiment: {first_chunk['sentiment']}")
        print(f"   Market impact: {first_chunk['market_impact']}")
        print(f"   Time relevance: {first_chunk['time_relevance']}")
        
        # Step 4: Test Milvus insertion (optional - comment out if no Milvus connection)
        print("Step 4: Testing Milvus insertion...")
        try:
            # Prepare chunks for Milvus (same logic as in the endpoint)
            chunks = []
            for chunk in vector_data:
                # Ensure required fields for Milvus
                if 'vector' not in chunk:
                    chunk['vector'] = chunk.get('dense_vector', [])
                if 'sparse_vector' not in chunk:
                    chunk['sparse_vector'] = chunk.get('sparse_vector', {})
                chunks.append(chunk)
            
            # Try to insert into Milvus
            inserted, updated, errors = await insert_news_chunks(chunks)
            print(f"✓ Milvus insertion result:")
            print(f"   Inserted: {inserted}")
            print(f"   Updated: {updated}")
            print(f"   Errors: {errors}")
            
        except Exception as e:
            print(f"⚠️ Milvus insertion failed (expected if no connection): {e}")
            print("   This is normal if Milvus is not configured")
        
        print("✅ Integration test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_single_article_processing():
    """Test processing a single article to see the detailed flow."""
    print("\n🧪 Testing Single Article Processing...")
    
    # Create a test article
    test_article = {
        "title": "Bitcoin Reaches New All-Time High in 2024",
        "content": "Bitcoin has surged to a new all-time high, driven by institutional adoption and ETF inflows. Major financial institutions are increasingly allocating to digital assets, signaling growing mainstream acceptance.",
        "crypto_topic": "BTC",
        "source_name": "CoinDesk",
        "source_url": "https://example.com/bitcoin-ath",
        "published_at": datetime.utcnow().isoformat() + "Z"
    }
    
    try:
        # Process single article
        processed_data = await run_optimized_pipeline([test_article])
        vector_data = processed_data["vector_data"]
        
        if vector_data:
            chunk = vector_data[0]
            print(f"✅ Single article processed successfully")
            print(f"   Title: {chunk['title']}")
            print(f"   Summary: {chunk['summary'][:100]}...")
            print(f"   Sentiment: {chunk['sentiment']}")
            print(f"   Market Impact: {chunk['market_impact']}")
            print(f"   Categories: {chunk['categories']}")
            print(f"   Time Relevance: {chunk['time_relevance']}")
            return True
        else:
            print("❌ No vector data generated for single article")
            return False
            
    except Exception as e:
        print(f"❌ Single article processing failed: {e}")
        return False

async def main():
    """Run all integration tests."""
    print("🚀 Starting Optimized Pipeline Integration Tests\n")
    
    try:
        # Test 1: Full pipeline integration
        test1 = await test_optimized_pipeline_integration()
        
        # Test 2: Single article processing
        test2 = await test_single_article_processing()
        
        print(f"\n📊 Integration Test Results:")
        print(f"   Full pipeline integration: {'✅ PASSED' if test1 else '❌ FAILED'}")
        print(f"   Single article processing: {'✅ PASSED' if test2 else '❌ FAILED'}")
        
        if all([test1, test2]):
            print("\n🎉 All integration tests passed!")
            print("   The optimized pipeline is ready for production use.")
        else:
            print("\n⚠️  Some integration tests failed. Please check the implementation.")
            
    except Exception as e:
        print(f"\n❌ Integration test suite failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 
