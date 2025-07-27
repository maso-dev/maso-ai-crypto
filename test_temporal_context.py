#!/usr/bin/env python3
"""
Test script for temporal context utilities.
Tests time-based relevance scoring, filtering, and sorting functionality.
"""

import sys
import os
from datetime import datetime, timedelta
from utils.temporal_context import (
    calculate_temporal_relevance_score,
    enhance_article_with_temporal_context,
    filter_articles_by_temporal_relevance,
    sort_articles_by_temporal_relevance,
    get_temporal_context_summary
)

def test_temporal_relevance_scoring():
    """Test temporal relevance score calculation."""
    print("🧪 Testing Temporal Relevance Scoring...")
    
    # Test with different time scenarios
    now = datetime.utcnow()
    
    # Breaking news (1 hour ago)
    breaking_time = (now - timedelta(hours=1)).isoformat() + "Z"
    breaking_score = calculate_temporal_relevance_score(breaking_time)
    
    # Recent news (12 hours ago)
    recent_time = (now - timedelta(hours=12)).isoformat() + "Z"
    recent_score = calculate_temporal_relevance_score(recent_time)
    
    # Historical news (1 week ago)
    historical_time = (now - timedelta(days=7)).isoformat() + "Z"
    historical_score = calculate_temporal_relevance_score(historical_time)
    
    # Validate breaking news
    assert breaking_score['is_breaking'] == True, "Breaking news should be flagged"
    assert breaking_score['urgency_score'] > 0.8, "Breaking news should have high urgency"
    print(f"✅ Breaking news (1h ago): urgency={breaking_score['urgency_score']}, recency={breaking_score['recency_score']}")
    
    # Validate recent news
    assert breaking_score['is_recent'] == True, "Breaking news should also be recent"
    assert recent_score['is_recent'] == True, "12h ago should be recent"
    assert recent_score['is_breaking'] == False, "12h ago should not be breaking"
    print(f"✅ Recent news (12h ago): urgency={recent_score['urgency_score']}, recency={recent_score['recency_score']}")
    
    # Validate historical news
    assert historical_score['is_historical'] == True, "1 week ago should be historical"
    assert historical_score['is_recent'] == False, "1 week ago should not be recent"
    print(f"✅ Historical news (1 week ago): urgency={historical_score['urgency_score']}, recency={historical_score['recency_score']}")
    
    print("✅ All temporal scoring tests passed!")
    return True

def test_article_enhancement():
    """Test article enhancement with temporal context."""
    print("\n🧪 Testing Article Enhancement...")
    
    # Sample articles with different timestamps
    now = datetime.utcnow()
    
    articles = [
        {
            "title": "Breaking: Bitcoin hits new ATH",
            "content": "Bitcoin just reached a new all-time high...",
            "published_at": (now - timedelta(hours=1)).isoformat() + "Z"
        },
        {
            "title": "Ethereum upgrade completed",
            "content": "The Ethereum network upgrade was successfully completed...",
            "published_at": (now - timedelta(hours=6)).isoformat() + "Z"
        },
        {
            "title": "Crypto market analysis from last week",
            "content": "Last week's market analysis shows...",
            "published_at": (now - timedelta(days=7)).isoformat() + "Z"
        }
    ]
    
    # Enhance articles
    enhanced_articles = [enhance_article_with_temporal_context(article) for article in articles]
    
    # Validate enhancement
    for i, article in enumerate(enhanced_articles):
        required_fields = ['hours_ago', 'recency_score', 'urgency_score', 'time_category']
        missing_fields = [field for field in required_fields if field not in article]
        
        if missing_fields:
            print(f"❌ Article {i+1} missing fields: {missing_fields}")
            return False
        
        print(f"✅ Article {i+1} ({article['time_category']}): "
              f"urgency={article['urgency_score']}, recency={article['recency_score']}")
    
    print("✅ All article enhancement tests passed!")
    return True

def test_filtering_and_sorting():
    """Test filtering and sorting by temporal relevance."""
    print("\n🧪 Testing Filtering and Sorting...")
    
    # Create test articles
    now = datetime.utcnow()
    
    articles = [
        {
            "title": "Breaking news",
            "published_at": (now - timedelta(hours=1)).isoformat() + "Z"
        },
        {
            "title": "Recent news",
            "published_at": (now - timedelta(hours=12)).isoformat() + "Z"
        },
        {
            "title": "Old news",
            "published_at": (now - timedelta(days=10)).isoformat() + "Z"
        }
    ]
    
    # Test filtering
    filtered = filter_articles_by_temporal_relevance(articles, min_recency_score=0.3)
    print(f"✅ Filtered articles: {len(filtered)}/{len(articles)} (min_recency=0.3)")
    
    # Test sorting
    sorted_articles = sort_articles_by_temporal_relevance(articles)
    print(f"✅ Sorted articles by relevance:")
    for i, article in enumerate(sorted_articles):
        print(f"   {i+1}. {article['title']} (score: {article.get('temporal_relevance_score', 0):.3f})")
    
    # Validate sorting order (most relevant first)
    if len(sorted_articles) >= 2:
        first_score = sorted_articles[0].get('temporal_relevance_score', 0)
        second_score = sorted_articles[1].get('temporal_relevance_score', 0)
        assert first_score >= second_score, "Articles should be sorted by relevance (descending)"
    
    print("✅ All filtering and sorting tests passed!")
    return True

def test_temporal_summary():
    """Test temporal context summary generation."""
    print("\n🧪 Testing Temporal Summary...")
    
    # Create test articles
    now = datetime.utcnow()
    
    articles = [
        {"published_at": (now - timedelta(hours=1)).isoformat() + "Z"},  # Breaking
        {"published_at": (now - timedelta(hours=3)).isoformat() + "Z"},  # Breaking
        {"published_at": (now - timedelta(hours=12)).isoformat() + "Z"}, # Recent
        {"published_at": (now - timedelta(days=10)).isoformat() + "Z"},  # Historical
    ]
    
    # Generate summary
    summary = get_temporal_context_summary(articles)
    
    # Validate summary
    assert summary['total_articles'] == 4, "Should have 4 articles"
    assert summary['breaking_news'] >= 1, "Should have at least 1 breaking news"
    assert summary['recent_news'] >= 2, "Should have at least 2 recent news"
    assert summary['historical_news'] >= 1, "Should have at least 1 historical news"
    
    print(f"✅ Temporal Summary:")
    print(f"   Total: {summary['total_articles']}")
    print(f"   Breaking: {summary['breaking_news']}")
    print(f"   Recent: {summary['recent_news']}")
    print(f"   Historical: {summary['historical_news']}")
    print(f"   Avg Recency: {summary['avg_recency_score']}")
    print(f"   Avg Urgency: {summary['avg_urgency_score']}")
    
    print("✅ All temporal summary tests passed!")
    return True

if __name__ == "__main__":
    print("🚀 Starting Temporal Context Tests\n")
    
    try:
        # Run all tests
        test1 = test_temporal_relevance_scoring()
        test2 = test_article_enhancement()
        test3 = test_filtering_and_sorting()
        test4 = test_temporal_summary()
        
        print(f"\n📊 Test Results:")
        print(f"   Temporal scoring: {'✅ PASSED' if test1 else '❌ FAILED'}")
        print(f"   Article enhancement: {'✅ PASSED' if test2 else '❌ FAILED'}")
        print(f"   Filtering & sorting: {'✅ PASSED' if test3 else '❌ FAILED'}")
        print(f"   Temporal summary: {'✅ PASSED' if test4 else '❌ FAILED'}")
        
        if all([test1, test2, test3, test4]):
            print("\n🎉 All temporal context tests passed!")
            print("   The temporal utilities are ready for integration.")
        else:
            print("\n⚠️  Some tests failed. Please check the implementation.")
            
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {str(e)}")
        sys.exit(1) 
