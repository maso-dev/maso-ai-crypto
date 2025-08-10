#!/usr/bin/env python3
"""
Portfolio User API Endpoints
Provides user-facing portfolio management and market analysis features.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import httpx
import json

# Import portfolio-specific utilities
from utils.hybrid_rag_fallback import hybrid_search
from utils.openai_utils import get_market_summary
from utils.binance_client import (
    get_portfolio_data,
    PortfolioData,
    PortfolioAsset as BinancePortfolioAsset,
)

router = APIRouter(prefix="/portfolio", tags=["portfolio"])


class MarketSummaryRequest(BaseModel):
    """Request model for market summary."""

    symbols: List[str] = Field(..., description="List of crypto symbols to analyze")
    limit: int = Field(default=10, description="Number of news articles to include")
    always_include_base_coins: bool = Field(
        default=True, description="Always include BTC and ETH in analysis"
    )


class MarketSummaryResponse(BaseModel):
    """Response model for market summary."""

    summary: str
    recommendations: List[str]
    news: List[Dict[str, Any]]
    timestamp: str
    symbols_analyzed: List[str]


class PortfolioAsset(BaseModel):
    """Portfolio asset model."""

    asset: str
    free: float
    locked: float
    total: float
    usdt_value: float


class PortfolioResponse(BaseModel):
    """Portfolio response model."""

    total_value_usdt: float
    assets: List[PortfolioAsset]
    last_updated: str


class ETFComparisonResponse(BaseModel):
    """ETF comparison response model."""

    etfs: List[Dict[str, Any]]
    comparison_date: str


class DetailedPortfolioAsset(BaseModel):
    """Detailed portfolio asset with cost basis and ROI."""

    asset: str
    free: float
    locked: float
    total: float
    usdt_value: float
    cost_basis: Optional[float] = None
    roi_percentage: Optional[float] = None
    avg_buy_price: Optional[float] = None


class DetailedPortfolioResponse(BaseModel):
    """Detailed portfolio response with cost basis analysis."""

    total_value_usdt: float
    total_cost_basis: float
    total_roi_percentage: float
    assets: List[DetailedPortfolioAsset]
    last_updated: str


@router.post("/market_summary", response_model=MarketSummaryResponse)
async def portfolio_market_summary(
    request: MarketSummaryRequest,
) -> MarketSummaryResponse:
    """Get AI-powered market summary for portfolio symbols."""
    try:
        # Ensure base coins are included if requested
        symbols_to_analyze = request.symbols.copy()
        if request.always_include_base_coins:
            if "BTC" not in symbols_to_analyze:
                symbols_to_analyze.append("BTC")
            if "ETH" not in symbols_to_analyze:
                symbols_to_analyze.append("ETH")

        # Get relevant news for the symbols
        news_results = await hybrid_search(
            "crypto news", symbols_to_analyze, limit=request.limit
        )
        news_articles = news_results.get("results", [])

        # Limit news articles
        limited_news = news_articles[: request.limit] if news_articles else []

        # Generate AI market summary
        summary, recommendations = await get_market_summary(
            limited_news, symbols_to_analyze
        )

        # Convert recommendations string to list
        recommendations_list = (
            [rec.strip() for rec in recommendations.split("\n") if rec.strip()]
            if recommendations
            else []
        )

        return MarketSummaryResponse(
            summary=summary,
            recommendations=recommendations_list,
            news=limited_news,
            timestamp=datetime.now(timezone.utc).isoformat(),
            symbols_analyzed=symbols_to_analyze,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error generating market summary: {str(e)}"
        )


@router.get("/assets", response_model=PortfolioResponse)
async def get_portfolio_assets() -> PortfolioResponse:
    """Get user's portfolio assets from Binance."""
    try:
        # Try to get real portfolio data from Binance
        portfolio_data = await get_portfolio_data()

        if portfolio_data:
            # Convert Binance portfolio data to our response format
            assets = [
                PortfolioAsset(
                    asset=asset.asset,
                    free=asset.free,
                    locked=asset.locked,
                    total=asset.total,
                    usdt_value=asset.usdt_value,
                )
                for asset in portfolio_data.assets
            ]

            return PortfolioResponse(
                total_value_usdt=portfolio_data.total_value_usdt,
                assets=assets,
                last_updated=portfolio_data.last_updated.isoformat(),
            )
        else:
            # Fallback to mock data if Binance is not configured
            mock_assets = [
                PortfolioAsset(
                    asset="BTC", free=0.5, locked=0.0, total=0.5, usdt_value=25000.0
                ),
                PortfolioAsset(
                    asset="ETH", free=2.0, locked=0.0, total=2.0, usdt_value=8000.0
                ),
                PortfolioAsset(
                    asset="ADA", free=1000.0, locked=0.0, total=1000.0, usdt_value=500.0
                ),
            ]

            total_value = sum(asset.usdt_value for asset in mock_assets)

            return PortfolioResponse(
                total_value_usdt=total_value,
                assets=mock_assets,
                last_updated=datetime.now(timezone.utc).isoformat(),
            )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving portfolio: {str(e)}"
        )


@router.get("/detailed", response_model=DetailedPortfolioResponse)
async def get_detailed_portfolio() -> DetailedPortfolioResponse:
    """Get detailed portfolio data with cost basis and ROI analysis."""
    try:
        # Get real portfolio data from Binance
        portfolio_data = await get_portfolio_data()

        if portfolio_data:
            # Convert to detailed response format
            assets = [
                DetailedPortfolioAsset(
                    asset=asset.asset,
                    free=asset.free,
                    locked=asset.locked,
                    total=asset.total,
                    usdt_value=asset.usdt_value,
                    cost_basis=asset.cost_basis,
                    roi_percentage=asset.roi_percentage,
                    avg_buy_price=asset.avg_buy_price,
                )
                for asset in portfolio_data.assets
            ]

            return DetailedPortfolioResponse(
                total_value_usdt=portfolio_data.total_value_usdt,
                total_cost_basis=portfolio_data.total_cost_basis,
                total_roi_percentage=portfolio_data.total_roi_percentage,
                assets=assets,
                last_updated=portfolio_data.last_updated.isoformat(),
            )
        else:
            # Fallback with mock data (no cost basis)
            mock_assets = [
                DetailedPortfolioAsset(
                    asset="BTC",
                    free=0.5,
                    locked=0.0,
                    total=0.5,
                    usdt_value=25000.0,
                    cost_basis=None,
                    roi_percentage=None,
                    avg_buy_price=None,
                ),
                DetailedPortfolioAsset(
                    asset="ETH",
                    free=2.0,
                    locked=0.0,
                    total=2.0,
                    usdt_value=8000.0,
                    cost_basis=None,
                    roi_percentage=None,
                    avg_buy_price=None,
                ),
            ]

            return DetailedPortfolioResponse(
                total_value_usdt=33000.0,
                total_cost_basis=0.0,
                total_roi_percentage=0.0,
                assets=mock_assets,
                last_updated=datetime.now(timezone.utc).isoformat(),
            )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving detailed portfolio: {str(e)}"
        )


@router.get("/etf-comparison", response_model=ETFComparisonResponse)
async def get_etf_comparison() -> ETFComparisonResponse:
    """Get ETF comparison data."""
    try:
        # Mock ETF data
        etfs = [
            {
                "symbol": "BITO",
                "name": "ProShares Bitcoin Strategy ETF",
                "price": 25.50,
                "change_24h": 2.5,
                "volume": 1500000,
                "aum": 850000000,
            },
            {
                "symbol": "BITX",
                "name": "Volatility Shares 2x Bitcoin Strategy ETF",
                "price": 12.75,
                "change_24h": -1.2,
                "volume": 750000,
                "aum": 320000000,
            },
            {
                "symbol": "XBTF",
                "name": "VanEck Bitcoin Strategy ETF",
                "price": 18.90,
                "change_24h": 1.8,
                "volume": 950000,
                "aum": 450000000,
            },
        ]

        return ETFComparisonResponse(
            etfs=etfs, comparison_date=datetime.now(timezone.utc).isoformat()
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving ETF comparison: {str(e)}"
        )


@router.get("/performance")
async def get_portfolio_performance() -> Dict[str, Any]:
    """Get portfolio performance metrics."""
    try:
        # Mock performance data
        return {
            "total_return_24h": 2.5,
            "total_return_7d": 8.2,
            "total_return_30d": 15.7,
            "best_performer": "BTC",
            "worst_performer": "ADA",
            "volatility": 12.3,
            "sharpe_ratio": 1.8,
            "last_updated": datetime.now(timezone.utc).isoformat(),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving performance: {str(e)}"
        )


@router.get("/alerts")
async def get_portfolio_alerts() -> Dict[str, Any]:
    """Get portfolio alerts and notifications."""
    try:
        # Mock alerts
        alerts = [
            {
                "type": "price_alert",
                "symbol": "BTC",
                "message": "Bitcoin price dropped below $50,000",
                "severity": "medium",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
            {
                "type": "portfolio_alert",
                "symbol": "ETH",
                "message": "Ethereum allocation exceeds 40%",
                "severity": "low",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        ]

        return {"alerts": alerts, "total_alerts": len(alerts), "unread_count": 2}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving alerts: {str(e)}"
        )
