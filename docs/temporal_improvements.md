# Temporal Context Improvements

## Overview

This document outlines the comprehensive temporal context improvements made to enhance the relevance and downstream processing of crypto news articles. These improvements ensure that time-sensitive information is properly prioritized and contextualized throughout the entire pipeline.

## 🕒 Key Improvements

### 1. Enhanced Enrichment with Temporal Awareness

**File:** `utils/enrichment.py`

The LangChain enrichment component now includes temporal context in its analysis:

#### New Fields Added:
- **`urgency_score`**: Float (0.01-1.0) - Higher for breaking news and time-sensitive events
- **`market_impact`**: String ('high', 'medium', 'low') - Expected market impact
- **`time_relevance`**: String ('breaking', 'recent', 'historical') - Time-based categorization

#### Enhanced Prompt:
The enrichment prompt now includes publication time and considers temporal factors:
```
Published: {published_at}
Consider the publication time for urgency and market impact assessment.
```

### 2. Enhanced NewsAPI with Temporal Context

**File:** `utils/newsapi.py`

The NewsAPI integration now provides better temporal control and context:

#### New Features:
- **Date Range Filtering**: Configurable `hours_back` parameter (default: 24 hours)
- **Temporal Metrics**: Automatic calculation of `hours_ago`, `is_breaking`, `is_recent`
- **Sorted Results**: Articles automatically sorted by recency
- **Increased Coverage**: Page size increased from 10 to 20 articles

#### Enhanced Article Structure:
```python
{
    "crypto_topic": "BTC",
    "source_url": "...",
    "published_at": "2024-01-15T10:30:00Z",
    "title": "...",
    "content": "...",
    "source_name": "CoinDesk",
    "hours_ago": 2.5,
    "is_breaking": True,    # < 2 hours
    "is_recent": True       # < 24 hours
}
```

### 3. Temporal Context Utilities

**File:** `utils/temporal_context.py`

A comprehensive utility module for handling temporal relevance:

#### Core Functions:

##### `calculate_temporal_relevance_score(published_at, current_time=None)`
Calculates detailed temporal metrics:
- **`recency_score`**: Decay over 1 week (0.01-1.0)
- **`urgency_score`**: Sharp decay over 48 hours (0.01-1.0)
- **`is_breaking`**: ≤ 2 hours (with 1.5x urgency bonus)
- **`is_recent`**: ≤ 24 hours (with 1.2x recency bonus)
- **`is_historical`**: > 1 week

##### `enhance_article_with_temporal_context(article)`
Adds temporal context to any article:
- Calculates all temporal metrics
- Adds `time_category` ('breaking', 'recent', 'historical')

##### `filter_articles_by_temporal_relevance(articles, min_recency_score=0.1, max_hours_ago=None)`
Filters articles based on temporal criteria:
- Minimum recency score threshold
- Maximum age limit

##### `sort_articles_by_temporal_relevance(articles, weights=None)`
Sorts articles by weighted relevance:
- Default weights: 40% recency, 60% urgency
- Breaking news gets 20% bonus
- Returns articles with `temporal_relevance_score`

##### `get_temporal_context_summary(articles)`
Generates summary statistics:
- Count of breaking/recent/historical news
- Average recency and urgency scores
- Temporal distribution analysis

## 🎯 Benefits for Downstream Processing

### 1. **Vector Database Relevance**
- **Temporal Weighting**: Articles can be weighted by temporal relevance before vector insertion
- **Breaking News Priority**: Time-sensitive articles get higher prominence in search results
- **Contextual Embeddings**: Temporal context influences embedding generation

### 2. **RAG Query Enhancement**
- **Time-Aware Retrieval**: Queries can prioritize recent/breaking news
- **Temporal Filtering**: Filter results by time relevance
- **Contextual Ranking**: Combine semantic similarity with temporal relevance

### 3. **Market Analysis Improvements**
- **Urgency Assessment**: AI can better assess market impact based on temporal context
- **Trend Analysis**: Historical vs. recent news comparison
- **Breaking News Alerts**: Immediate flagging of time-sensitive information

### 4. **Portfolio Recommendations**
- **Time-Sensitive Actions**: Recommendations based on news urgency
- **Market Timing**: Better timing for buy/sell decisions
- **Risk Assessment**: Temporal context for risk evaluation

## 📊 Usage Examples

### Enhanced News Fetching
```python
from utils.newsapi import fetch_news_articles
from utils.temporal_context import sort_articles_by_temporal_relevance

# Fetch recent news with temporal context
articles = await fetch_news_articles(["BTC", "ETH"], hours_back=48)

# Sort by temporal relevance
sorted_articles = sort_articles_by_temporal_relevance(articles)

# Filter for breaking news only
breaking_news = [a for a in sorted_articles if a['is_breaking']]
```

### Enhanced Enrichment
```python
from utils.enrichment import get_enrichment_chain

chain = get_enrichment_chain()

# Enrich with temporal context
result = chain.invoke({
    "title": "Bitcoin ETF Approval",
    "content": "...",
    "source_name": "CoinDesk",
    "published_at": "2024-01-15T10:30:00Z"
})

print(f"Urgency: {result.urgency_score}")
print(f"Market Impact: {result.market_impact}")
print(f"Time Relevance: {result.time_relevance}")
```

### Temporal Analysis
```python
from utils.temporal_context import get_temporal_context_summary

# Analyze temporal distribution
summary = get_temporal_context_summary(articles)
print(f"Breaking news: {summary['breaking_news']}")
print(f"Recent news: {summary['recent_news']}")
print(f"Historical news: {summary['historical_news']}")
```

## 🔄 Integration Points

### 1. **News Ingestion Pipeline**
```python
# In crypto_news_rag.py
articles = await fetch_news_articles(req.terms, hours_back=24)
enhanced_articles = [enhance_article_with_temporal_context(article) for article in articles]
sorted_articles = sort_articles_by_temporal_relevance(enhanced_articles)
```

### 2. **Enrichment Integration**
```python
# Enhanced enrichment with temporal context
meta = await enrich_news_metadata({
    "title": article['title'],
    "content": chunk['chunk_text'],
    "source_name": article.get('source_name', ''),
    "published_at": article['published_at']  # New temporal context
})
```

### 3. **Vector Storage Enhancement**
```python
# Add temporal relevance to vector metadata
chunk['temporal_relevance_score'] = article.get('temporal_relevance_score', 0)
chunk['is_breaking'] = article.get('is_breaking', False)
chunk['time_category'] = article.get('time_category', 'historical')
```

## 🚀 Future Enhancements

### 1. **Advanced Temporal Features**
- **Event Correlation**: Link related news across time
- **Trend Detection**: Identify emerging patterns over time
- **Seasonal Analysis**: Account for market cycles and events

### 2. **Real-time Processing**
- **Streaming Updates**: Real-time breaking news alerts
- **Live Scoring**: Dynamic temporal relevance updates
- **Predictive Relevance**: Forecast news importance

### 3. **Multi-timeframe Analysis**
- **Short-term**: Minutes to hours (breaking news)
- **Medium-term**: Hours to days (trend analysis)
- **Long-term**: Days to weeks (market cycles)

## 📈 Performance Impact

### Positive Impacts:
- **Better Relevance**: More accurate search results
- **Improved UX**: Breaking news gets priority
- **Enhanced AI**: Better context for market analysis
- **Reduced Noise**: Filter out outdated information

### Considerations:
- **Processing Overhead**: Additional temporal calculations
- **Storage**: Extra metadata fields
- **API Limits**: More comprehensive NewsAPI usage

## 🧪 Testing

All temporal improvements are thoroughly tested:

```bash
# Test enrichment with temporal context
python3 test_enrichment.py

# Test temporal utilities
python3 test_temporal_context.py
```

## 📋 Migration Guide

### For Existing Code:
1. **Update enrichment calls** to include `published_at`
2. **Enhance article processing** with temporal context
3. **Update vector storage** to include temporal metadata
4. **Modify queries** to consider temporal relevance

### Backward Compatibility:
- All existing functionality remains intact
- New fields are optional with sensible defaults
- Gradual migration supported

---

**These temporal improvements significantly enhance the relevance and usefulness of the crypto news pipeline, ensuring that time-sensitive information is properly prioritized and contextualized throughout the entire system.** 
