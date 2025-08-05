#!/usr/bin/env python3
"""
Test script for Enhanced Vector RAG System
Tests the integration with existing milvus.py and enrichment.py work.
"""

import asyncio
import os
from datetime import datetime, timezone
from utils.vector_rag import (
    EnhancedVectorRAG,
    VectorQuery,
    QueryType,
    intelligent_search,
    insert_enhanced_news_batch,
)

# Test data
TEST_NEWS_ITEMS = [
    {
        "title": "Bitcoin ETF inflows reach record highs",
        "content": "Bitcoin ETFs have seen unprecedented inflows this week, with over $1 billion in new investments. Analysts suggest this could signal a new bull market phase.",
        "url": "https://example.com/bitcoin-etf-news",
        "publishedAt": "2024-01-15T10:00:00Z",
        "source_name": "CryptoNews",
        "crypto_topic": "Bitcoin",
    },
    {
        "title": "Ethereum layer 2 solutions gain traction",
        "content": "Ethereum layer 2 scaling solutions like Arbitrum and Optimism are seeing increased adoption as gas fees remain high on the mainnet.",
        "url": "https://example.com/ethereum-l2-news",
        "publishedAt": "2024-01-15T11:00:00Z",
        "source_name": "DeFiPulse",
        "crypto_topic": "Ethereum",
    },
]


async def test_vector_rag_integration():
    """Test the enhanced vector RAG system integration."""
    print("🧪 Testing Enhanced Vector RAG System")
    print("=" * 50)

    # Initialize the system
    rag = EnhancedVectorRAG()
    print(f"✅ Initialized Enhanced Vector RAG")
    print(f"   Milvus URI: {rag.milvus_uri}")
    print(f"   Collection: {rag.collection_name}")
    print(f"   LangSmith: {'Enabled' if rag.tracer else 'Disabled'}")

    # Test 1: Insert enhanced news
    print("\n📝 Test 1: Insert Enhanced News")
    try:
        inserted, updated, errors = await insert_enhanced_news_batch(TEST_NEWS_ITEMS)
        print(f"   ✅ Inserted: {inserted}, Updated: {updated}, Errors: {len(errors)}")
        if errors:
            print(f"   ⚠️ Errors: {errors}")
    except Exception as e:
        print(f"   ❌ Insertion failed: {e}")

    # Test 2: Semantic search
    print("\n🔍 Test 2: Semantic Search")
    try:
        query = VectorQuery(
            query_text="Bitcoin ETF performance",
            query_type=QueryType.SEMANTIC_SEARCH,
            symbols=["Bitcoin"],
            limit=5,
        )
        results = await rag.intelligent_search(query)
        print(f"   ✅ Found {len(results)} results")
        for i, result in enumerate(results[:3]):
            print(
                f"   {i+1}. {result.title[:50]}... (score: {result.similarity_score:.3f})"
            )
    except Exception as e:
        print(f"   ❌ Semantic search failed: {e}")

    # Test 3: ReAct agent search
    print("\n🤖 Test 3: ReAct Agent Search")
    try:
        query = VectorQuery(
            query_text="What are the latest developments in crypto ETFs?",
            query_type=QueryType.REACT_AGENT,
            symbols=["Bitcoin", "Ethereum"],
            limit=5,
        )
        results = await rag.intelligent_search(query)
        print(f"   ✅ ReAct Agent found {len(results)} results")
        for i, result in enumerate(results[:3]):
            print(
                f"   {i+1}. {result.title[:50]}... (score: {result.similarity_score:.3f})"
            )
    except Exception as e:
        print(f"   ❌ ReAct search failed: {e}")

    # Test 4: Temporal search
    print("\n⏰ Test 4: Temporal Search")
    try:
        query = VectorQuery(
            query_text="recent crypto news",
            query_type=QueryType.TEMPORAL_SEARCH,
            time_range_hours=24,
            limit=5,
        )
        results = await rag.intelligent_search(query)
        print(f"   ✅ Temporal search found {len(results)} results")
        for i, result in enumerate(results[:3]):
            print(
                f"   {i+1}. {result.title[:50]}... ({result.published_at.strftime('%H:%M')})"
            )
    except Exception as e:
        print(f"   ❌ Temporal search failed: {e}")

    # Test 5: Hybrid search
    print("\n🔄 Test 5: Hybrid Search")
    try:
        query = VectorQuery(
            query_text="Ethereum scaling solutions",
            query_type=QueryType.HYBRID_SEARCH,
            symbols=["Ethereum"],
            limit=5,
        )
        results = await rag.intelligent_search(query)
        print(f"   ✅ Hybrid search found {len(results)} results")
        for i, result in enumerate(results[:3]):
            print(
                f"   {i+1}. {result.title[:50]}... (score: {result.similarity_score:.3f})"
            )
    except Exception as e:
        print(f"   ❌ Hybrid search failed: {e}")

    print("\n" + "=" * 50)
    print("✅ Enhanced Vector RAG System Tests Complete")


async def test_convenience_functions():
    """Test convenience functions."""
    print("\n🧪 Testing Convenience Functions")
    print("=" * 30)

    # Test intelligent_search convenience function
    try:
        results = await intelligent_search(
            query_text="Bitcoin market analysis",
            query_type=QueryType.SEMANTIC_SEARCH,
            symbols=["Bitcoin"],
            time_range_hours=24,
            limit=3,
        )
        print(f"✅ Convenience search found {len(results)} results")
    except Exception as e:
        print(f"❌ Convenience search failed: {e}")


async def test_langsmith_integration():
    """Test LangSmith integration."""
    print("\n🧪 Testing LangSmith Integration")
    print("=" * 30)

    if not os.getenv("LANGSMITH_API_KEY"):
        print("⚠️ LANGSMITH_API_KEY not set - skipping LangSmith tests")
        return

    try:
        # Test with LangSmith tracing
        config = {
            "tags": ["test", "vector_rag"],
            "metadata": {
                "test_type": "langsmith_integration",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        }

        query = VectorQuery(
            query_text="crypto market trends", query_type=QueryType.REACT_AGENT, limit=3
        )

        rag = EnhancedVectorRAG()
        results = await rag.intelligent_search(query, config)
        print(f"✅ LangSmith traced search found {len(results)} results")
        print("   Check LangSmith dashboard for traces")

    except Exception as e:
        print(f"❌ LangSmith integration failed: {e}")


async def main():
    """Run all tests."""
    print("🚀 Starting Enhanced Vector RAG System Tests")
    print("=" * 60)

    await test_vector_rag_integration()
    await test_convenience_functions()
    await test_langsmith_integration()

    print("\n🎉 All tests completed!")


if __name__ == "__main__":
    asyncio.run(main())
