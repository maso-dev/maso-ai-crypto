#!/usr/bin/env python3
"""
Crypto News API Endpoints
Provides news-related operations for crypto market analysis.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import asyncio

# Import news-specific utilities
from utils.newsapi import fetch_news_articles
from utils.optimized_pipeline import run_optimized_pipeline
from utils.milvus import insert_news_chunks

router = APIRouter(prefix="/news", tags=["crypto-news"])


class PopulateNewsRequest(BaseModel):
    """Request model for populating news RAG."""

    hours_back: int = Field(default=24, description="Hours back to fetch news")
    enable_validation: bool = Field(default=True, description="Enable REACT validation")
    chunk_size: int = Field(default=500, description="Text chunk size for processing")


class PopulateNewsResponse(BaseModel):
    """Response model for news population."""

    status: str
    articles_processed: int
    chunks_created: int
    validation_summary: Optional[Dict[str, Any]]
    processing_time: float
    timestamp: str


class NewsSearchRequest(BaseModel):
    """Request model for news search."""

    symbols: List[str] = Field(..., description="Crypto symbols to search for")
    limit: int = Field(default=10, description="Number of articles to return")
    hours_back: int = Field(default=24, description="Hours back to search")


class NewsSearchResponse(BaseModel):
    """Response model for news search."""

    articles: List[Dict[str, Any]]
    total_found: int
    search_symbols: List[str]
    timestamp: str


@router.post("/populate", response_model=PopulateNewsResponse)
async def populate_crypto_news_rag(
    request: PopulateNewsRequest,
) -> PopulateNewsResponse:
    """Populate the crypto news RAG with fresh articles."""
    try:
        start_time = datetime.now(timezone.utc)

        # Fetch news articles
        print(f"📰 Fetching crypto news from the last {request.hours_back} hours...")
        articles = await fetch_news_articles(
            terms=["cryptocurrency", "bitcoin", "ethereum"],
            hours_back=request.hours_back,
        )

        if not articles:
            return PopulateNewsResponse(
                status="no_articles",
                articles_processed=0,
                chunks_created=0,
                validation_summary=None,
                processing_time=0.0,
                timestamp=start_time.isoformat(),
            )

        print(f"📊 Processing {len(articles)} articles...")

        # Run optimized pipeline
        pipeline_result = await run_optimized_pipeline(
            articles=articles, enable_validation=request.enable_validation
        )

        # Insert into Milvus
        if pipeline_result["vector_data"]:
            print(
                f"🗄️ Inserting {len(pipeline_result['vector_data'])} chunks into Milvus..."
            )
            await insert_news_chunks(pipeline_result["vector_data"])

        end_time = datetime.now(timezone.utc)
        processing_time = (end_time - start_time).total_seconds()

        return PopulateNewsResponse(
            status="success",
            articles_processed=len(articles),
            chunks_created=len(pipeline_result["vector_data"]),
            validation_summary=pipeline_result.get("validation_summary"),
            processing_time=processing_time,
            timestamp=end_time.isoformat(),
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error populating news RAG: {str(e)}"
        )


@router.post("/search", response_model=NewsSearchResponse)
async def search_crypto_news(request: NewsSearchRequest) -> NewsSearchResponse:
    """Search for crypto news articles by symbols."""
    try:
        from utils.milvus import query_news_for_symbols

        # Search for news articles
        articles = await query_news_for_symbols(
            symbols=request.symbols, limit=request.limit
        )

        return NewsSearchResponse(
            articles=articles,
            total_found=len(articles),
            search_symbols=request.symbols,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching news: {str(e)}")


@router.get("/trending")
async def get_trending_topics() -> Dict[str, Any]:
    """Get trending crypto topics and themes."""
    try:
        # Mock trending topics
        trending_topics = [
            {"topic": "Bitcoin ETF", "mentions": 1250, "sentiment": 0.7, "trend": "up"},
            {
                "topic": "Ethereum Layer 2",
                "mentions": 890,
                "sentiment": 0.6,
                "trend": "up",
            },
            {
                "topic": "DeFi Regulation",
                "mentions": 650,
                "sentiment": 0.3,
                "trend": "down",
            },
            {
                "topic": "NFT Market",
                "mentions": 420,
                "sentiment": 0.5,
                "trend": "stable",
            },
        ]

        return {
            "trending_topics": trending_topics,
            "analysis_date": datetime.now(timezone.utc).isoformat(),
            "total_articles_analyzed": 1500,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving trending topics: {str(e)}"
        )


@router.get("/sentiment/{symbol}")
async def get_symbol_sentiment(symbol: str) -> Dict[str, Any]:
    """Get sentiment analysis for a specific crypto symbol."""
    try:
        from utils.milvus import query_news_for_symbols

        # Get recent news for the symbol
        articles = await query_news_for_symbols([symbol], limit=50)

        if not articles:
            return {
                "symbol": symbol,
                "sentiment_score": 0.0,
                "confidence": 0.0,
                "articles_analyzed": 0,
                "last_updated": datetime.now(timezone.utc).isoformat(),
            }

        # Calculate average sentiment
        sentiment_scores = []
        for article in articles:
            if "metadata" in article and "sentiment" in article["metadata"]:
                sentiment_scores.append(article["metadata"]["sentiment"])

        avg_sentiment = (
            sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0.0
        )

        return {
            "symbol": symbol,
            "sentiment_score": avg_sentiment,
            "confidence": len(sentiment_scores) / len(articles),
            "articles_analyzed": len(articles),
            "sentiment_distribution": {
                "positive": len([s for s in sentiment_scores if s > 0.6]),
                "neutral": len([s for s in sentiment_scores if 0.4 <= s <= 0.6]),
                "negative": len([s for s in sentiment_scores if s < 0.4]),
            },
            "last_updated": datetime.now(timezone.utc).isoformat(),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving sentiment: {str(e)}"
        )


@router.get("/sources")
async def get_news_sources() -> Dict[str, Any]:
    """Get list of news sources and their reliability scores."""
    try:
        sources = [
            {
                "name": "CoinDesk",
                "reliability_score": 0.9,
                "bias": "neutral",
                "coverage": "comprehensive",
            },
            {
                "name": "CoinTelegraph",
                "reliability_score": 0.85,
                "bias": "slightly_bullish",
                "coverage": "comprehensive",
            },
            {
                "name": "Reuters",
                "reliability_score": 0.95,
                "bias": "neutral",
                "coverage": "selective",
            },
            {
                "name": "Bloomberg",
                "reliability_score": 0.92,
                "bias": "neutral",
                "coverage": "comprehensive",
            },
        ]

        return {
            "sources": sources,
            "total_sources": len(sources),
            "last_updated": datetime.now(timezone.utc).isoformat(),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving sources: {str(e)}"
        )


@router.get("/stats")
async def get_news_stats() -> Dict[str, Any]:
    """Get news processing statistics."""
    try:
        # Mock statistics
        return {
            "total_articles_processed": 15420,
            "articles_today": 156,
            "articles_this_week": 892,
            "validation_rate": 0.87,
            "avg_processing_time": 2.3,
            "storage_used_mb": 45.2,
            "last_updated": datetime.now(timezone.utc).isoformat(),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving stats: {str(e)}")
