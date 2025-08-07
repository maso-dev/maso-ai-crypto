#!/usr/bin/env python3
"""
LiveCoinWatch Router
Provides secure admin endpoints for LiveCoinWatch data collection and testing.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Request
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel

# Import LiveCoinWatch processor
from utils.livecoinwatch_processor import (
    collect_price_data,
    collect_historical_data,
    calculate_technical_indicators,
    get_latest_prices,
    livecoinwatch_processor,
)

router = APIRouter(prefix="/api/livecoinwatch", tags=["livecoinwatch"])


# Pydantic models
class PriceDataRequest(BaseModel):
    symbols: List[str]
    include_historical: bool = False
    include_indicators: bool = False


class HistoricalDataRequest(BaseModel):
    symbol: str
    days: int = 30


class TechnicalIndicatorsRequest(BaseModel):
    symbol: str
    days: int = 30


def is_admin_user(request: Request) -> bool:
    """Check if user has admin access."""
    # Simple admin check - you can enhance this
    admin_secret = request.headers.get("Authorization", "").replace("Bearer ", "")
    return admin_secret == "your_admin_secret_key"  # Replace with your actual secret


# ============================================================================
# ADMIN ENDPOINTS (Secure)
# ============================================================================


@router.post("/collect-prices")
async def trigger_price_collection(
    request: Request, background_tasks: BackgroundTasks, data_request: PriceDataRequest
):
    """Trigger price data collection (admin only)."""
    if not is_admin_user(request):
        raise HTTPException(status_code=403, detail="Admin access required")

    try:
        # Collect price data
        background_tasks.add_task(collect_price_data, data_request.symbols)

        # Collect historical data if requested
        if data_request.include_historical:
            for symbol in data_request.symbols:
                background_tasks.add_task(collect_historical_data, symbol, 30)

        # Calculate indicators if requested
        if data_request.include_indicators:
            for symbol in data_request.symbols:
                background_tasks.add_task(calculate_technical_indicators, symbol, 30)

        return {
            "message": "Price collection triggered",
            "symbols": data_request.symbols,
            "include_historical": data_request.include_historical,
            "include_indicators": data_request.include_indicators,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error triggering collection: {str(e)}"
        )


@router.post("/trigger-collection")
async def trigger_data_collection(
    background_tasks: BackgroundTasks, data_request: PriceDataRequest
):
    """Trigger price data collection (public endpoint for admin page)."""
    try:
        # Collect price data
        background_tasks.add_task(collect_price_data, data_request.symbols)

        # Collect historical data if requested
        if data_request.include_historical:
            for symbol in data_request.symbols:
                background_tasks.add_task(collect_historical_data, symbol, 30)

        # Calculate indicators if requested
        if data_request.include_indicators:
            for symbol in data_request.symbols:
                background_tasks.add_task(calculate_technical_indicators, symbol, 30)

        return {
            "message": "Price collection triggered",
            "symbols": data_request.symbols,
            "include_historical": data_request.include_historical,
            "include_indicators": data_request.include_indicators,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error triggering collection: {str(e)}"
        )


@router.post("/collect-historical")
async def trigger_historical_collection(
    request: Request,
    background_tasks: BackgroundTasks,
    data_request: HistoricalDataRequest,
):
    """Trigger historical data collection (admin only)."""
    if not is_admin_user(request):
        raise HTTPException(status_code=403, detail="Admin access required")

    try:
        background_tasks.add_task(
            collect_historical_data, data_request.symbol, data_request.days
        )

        return {
            "message": "Historical data collection triggered",
            "symbol": data_request.symbol,
            "days": data_request.days,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error triggering historical collection: {str(e)}"
        )


@router.post("/calculate-indicators")
async def trigger_indicators_calculation(
    request: Request,
    background_tasks: BackgroundTasks,
    data_request: TechnicalIndicatorsRequest,
):
    """Trigger technical indicators calculation (admin only)."""
    if not is_admin_user(request):
        raise HTTPException(status_code=403, detail="Admin access required")

    try:
        background_tasks.add_task(
            calculate_technical_indicators, data_request.symbol, data_request.days
        )

        return {
            "message": "Technical indicators calculation triggered",
            "symbol": data_request.symbol,
            "days": data_request.days,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error triggering indicators calculation: {str(e)}"
        )


# ============================================================================
# DATA RETRIEVAL ENDPOINTS
# ============================================================================


@router.get("/latest-prices")
async def get_latest_price_data(symbols: Optional[str] = None):
    """Get latest price data for symbols."""
    try:
        symbol_list = symbols.split(",") if symbols else None
        latest_prices = await get_latest_prices(symbol_list)

        # Convert to serializable format
        price_data = {}
        for symbol, price in latest_prices.items():
            price_data[symbol] = {
                "symbol": price.symbol,
                "timestamp": price.timestamp.isoformat(),
                "price_usd": price.price_usd,
                "market_cap": price.market_cap,
                "volume_24h": price.volume_24h,
                "change_24h": price.change_24h,
                "change_7d": price.change_7d,
                "circulating_supply": price.circulating_supply,
                "total_supply": price.total_supply,
                "max_supply": price.max_supply,
                "rank": price.rank,
                "dominance": price.dominance,
            }

        return {
            "latest_prices": price_data,
            "count": len(price_data),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving price data: {str(e)}"
        )


@router.get("/symbol/{symbol}/indicators")
async def get_symbol_indicators(symbol: str, days: int = 30):
    """Get technical indicators for a symbol."""
    try:
        indicators = await calculate_technical_indicators(symbol, days)

        return {
            "symbol": symbol,
            "indicators": indicators,
            "days": days,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error calculating indicators: {str(e)}"
        )


# ============================================================================
# STATUS & HEALTH ENDPOINTS
# ============================================================================


@router.get("/health")
async def livecoinwatch_health():
    """Get LiveCoinWatch processor health status."""
    try:
        api_key_configured = bool(livecoinwatch_processor.api_key)

        return {
            "status": "healthy" if api_key_configured else "configured",
            "service": "LiveCoinWatch Processor",
            "api_key_configured": api_key_configured,
            "database_path": livecoinwatch_processor.db_path,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "LiveCoinWatch Processor",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


@router.get("/stats")
async def get_livecoinwatch_stats():
    """Get LiveCoinWatch data statistics."""
    try:
        import sqlite3

        conn = sqlite3.connect(livecoinwatch_processor.db_path)
        cursor = conn.cursor()

        # Get price data stats
        cursor.execute("SELECT COUNT(*) FROM price_data")
        price_data_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(DISTINCT symbol) FROM price_data")
        unique_symbols = cursor.fetchone()[0]

        cursor.execute("SELECT MAX(timestamp) FROM price_data")
        latest_update = cursor.fetchone()[0]

        # Get historical data stats
        cursor.execute("SELECT COUNT(*) FROM historical_data")
        historical_data_count = cursor.fetchone()[0]

        # Get technical indicators stats
        cursor.execute("SELECT COUNT(*) FROM technical_indicators")
        indicators_count = cursor.fetchone()[0]

        conn.close()

        return {
            "price_data": {
                "total_records": price_data_count,
                "unique_symbols": unique_symbols,
                "latest_update": latest_update,
            },
            "historical_data": {"total_records": historical_data_count},
            "technical_indicators": {"total_records": indicators_count},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving stats: {str(e)}")


# ============================================================================
# TESTING ENDPOINTS
# ============================================================================


@router.post("/test-collection")
async def test_data_collection(
    request: Request, symbols: List[str] = ["BTC", "ETH", "SOL"]
):
    """Test data collection with sample symbols (admin only)."""
    if not is_admin_user(request):
        raise HTTPException(status_code=403, detail="Admin access required")

    try:
        # Test price collection
        price_data = await collect_price_data(symbols)

        # Test historical collection for first symbol
        if symbols:
            historical_data = await collect_historical_data(symbols[0], days=7)
            indicators = await calculate_technical_indicators(symbols[0], days=7)
        else:
            historical_data = []
            indicators = {}

        return {
            "test_results": {
                "price_data_collected": len(price_data),
                "historical_data_collected": len(historical_data),
                "indicators_calculated": bool(indicators),
            },
            "sample_price_data": [
                {
                    "symbol": data.symbol,
                    "price_usd": data.price_usd,
                    "change_24h": data.change_24h,
                }
                for data in price_data[:3]
            ],
            "symbols_tested": symbols,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Test failed: {str(e)}")


@router.get("/info")
async def get_livecoinwatch_info():
    """Get information about LiveCoinWatch integration."""
    return {
        "service": "LiveCoinWatch Data Processor",
        "version": "1.0.0",
        "description": "Real-time cryptocurrency price data collection and analysis",
        "features": [
            "Real-time price data collection",
            "Historical price data",
            "Technical indicators calculation",
            "Database storage and retrieval",
            "Background processing support",
        ],
        "endpoints": [
            "POST /livecoinwatch/collect-prices (admin)",
            "POST /livecoinwatch/collect-historical (admin)",
            "POST /livecoinwatch/calculate-indicators (admin)",
            "GET /livecoinwatch/latest-prices",
            "GET /livecoinwatch/symbol/{symbol}/indicators",
            "GET /livecoinwatch/health",
            "GET /livecoinwatch/stats",
            "POST /livecoinwatch/test-collection (admin)",
        ],
        "supported_indicators": [
            "RSI (Relative Strength Index)",
            "MACD (Moving Average Convergence Divergence)",
            "Bollinger Bands",
            "Simple Moving Averages (SMA 20, 50)",
            "Volatility calculation",
        ],
        "database_tables": ["price_data", "historical_data", "technical_indicators"],
    }
