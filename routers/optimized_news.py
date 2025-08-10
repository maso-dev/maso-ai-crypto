"""
Optimized News Router - Phase 3 of Temporal Optimization
========================================================

This router demonstrates the "fast serving" approach where:
1. No expensive API calls during user requests
2. Queries pre-processed data from databases
3. Minimal LLM usage for final summarization only
4. Sub-second response times

This is the "customer-facing service" with a fully prepped kitchen.
"""

import sqlite3
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

try:
    from utils.config import ConfigManager
    from utils.milvus import EnhancedVectorRAG
    from utils.graph_rag import Neo4jGraphRAG
except ImportError:
    # Graceful fallback for missing dependencies
    ConfigManager = lambda: None
    EnhancedVectorRAG = None
    Neo4jGraphRAG = None
from utils.openai_utils import get_openai_client


# Response models
class NewsArticle(BaseModel):
    id: int
    title: str
    content: Optional[str]
    url: str
    source: str
    crypto_symbol: str
    sentiment: str
    sentiment_score: float
    category: str
    market_impact: str
    is_breaking: bool
    is_recent: bool
    recency_score: float
    urgency_score: float
    published_at: str
    hours_ago: Optional[float]


class NewsResponse(BaseModel):
    articles: List[NewsArticle]
    total_count: int
    processing_time_ms: float
    data_freshness: str
    summary: Optional[str] = None


class MarketInsights(BaseModel):
    breaking_news_count: int
    recent_news_count: int
    sentiment_distribution: Dict[str, int]
    top_categories: Dict[str, int]
    market_impact_summary: Dict[str, int]
    urgency_stats: Dict[str, float]


router = APIRouter(prefix="/api/optimized", tags=["optimized-news"])


class OptimizedNewsService:
    """
    Fast news service that queries pre-processed data.

    This is the "efficient waiter" that serves pre-prepared dishes.
    """

    def __init__(self):
        self.config = ConfigManager() if ConfigManager else None
        self.raw_db_path = "data/raw_news.db"

        # Initialize search systems (with error handling)
        self.vector_rag = None
        self.graph_rag = None
        self.openai_client = None

        try:
            self.vector_rag = EnhancedVectorRAG()
        except Exception:
            pass  # Will use database fallback

        try:
            self.graph_rag = Neo4jGraphRAG()
        except Exception:
            pass  # Will use database fallback

        try:
            self.openai_client = get_openai_client()
        except Exception:
            pass  # Will skip summarization

    def get_processed_articles(
        self,
        crypto_symbols: Optional[List[str]] = None,
        hours_back: int = 24,
        sentiment_filter: Optional[str] = None,
        breaking_only: bool = False,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        Get processed articles from the raw database.

        This is FAST because all the expensive processing was done offline.
        """
        try:
            with sqlite3.connect(self.raw_db_path) as conn:
                conn.row_factory = sqlite3.Row

                # Build query conditions
                conditions = ["processed = 1"]  # Only processed articles
                params = []

                # Time filter
                cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours_back)
                conditions.append("published_at > ?")
                params.append(cutoff_time.isoformat())

                # Crypto symbol filter
                if crypto_symbols:
                    placeholders = ",".join("?" * len(crypto_symbols))
                    conditions.append(f"crypto_symbol IN ({placeholders})")
                    params.extend(crypto_symbols)

                # Sentiment filter
                if sentiment_filter:
                    conditions.append("JSON_EXTRACT(raw_data, '$.sentiment') = ?")
                    params.append(sentiment_filter)

                # Breaking news filter
                if breaking_only:
                    conditions.append("JSON_EXTRACT(raw_data, '$.is_breaking') = 1")

                # Build full query
                query = f"""
                    SELECT *, 
                           JSON_EXTRACT(raw_data, '$.sentiment') as sentiment,
                           JSON_EXTRACT(raw_data, '$.sentiment_score') as sentiment_score,
                           JSON_EXTRACT(raw_data, '$.category') as category,
                           JSON_EXTRACT(raw_data, '$.market_impact') as market_impact,
                           JSON_EXTRACT(raw_data, '$.is_breaking') as is_breaking,
                           JSON_EXTRACT(raw_data, '$.is_recent') as is_recent,
                           JSON_EXTRACT(raw_data, '$.recency_score') as recency_score,
                           JSON_EXTRACT(raw_data, '$.urgency_score') as urgency_score,
                           JSON_EXTRACT(raw_data, '$.hours_ago') as hours_ago
                    FROM raw_articles 
                    WHERE {' AND '.join(conditions)}
                    ORDER BY published_at DESC, urgency_score DESC
                    LIMIT ? OFFSET ?
                """

                params.extend([limit, offset])

                cursor = conn.execute(query, params)
                articles = [dict(row) for row in cursor.fetchall()]

                return articles

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database query failed: {e}")

    def get_market_insights(self, articles: List[Dict[str, Any]]) -> MarketInsights:
        """Generate market insights from processed articles."""

        breaking_count = sum(1 for a in articles if a.get("is_breaking"))
        recent_count = sum(1 for a in articles if a.get("is_recent"))

        # Sentiment distribution
        sentiment_dist = {}
        for article in articles:
            sentiment = article.get("sentiment", "neutral")
            sentiment_dist[sentiment] = sentiment_dist.get(sentiment, 0) + 1

        # Category distribution
        category_dist = {}
        for article in articles:
            category = article.get("category", "general")
            category_dist[category] = category_dist.get(category, 0) + 1

        # Market impact distribution
        impact_dist = {}
        for article in articles:
            impact = article.get("market_impact", "medium")
            impact_dist[impact] = impact_dist.get(impact, 0) + 1

        # Urgency statistics
        urgency_scores = [
            a.get("urgency_score", 0) for a in articles if a.get("urgency_score")
        ]
        urgency_stats = {
            "average": (
                sum(urgency_scores) / len(urgency_scores) if urgency_scores else 0
            ),
            "max": max(urgency_scores) if urgency_scores else 0,
            "min": min(urgency_scores) if urgency_scores else 0,
        }

        return MarketInsights(
            breaking_news_count=breaking_count,
            recent_news_count=recent_count,
            sentiment_distribution=sentiment_dist,
            top_categories=dict(
                sorted(category_dist.items(), key=lambda x: x[1], reverse=True)[:5]
            ),
            market_impact_summary=impact_dist,
            urgency_stats=urgency_stats,
        )

    async def generate_summary(self, articles: List[Dict[str, Any]]) -> Optional[str]:
        """Generate a quick summary of the articles using OpenAI."""
        if not self.openai_client or not articles:
            return None

        try:
            # Prepare article summaries for LLM
            article_summaries = []
            for article in articles[:10]:  # Limit to top 10 for summary
                summary = f"- {article['title']} ({article.get('sentiment', 'neutral')} sentiment, {article.get('market_impact', 'medium')} impact)"
                article_summaries.append(summary)

            prompt = f"""Provide a brief 2-3 sentence summary of the current crypto market sentiment based on these recent news articles:

{chr(10).join(article_summaries)}

Focus on overall market sentiment and any significant trends."""

            response = await self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.3,
            )

            return response.choices[0].message.content.strip()

        except Exception:
            return None  # Fail gracefully


# Initialize service
news_service = OptimizedNewsService()


@router.get("/news", response_model=NewsResponse)
async def get_optimized_news(
    crypto_symbols: Optional[str] = Query(
        None, description="Comma-separated crypto symbols"
    ),
    hours_back: int = Query(24, description="Hours back to search"),
    sentiment: Optional[str] = Query(None, description="Filter by sentiment"),
    breaking_only: bool = Query(False, description="Only breaking news"),
    limit: int = Query(50, description="Maximum articles to return"),
    offset: int = Query(0, description="Pagination offset"),
    include_summary: bool = Query(False, description="Include AI summary"),
):
    """
    Get optimized news articles from pre-processed data.

    This endpoint is FAST because all expensive processing was done offline.
    Response time should be under 200ms.
    """
    start_time = datetime.now()

    # Parse crypto symbols
    symbols_list = None
    if crypto_symbols:
        symbols_list = [
            s.strip().upper() for s in crypto_symbols.split(",") if s.strip()
        ]

    # Get processed articles (FAST database query)
    articles = news_service.get_processed_articles(
        crypto_symbols=symbols_list,
        hours_back=hours_back,
        sentiment_filter=sentiment,
        breaking_only=breaking_only,
        limit=limit,
        offset=offset,
    )

    # Convert to response format
    article_models = []
    for article in articles:
        article_models.append(
            NewsArticle(
                id=article["id"],
                title=article["title"],
                content=article["content"],
                url=article["url"],
                source=article["source"],
                crypto_symbol=article["crypto_symbol"],
                sentiment=article.get("sentiment", "neutral"),
                sentiment_score=float(article.get("sentiment_score", 0)),
                category=article.get("category", "general"),
                market_impact=article.get("market_impact", "medium"),
                is_breaking=bool(article.get("is_breaking", False)),
                is_recent=bool(article.get("is_recent", True)),
                recency_score=float(article.get("recency_score", 0.5)),
                urgency_score=float(article.get("urgency_score", 0.5)),
                published_at=article["published_at"],
                hours_ago=article.get("hours_ago"),
            )
        )

    # Generate summary if requested (optional, quick LLM call)
    summary = None
    if include_summary:
        summary = await news_service.generate_summary(articles)

    # Calculate processing time
    processing_time = (datetime.now() - start_time).total_seconds() * 1000

    # Determine data freshness
    if articles:
        newest_article = min(articles, key=lambda x: x.get("hours_ago", 999))
        hours_ago = newest_article.get("hours_ago", 999)
        if hours_ago < 1:
            freshness = "Very Fresh (< 1 hour)"
        elif hours_ago < 6:
            freshness = "Fresh (< 6 hours)"
        elif hours_ago < 24:
            freshness = "Recent (< 24 hours)"
        else:
            freshness = "Older (> 24 hours)"
    else:
        freshness = "No Data"

    return NewsResponse(
        articles=article_models,
        total_count=len(article_models),
        processing_time_ms=processing_time,
        data_freshness=freshness,
        summary=summary,
    )


@router.get("/insights", response_model=MarketInsights)
async def get_market_insights(
    crypto_symbols: Optional[str] = Query(
        None, description="Comma-separated crypto symbols"
    ),
    hours_back: int = Query(24, description="Hours back to analyze"),
):
    """
    Get market insights from pre-processed news data.

    This provides aggregated statistics without expensive processing.
    """
    # Parse crypto symbols
    symbols_list = None
    if crypto_symbols:
        symbols_list = [s.strip().upper() for s in crypto_symbols.split(",")]

    # Get processed articles
    articles = news_service.get_processed_articles(
        crypto_symbols=symbols_list,
        hours_back=hours_back,
        limit=1000,  # Get more for better statistics
    )

    # Generate insights
    insights = news_service.get_market_insights(articles)

    return insights


@router.get("/status")
async def get_optimization_status():
    """Get the status of the temporal optimization system."""
    try:
        with sqlite3.connect(news_service.raw_db_path) as conn:
            # Total articles
            cursor = conn.execute("SELECT COUNT(*) FROM raw_articles")
            total_articles = cursor.fetchone()[0]

            # Processed articles
            cursor = conn.execute(
                "SELECT COUNT(*) FROM raw_articles WHERE processed = 1"
            )
            processed_articles = cursor.fetchone()[0]

            # Recent articles (last 24 hours)
            cursor = conn.execute(
                """
                SELECT COUNT(*) FROM raw_articles 
                WHERE collected_at > datetime('now', '-24 hours')
            """
            )
            recent_collected = cursor.fetchone()[0]

            # Breaking news count
            cursor = conn.execute(
                """
                SELECT COUNT(*) FROM raw_articles 
                WHERE processed = 1 
                AND JSON_EXTRACT(raw_data, '$.is_breaking') = 1
                AND published_at > datetime('now', '-6 hours')
            """
            )
            breaking_news = cursor.fetchone()[0]

            return {
                "status": "operational",
                "total_articles": total_articles,
                "processed_articles": processed_articles,
                "unprocessed_articles": total_articles - processed_articles,
                "recent_collected_24h": recent_collected,
                "breaking_news_6h": breaking_news,
                "processing_percentage": (
                    round((processed_articles / total_articles * 100), 1)
                    if total_articles > 0
                    else 0
                ),
                "last_updated": datetime.now(timezone.utc).isoformat(),
                "optimization_active": True,
            }

    except Exception as e:
        return {"status": "error", "error": str(e), "optimization_active": False}
