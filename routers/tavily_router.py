#!/usr/bin/env python3
"""
Tavily Search Router
FastAPI endpoints for real-time web search and news aggregation.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict, Any
import logging

from utils.tavily_search import (
    tavily_client,
    search_crypto_news,
    get_crypto_market_data as get_crypto_market_data_func,
    get_trending_crypto_topics,
    search_tavily_news,
    search_tavily_finance,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/tavily", tags=["tavily"])


@router.get("/status")
async def get_tavily_status():
    """Get Tavily service status."""
    try:
        status = await tavily_client.get_system_status()
        return {
            "service": "tavily_search",
            "status": status["status"],
            "available": status["status"] == "ready",
            "features": status["features"],
            "api_key_available": status["api_key_available"],
        }
    except Exception as e:
        logger.error(f"Error getting Tavily status: {e}")
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")


@router.get("/news")
async def search_news(
    query: str = Query(..., description="Search query for news"),
    max_results: int = Query(20, description="Maximum number of results"),
    time_period: str = Query("1d", description="Time period: 1d, 1w, 1m"),
):
    """Search for recent news articles."""
    try:
        response = await tavily_client.search_news(query, max_results, time_period)

        return {
            "success": True,
            "query": response.query,
            "total_results": response.total_results,
            "search_time": response.search_time,
            "search_type": response.search_type,
            "results": [
                {
                    "title": result.title,
                    "url": result.url,
                    "content": result.content,
                    "score": result.score,
                    "source": result.source,
                    "published_date": (
                        result.published_date.isoformat()
                        if result.published_date
                        else None
                    ),
                    "search_type": result.search_type,
                    "metadata": result.metadata,
                }
                for result in response.results
            ],
            "metadata": response.metadata,
        }
    except Exception as e:
        logger.error(f"Error searching news: {e}")
        raise HTTPException(status_code=500, detail=f"News search failed: {str(e)}")


@router.get("/finance")
async def search_finance(
    query: str = Query(..., description="Financial search query"),
    max_results: int = Query(15, description="Maximum number of results"),
):
    """Search for financial and market data."""
    try:
        response = await tavily_client.search_finance(query, max_results)

        return {
            "success": True,
            "query": response.query,
            "total_results": response.total_results,
            "search_time": response.search_time,
            "search_type": response.search_type,
            "results": [
                {
                    "title": result.title,
                    "url": result.url,
                    "content": result.content,
                    "score": result.score,
                    "source": result.source,
                    "published_date": (
                        result.published_date.isoformat()
                        if result.published_date
                        else None
                    ),
                    "search_type": result.search_type,
                    "metadata": result.metadata,
                }
                for result in response.results
            ],
            "metadata": response.metadata,
        }
    except Exception as e:
        logger.error(f"Error searching finance: {e}")
        raise HTTPException(status_code=500, detail=f"Finance search failed: {str(e)}")


@router.get("/web")
async def search_web(
    query: str = Query(..., description="Web search query"),
    max_results: int = Query(10, description="Maximum number of results"),
):
    """General web search for current information."""
    try:
        response = await tavily_client.search_web(query, max_results)

        return {
            "success": True,
            "query": response.query,
            "total_results": response.total_results,
            "search_time": response.search_time,
            "search_type": response.search_type,
            "results": [
                {
                    "title": result.title,
                    "url": result.url,
                    "content": result.content,
                    "score": result.score,
                    "source": result.source,
                    "published_date": (
                        result.published_date.isoformat()
                        if result.published_date
                        else None
                    ),
                    "search_type": result.search_type,
                    "metadata": result.metadata,
                }
                for result in response.results
            ],
            "metadata": response.metadata,
        }
    except Exception as e:
        logger.error(f"Error searching web: {e}")
        raise HTTPException(status_code=500, detail=f"Web search failed: {str(e)}")


@router.get("/crypto/news")
async def get_crypto_news(
    symbols: List[str] = Query(..., description="List of cryptocurrency symbols"),
    max_results: int = Query(20, description="Maximum number of results"),
):
    """Get crypto news for specific symbols."""
    try:
        results = await search_crypto_news(symbols, max_results)

        return {
            "success": True,
            "symbols": symbols,
            "total_results": len(results),
            "results": [
                {
                    "title": result.title,
                    "url": result.url,
                    "content": result.content,
                    "score": result.score,
                    "source": result.source,
                    "published_date": (
                        result.published_date.isoformat()
                        if result.published_date
                        else None
                    ),
                    "search_type": result.search_type,
                    "metadata": result.metadata,
                }
                for result in results
            ],
        }
    except Exception as e:
        logger.error(f"Error getting crypto news: {e}")
        raise HTTPException(
            status_code=500, detail=f"Crypto news search failed: {str(e)}"
        )


@router.get("/crypto/market-data")
async def get_crypto_market_data(
    symbols: List[str] = Query(..., description="List of cryptocurrency symbols")
):
    """Get current market data for symbols."""
    try:
        market_data = await get_crypto_market_data_func(symbols)

        return {"success": True, "symbols": symbols, "market_data": market_data}
    except Exception as e:
        logger.error(f"Error getting crypto market data: {e}")
        raise HTTPException(
            status_code=500, detail=f"Market data search failed: {str(e)}"
        )


@router.get("/crypto/trending")
async def get_trending_topics():
    """Get trending crypto topics."""
    try:
        trending_topics = await get_trending_crypto_topics()

        return {
            "success": True,
            "trending_topics": trending_topics,
            "count": len(trending_topics),
        }
    except Exception as e:
        logger.error(f"Error getting trending topics: {e}")
        raise HTTPException(
            status_code=500, detail=f"Trending topics search failed: {str(e)}"
        )


@router.post("/search")
async def multi_search(
    queries: List[str] = Query(..., description="List of search queries"),
    search_types: List[str] = Query(
        ["news"], description="Types of search: news, finance, web"
    ),
    max_results: int = Query(10, description="Maximum results per query"),
):
    """Perform multiple searches across different types."""
    try:
        results = {}

        for query in queries:
            query_results = {}

            for search_type in search_types:
                if search_type == "news":
                    response = await tavily_client.search_news(query, max_results)
                elif search_type == "finance":
                    response = await tavily_client.search_finance(query, max_results)
                elif search_type == "web":
                    response = await tavily_client.search_web(query, max_results)
                else:
                    continue

                query_results[search_type] = {
                    "total_results": response.total_results,
                    "search_time": response.search_time,
                    "results": [
                        {
                            "title": result.title,
                            "url": result.url,
                            "content": (
                                result.content[:200] + "..."
                                if len(result.content) > 200
                                else result.content
                            ),
                            "score": result.score,
                            "source": result.source,
                        }
                        for result in response.results
                    ],
                }

            results[query] = query_results

        return {
            "success": True,
            "queries": queries,
            "search_types": search_types,
            "results": results,
        }
    except Exception as e:
        logger.error(f"Error in multi-search: {e}")
        raise HTTPException(status_code=500, detail=f"Multi-search failed: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        status = await tavily_client.get_system_status()
        return {
            "service": "tavily_search",
            "status": "healthy" if status["status"] == "ready" else "unhealthy",
            "available": status["status"] == "ready",
            "timestamp": "2025-08-03T01:30:00Z",
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "service": "tavily_search",
            "status": "unhealthy",
            "available": False,
            "error": str(e),
            "timestamp": "2025-08-03T01:30:00Z",
        }
