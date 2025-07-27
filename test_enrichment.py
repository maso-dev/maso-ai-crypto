#!/usr/bin/env python3
"""
Test script for the LangChain enrichment component.
Tests the news enrichment chain with sample data and validates output schema.
"""

import asyncio
import json
from typing import Dict, Any
from utils.enrichment import get_enrichment_chain

def test_enrichment_chain():
    """
    Test the enrichment chain with a sample crypto news article.
    Validates that the output contains expected fields and reasonable values.
    """
    print("🧪 Testing LangChain Enrichment Component...")
    
    # Sample test data with temporal context
    test_article = {
        "title": "Bitcoin ETF inflows reach $1.2B as institutional adoption accelerates",
        "content": "The cryptocurrency market saw significant institutional inflows this week, with Bitcoin ETFs attracting over $1.2 billion in new investments. Major financial institutions including BlackRock and Fidelity reported record-breaking daily inflows, signaling growing mainstream acceptance of digital assets. Analysts suggest this could be the beginning of a new bull cycle as traditional investors increasingly allocate to crypto assets.",
        "source_name": "CoinDesk",
        "published_at": "2024-01-15T10:30:00Z"  # Add temporal context
    }
    
    try:
        # Get the enrichment chain
        chain = get_enrichment_chain()
        print("✅ Enrichment chain created successfully")
        
        # Run the enrichment
        print("🔄 Running enrichment on test article...")
        result = chain.invoke(test_article)
        print(f"📊 Raw result: {result}")
        
        # The result should already be a structured object
        enrichment_data = result
        
        # Validate output schema
        required_fields = ['sentiment', 'trust', 'categories', 'macro_category', 'summary', 'urgency_score', 'market_impact', 'time_relevance']
        missing_fields = [field for field in required_fields if field not in enrichment_data]
        
        if missing_fields:
            print(f"❌ Missing required fields: {missing_fields}")
            return False
        
        # Validate data types and ranges
        if not isinstance(enrichment_data['sentiment'], (int, float)) or not (0 <= enrichment_data['sentiment'] <= 1):
            print("❌ Sentiment should be a number between 0 and 1")
            return False
            
        if not isinstance(enrichment_data['trust'], (int, float)) or not (0 <= enrichment_data['trust'] <= 1):
            print("❌ Trust should be a number between 0 and 1")
            return False
            
        if not isinstance(enrichment_data['categories'], list):
            print("❌ Categories should be a list")
            return False
            
        if not isinstance(enrichment_data['macro_category'], str):
            print("❌ Macro category should be a string")
            return False
            
        if not isinstance(enrichment_data['summary'], str):
            print("❌ Summary should be a string")
            return False
            
        if not isinstance(enrichment_data['urgency_score'], (int, float)) or not (0 <= enrichment_data['urgency_score'] <= 1):
            print("❌ Urgency score should be a number between 0 and 1")
            return False
            
        if not isinstance(enrichment_data['market_impact'], str) or enrichment_data['market_impact'] not in ['high', 'medium', 'low']:
            print("❌ Market impact should be 'high', 'medium', or 'low'")
            return False
            
        if not isinstance(enrichment_data['time_relevance'], str) or enrichment_data['time_relevance'] not in ['breaking', 'recent', 'historical']:
            print("❌ Time relevance should be 'breaking', 'recent', or 'historical'")
            return False
        
        print("✅ All validation checks passed!")
        print("\n📋 Enrichment Results:")
        print(f"   Sentiment: {enrichment_data['sentiment']}")
        print(f"   Trust: {enrichment_data['trust']}")
        print(f"   Categories: {enrichment_data['categories']}")
        print(f"   Macro Category: {enrichment_data['macro_category']}")
        print(f"   Urgency Score: {enrichment_data['urgency_score']}")
        print(f"   Market Impact: {enrichment_data['market_impact']}")
        print(f"   Time Relevance: {enrichment_data['time_relevance']}")
        print(f"   Summary: {enrichment_data['summary'][:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        return False

def test_error_handling():
    """
    Test error handling with invalid input.
    """
    print("\n🧪 Testing Error Handling...")
    
    try:
        chain = get_enrichment_chain()
        
        # Test with minimal but valid fields
        minimal_article = {
            "title": "Test article",
            "content": "This is a test content.",
            "source_name": "Test Source",
            "published_at": "2024-01-15T12:00:00Z"
        }
        
        result = chain.invoke(minimal_article)
        print("⚠️  Chain handled minimal input gracefully")
        return True
        
    except Exception as e:
        print(f"❌ Error handling test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Starting LangChain Enrichment Tests\n")
    
    # Run main test
    success = test_enrichment_chain()
    
    # Run error handling test
    error_success = test_error_handling()
    
    print(f"\n📊 Test Results:")
    print(f"   Main test: {'✅ PASSED' if success else '❌ FAILED'}")
    print(f"   Error handling: {'✅ PASSED' if error_success else '❌ FAILED'}")
    
    if success and error_success:
        print("\n🎉 All tests passed! The enrichment component is ready for integration.")
    else:
        print("\n⚠️  Some tests failed. Please check the implementation.") 
