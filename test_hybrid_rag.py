#!/usr/bin/env python3
"""
Test script for Hybrid RAG System
Tests vector + graph database integration.
"""

import asyncio
import os
from datetime import datetime, timezone
from utils.hybrid_rag import (
    HybridRAGSystem,
    HybridQueryType,
    hybrid_search,
    insert_hybrid_news_article,
    get_hybrid_statistics,
)


async def test_hybrid_rag_system():
    """Test the hybrid RAG system."""
    print("🧪 Testing Hybrid RAG System")
    print("=" * 50)

    # Initialize the hybrid system
    hybrid_system = HybridRAGSystem()
    print(f"✅ Initialized Hybrid RAG System")

    # Test 1: Vector-only search
    print("\n📊 Test 1: Vector-only search")
    try:
        results = await hybrid_search(
            query_text="Bitcoin price analysis",
            query_type=HybridQueryType.VECTOR_ONLY,
            symbols=["Bitcoin"],
            limit=3,
        )
        print(f"   ✅ Vector search completed: {len(results)} results")
        for i, result in enumerate(results[:2]):
            print(
                f"   {i+1}. {result.title[:50]}... (confidence: {result.confidence_score:.2f})"
            )
    except Exception as e:
        print(f"   ❌ Vector search failed: {e}")

    # Test 2: Graph-only search
    print("\n🕸️ Test 2: Graph-only search")
    try:
        results = await hybrid_search(
            query_text="Bitcoin",
            query_type=HybridQueryType.GRAPH_ONLY,
            symbols=["Bitcoin"],
            limit=3,
        )
        print(f"   ✅ Graph search completed: {len(results)} results")
        for i, result in enumerate(results[:2]):
            print(
                f"   {i+1}. {result.title[:50]}... (confidence: {result.confidence_score:.2f})"
            )
    except Exception as e:
        print(f"   ❌ Graph search failed: {e}")

    # Test 3: Hybrid search
    print("\n🔗 Test 3: Hybrid search")
    try:
        results = await hybrid_search(
            query_text="crypto market trends",
            query_type=HybridQueryType.HYBRID,
            symbols=["Bitcoin", "Ethereum"],
            limit=5,
        )
        print(f"   ✅ Hybrid search completed: {len(results)} results")
        for i, result in enumerate(results[:3]):
            print(
                f"   {i+1}. {result.title[:50]}... (confidence: {result.confidence_score:.2f})"
            )
    except Exception as e:
        print(f"   ❌ Hybrid search failed: {e}")

    # Test 4: ReAct hybrid search
    print("\n🤖 Test 4: ReAct hybrid search")
    try:
        results = await hybrid_search(
            query_text="Bitcoin ETF developments",
            query_type=HybridQueryType.REACT_HYBRID,
            symbols=["Bitcoin"],
            limit=3,
        )
        print(f"   ✅ ReAct hybrid search completed: {len(results)} results")
        for i, result in enumerate(results[:2]):
            print(
                f"   {i+1}. {result.title[:50]}... (confidence: {result.confidence_score:.2f})"
            )
    except Exception as e:
        print(f"   ❌ ReAct hybrid search failed: {e}")

    # Test 5: Entity network search
    print("\n🕸️ Test 5: Entity network search")
    try:
        results = await hybrid_search(
            query_text="Elon Musk",
            query_type=HybridQueryType.ENTITY_NETWORK,
            symbols=["Bitcoin"],
            limit=3,
        )
        print(f"   ✅ Entity network search completed: {len(results)} results")
        for i, result in enumerate(results[:2]):
            print(
                f"   {i+1}. {result.title[:50]}... (confidence: {result.confidence_score:.2f})"
            )
    except Exception as e:
        print(f"   ❌ Entity network search failed: {e}")

    # Test 6: Sentiment analysis search
    print("\n😊 Test 6: Sentiment analysis search")
    try:
        results = await hybrid_search(
            query_text="market sentiment",
            query_type=HybridQueryType.SENTIMENT_ANALYSIS,
            symbols=["Bitcoin", "Ethereum"],
            limit=3,
        )
        print(f"   ✅ Sentiment analysis search completed: {len(results)} results")
        for i, result in enumerate(results[:2]):
            print(
                f"   {i+1}. {result.title[:50]}... (confidence: {result.confidence_score:.2f})"
            )
    except Exception as e:
        print(f"   ❌ Sentiment analysis search failed: {e}")

    print("\n" + "=" * 50)
    print("✅ Hybrid RAG System Tests Complete")


async def test_hybrid_insertion():
    """Test hybrid news insertion."""
    print("\n🧪 Testing Hybrid News Insertion")
    print("=" * 40)

    # Sample news article
    article_data = {
        "title": "Bitcoin Reaches New All-Time High",
        "content": "Bitcoin has reached a new all-time high of $50,000, driven by increased institutional adoption and positive market sentiment.",
        "source_url": "https://example.com/bitcoin-ath",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "sentiment_score": 0.8,
        "crypto_topic": "Bitcoin",
        "relevance_score": 0.9,
        "symbols": ["Bitcoin"],
    }

    # Sample entities
    entities = [
        {"name": "Bitcoin", "type": "cryptocurrency", "related_symbols": ["Bitcoin"]},
        {
            "name": "Institutional Investors",
            "type": "market_participant",
            "related_symbols": ["Bitcoin", "Ethereum"],
        },
    ]

    try:
        hybrid_id = await insert_hybrid_news_article(article_data, entities)
        print(f"✅ Hybrid insertion completed: {hybrid_id}")
    except Exception as e:
        print(f"❌ Hybrid insertion failed: {e}")


async def test_hybrid_statistics():
    """Test hybrid system statistics."""
    print("\n🧪 Testing Hybrid Statistics")
    print("=" * 35)

    try:
        stats = await get_hybrid_statistics()
        print(f"✅ Hybrid statistics retrieved")
        print(f"   Vector RAG: {'✅' if stats.get('vector_rag') else '❌'}")
        print(
            f"   Graph RAG: {'✅' if stats.get('graph_rag', {}).get('connected', False) else '❌'}"
        )
        print(
            f"   Hybrid System: {stats.get('hybrid_system', {}).get('status', 'unknown')}"
        )
    except Exception as e:
        print(f"❌ Hybrid statistics failed: {e}")


async def test_api_endpoints():
    """Test the hybrid RAG API endpoints."""
    print("\n🧪 Testing Hybrid RAG API Endpoints")
    print("=" * 45)

    import httpx

    base_url = "http://localhost:8000/brain"

    # Test query types endpoint
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/hybrid/query-types")
            if response.status_code == 200:
                data = response.json()
                print(
                    f"✅ Query types endpoint: {len(data.get('query_types', []))} types"
                )
            else:
                print(f"❌ Query types endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Query types endpoint error: {e}")

    # Test stats endpoint
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/hybrid/stats")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Stats endpoint: {data.get('success', False)}")
            else:
                print(f"❌ Stats endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Stats endpoint error: {e}")

    # Test hybrid search endpoint
    try:
        async with httpx.AsyncClient() as client:
            search_data = {
                "query": "Bitcoin market analysis",
                "query_type": "hybrid",
                "symbols": ["Bitcoin"],
                "limit": 3,
            }
            response = await client.post(f"{base_url}/hybrid/search", json=search_data)
            if response.status_code == 200:
                data = response.json()
                print(
                    f"✅ Hybrid search endpoint: {data.get('results_count', 0)} results"
                )
            else:
                print(f"❌ Hybrid search endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Hybrid search endpoint error: {e}")


async def main():
    """Run all tests."""
    print("🚀 Starting Hybrid RAG System Tests")
    print("=" * 60)

    await test_hybrid_rag_system()
    await test_hybrid_insertion()
    await test_hybrid_statistics()
    await test_api_endpoints()

    print("\n🎉 All Hybrid RAG tests completed!")


if __name__ == "__main__":
    asyncio.run(main())
