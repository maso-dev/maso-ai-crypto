#!/usr/bin/env python3
"""
Test Qdrant Integration Step by Step
This script tests the Qdrant integration in isolation
"""

import os
import sys
import asyncio
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.qdrant_client import (
    QdrantVectorSearch,
    test_qdrant_connection,
    is_qdrant_available,
)
from utils.local_vector_fallback import simple_vectorize


async def test_qdrant_step_by_step():
    """Test Qdrant integration step by step"""

    print("🧪 Testing Qdrant Integration Step by Step")
    print("=" * 50)

    # Step 1: Check if Qdrant is available
    print("\n1️⃣ Checking Qdrant availability...")
    if not is_qdrant_available():
        print("❌ Qdrant is not available")
        print("   Make sure QDRANT_VECTOR_API environment variable is set")
        return False

    print("✅ Qdrant appears to be available")

    # Step 2: Test connection
    print("\n2️⃣ Testing Qdrant connection...")
    try:
        connection_status = test_qdrant_connection()
        print(f"   Status: {connection_status['status']}")

        if connection_status["status"] == "connected":
            print("✅ Qdrant connection successful")
            if "collection_info" in connection_status:
                info = connection_status["collection_info"]
                print(f"   Collection: {info.get('name', 'unknown')}")
                print(
                    f"   Vector size: {info.get('config', {}).get('vector_size', 'unknown')}"
                )
                print(f"   Points count: {info.get('points_count', 'unknown')}")
        else:
            print(
                f"❌ Qdrant connection failed: {connection_status.get('error', 'unknown error')}"
            )
            return False

    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

    # Step 3: Test document addition
    print("\n3️⃣ Testing document addition...")
    try:
        client = QdrantVectorSearch()

        # Test document
        test_content = (
            "Bitcoin reaches new all-time high as institutional adoption increases"
        )
        test_metadata = {
            "symbols": ["BTC"],
            "category": "crypto_news",
            "sentiment": "positive",
            "source": "test_script",
        }

        # Generate vector
        vector = simple_vectorize(test_content)
        print(f"   Generated vector with {len(vector)} dimensions")

        # Add document
        doc_id = client.add_document(test_content, test_metadata, vector)
        print(f"✅ Document added successfully with ID: {doc_id}")

    except Exception as e:
        print(f"❌ Document addition failed: {e}")
        return False

    # Step 4: Test search
    print("\n4️⃣ Testing document search...")
    try:
        # Search for the document we just added
        search_query = "Bitcoin institutional adoption"
        query_vector = simple_vectorize(search_query)

        results = client.search(query_vector=query_vector, limit=5, min_score=0.1)

        print(f"✅ Search returned {len(results)} results")

        if results:
            print("   Top result:")
            top_result = results[0]
            print(f"     Score: {top_result['score']:.3f}")
            print(f"     Content: {top_result['content'][:100]}...")
            print(f"     Symbols: {top_result['symbols']}")

    except Exception as e:
        print(f"❌ Search failed: {e}")
        return False

    # Step 5: Test collection info
    print("\n5️⃣ Testing collection info...")
    try:
        info = client.get_collection_info()
        print(f"✅ Collection info retrieved:")
        print(f"   Name: {info.get('name', 'unknown')}")
        print(f"   Points count: {info.get('points_count', 'unknown')}")
        print(f"   Vector size: {info.get('config', {}).get('vector_size', 'unknown')}")

    except Exception as e:
        print(f"❌ Collection info failed: {e}")
        return False

    print("\n🎉 All tests passed! Qdrant integration is working correctly.")
    return True


async def test_with_fallback():
    """Test the enhanced hybrid RAG system with Qdrant"""

    print("\n🔄 Testing Enhanced Hybrid RAG with Qdrant")
    print("=" * 50)

    try:
        from utils.enhanced_hybrid_rag import get_enhanced_hybrid_rag

        rag = get_enhanced_hybrid_rag()

        # Test status
        status = rag.get_status()
        print(f"   System: {status.get('system', 'unknown')}")
        print(f"   Qdrant available: {status.get('qdrant_available', False)}")
        print(f"   Qdrant operational: {status.get('qdrant_operational', False)}")
        print(f"   Fallback mode: {status.get('fallback_mode', False)}")

        # Test document addition through RAG
        print("\n   Testing document addition through RAG...")
        test_content = (
            "Ethereum 2.0 staking reaches new milestones as DeFi continues to grow"
        )
        test_metadata = {
            "symbols": ["ETH"],
            "category": "crypto_news",
            "sentiment": "positive",
            "source": "test_script",
        }

        result = await rag.add_document(test_content, test_metadata)
        print(f"   RAG add result: {result}")

        # Test search through RAG
        print("\n   Testing search through RAG...")
        search_result = await rag.search("Ethereum staking DeFi", limit=3)
        print(f"   Search source: {search_result.get('source', 'unknown')}")
        print(f"   Results count: {len(search_result.get('results', []))}")

        return True

    except Exception as e:
        print(f"❌ Enhanced RAG test failed: {e}")
        return False


def main():
    """Main test function"""

    print("🚀 Starting Qdrant Integration Tests")
    print("Make sure your environment variables are set:")
    print("  - QDRANT_VECTOR_API: Your Qdrant API key")
    print()

    # Check environment
    api_key = os.getenv("QDRANT_VECTOR_API")
    if not api_key:
        print("❌ QDRANT_VECTOR_API environment variable not set")
        print("   Please set it and try again")
        return False

    print(f"✅ API key found: {api_key[:10]}...")

    # Run tests
    try:
        # Test basic Qdrant functionality
        basic_success = asyncio.run(test_qdrant_step_by_step())

        if basic_success:
            # Test enhanced RAG system
            rag_success = asyncio.run(test_with_fallback())

            if rag_success:
                print("\n🎯 All integration tests completed successfully!")
                return True
            else:
                print("\n⚠️ Basic Qdrant works but RAG integration has issues")
                return False
        else:
            print("\n❌ Basic Qdrant tests failed")
            return False

    except Exception as e:
        print(f"\n💥 Test execution failed: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
