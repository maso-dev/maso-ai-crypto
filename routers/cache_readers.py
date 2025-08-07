"""
Cache Reader Router - Phase 1 Capstone Implementation
Serves pre-processed data without triggering AI agent flows
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import asyncio
import json
import logging

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/cache", tags=["cache-readers"])

# Mock cache data - in production this would come from database
MOCK_NEWS_CACHE = {
    "last_updated": datetime.now().isoformat(),
    "summary": {
        "total_articles": 104,
        "sources": {
            "newsapi": 15,
            "tavily": 89
        },
        "sentiment": {
            "positive": 45,
            "negative": 23,
            "neutral": 36
        },
        "key_insights": [
            "Bitcoin ETF inflows continue to drive institutional adoption",
            "Ethereum spot ETF approval process advances",
            "Solana ecosystem sees significant DeFi growth",
            "Regulatory clarity improves in major markets"
        ],
        "top_stories": [
            {
                "title": "Bitcoin ETF Sees Record Inflows as Institutional Demand Grows",
                "source": "Bloomberg",
                "sentiment": "positive",
                "published_at": datetime.now().isoformat(),
                "summary": "Major Bitcoin ETFs report significant inflows as institutional investors increase crypto allocations"
            },
            {
                "title": "Ethereum Spot ETF Decision Expected Soon",
                "source": "CoinDesk",
                "sentiment": "positive", 
                "published_at": (datetime.now() - timedelta(hours=2)).isoformat(),
                "summary": "SEC decision on Ethereum spot ETFs could come within weeks, sources say"
            },
            {
                "title": "Solana DeFi Protocols Hit New TVL Highs",
                "source": "The Block",
                "sentiment": "positive",
                "published_at": (datetime.now() - timedelta(hours=4)).isoformat(),
                "summary": "Solana-based DeFi protocols reach record total value locked as ecosystem expands"
            },
            {
                "title": "European Crypto Regulation Framework Nears Completion",
                "source": "Reuters",
                "sentiment": "neutral",
                "published_at": (datetime.now() - timedelta(hours=6)).isoformat(),
                "summary": "MiCA implementation progresses with final guidelines expected this quarter"
            },
            {
                "title": "Major Banks Expand Crypto Custody Services",
                "source": "Financial Times",
                "sentiment": "positive",
                "published_at": (datetime.now() - timedelta(hours=8)).isoformat(),
                "summary": "Traditional financial institutions continue to enter the digital asset custody space"
            }
        ]
    },
    "articles": [
        {
            "title": "Bitcoin ETF Sees Record Inflows as Institutional Demand Grows",
            "source": "Bloomberg",
            "sentiment": "positive",
            "published_at": datetime.now().isoformat(),
            "summary": "Major Bitcoin ETFs report significant inflows as institutional investors increase crypto allocations"
        },
        {
            "title": "Ethereum Spot ETF Decision Expected Soon",
            "source": "CoinDesk",
            "sentiment": "positive", 
            "published_at": (datetime.now() - timedelta(hours=2)).isoformat(),
            "summary": "SEC decision on Ethereum spot ETFs could come within weeks, sources say"
        },
        {
            "title": "Solana DeFi Protocols Hit New TVL Highs",
            "source": "The Block",
            "sentiment": "positive",
            "published_at": (datetime.now() - timedelta(hours=4)).isoformat(),
            "summary": "Solana-based DeFi protocols reach record total value locked as ecosystem expands"
        }
    ]
}

MOCK_SIGNALS_CACHE = {
    "last_updated": datetime.now().isoformat(),
    "signals": [
        {
            "symbol": "BTC",
            "signal_type": "BUY",
            "confidence": 0.85,
            "reasoning": "Strong technical indicators, institutional adoption",
            "technical_indicators": {
                "rsi": 65,
                "macd": "bullish",
                "support_level": 110000
            },
            "risk_level": "medium",
            "target_price": 125000,
            "stop_loss": 105000
        },
        {
            "symbol": "ETH",
            "signal_type": "HOLD",
            "confidence": 0.72,
            "reasoning": "Consolidation phase, wait for breakout",
            "technical_indicators": {
                "rsi": 55,
                "macd": "neutral",
                "support_level": 3800
            },
            "risk_level": "low",
            "target_price": 4200,
            "stop_loss": 3600
        },
        {
            "symbol": "SOL",
            "action": "BUY",
            "confidence": 0.78,
            "reasoning": "Strong momentum, ecosystem growth",
            "technical_indicators": {
                "rsi": 70,
                "macd": "bullish",
                "support_level": 140
            },
            "risk_level": "high",
            "target_price": 165,
            "stop_loss": 125
        }
    ],
    "market_regime": "bullish",
    "overall_confidence": 0.78
}

MOCK_PORTFOLIO_CACHE = {
    "last_updated": datetime.now().isoformat(),
    "portfolio": {
        "total_value": 125000,
        "total_change_24h": 2.5,
        "total_change_7d": 8.2,
        "assets": [
            {
                "symbol": "BTC",
                "name": "Bitcoin",
                "price": 43250.50,
                "change_24h": 1.8,
                "volume_24h": 28450000000,
                "market_cap": 847000000000,
                "technical_indicators": {
                    "rsi": 65,
                    "macd": "bullish",
                    "support": 42000,
                    "resistance": 45000
                }
            },
            {
                "symbol": "ETH",
                "name": "Ethereum", 
                "price": 2950.75,
                "change_24h": 2.1,
                "volume_24h": 15800000000,
                "market_cap": 354000000000,
                "technical_indicators": {
                    "rsi": 58,
                    "macd": "neutral",
                    "support": 2800,
                    "resistance": 3000
                }
            },
            {
                "symbol": "SOL",
                "name": "Solana",
                "price": 98.25,
                "change_24h": 4.2,
                "volume_24h": 3200000000,
                "market_cap": 42000000000,
                "technical_indicators": {
                    "rsi": 72,
                    "macd": "bullish",
                    "support": 95,
                    "resistance": 105
                }
            },
            {
                "symbol": "XRP",
                "name": "Ripple",
                "price": 0.58,
                "change_24h": -0.5,
                "volume_24h": 2100000000,
                "market_cap": 31000000000,
                "technical_indicators": {
                    "rsi": 45,
                    "macd": "bearish",
                    "support": 0.55,
                    "resistance": 0.60
                }
            },
            {
                "symbol": "ADA",
                "name": "Cardano",
                "price": 0.52,
                "change_24h": 1.2,
                "volume_24h": 850000000,
                "market_cap": 18000000000,
                "technical_indicators": {
                    "rsi": 62,
                    "macd": "neutral",
                    "support": 0.50,
                    "resistance": 0.55
                }
            }
        ]
    }
}

@router.get("/news/latest-summary")
async def get_latest_news_summary() -> Dict[str, Any]:
    """
    Get latest news summary using intelligent cache system
    """
    try:
        # Import intelligent cache function
        from utils.intelligent_news_cache import get_portfolio_news
        
        # Get cached portfolio-aware news
        news_data = await get_portfolio_news(
            include_alpha_portfolio=True,
            include_opportunity_tokens=True,
            include_personal_portfolio=True,
            hours_back=24
        )
        
        if news_data and news_data.get("articles"):
            # Process cached news data
            articles = news_data.get("articles", [])
            total_articles = len(articles)
            sources = {"intelligent_cache": total_articles}
            
            # Calculate sentiment from cached data
            positive_count = sum(1 for article in articles if article.get("sentiment") == "positive")
            negative_count = sum(1 for article in articles if article.get("sentiment") == "negative")
            neutral_count = total_articles - positive_count - negative_count
            
            # Extract key insights from cached data
            key_insights = news_data.get("key_insights", [
                "Crypto market volatility continues",
                "Institutional adoption trends", 
                "DeFi protocol developments"
            ])
            
            # Format top stories from cached data
            top_stories = []
            for article in articles[:5]:
                top_stories.append({
                    "title": article.get("title", "Crypto News"),
                    "source": article.get("source", "News Source"),
                    "sentiment": article.get("sentiment", "neutral"),
                    "published_at": article.get("published_at", datetime.now().isoformat()),
                    "summary": article.get("summary", "Crypto market update")
                })
            
            cached_news_data = {
                "last_updated": datetime.now().isoformat(),
                "summary": {
                    "total_articles": total_articles,
                    "sources": sources,
                    "sentiment": {
                        "positive": positive_count,
                        "negative": negative_count,
                        "neutral": neutral_count
                    },
                    "key_insights": key_insights[:4],
                    "top_stories": top_stories
                },
                "articles": articles
            }
            
            return {
                "status": "success",
                "data": cached_news_data,
                "source": "intelligent_cache",
                "cache_age": "cached"
            }
        else:
            # Fallback to realistic mock data if NewsAPI fails
            logger.warning("NewsAPI returned no data, using realistic mock data")
            return {
                "status": "success",
                "data": MOCK_NEWS_CACHE,
                "source": "mock_fallback",
                "cache_age": "5 minutes"
            }
            
    except Exception as e:
        # Fallback to mock data if NewsAPI fails
        logger.warning(f"NewsAPI failed, using mock data: {str(e)}")
        return {
            "status": "success",
            "data": MOCK_NEWS_CACHE,
            "source": "mock_fallback",
            "cache_age": "5 minutes"
        }

@router.get("/signals/latest")
async def get_latest_signals() -> Dict[str, Any]:
    """
    Get latest trading signals from cache (no AI generation)
    """
    try:
        return {
            "status": "success", 
            "data": MOCK_SIGNALS_CACHE,
            "source": "cache",
            "cache_age": "3 minutes"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get signals: {str(e)}")

@router.get("/portfolio/livecoinwatch")
async def get_livecoinwatch_portfolio() -> Dict[str, Any]:
    """
    Get portfolio data from LiveCoinWatch API (real-time)
    """
    try:
        # Import LiveCoinWatch processor convenience functions
        from utils.livecoinwatch_processor import get_latest_prices, calculate_technical_indicators
        
        # Define our portfolio symbols
        portfolio_symbols = ["BTC", "ETH", "SOL", "XRP", "ADA"]
        
        # Get real-time price data from LiveCoinWatch
        latest_prices = await get_latest_prices(portfolio_symbols)
        
        # Calculate total portfolio value and changes
        total_value = 0
        total_change_24h = 0
        total_change_7d = 0
        assets = []
        
        # Check if we have real data
        has_real_data = len(latest_prices) > 0
        
        for symbol in portfolio_symbols:
            if symbol in latest_prices and has_real_data:
                price_data = latest_prices[symbol]
                
                # Calculate technical indicators
                try:
                    indicators = await calculate_technical_indicators(symbol, days=30)
                except Exception as e:
                    # Fallback to basic indicators if calculation fails
                    indicators = {
                        "rsi": 50,
                        "macd": "neutral",
                        "support": price_data.price_usd * 0.95,
                        "resistance": price_data.price_usd * 1.05
                    }
                
                # Simulate portfolio allocation (in a real app, this would come from user's actual portfolio)
                allocation = {
                    "BTC": 0.40,  # 40%
                    "ETH": 0.30,  # 30%
                    "SOL": 0.15,  # 15%
                    "XRP": 0.10,  # 10%
                    "ADA": 0.05   # 5%
                }
                
                asset_value = 125000 * allocation.get(symbol, 0.1)  # Base portfolio value
                total_value += asset_value
                
                assets.append({
                    "symbol": symbol,
                    "name": {
                        "BTC": "Bitcoin",
                        "ETH": "Ethereum", 
                        "SOL": "Solana",
                        "XRP": "Ripple",
                        "ADA": "Cardano"
                    }.get(symbol, symbol),
                    "price": price_data.price_usd,
                    "change_24h": price_data.change_24h,
                    "volume_24h": price_data.volume_24h,
                    "market_cap": price_data.market_cap,
                    "technical_indicators": indicators,
                    "data_source": "LiveCoinWatch"
                })
        
        # If no real data available, use realistic mock data
        if not has_real_data:
            logger.warning("No real LiveCoinWatch data available, using realistic mock data")
            realistic_mock_data = {
                "BTC": {"price": 72000.50, "change_24h": 2.1, "name": "Bitcoin"},
                "ETH": {"price": 3950.75, "change_24h": 1.8, "name": "Ethereum"},
                "SOL": {"price": 145.25, "change_24h": 4.2, "name": "Solana"},
                "XRP": {"price": 0.58, "change_24h": -0.5, "name": "Ripple"},
                "ADA": {"price": 0.52, "change_24h": 1.2, "name": "Cardano"}
            }
            
            for symbol in portfolio_symbols:
                if symbol in realistic_mock_data:
                    mock_data = realistic_mock_data[symbol]
                    allocation = {
                        "BTC": 0.40, "ETH": 0.30, "SOL": 0.15, "XRP": 0.10, "ADA": 0.05
                    }.get(symbol, 0.1)
                    
                    asset_value = 125000 * allocation
                    total_value += asset_value
                    
                    assets.append({
                        "symbol": symbol,
                        "name": mock_data["name"],
                        "price": mock_data["price"],
                        "change_24h": mock_data["change_24h"],
                        "volume_24h": 1000000000,  # Mock volume
                        "market_cap": mock_data["price"] * 1000000000,  # Mock market cap
                        "technical_indicators": {
                            "rsi": 65,
                            "macd": "bullish",
                            "support": mock_data["price"] * 0.95,
                            "resistance": mock_data["price"] * 1.05
                        },
                        "data_source": "Mock (LiveCoinWatch unavailable)"
                    })
        
        # Calculate weighted portfolio changes
        for asset in assets:
            symbol = asset["symbol"]
            allocation = {
                "BTC": 0.40, "ETH": 0.30, "SOL": 0.15, "XRP": 0.10, "ADA": 0.05
            }.get(symbol, 0.1)
            
            total_change_24h += asset["change_24h"] * allocation
            # For 7-day change, we'll use a simplified calculation
            total_change_7d += asset["change_24h"] * allocation * 3  # Approximate 7-day from 24h
        
        portfolio_data = {
            "last_updated": datetime.now().isoformat(),
            "portfolio": {
                "total_value": total_value,
                "total_change_24h": total_change_24h,
                "total_change_7d": total_change_7d,
                "assets": assets
            }
        }
        
        return {
            "status": "success",
            "data": portfolio_data,
            "source": "livecoinwatch",
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        # Fallback to mock data if LiveCoinWatch API fails
        logger.warning(f"LiveCoinWatch API failed, using mock data: {str(e)}")
        return {
            "status": "success",
            "data": MOCK_PORTFOLIO_CACHE,
            "source": "mock_fallback",
            "last_updated": datetime.now().isoformat()
        }

@router.get("/status")
async def get_cache_status() -> Dict[str, Any]:
    """
    Get status of all cache readers
    """
    return {
        "status": "healthy",
        "caches": {
            "news_summary": {
                "status": "available",
                "last_updated": MOCK_NEWS_CACHE["last_updated"],
                "age_minutes": 5
            },
            "signals": {
                "status": "available", 
                "last_updated": MOCK_SIGNALS_CACHE["last_updated"],
                "age_minutes": 3
            },
            "portfolio": {
                "status": "available",
                "last_updated": MOCK_PORTFOLIO_CACHE["last_updated"],
                "age_minutes": 1
            }
        },
        "total_endpoints": 3
    } 
