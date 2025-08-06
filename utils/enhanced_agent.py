#!/usr/bin/env python3
"""
Enhanced Agent Decision Engine
Combines portfolio analysis with market data and news sentiment for intelligent recommendations.
"""

import os
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel, Field
from enum import Enum
import httpx

# Local imports
from utils.binance_client import PortfolioData, PortfolioAsset
from utils.news_sentiment import (
    get_market_sentiment,
    get_market_context,
    NewsSentiment,
    MarketContext,
)
from utils.openai_utils import get_openai_client


class ActionType(str, Enum):
    """Types of actions the agent can recommend."""

    HOLD = "HOLD"
    BUY = "BUY"
    SELL = "SELL"
    REBALANCE = "REBALANCE"
    TAKE_PROFIT = "TAKE_PROFIT"
    STOP_LOSS = "STOP_LOSS"


class RiskLevel(str, Enum):
    """Risk levels for recommendations."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class MarketRegime(str, Enum):
    """Market regime classifications."""

    BULL = "BULL"
    BEAR = "BEAR"
    SIDEWAYS = "SIDEWAYS"
    VOLATILE = "VOLATILE"


class MarketData(BaseModel):
    """Market data for analysis."""

    symbol: str
    current_price: float
    price_change_24h: float
    price_change_percent_24h: float
    volume_24h: float
    market_cap: Optional[float] = None
    rsi: Optional[float] = None
    sentiment_score: Optional[float] = None


# Remove duplicate NewsSentiment class - using the one from news_sentiment module


class PortfolioAnalysis(BaseModel):
    """Enhanced portfolio analysis."""

    total_value: float
    total_cost_basis: float
    total_roi_percentage: float
    portfolio_risk_score: float
    market_regime: MarketRegime
    top_performers: List[str]
    underperformers: List[str]
    diversification_score: float
    liquidity_score: float
    rebalancing_needed: bool
    risk_adjustment_needed: bool
    market_data: Dict[str, MarketData]
    news_sentiment: Optional[NewsSentiment] = None


class Recommendation(BaseModel):
    """Enhanced recommendation with market context."""

    action_type: ActionType
    asset: str
    quantity: Optional[float] = None
    percentage: Optional[float] = None
    reason: str
    confidence_score: float
    risk_level: RiskLevel
    expected_impact: str
    personal_context: str
    market_context: str
    execution_priority: int
    market_data: Optional[MarketData] = None
    news_context: Optional[str] = None


class AgentAnalysis(BaseModel):
    """Complete enhanced agent analysis."""

    portfolio_analysis: PortfolioAnalysis
    recommendations: List[Recommendation]
    market_summary: str
    risk_assessment: str
    next_actions: List[str]
    confidence_overall: float
    timestamp: datetime
    agent_insights: str


class EnhancedAgentEngine:
    """Enhanced agent with market data and news integration."""

    def __init__(self):
        self.openai_client = get_openai_client()

    async def get_market_data(
        self, symbols: Optional[List[str]]
    ) -> Dict[str, MarketData]:
        """Fetch real-time market data for symbols using LiveCoinWatch."""
        market_data = {}

        try:
            # Use LiveCoinWatch as primary source
            from utils.livecoinwatch_processor import get_latest_prices, calculate_technical_indicators
            
            if not symbols:
                return {}

            # Get real-time prices from LiveCoinWatch
            latest_prices = await get_latest_prices(symbols)
            
            for symbol in symbols:
                if symbol in latest_prices:
                    price_data = latest_prices[symbol]
                    
                    # Get technical indicators
                    try:
                        indicators = await calculate_technical_indicators(symbol, days=30)
                        rsi = indicators.get("rsi", 50.0)
                    except Exception:
                        rsi = 50.0  # Fallback
                    
                    market_data[symbol] = MarketData(
                        symbol=symbol,
                        current_price=price_data.price_usd,
                        price_change_24h=price_data.change_24h,
                        price_change_percent_24h=getattr(price_data, 'change_24h_percent', 0.0),
                        volume_24h=price_data.volume_24h,
                        market_cap=price_data.market_cap,
                        rsi=rsi,
                        sentiment_score=self._calculate_sentiment_score_livecoinwatch(price_data),
                    )
                    
        except Exception as e:
            print(f"Error fetching LiveCoinWatch market data: {e}")
            
            # Fallback: Try to get basic data without technical indicators
            try:
                if symbols:  # Check if symbols is not None
                    for symbol in symbols:
                        market_data[symbol] = MarketData(
                            symbol=symbol,
                            current_price=0.0,  # No data available
                            price_change_24h=0.0,
                            price_change_percent_24h=0.0,
                            volume_24h=0.0,
                            market_cap=None,
                            rsi=50.0,
                            sentiment_score=0.0,
                        )
            except Exception as fallback_error:
                print(f"Fallback market data also failed: {fallback_error}")

        return market_data

    async def get_news_sentiment(
        self, symbols: Optional[List[str]] = None
    ) -> Optional[NewsSentiment]:
        """Fetch and analyze news sentiment using the news sentiment module."""
        try:
            from utils.news_sentiment import get_market_sentiment

            sentiment = await get_market_sentiment(symbols if symbols else [])
            return sentiment
        except Exception as e:
            print(f"Error fetching news sentiment: {e}")
            return None

    def _calculate_rsi(self, ticker: Dict[str, Any]) -> float:
        """Calculate simplified RSI based on price change."""
        price_change = float(ticker["priceChangePercent"])

        # Simplified RSI calculation
        if price_change > 5:
            return 70.0  # Overbought
        elif price_change < -5:
            return 30.0  # Oversold
        else:
            return 50.0  # Neutral

    def _calculate_sentiment_score(self, ticker: Dict[str, Any]) -> float:
        """Calculate sentiment score based on price action."""
        price_change = float(ticker["priceChangePercent"])
        volume_change = float(ticker.get("volume", 0))

        # Simple sentiment calculation
        if price_change > 2 and volume_change > 1000000:
            return 0.7  # Positive
        elif price_change < -2:
            return -0.3  # Negative
        else:
            return 0.0  # Neutral

    def _calculate_sentiment_score_livecoinwatch(self, price_data) -> float:
        """Calculate sentiment score based on LiveCoinWatch price data."""
        try:
            price_change = price_data.change_24h_percent if hasattr(price_data, 'change_24h_percent') else 0.0
            volume = price_data.volume_24h if hasattr(price_data, 'volume_24h') else 0.0

            # Simple sentiment calculation
            if price_change > 2 and volume > 1000000:
                return 0.7  # Positive
            elif price_change < -2:
                return -0.3  # Negative
            else:
                return 0.0  # Neutral
        except Exception:
            return 0.0  # Neutral if calculation fails

    def analyze_portfolio(
        self, portfolio_data: PortfolioData, market_data: Dict[str, MarketData]
    ) -> PortfolioAnalysis:
        """Analyze portfolio with market data."""

        total_value = portfolio_data.total_value_usdt
        total_cost_basis = portfolio_data.total_cost_basis
        total_roi = portfolio_data.total_roi_percentage

        # Determine market regime
        if total_roi > 10:
            market_regime = MarketRegime.BULL
        elif total_roi < -10:
            market_regime = MarketRegime.BEAR
        else:
            market_regime = MarketRegime.SIDEWAYS

        # Calculate risk score
        risk_score = self._calculate_risk_score(portfolio_data, market_data)

        # Identify top performers and underperformers
        top_performers = []
        underperformers = []

        for asset in portfolio_data.assets:
            if asset.asset in market_data:
                market_info = market_data[asset.asset]
                if market_info.price_change_percent_24h > 5:
                    top_performers.append(asset.asset)
                elif market_info.price_change_percent_24h < -5:
                    underperformers.append(asset.asset)

        # Calculate diversification score
        diversification_score = self._calculate_diversification_score(portfolio_data)

        # Determine if rebalancing is needed
        rebalancing_needed = len(top_performers) > 0 or len(underperformers) > 0

        return PortfolioAnalysis(
            total_value=total_value,
            total_cost_basis=total_cost_basis,
            total_roi_percentage=total_roi,
            portfolio_risk_score=risk_score,
            market_regime=market_regime,
            top_performers=top_performers,
            underperformers=underperformers,
            diversification_score=diversification_score,
            liquidity_score=0.7,  # Simplified
            rebalancing_needed=rebalancing_needed,
            risk_adjustment_needed=risk_score > 0.7,
            market_data=market_data,
        )

    def generate_recommendations(
        self, analysis: PortfolioAnalysis, portfolio_data: PortfolioData
    ) -> List[Recommendation]:
        """Generate intelligent recommendations based on analysis."""
        recommendations = []

        # Portfolio-level recommendation
        if analysis.rebalancing_needed:
            recommendations.append(
                Recommendation(
                    action_type=ActionType.REBALANCE,
                    asset="PORTFOLIO",
                    reason="Portfolio rebalancing recommended due to performance divergence",
                    confidence_score=0.8,
                    risk_level=RiskLevel.MEDIUM,
                    expected_impact="Optimize portfolio allocation and risk management",
                    personal_context=f"Your portfolio shows {len(analysis.top_performers)} top performers and {len(analysis.underperformers)} underperformers",
                    market_context=f"Market regime: {analysis.market_regime.value}",
                    execution_priority=1,
                )
            )

        # Asset-specific recommendations
        for asset in portfolio_data.assets:
            if asset.asset in analysis.market_data:
                market_info = analysis.market_data[asset.asset]

                # RSI-based recommendations
                if market_info.rsi and market_info.rsi > 70:
                    recommendations.append(
                        Recommendation(
                            action_type=ActionType.TAKE_PROFIT,
                            asset=asset.asset,
                            percentage=25.0,
                            reason=f"{asset.asset} showing overbought conditions (RSI: {market_info.rsi:.1f})",
                            confidence_score=0.7,
                            risk_level=RiskLevel.MEDIUM,
                            expected_impact="Lock in profits on overbought asset",
                            personal_context=f"Your {asset.asset} position may be ready for profit taking",
                            market_context=f"{asset.asset} up {market_info.price_change_percent_24h:.1f}% in 24h",
                            execution_priority=2,
                            market_data=market_info,
                        )
                    )

                elif market_info.rsi and market_info.rsi < 30:
                    recommendations.append(
                        Recommendation(
                            action_type=ActionType.BUY,
                            asset=asset.asset,
                            reason=f"{asset.asset} showing oversold conditions (RSI: {market_info.rsi:.1f})",
                            confidence_score=0.6,
                            risk_level=RiskLevel.HIGH,
                            expected_impact="Potential buying opportunity for oversold asset",
                            personal_context=f"Consider adding to your {asset.asset} position",
                            market_context=f"{asset.asset} down {market_info.price_change_percent_24h:.1f}% in 24h",
                            execution_priority=3,
                            market_data=market_info,
                        )
                    )

        # Default HOLD recommendation if no specific actions
        if not recommendations:
            recommendations.append(
                Recommendation(
                    action_type=ActionType.HOLD,
                    asset="PORTFOLIO",
                    reason="Portfolio is well-positioned for current market conditions",
                    confidence_score=0.7,
                    risk_level=RiskLevel.LOW,
                    expected_impact="Maintain current positions and monitor market developments",
                    personal_context="Your portfolio shows stable performance",
                    market_context=f"Market regime: {analysis.market_regime.value}",
                    execution_priority=1,
                )
            )

        return recommendations

    def _calculate_risk_score(
        self, portfolio_data: PortfolioData, market_data: Dict[str, MarketData]
    ) -> float:
        """Calculate portfolio risk score."""
        risk_score = 0.5  # Base risk score

        # Adjust based on market volatility
        for asset in portfolio_data.assets:
            if asset.asset in market_data:
                market_info = market_data[asset.asset]
                if abs(market_info.price_change_percent_24h) > 10:
                    risk_score += 0.2
                elif abs(market_info.price_change_percent_24h) > 5:
                    risk_score += 0.1

        return min(risk_score, 1.0)

    def _calculate_diversification_score(self, portfolio_data: PortfolioData) -> float:
        """Calculate portfolio diversification score."""
        if not portfolio_data.assets:
            return 0.0

        # Simple diversification based on number of assets
        num_assets = len(portfolio_data.assets)
        if num_assets >= 5:
            return 0.9
        elif num_assets >= 3:
            return 0.7
        elif num_assets >= 2:
            return 0.5
        else:
            return 0.3

    async def generate_complete_analysis(
        self, portfolio_data: PortfolioData, symbols: Optional[List[str]] = None
    ) -> AgentAnalysis:
        """Generate complete enhanced analysis."""

        # Get symbols to analyze
        if not symbols:
            symbols = [asset.asset for asset in portfolio_data.assets]

        # Fetch market data and news sentiment
        market_data = await self.get_market_data(symbols if symbols else [])
        news_sentiment = await self.get_news_sentiment(symbols if symbols else [])

        # Analyze portfolio
        analysis = self.analyze_portfolio(portfolio_data, market_data)
        if news_sentiment:
            analysis.news_sentiment = news_sentiment

        # Generate recommendations
        recommendations = self.generate_recommendations(analysis, portfolio_data)

        # Generate summaries
        market_summary = self._generate_market_summary(analysis)
        risk_assessment = self._generate_risk_assessment(analysis, recommendations)
        next_actions = self._generate_next_actions(recommendations)
        agent_insights = self._generate_agent_insights(analysis, recommendations)

        return AgentAnalysis(
            portfolio_analysis=analysis,
            recommendations=recommendations,
            market_summary=market_summary,
            risk_assessment=risk_assessment,
            next_actions=next_actions,
            confidence_overall=0.75,
            timestamp=datetime.now(timezone.utc),
            agent_insights=agent_insights,
        )

    def _generate_market_summary(self, analysis: PortfolioAnalysis) -> str:
        """Generate market summary."""
        summary = f"Market Analysis: {analysis.market_regime.value} market conditions. "
        summary += f"Portfolio ROI: {analysis.total_roi_percentage:.1f}%. "

        if analysis.news_sentiment:
            summary += f"News sentiment: {analysis.news_sentiment.overall_sentiment}. "

        if analysis.top_performers:
            summary += f"Top performers: {', '.join(analysis.top_performers)}. "

        if analysis.underperformers:
            summary += f"Underperformers: {', '.join(analysis.underperformers)}. "

        return summary

    def _generate_risk_assessment(
        self, analysis: PortfolioAnalysis, recommendations: List[Recommendation]
    ) -> str:
        """Generate risk assessment."""
        risk_text = f"Portfolio risk: {analysis.portfolio_risk_score:.2f}/1.0. "

        if analysis.portfolio_risk_score > 0.7:
            risk_text += "High risk detected - consider reducing exposure. "
        elif analysis.portfolio_risk_score > 0.5:
            risk_text += "Moderate risk - monitor positions closely. "
        else:
            risk_text += "Low risk - portfolio is well-balanced. "

        return risk_text

    def _generate_next_actions(
        self, recommendations: List[Recommendation]
    ) -> List[str]:
        """Generate next actions list."""
        actions = []
        for rec in recommendations[:3]:  # Limit to top 3
            actions.append(f"{rec.action_type.value} {rec.asset}")
        return actions

    def _generate_agent_insights(
        self, analysis: PortfolioAnalysis, recommendations: List[Recommendation]
    ) -> str:
        """Generate agent insights."""
        insights = f"Portfolio value: ${analysis.total_value:,.2f} "

        if analysis.total_roi_percentage > 0:
            insights += f"with {analysis.total_roi_percentage:.1f}% gains. "
        else:
            insights += f"with {abs(analysis.total_roi_percentage):.1f}% losses. "

        if recommendations:
            primary_action = recommendations[0]
            insights += f"Primary recommendation: {primary_action.action_type.value} {primary_action.asset} "
            insights += f"({primary_action.confidence_score:.0%} confidence). "

        return insights


# Global instance
_enhanced_agent = None


def get_enhanced_agent() -> EnhancedAgentEngine:
    """Get or create enhanced agent instance."""
    global _enhanced_agent
    if _enhanced_agent is None:
        _enhanced_agent = EnhancedAgentEngine()
    return _enhanced_agent


async def generate_enhanced_agent_analysis(
    portfolio_data: PortfolioData, symbols: Optional[List[str]] = None
) -> AgentAnalysis:
    """Generate enhanced agent analysis."""
    agent = get_enhanced_agent()
    return await agent.generate_complete_analysis(portfolio_data, symbols)
