"""
Temporal Context Utilities for Crypto News

This module provides utilities for handling time-based relevance in crypto news articles,
including scoring, filtering, and temporal context enhancement.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import math

def calculate_temporal_relevance_score(published_at: str, current_time: Optional[datetime] = None) -> Dict[str, float]:
    """
    Calculate temporal relevance scores for a news article.
    
    Args:
        published_at: ISO format timestamp string
        current_time: Current time (defaults to UTC now)
    
    Returns:
        Dict with temporal relevance metrics
    """
    if current_time is None:
        current_time = datetime.utcnow()
    
    # Parse published time
    if isinstance(published_at, str):
        pub_time = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
        if pub_time.tzinfo is None:
            pub_time = pub_time.replace(tzinfo=None)
    else:
        pub_time = published_at
    
    # Calculate time differences
    time_diff = current_time - pub_time.replace(tzinfo=None)
    hours_ago = time_diff.total_seconds() / 3600
    days_ago = hours_ago / 24
    
    # Calculate relevance scores (higher = more relevant)
    recency_score = max(0.01, 1.0 - (hours_ago / 168))  # Decay over 1 week
    urgency_score = max(0.01, 1.0 - (hours_ago / 48))   # Sharp decay for urgency
    
    # Breaking news bonus (first 2 hours)
    if hours_ago <= 2:
        urgency_score = min(1.0, urgency_score * 1.5)
    
    # Recent news bonus (first 24 hours)
    if hours_ago <= 24:
        recency_score = min(1.0, recency_score * 1.2)
    
    return {
        "hours_ago": hours_ago,
        "days_ago": days_ago,
        "recency_score": round(recency_score, 3),
        "urgency_score": round(urgency_score, 3),
        "is_breaking": hours_ago <= 2,
        "is_recent": hours_ago <= 24,
        "is_historical": hours_ago > 168  # > 1 week
    }

def enhance_article_with_temporal_context(article: Dict) -> Dict:
    """
    Enhance an article with temporal context information.
    
    Args:
        article: Article dictionary with 'published_at' field
    
    Returns:
        Enhanced article with temporal context
    """
    if 'published_at' not in article:
        return article
    
    temporal_metrics = calculate_temporal_relevance_score(article['published_at'])
    article.update(temporal_metrics)
    
    # Add time-based categorization
    if temporal_metrics['is_breaking']:
        article['time_category'] = 'breaking'
    elif temporal_metrics['is_recent']:
        article['time_category'] = 'recent'
    else:
        article['time_category'] = 'historical'
    
    return article

def filter_articles_by_temporal_relevance(
    articles: List[Dict], 
    min_recency_score: float = 0.1,
    max_hours_ago: Optional[int] = None
) -> List[Dict]:
    """
    Filter articles based on temporal relevance criteria.
    
    Args:
        articles: List of articles with temporal context
        min_recency_score: Minimum recency score (0.01-1.0)
        max_hours_ago: Maximum hours ago (None = no limit)
    
    Returns:
        Filtered list of articles
    """
    filtered = []
    
    for article in articles:
        # Ensure temporal context is calculated
        if 'recency_score' not in article:
            article = enhance_article_with_temporal_context(article)
        
        # Apply filters
        if article['recency_score'] < min_recency_score:
            continue
            
        if max_hours_ago and article['hours_ago'] > max_hours_ago:
            continue
            
        filtered.append(article)
    
    return filtered

def sort_articles_by_temporal_relevance(articles: List[Dict], weights: Optional[Dict] = None) -> List[Dict]:
    """
    Sort articles by temporal relevance using weighted scoring.
    
    Args:
        articles: List of articles with temporal context
        weights: Scoring weights {'recency': 0.4, 'urgency': 0.6}
    
    Returns:
        Sorted list of articles (most relevant first)
    """
    if weights is None:
        weights = {'recency': 0.4, 'urgency': 0.6}
    
    def calculate_relevance_score(article: Dict) -> float:
        # Ensure temporal context is calculated
        if 'recency_score' not in article:
            article = enhance_article_with_temporal_context(article)
        
        # Weighted relevance score
        score = (
            article['recency_score'] * weights.get('recency', 0.4) +
            article['urgency_score'] * weights.get('urgency', 0.6)
        )
        
        # Bonus for breaking news
        if article.get('is_breaking', False):
            score *= 1.2
        
        return score
    
    # Sort by relevance score (descending)
    sorted_articles = sorted(articles, key=calculate_relevance_score, reverse=True)
    
    # Add relevance score to each article
    for article in sorted_articles:
        article['temporal_relevance_score'] = calculate_relevance_score(article)
    
    return sorted_articles

def get_temporal_context_summary(articles: List[Dict]) -> Dict:
    """
    Generate a summary of temporal context for a collection of articles.
    
    Args:
        articles: List of articles with temporal context
    
    Returns:
        Summary statistics
    """
    if not articles:
        return {}
    
    # Ensure all articles have temporal context
    enhanced_articles = [enhance_article_with_temporal_context(article) for article in articles]
    
    breaking_count = sum(1 for a in enhanced_articles if a.get('is_breaking', False))
    recent_count = sum(1 for a in enhanced_articles if a.get('is_recent', False))
    historical_count = sum(1 for a in enhanced_articles if a.get('is_historical', False))
    
    avg_recency = sum(a.get('recency_score', 0) for a in enhanced_articles) / len(enhanced_articles)
    avg_urgency = sum(a.get('urgency_score', 0) for a in enhanced_articles) / len(enhanced_articles)
    
    return {
        "total_articles": len(enhanced_articles),
        "breaking_news": breaking_count,
        "recent_news": recent_count,
        "historical_news": historical_count,
        "avg_recency_score": round(avg_recency, 3),
        "avg_urgency_score": round(avg_urgency, 3),
        "temporal_distribution": {
            "breaking": breaking_count,
            "recent": recent_count - breaking_count,  # Recent but not breaking
            "historical": historical_count
        }
    } 
