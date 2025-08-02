#!/usr/bin/env python3
"""
Test script for the LangChain Enrichment Component
Validates output schema, data types, and LangSmith integration.
"""

import os
import sys
from typing import Dict, Any
import json

def test_enrichment_imports():
    """Test that enrichment component can be imported."""
    print("🧪 Testing Enrichment Component Imports...")
    
    try:
        from utils.enrichment import get_enrichment_chain, NewsEnrichment
        print("✅ Enrichment component imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_enrichment_schema():
    """Test the NewsEnrichment Pydantic model."""
    print("\n📋 Testing Enrichment Schema...")
    
    try:
        from utils.enrichment import NewsEnrichment
        
        # Test valid data
        test_data = {
            "sentiment": 0.85,
            "trust": 0.75,
            "categories": ["Bitcoin", "ETF", "Institutional Investment"],
            "macro_category": "Cryptocurrency",
            "summary": "Bitcoin ETFs experienced significant inflows",
            "urgency_score": 0.6,
            "market_impact": "high",
            "time_relevance": "recent"
        }
        
        enrichment = NewsEnrichment(**test_data)
        print("✅ NewsEnrichment model created successfully")
        print(f"   Sentiment: {enrichment.sentiment}")
        print(f"   Trust: {enrichment.trust}")
        print(f"   Categories: {enrichment.categories}")
        print(f"   Macro Category: {enrichment.macro_category}")
        print(f"   Summary: {enrichment.summary[:50]}...")
        print(f"   Urgency: {enrichment.urgency_score}")
        print(f"   Market Impact: {enrichment.market_impact}")
        print(f"   Time Relevance: {enrichment.time_relevance}")
        
        return True
    except Exception as e:
        print(f"❌ Schema test failed: {e}")
        return False

def test_enrichment_chain():
    """Test the enrichment chain creation."""
    print("\n🔗 Testing Enrichment Chain...")
    
    try:
        from utils.enrichment import get_enrichment_chain
        
        chain = get_enrichment_chain()
        
        if chain is None:
            print("⚠️ Chain creation failed - OpenAI API key not configured")
            return False
        
        print("✅ Enrichment chain created successfully")
        return True
    except Exception as e:
        print(f"❌ Chain test failed: {e}")
        return False

def test_enrichment_integration():
    """Test full enrichment integration with sample data."""
    print("\n🎯 Testing Enrichment Integration...")
    
    try:
        from utils.enrichment import get_enrichment_chain
        
        chain = get_enrichment_chain()
        
        if chain is None:
            print("⚠️ Skipping integration test - OpenAI API key not configured")
            return True
        
        # Test article data
        test_article = {
            "title": "Bitcoin ETF inflows reach $1.2B as institutional adoption accelerates",
            "content": "The cryptocurrency market saw significant institutional inflows today as Bitcoin ETFs reported record-breaking volumes. Major financial institutions are increasingly allocating capital to digital assets, signaling a broader acceptance of cryptocurrency as a legitimate investment class.",
            "source_name": "CoinDesk",
            "published_at": "2024-01-15T10:30:00Z"
        }
        
        print("   Processing test article...")
        result = chain.invoke(test_article)
        
        print("✅ Enrichment integration successful!")
        print(f"   Sentiment: {result.get('sentiment', 'N/A')}")
        print(f"   Trust: {result.get('trust', 'N/A')}")
        print(f"   Categories: {result.get('categories', [])}")
        print(f"   Macro Category: {result.get('macro_category', 'N/A')}")
        print(f"   Summary: {result.get('summary', 'N/A')[:100]}...")
        print(f"   Urgency: {result.get('urgency_score', 'N/A')}")
        print(f"   Market Impact: {result.get('market_impact', 'N/A')}")
        print(f"   Time Relevance: {result.get('time_relevance', 'N/A')}")
        
        return True
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

def test_langsmith_integration():
    """Test LangSmith integration for tracing and monitoring."""
    print("\n🔍 Testing LangSmith Integration...")
    
    try:
        # Check if LangSmith is configured
        langsmith_key = os.getenv("LANGSMITH_API_KEY")
        if not langsmith_key:
            print("⚠️ LANGSMITH_API_KEY not set - LangSmith tracing disabled")
            return True
        
        # Set up LangSmith
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_PROJECT"] = "masonic-enrichment"
        os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
        
        from utils.enrichment import get_enrichment_chain
        
        chain = get_enrichment_chain()
        
        if chain is None:
            print("⚠️ Skipping LangSmith test - OpenAI API key not configured")
            return True
        
        # Test with tracing
        test_article = {
            "title": "Ethereum upgrade shows promise for scalability",
            "content": "The latest Ethereum upgrade demonstrates significant improvements in transaction processing speed and gas efficiency.",
            "source_name": "CryptoNews",
            "published_at": "2024-01-15T14:00:00Z"
        }
        
        print("   Running enrichment with LangSmith tracing...")
        result = chain.invoke(test_article)
        
        print("✅ LangSmith integration successful!")
        print(f"   Result: {result.get('macro_category', 'N/A')} - {result.get('sentiment', 'N/A')} sentiment")
        print("   Check https://smith.langchain.com for traces")
        
        return True
    except Exception as e:
        print(f"❌ LangSmith test failed: {e}")
        return False

def main():
    """Run all enrichment tests."""
    print("🧠 Masonic Enrichment Component Test Suite")
    print("=" * 50)
    
    tests = [
        test_enrichment_imports,
        test_enrichment_schema,
        test_enrichment_chain,
        test_enrichment_integration,
        test_langsmith_integration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All enrichment tests passed!")
        return True
    else:
        print("⚠️ Some tests failed - check configuration")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 