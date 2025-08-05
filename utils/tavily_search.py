#!/usr/bin/env python3
"""
Tavily Search Integration
Real-time web search, news aggregation, and market data collection.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
import httpx

# Import centralized config
from utils.config import get_api_key, is_api_available

logger = logging.getLogger(__name__)


@dataclass
class TavilySearchResult:
    """Result from Tavily search."""

    title: str
    url: str
    content: str
    score: float
    source: str
    published_date: Optional[datetime]
    search_type: str  # "news", "web", "finance"
    metadata: Dict[str, Any]


@dataclass
class TavilySearchResponse:
    """Complete response from Tavily search."""

    query: str
    results: List[TavilySearchResult]
    total_results: int
    search_time: float
    search_type: str
    metadata: Dict[str, Any]


class TavilySearchClient:
    """Tavily search client for real-time data collection."""

    def __init__(self):
        self.api_key = get_api_key("tavily")
        self.base_url = "https://api.tavily.com"
        self.available = is_api_available("tavily")

        if not self.api_key:
            logger.warning("TAVILY_API_KEY not found. Tavily search will be disabled.")
        else:
            logger.info("TavilySearchClient initialized")

    async def search_news(
        self, query: str, max_results: int = 20, time_period: str = "1d"
    ) -> TavilySearchResponse:
        """
        Search for recent news articles.

        Args:
            query: Search query
            max_results: Maximum number of results
            time_period: Time period for news (1d, 1w, 1m)

        Returns:
            TavilySearchResponse with news results
        """
        if not self.available:
            return TavilySearchResponse(
                query=query,
                results=[],
                total_results=0,
                search_time=0.0,
                search_type="news",
                metadata={"error": "Tavily API not available"},
            )

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/search",
                    headers={"X-API-Key": self.api_key or ""},
                    json={
                        "query": query,
                        "search_depth": "basic",
                        "include_answer": False,
                        "include_raw_content": False,
                        "include_images": False,
                        "max_results": max_results,
                        "search_type": "news",
                        "time_period": time_period,
                    },
                    timeout=30.0,
                )

                if response.status_code == 200:
                    data = response.json()
                    return self._parse_search_response(data, "news")
                else:
                    logger.error(f"Tavily search failed: {response.status_code}")
                    return TavilySearchResponse(
                        query=query,
                        results=[],
                        total_results=0,
                        search_time=0.0,
                        search_type="news",
                        metadata={"error": f"HTTP {response.status_code}"},
                    )

        except Exception as e:
            logger.error(f"Tavily search error: {e}")
            return TavilySearchResponse(
                query=query,
                results=[],
                total_results=0,
                search_time=0.0,
                search_type="news",
                metadata={"error": str(e)},
            )

    async def search_finance(
        self, query: str, max_results: int = 15
    ) -> TavilySearchResponse:
        """
        Search for financial and market data.

        Args:
            query: Financial search query
            max_results: Maximum number of results

        Returns:
            TavilySearchResponse with financial results
        """
        if not self.available:
            return TavilySearchResponse(
                query=query,
                results=[],
                total_results=0,
                search_time=0.0,
                search_type="finance",
                metadata={"error": "Tavily API not available"},
            )

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/search",
                    headers={"X-API-Key": self.api_key or ""},
                    json={
                        "query": query,
                        "search_depth": "advanced",
                        "include_answer": True,
                        "include_raw_content": False,
                        "include_images": False,
                        "max_results": max_results,
                        "search_type": "finance",
                    },
                    timeout=30.0,
                )

                if response.status_code == 200:
                    data = response.json()
                    return self._parse_search_response(data, "finance")
                else:
                    logger.error(
                        f"Tavily finance search failed: {response.status_code}"
                    )
                    return TavilySearchResponse(
                        query=query,
                        results=[],
                        total_results=0,
                        search_time=0.0,
                        search_type="finance",
                        metadata={"error": f"HTTP {response.status_code}"},
                    )

        except Exception as e:
            logger.error(f"Tavily finance search error: {e}")
            return TavilySearchResponse(
                query=query,
                results=[],
                total_results=0,
                search_time=0.0,
                search_type="finance",
                metadata={"error": str(e)},
            )

    async def search_web(
        self, query: str, max_results: int = 10
    ) -> TavilySearchResponse:
        """
        General web search for current information.

        Args:
            query: Web search query
            max_results: Maximum number of results

        Returns:
            TavilySearchResponse with web results
        """
        if not self.available:
            return TavilySearchResponse(
                query=query,
                results=[],
                total_results=0,
                search_time=0.0,
                search_type="web",
                metadata={"error": "Tavily API not available"},
            )

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/search",
                    headers={"X-API-Key": self.api_key or ""},
                    json={
                        "query": query,
                        "search_depth": "basic",
                        "include_answer": False,
                        "include_raw_content": False,
                        "include_images": False,
                        "max_results": max_results,
                        "search_type": "web",
                    },
                    timeout=30.0,
                )

                if response.status_code == 200:
                    data = response.json()
                    return self._parse_search_response(data, "web")
                else:
                    logger.error(f"Tavily web search failed: {response.status_code}")
                    return TavilySearchResponse(
                        query=query,
                        results=[],
                        total_results=0,
                        search_time=0.0,
                        search_type="web",
                        metadata={"error": f"HTTP {response.status_code}"},
                    )

        except Exception as e:
            logger.error(f"Tavily web search error: {e}")
            return TavilySearchResponse(
                query=query,
                results=[],
                total_results=0,
                search_time=0.0,
                search_type="web",
                metadata={"error": str(e)},
            )

    def _parse_search_response(
        self, data: Dict[str, Any], search_type: str
    ) -> TavilySearchResponse:
        """Parse Tavily search response."""
        results = []

        for result in data.get("results", []):
            try:
                # Parse published date
                published_date = None
                if result.get("published_date"):
                    try:
                        published_date = datetime.fromisoformat(
                            result["published_date"].replace("Z", "+00:00")
                        )
                    except:
                        pass

                # Create search result
                search_result = TavilySearchResult(
                    title=result.get("title", ""),
                    url=result.get("url", ""),
                    content=result.get("content", ""),
                    score=result.get("score", 0.0),
                    source=result.get("source", ""),
                    published_date=published_date,
                    search_type=search_type,
                    metadata={
                        "language": result.get("language"),
                        "country": result.get("country"),
                        "category": result.get("category"),
                    },
                )
                results.append(search_result)

            except Exception as e:
                logger.warning(f"Failed to parse search result: {e}")
                continue

        return TavilySearchResponse(
            query=data.get("query", ""),
            results=results,
            total_results=len(results),
            search_time=data.get("search_time", 0.0),
            search_type=search_type,
            metadata={
                "answer": data.get("answer"),
                "images": data.get("images", []),
                "follow_up_questions": data.get("follow_up_questions", []),
            },
        )

    async def get_crypto_news(
        self, symbols: List[str], max_results: int = 20
    ) -> List[TavilySearchResult]:
        """
        Get crypto news for specific symbols.

        Args:
            symbols: List of cryptocurrency symbols
            max_results: Maximum number of results per symbol

        Returns:
            List of news results
        """
        all_results = []

        for symbol in symbols:
            try:
                # Search for news about the symbol
                query = f"{symbol} cryptocurrency news market analysis"
                response = await self.search_news(
                    query, max_results=max_results // len(symbols)
                )

                if response.results:
                    all_results.extend(response.results)
                    logger.info(
                        f"Found {len(response.results)} news articles for {symbol}"
                    )
                else:
                    logger.warning(f"No news found for {symbol}")

            except Exception as e:
                logger.error(f"Error searching news for {symbol}: {e}")

        # Sort by relevance and date
        all_results.sort(
            key=lambda x: (x.score, x.published_date or datetime.min), reverse=True
        )

        return all_results[:max_results]

    async def get_market_data(self, symbols: List[str]) -> Dict[str, Any]:
        """
        Get current market data for symbols.

        Args:
            symbols: List of cryptocurrency symbols

        Returns:
            Dictionary with market data
        """
        market_data = {}

        for symbol in symbols:
            try:
                # Search for current market data
                query = f"{symbol} current price market cap volume cryptocurrency"
                response = await self.search_finance(query, max_results=5)

                if response.results:
                    market_data[symbol] = {
                        "results": response.results,
                        "answer": response.metadata.get("answer"),
                        "search_time": response.search_time,
                    }
                    logger.info(f"Found market data for {symbol}")
                else:
                    logger.warning(f"No market data found for {symbol}")

            except Exception as e:
                logger.error(f"Error getting market data for {symbol}: {e}")

        return market_data

    async def get_trending_topics(self) -> List[str]:
        """
        Get trending crypto topics.

        Returns:
            List of trending topics
        """
        try:
            query = "trending cryptocurrency topics blockchain DeFi NFT"
            response = await self.search_web(query, max_results=10)

            trending_topics = []
            for result in response.results:
                # Extract potential trending topics from titles
                title = result.title.lower()
                if any(
                    keyword in title
                    for keyword in ["trending", "popular", "hot", "rising", "top"]
                ):
                    trending_topics.append(result.title)

            return trending_topics[:5]  # Return top 5 trending topics

        except Exception as e:
            logger.error(f"Error getting trending topics: {e}")
            return []

    async def get_system_status(self) -> Dict[str, Any]:
        """Get system status for monitoring."""
        return {
            "service": "tavily_search",
            "status": "ready" if self.available else "disabled",
            "api_key_available": bool(self.api_key),
            "base_url": self.base_url,
            "features": {
                "news_search": self.available,
                "finance_search": self.available,
                "web_search": self.available,
                "crypto_news": self.available,
                "market_data": self.available,
                "trending_topics": self.available,
            },
        }


# Global instance
tavily_client = TavilySearchClient()


# Convenience functions
async def search_crypto_news(
    symbols: List[str], max_results: int = 20
) -> List[TavilySearchResult]:
    """Search for crypto news using Tavily."""
    return await tavily_client.get_crypto_news(symbols, max_results)


async def get_crypto_market_data(symbols: List[str]) -> Dict[str, Any]:
    """Get crypto market data using Tavily."""
    return await tavily_client.get_market_data(symbols)


async def get_trending_crypto_topics() -> List[str]:
    """Get trending crypto topics using Tavily."""
    return await tavily_client.get_trending_topics()


async def search_tavily_news(query: str, max_results: int = 20) -> TavilySearchResponse:
    """Search for news using Tavily."""
    return await tavily_client.search_news(query, max_results)


async def search_tavily_finance(
    query: str, max_results: int = 15
) -> TavilySearchResponse:
    """Search for financial data using Tavily."""
    return await tavily_client.search_finance(query, max_results)
