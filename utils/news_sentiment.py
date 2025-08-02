#!/usr/bin/env python3
"""
News Sentiment Analysis Module
Provides comprehensive crypto news analysis with sentiment scoring and market impact assessment.
"""

import os
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel, Field
import httpx

# Local imports
from utils.newsapi import fetch_news_articles
from utils.openai_utils import get_openai_client

class NewsArticle(BaseModel):
    """Enhanced news article model."""
    title: str
    description: str
    content: Optional[str] = None
    source_name: str
    published_at: datetime
    url: str
    sentiment_score: Optional[float] = None
    relevance_score: Optional[float] = None
    market_impact: Optional[str] = None
    crypto_topics: List[str] = []
    breaking_news: bool = False

class NewsSentiment(BaseModel):
    """Comprehensive news sentiment analysis."""
    overall_sentiment: str
    sentiment_score: float
    key_topics: List[str]
    breaking_news: List[str]
    market_impact: str
    confidence_score: float
    articles_analyzed: int
    time_period: str
    top_sources: List[str]

class MarketContext(BaseModel):
    """Market context derived from news."""
    market_regime: str
    volatility_level: str
    key_catalysts: List[str]
    risk_factors: List[str]
    opportunities: List[str]
    sentiment_trend: str

class NewsAnalyzer:
    """Advanced news sentiment analyzer for crypto markets."""
    
    def __init__(self):
        self.openai_client = get_openai_client()
        self.news_api_key = os.getenv("NEWSAPI_KEY")
    
    async def get_crypto_news(self, symbols: Optional[List[str]] = None, hours: int = 24) -> List[NewsArticle]:
        """Fetch and process crypto news articles."""
        try:
            # Check if NewsAPI key is available
            if not self.news_api_key:
                print("No NewsAPI key provided - using mock news data")
                return self._get_mock_news_articles()
            
            # Define search terms
            search_terms = ["cryptocurrency", "bitcoin", "ethereum", "crypto market"]
            if symbols:
                search_terms.extend(symbols)
            
            # Fetch news articles
            articles_data = await fetch_news_articles(search_terms[:5])  # Limit to avoid rate limits
            
            if not articles_data:
                return []
            
            # Convert to NewsArticle objects
            articles = []
            for article_data in articles_data:
                try:
                    # Parse published date
                    published_at = datetime.fromisoformat(
                        article_data.get('published_at', '').replace('Z', '+00:00')
                    )
                    
                    article = NewsArticle(
                        title=article_data.get('title', ''),
                        description=article_data.get('description', ''),
                        content=article_data.get('content', ''),
                        source_name=article_data.get('source_name', ''),
                        published_at=published_at,
                        url=article_data.get('url', ''),
                        breaking_news=self._is_breaking_news(article_data.get('title', ''), published_at)
                    )
                    
                    # Analyze sentiment
                    sentiment = await self._analyze_article_sentiment(article)
                    article.sentiment_score = sentiment.get('score', 0.0)
                    article.market_impact = sentiment.get('impact', 'neutral')
                    article.crypto_topics = sentiment.get('topics', [])
                    
                    articles.append(article)
                    
                except Exception as e:
                    print(f"Error processing article: {e}")
                    continue
            
            return articles
            
        except Exception as e:
            print(f"Error fetching crypto news: {e}")
            return []
    
    async def analyze_market_sentiment(self, symbols: Optional[List[str]] = None) -> NewsSentiment:
        """Analyze overall market sentiment from news."""
        try:
            # Get recent news
            articles = await self.get_crypto_news(symbols, hours=24)
            
            if not articles:
                return self._get_default_sentiment()
            
            # Calculate overall sentiment
            sentiment_scores = [a.sentiment_score for a in articles if a.sentiment_score is not None]
            if not sentiment_scores:
                return self._get_default_sentiment()
            
            avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
            
            # Determine sentiment category
            if avg_sentiment > 0.3:
                overall_sentiment = "positive"
            elif avg_sentiment < -0.3:
                overall_sentiment = "negative"
            else:
                overall_sentiment = "neutral"
            
            # Extract key topics and breaking news
            all_topics = []
            breaking_news = []
            sources = []
            
            for article in articles:
                all_topics.extend(article.crypto_topics)
                if article.breaking_news:
                    breaking_news.append(article.title)
                sources.append(article.source_name)
            
            # Get unique topics and sources
            key_topics = list(set(all_topics))[:10]  # Top 10 topics
            top_sources = list(set(sources))[:5]     # Top 5 sources
            
            # Determine market impact
            market_impact = self._determine_market_impact(articles, avg_sentiment)
            
            # Calculate confidence based on number of articles
            confidence_score = min(len(articles) / 20.0, 1.0)  # Max confidence with 20+ articles
            
            return NewsSentiment(
                overall_sentiment=overall_sentiment,
                sentiment_score=avg_sentiment,
                key_topics=key_topics,
                breaking_news=breaking_news,
                market_impact=market_impact,
                confidence_score=confidence_score,
                articles_analyzed=len(articles),
                time_period="24h",
                top_sources=top_sources
            )
            
        except Exception as e:
            print(f"Error analyzing market sentiment: {e}")
            return self._get_default_sentiment()
    
    async def get_market_context(self, symbols: Optional[List[str]] = None) -> MarketContext:
        """Get market context from news analysis."""
        try:
            sentiment = await self.analyze_market_sentiment(symbols)
            
            # Determine market regime
            if sentiment.sentiment_score > 0.2:
                market_regime = "bullish"
            elif sentiment.sentiment_score < -0.2:
                market_regime = "bearish"
            else:
                market_regime = "neutral"
            
            # Determine volatility level
            volatility_level = self._determine_volatility(sentiment)
            
            # Extract catalysts and risks
            key_catalysts = [topic for topic in sentiment.key_topics if self._is_catalyst(topic)]
            risk_factors = [topic for topic in sentiment.key_topics if self._is_risk_factor(topic)]
            opportunities = [topic for topic in sentiment.key_topics if self._is_opportunity(topic)]
            
            # Determine sentiment trend
            sentiment_trend = self._determine_sentiment_trend(sentiment)
            
            return MarketContext(
                market_regime=market_regime,
                volatility_level=volatility_level,
                key_catalysts=key_catalysts,
                risk_factors=risk_factors,
                opportunities=opportunities,
                sentiment_trend=sentiment_trend
            )
            
        except Exception as e:
            print(f"Error getting market context: {e}")
            return MarketContext(
                market_regime="neutral",
                volatility_level="medium",
                key_catalysts=[],
                risk_factors=[],
                opportunities=[],
                sentiment_trend="stable"
            )
    
    async def _analyze_article_sentiment(self, article: NewsArticle) -> Dict[str, Any]:
        """Analyze sentiment of individual article using OpenAI."""
        try:
            if not self.openai_client:
                return {"score": 0.0, "impact": "neutral", "topics": []}
            
            # Prepare content for analysis
            content = f"Title: {article.title}\nDescription: {article.description}"
            if article.content:
                content += f"\nContent: {article.content[:500]}..."  # Limit content length
            
            prompt = f"""
            Analyze this crypto news article and provide:
            1. Sentiment score (-1 to 1, where -1 is very negative, 1 is very positive)
            2. Market impact (bullish, bearish, or neutral)
            3. Key crypto topics mentioned (list of relevant topics)
            
            Article:
            {content}
            
            Respond with JSON format:
            {{
                "score": float,
                "impact": "bullish|bearish|neutral",
                "topics": ["topic1", "topic2", ...]
            }}
            """
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            content = response.choices[0].message.content
            
            # Parse response (simplified)
            content_lower = content.lower() if content else ""
            if "bullish" in content_lower:
                impact = "bullish"
                score = 0.6
            elif "bearish" in content_lower:
                impact = "bearish"
                score = -0.4
            else:
                impact = "neutral"
                score = 0.0
            
            # Extract topics (simplified)
            topics = []
            crypto_keywords = ["bitcoin", "ethereum", "crypto", "blockchain", "defi", "nft", "regulation"]
            for keyword in crypto_keywords:
                if keyword.lower() in content_lower:
                    topics.append(keyword)
            
            return {
                "score": score,
                "impact": impact,
                "topics": topics
            }
            
        except Exception as e:
            print(f"Error analyzing article sentiment: {e}")
            return {"score": 0.0, "impact": "neutral", "topics": []}
    
    def _is_breaking_news(self, title: str, published_at: datetime) -> bool:
        """Determine if article is breaking news."""
        # Check if published in last 2 hours
        time_diff = datetime.now(timezone.utc) - published_at
        is_recent = time_diff.total_seconds() < 7200  # 2 hours
        
        # Check for breaking news keywords
        breaking_keywords = ["breaking", "urgent", "just in", "alert", "update"]
        has_breaking_keywords = any(keyword in title.lower() for keyword in breaking_keywords)
        
        return is_recent and has_breaking_keywords
    
    def _determine_market_impact(self, articles: List[NewsArticle], avg_sentiment: float) -> str:
        """Determine overall market impact from articles."""
        if avg_sentiment > 0.3:
            return "Positive market sentiment with potential upside catalysts"
        elif avg_sentiment < -0.3:
            return "Negative market sentiment with risk factors present"
        else:
            return "Mixed market sentiment with balanced outlook"
    
    def _determine_volatility(self, sentiment: NewsSentiment) -> str:
        """Determine market volatility level."""
        if len(sentiment.breaking_news) > 3:
            return "high"
        elif abs(sentiment.sentiment_score) > 0.5:
            return "medium"
        else:
            return "low"
    
    def _is_catalyst(self, topic: str) -> bool:
        """Check if topic is a market catalyst."""
        catalysts = ["adoption", "institutional", "etf", "upgrade", "partnership", "launch"]
        return any(catalyst in topic.lower() for catalyst in catalysts)
    
    def _is_risk_factor(self, topic: str) -> bool:
        """Check if topic is a risk factor."""
        risks = ["regulation", "hack", "security", "ban", "crackdown", "lawsuit"]
        return any(risk in topic.lower() for risk in risks)
    
    def _is_opportunity(self, topic: str) -> bool:
        """Check if topic represents an opportunity."""
        opportunities = ["innovation", "growth", "expansion", "adoption", "technology"]
        return any(opp in topic.lower() for opp in opportunities)
    
    def _determine_sentiment_trend(self, sentiment: NewsSentiment) -> str:
        """Determine sentiment trend."""
        if sentiment.sentiment_score > 0.2:
            return "improving"
        elif sentiment.sentiment_score < -0.2:
            return "declining"
        else:
            return "stable"
    
    def _get_mock_news_articles(self) -> List[NewsArticle]:
        """Get mock news articles for development/testing."""
        mock_articles = [
            NewsArticle(
                title="Bitcoin Shows Resilience Amid Market Volatility",
                description="Bitcoin maintains strong support levels despite recent market fluctuations.",
                content="Bitcoin has demonstrated remarkable resilience in the face of market volatility...",
                source_name="CryptoNews",
                published_at=datetime.now(timezone.utc) - timedelta(hours=2),
                url="https://example.com/bitcoin-resilience",
                sentiment_score=0.3,
                market_impact="bullish",
                crypto_topics=["bitcoin", "market analysis"],
                breaking_news=False
            ),
            NewsArticle(
                title="Ethereum Upgrade Shows Promising Results",
                description="Recent Ethereum network upgrades improve transaction efficiency.",
                content="The latest Ethereum upgrade has shown significant improvements...",
                source_name="BlockchainDaily",
                published_at=datetime.now(timezone.utc) - timedelta(hours=4),
                url="https://example.com/ethereum-upgrade",
                sentiment_score=0.5,
                market_impact="bullish",
                crypto_topics=["ethereum", "upgrade"],
                breaking_news=False
            ),
            NewsArticle(
                title="Crypto Market Analysis: Mixed Signals",
                description="Market analysts provide mixed outlook for cryptocurrency sector.",
                content="Recent market analysis shows conflicting signals...",
                source_name="CryptoInsider",
                published_at=datetime.now(timezone.utc) - timedelta(hours=6),
                url="https://example.com/market-analysis",
                sentiment_score=0.0,
                market_impact="neutral",
                crypto_topics=["market analysis", "cryptocurrency"],
                breaking_news=False
            )
        ]
        return mock_articles

    def _get_default_sentiment(self) -> NewsSentiment:
        """Get default sentiment when no news is available."""
        return NewsSentiment(
            overall_sentiment="neutral",
            sentiment_score=0.0,
            key_topics=["cryptocurrency", "market analysis"],
            breaking_news=[],
            market_impact="Standard market conditions",
            confidence_score=0.0,
            articles_analyzed=0,
            time_period="24h",
            top_sources=[]
        )

# Global analyzer instance
_news_analyzer = None

def get_news_analyzer() -> NewsAnalyzer:
    """Get or create news analyzer instance."""
    global _news_analyzer
    if _news_analyzer is None:
        _news_analyzer = NewsAnalyzer()
    return _news_analyzer

async def get_market_sentiment(symbols: Optional[List[str]] = None) -> NewsSentiment:
    """Get market sentiment analysis."""
    analyzer = get_news_analyzer()
    return await analyzer.analyze_market_sentiment(symbols)

async def get_market_context(symbols: Optional[List[str]] = None) -> MarketContext:
    """Get market context from news."""
    analyzer = get_news_analyzer()
    return await analyzer.get_market_context(symbols) 
