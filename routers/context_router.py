#!/usr/bin/env python3
"""
Context Router
Provides enhanced context data to frontend UI including portfolio insights and market analysis.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel

# Import enhanced context utilities
from utils.enhanced_context_rag import get_portfolio_context, get_symbol_context
from utils.intelligent_news_cache import (
    get_portfolio_news,
    get_cache_statistics,
    clear_expired_cache,
)

router = APIRouter(prefix="/context", tags=["context"])


# Pydantic models for API responses
class PortfolioInsightResponse(BaseModel):
    """Portfolio insight response model."""

    symbol: str
    insight_type: str
    title: str
    description: str
    confidence_score: float
    actionable: bool
    recommended_action: Optional[str] = None
    supporting_data: Optional[Dict[str, Any]] = None
    timestamp: str


class TradingOpportunityResponse(BaseModel):
    """Trading opportunity response model."""

    symbol: str
    opportunity_type: str
    description: str
    confidence_score: float
    risk_level: str
    recommended_action: str
    supporting_evidence: List[str]
    timestamp: str


class MarketContextResponse(BaseModel):
    """Market context response model."""

    market_summary: str
    key_trends: List[str]
    market_sentiment: str
    risk_factors: List[str]
    opportunities: List[str]
    recent_news_count: int
    analysis_timestamp: str


class RiskAssessmentResponse(BaseModel):
    """Risk assessment response model."""

    overall_risk_level: str
    risk_factors: List[str]
    risk_score: float
    recommendations: List[str]
    diversification_score: float
    concentration_risk: Dict[str, Any]
    assessment_timestamp: str


class PortfolioContextResponse(BaseModel):
    """Complete portfolio context response model."""

    portfolio_summary: Dict[str, Any]
    portfolio_insights: List[PortfolioInsightResponse]
    market_context: MarketContextResponse
    trading_opportunities: List[TradingOpportunityResponse]
    risk_assessment: RiskAssessmentResponse
    news_sentiment: Dict[str, Any]
    timestamp: str


# ============================================================================
# PORTFOLIO CONTEXT ENDPOINTS
# ============================================================================


@router.get("/portfolio", response_model=PortfolioContextResponse)
async def get_comprehensive_portfolio_context(
    include_news: bool = True,
    include_analysis: bool = True,
    include_opportunities: bool = True,
) -> PortfolioContextResponse:
    """Get comprehensive portfolio context for frontend UI."""
    try:
        context_data = await get_portfolio_context(
            include_news=include_news,
            include_analysis=include_analysis,
            include_opportunities=include_opportunities,
        )

        if "error" in context_data:
            raise HTTPException(status_code=500, detail=context_data["error"])

        return PortfolioContextResponse(**context_data)

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error getting portfolio context: {str(e)}"
        )


@router.get("/portfolio/summary")
async def get_portfolio_summary() -> Dict[str, Any]:
    """Get portfolio summary only."""
    try:
        context_data = await get_portfolio_context(
            include_news=False, include_analysis=False, include_opportunities=False
        )

        if "error" in context_data:
            raise HTTPException(status_code=500, detail=context_data["error"])

        return {
            "portfolio_summary": context_data["portfolio_summary"],
            "timestamp": context_data["timestamp"],
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error getting portfolio summary: {str(e)}"
        )


@router.get("/portfolio/insights", response_model=List[PortfolioInsightResponse])
async def get_portfolio_insights() -> List[PortfolioInsightResponse]:
    """Get portfolio insights only."""
    try:
        context_data = await get_portfolio_context(
            include_news=False, include_analysis=True, include_opportunities=False
        )

        if "error" in context_data:
            raise HTTPException(status_code=500, detail=context_data["error"])

        return [
            PortfolioInsightResponse(**insight)
            for insight in context_data["portfolio_insights"]
        ]

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error getting portfolio insights: {str(e)}"
        )


@router.get("/portfolio/opportunities", response_model=List[TradingOpportunityResponse])
async def get_trading_opportunities() -> List[TradingOpportunityResponse]:
    """Get trading opportunities only."""
    try:
        context_data = await get_portfolio_context(
            include_news=False, include_analysis=False, include_opportunities=True
        )

        if "error" in context_data:
            raise HTTPException(status_code=500, detail=context_data["error"])

        return [
            TradingOpportunityResponse(**opp)
            for opp in context_data["trading_opportunities"]
        ]

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error getting trading opportunities: {str(e)}"
        )


@router.get("/portfolio/risk", response_model=RiskAssessmentResponse)
async def get_risk_assessment() -> RiskAssessmentResponse:
    """Get portfolio risk assessment only."""
    try:
        context_data = await get_portfolio_context(
            include_news=False, include_analysis=True, include_opportunities=False
        )

        if "error" in context_data:
            raise HTTPException(status_code=500, detail=context_data["error"])

        return RiskAssessmentResponse(**context_data["risk_assessment"])

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error getting risk assessment: {str(e)}"
        )


@router.get("/portfolio/sentiment")
async def get_news_sentiment() -> Dict[str, Any]:
    """Get news sentiment analysis only."""
    try:
        context_data = await get_portfolio_context(
            include_news=True, include_analysis=False, include_opportunities=False
        )

        if "error" in context_data:
            raise HTTPException(status_code=500, detail=context_data["error"])

        return context_data["news_sentiment"]

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error getting news sentiment: {str(e)}"
        )


# ============================================================================
# SYMBOL CONTEXT ENDPOINTS
# ============================================================================


@router.get("/symbol/{symbol}")
async def get_symbol_context(symbol: str) -> Dict[str, Any]:
    """Get detailed context for a specific symbol."""
    try:
        from utils.enhanced_context_rag import get_symbol_context

        context_data = await get_symbol_context(symbol)

        if "error" in context_data:
            raise HTTPException(status_code=500, detail=context_data["error"])

        return context_data

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error getting symbol context: {str(e)}"
        )


@router.get("/symbol/{symbol}/analysis")
async def get_symbol_analysis(symbol: str) -> Dict[str, Any]:
    """Get AI analysis for a specific symbol."""
    try:
        from utils.enhanced_context_rag import get_symbol_context

        context_data = await get_symbol_context(symbol)

        if "error" in context_data:
            raise HTTPException(status_code=500, detail=context_data["error"])

        return {
            "symbol": symbol,
            "analysis": context_data.get("analysis", {}),
            "recommendations": context_data.get("recommendations", []),
            "sentiment": context_data.get("sentiment", "neutral"),
            "confidence_score": context_data.get("confidence_score", 0.0),
            "timestamp": context_data.get("timestamp"),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error getting symbol analysis: {str(e)}"
        )


@router.get("/symbol/{symbol}/news")
async def get_symbol_news(symbol: str, hours_back: int = 24) -> Dict[str, Any]:
    """Get news for a specific symbol."""
    try:
        from utils.intelligent_news_cache import get_cached_news_for_symbols

        news_data = await get_cached_news_for_symbols([symbol], hours_back=hours_back)

        return {
            "symbol": symbol,
            "news_count": len(news_data),
            "articles": news_data,
            "hours_back": hours_back,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error getting symbol news: {str(e)}"
        )


# ============================================================================
# NEWS CONTEXT ENDPOINTS
# ============================================================================


@router.get("/news/portfolio")
async def get_portfolio_news(
    include_alpha_portfolio: bool = True,
    include_opportunity_tokens: bool = True,
    include_personal_portfolio: bool = True,
    hours_back: int = 24,
) -> Dict[str, Any]:
    """Get portfolio-aware news with intelligent caching."""
    try:
        news_data = await get_portfolio_news(
            include_alpha_portfolio=include_alpha_portfolio,
            include_opportunity_tokens=include_opportunity_tokens,
            include_personal_portfolio=include_personal_portfolio,
            hours_back=hours_back,
        )

        return news_data

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error getting portfolio news: {str(e)}"
        )


@router.get("/news/cache/stats")
async def get_news_cache_statistics() -> Dict[str, Any]:
    """Get news cache statistics."""
    try:
        stats = get_cache_statistics()
        return {
            "cache_statistics": stats,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error getting cache statistics: {str(e)}"
        )


@router.post("/news/cache/clear")
async def clear_news_cache(background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """Clear expired news cache entries."""
    try:
        background_tasks.add_task(clear_expired_cache)

        return {
            "message": "Cache cleanup initiated",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing cache: {str(e)}")


# ============================================================================
# MARKET CONTEXT ENDPOINTS
# ============================================================================


@router.get("/market/overview", response_model=MarketContextResponse)
async def get_market_overview() -> MarketContextResponse:
    """Get market overview and analysis."""
    try:
        context_data = await get_portfolio_context(
            include_news=False, include_analysis=True, include_opportunities=False
        )

        if "error" in context_data:
            raise HTTPException(status_code=500, detail=context_data["error"])

        return MarketContextResponse(**context_data["market_context"])

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error getting market overview: {str(e)}"
        )


@router.get("/market/trends")
async def get_market_trends() -> Dict[str, Any]:
    """Get current market trends."""
    try:
        context_data = await get_portfolio_context(
            include_news=False, include_analysis=True, include_opportunities=False
        )

        if "error" in context_data:
            raise HTTPException(status_code=500, detail=context_data["error"])

        market_context = context_data["market_context"]

        return {
            "key_trends": market_context.get("key_trends", []),
            "market_sentiment": market_context.get("market_sentiment", "neutral"),
            "risk_factors": market_context.get("risk_factors", []),
            "opportunities": market_context.get("opportunities", []),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error getting market trends: {str(e)}"
        )


# ============================================================================
# UTILITY ENDPOINTS
# ============================================================================


@router.get("/health")
async def context_health_check() -> Dict[str, Any]:
    """Health check for context system."""
    try:
        # Test basic functionality
        summary = await get_portfolio_context(
            include_news=False, include_analysis=False, include_opportunities=False
        )

        return {
            "status": "healthy",
            "service": "Enhanced Context RAG System",
            "version": "1.0.0",
            "portfolio_available": "error" not in summary,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "Enhanced Context RAG System",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


@router.get("/info")
async def get_context_info() -> Dict[str, Any]:
    """Get information about the context system."""
    return {
        "service": "Enhanced Context RAG System",
        "version": "1.0.0",
        "description": "Provides portfolio insights, market analysis, and trading opportunities",
        "features": [
            "Portfolio context and insights",
            "Market analysis and trends",
            "Trading opportunities identification",
            "Risk assessment",
            "News sentiment analysis",
            "Symbol-specific analysis",
            "Intelligent news caching",
        ],
        "endpoints": [
            "/context/portfolio",
            "/context/portfolio/insights",
            "/context/portfolio/opportunities",
            "/context/portfolio/risk",
            "/context/symbol/{symbol}",
            "/context/news/portfolio",
            "/context/market/overview",
        ],
        "cache_duration": "24 hours",
        "supported_symbols": [
            "BTC",
            "ETH",
            "XRP",
            "SOL",
            "DOGE",
            "AVAX",
            "ADA",
            "DOT",
            "LINK",
            "MATIC",
        ],
    }
