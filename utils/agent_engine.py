#!/usr/bin/env python3
"""
Agent Decision Engine
The core intelligence system that provides personalized, actionable recommendations
based on real portfolio data, cost basis, and market conditions.
"""

import os
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone
from pydantic import BaseModel, Field
from enum import Enum
import json

# LangChain imports
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import BaseOutputParser
from langchain_core.output_parsers import JsonOutputParser

# Local imports
from utils.binance_client import PortfolioData, PortfolioAsset
from utils.milvus import query_news_for_symbols
from utils.cost_tracker import track_openai_call

# Environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


class ActionType(str, Enum):
    """Types of actions the agent can recommend."""

    HOLD = "HOLD"
    BUY = "BUY"
    SELL = "SELL"
    REBALANCE = "REBALANCE"
    DCA = "DCA"  # Dollar Cost Average
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


class PortfolioAnalysis(BaseModel):
    """Analysis of portfolio performance and risk."""

    total_value: float
    total_cost_basis: float
    total_roi_percentage: float
    portfolio_risk_score: float  # 0-1 scale
    market_regime: MarketRegime
    top_performers: List[str]
    underperformers: List[str]
    diversification_score: float  # 0-1 scale
    liquidity_score: float  # 0-1 scale
    rebalancing_needed: bool
    risk_adjustment_needed: bool


class Recommendation(BaseModel):
    """Individual recommendation with confidence and context."""

    action_type: ActionType
    asset: str
    quantity: Optional[float] = None
    percentage: Optional[float] = None
    reason: str
    confidence_score: float  # 0-1 scale
    risk_level: RiskLevel
    expected_impact: str
    personal_context: str  # Personal ROI, cost basis context
    market_context: str  # Market conditions, news sentiment
    execution_priority: int  # 1-5 scale (1 = highest priority)


class AgentAnalysis(BaseModel):
    """Complete agent analysis and recommendations."""

    portfolio_analysis: PortfolioAnalysis
    recommendations: List[Recommendation]
    market_summary: str
    risk_assessment: str
    next_actions: List[str]
    confidence_overall: float
    timestamp: datetime


class AgentDecisionEngine:
    """Core agent that analyzes portfolio and generates personalized recommendations."""

    def __init__(self):
        if not OPENAI_API_KEY:
            print("⚠️ OpenAI API key not configured - using fallback agent")
            self.llm = None
        else:
            self.llm = ChatOpenAI(
                model="gpt-4-turbo", temperature=0.1, api_key=OPENAI_API_KEY
            )
        self.analysis_prompt = self._create_analysis_prompt()
        self.recommendation_prompt = self._create_recommendation_prompt()
        self.parser = JsonOutputParser()

    def _create_analysis_prompt(self) -> ChatPromptTemplate:
        """Create prompt for portfolio analysis."""
        return ChatPromptTemplate.from_template(
            """
You are an expert crypto portfolio analyst. Analyze the following portfolio data and provide insights.

PORTFOLIO DATA:
{portfolio_data}

MARKET NEWS:
{market_news}

TASK: Analyze the portfolio and provide insights on:
1. Overall performance and risk
2. Market regime classification
3. Top performers and underperformers
4. Diversification assessment
5. Rebalancing needs

Return your analysis as JSON with the following structure:
{{
    "total_value": float,
    "total_cost_basis": float,
    "total_roi_percentage": float,
    "portfolio_risk_score": float (0-1),
    "market_regime": "BULL|BEAR|SIDEWAYS|VOLATILE",
    "top_performers": ["asset1", "asset2"],
    "underperformers": ["asset1", "asset2"],
    "diversification_score": float (0-1),
    "liquidity_score": float (0-1),
    "rebalancing_needed": boolean,
    "risk_adjustment_needed": boolean
}}

Focus on data-driven insights and be conservative in risk assessments.
"""
        )

    def _create_recommendation_prompt(self) -> ChatPromptTemplate:
        """Create prompt for generating personalized recommendations."""
        return ChatPromptTemplate.from_template(
            """
You are an expert crypto investment advisor. Generate personalized recommendations based on the portfolio analysis.

PORTFOLIO ANALYSIS:
{portfolio_analysis}

PORTFOLIO DATA:
{portfolio_data}

MARKET NEWS:
{market_news}

TASK: Generate personalized recommendations that consider:
1. Individual asset performance and personal ROI
2. Cost basis and profit/loss positions
3. Market conditions and news sentiment
4. Risk tolerance and portfolio balance
5. Liquidity and execution feasibility

For each recommendation, provide:
- Action type (HOLD, BUY, SELL, REBALANCE, DCA, TAKE_PROFIT, STOP_LOSS)
- Asset symbol
- Quantity or percentage (if applicable)
- Detailed reasoning with personal context
- Confidence score (0-1)
- Risk level (LOW, MEDIUM, HIGH)
- Expected impact
- Personal context (mention cost basis, ROI)
- Market context (news, sentiment)
- Execution priority (1-5, 1=highest)

Return recommendations as JSON array:
[
    {{
        "action_type": "HOLD|BUY|SELL|REBALANCE|DCA|TAKE_PROFIT|STOP_LOSS",
        "asset": "BTC",
        "quantity": 0.1,
        "percentage": null,
        "reason": "Detailed reasoning...",
        "confidence_score": 0.85,
        "risk_level": "LOW|MEDIUM|HIGH",
        "expected_impact": "Expected outcome...",
        "personal_context": "Your BTC position has 45% ROI...",
        "market_context": "BTC showing bullish momentum...",
        "execution_priority": 1
    }}
]

Be specific about personal context (cost basis, ROI) and provide actionable advice.
"""
        )

    async def analyze_portfolio(
        self, portfolio_data: PortfolioData, market_news: List[Dict[str, Any]]
    ) -> PortfolioAnalysis:
        """Analyze portfolio performance and risk."""
        try:
            # Prepare portfolio data for analysis
            portfolio_summary = self._prepare_portfolio_summary(portfolio_data)
            news_summary = self._prepare_news_summary(market_news)

            # Generate analysis using LLM
            chain = self.analysis_prompt | self.llm | self.parser

            analysis_result = await chain.ainvoke(
                {"portfolio_data": portfolio_summary, "market_news": news_summary}
            )

            return PortfolioAnalysis(**analysis_result)

        except Exception as e:
            # Fallback analysis if LLM fails
            return self._fallback_analysis(portfolio_data)

    async def generate_recommendations(
        self,
        portfolio_analysis: PortfolioAnalysis,
        portfolio_data: PortfolioData,
        market_news: List[Dict[str, Any]],
    ) -> List[Recommendation]:
        """Generate personalized recommendations."""
        try:
            # Prepare data for recommendation generation
            analysis_summary = portfolio_analysis.model_dump_json()
            portfolio_summary = self._prepare_portfolio_summary(portfolio_data)
            news_summary = self._prepare_news_summary(market_news)

            # Generate recommendations using LLM
            chain = self.recommendation_prompt | self.llm | self.parser

            recommendations_data = await chain.ainvoke(
                {
                    "portfolio_analysis": analysis_summary,
                    "portfolio_data": portfolio_summary,
                    "market_news": news_summary,
                }
            )

            # Convert to Recommendation objects
            recommendations = [Recommendation(**rec) for rec in recommendations_data]

            # Sort by execution priority
            recommendations.sort(key=lambda x: x.execution_priority)

            return recommendations

        except Exception as e:
            # Fallback recommendations
            return self._fallback_recommendations(portfolio_data)

    async def calculate_confidence(
        self, recommendation: Recommendation, portfolio_data: PortfolioData
    ) -> float:
        """Calculate confidence score for a recommendation."""
        try:
            # Factors that influence confidence:
            # 1. Portfolio data quality
            # 2. Market news relevance
            # 3. Historical accuracy (future enhancement)
            # 4. Risk level alignment

            base_confidence = recommendation.confidence_score

            # Adjust based on data quality
            data_quality_bonus = 0.1 if portfolio_data.total_cost_basis > 0 else -0.1

            # Adjust based on risk level
            risk_adjustment = {
                RiskLevel.LOW: 0.05,
                RiskLevel.MEDIUM: 0.0,
                RiskLevel.HIGH: -0.1,
            }.get(recommendation.risk_level, 0.0)

            final_confidence = min(
                1.0, max(0.0, base_confidence + data_quality_bonus + risk_adjustment)
            )

            return final_confidence

        except Exception as e:
            return 0.5  # Default confidence

    async def generate_complete_analysis(
        self, portfolio_data: PortfolioData, symbols: List[str] = None
    ) -> AgentAnalysis:
        """Generate complete agent analysis with recommendations."""
        try:
            # Get relevant market news
            if symbols is None:
                symbols = [asset.asset for asset in portfolio_data.assets]

            market_news = await query_news_for_symbols(symbols) if symbols else []

            # Analyze portfolio
            portfolio_analysis = await self.analyze_portfolio(
                portfolio_data, market_news
            )

            # Generate recommendations
            recommendations = await self.generate_recommendations(
                portfolio_analysis, portfolio_data, market_news
            )

            # Calculate confidence scores
            for rec in recommendations:
                rec.confidence_score = await self.calculate_confidence(
                    rec, portfolio_data
                )

            # Generate market summary
            market_summary = self._generate_market_summary(
                portfolio_analysis, market_news
            )

            # Generate risk assessment
            risk_assessment = self._generate_risk_assessment(
                portfolio_analysis, recommendations
            )

            # Generate next actions
            next_actions = self._generate_next_actions(recommendations)

            # Calculate overall confidence
            overall_confidence = (
                sum(rec.confidence_score for rec in recommendations)
                / len(recommendations)
                if recommendations
                else 0.0
            )

            return AgentAnalysis(
                portfolio_analysis=portfolio_analysis,
                recommendations=recommendations,
                market_summary=market_summary,
                risk_assessment=risk_assessment,
                next_actions=next_actions,
                confidence_overall=overall_confidence,
                timestamp=datetime.now(timezone.utc),
            )

        except Exception as e:
            raise Exception(f"Error generating complete analysis: {str(e)}")

    def _prepare_portfolio_summary(self, portfolio_data: PortfolioData) -> str:
        """Prepare portfolio data for LLM analysis."""
        summary = f"Total Value: ${portfolio_data.total_value_usdt:,.2f}\n"
        summary += f"Total Cost Basis: ${portfolio_data.total_cost_basis:,.2f}\n"
        summary += f"Total ROI: {portfolio_data.total_roi_percentage:.2f}%\n\n"

        summary += "Assets:\n"
        for asset in portfolio_data.assets:
            roi_text = (
                f"ROI: {asset.roi_percentage:.2f}%"
                if asset.roi_percentage
                else "ROI: N/A"
            )
            cost_basis_text = (
                f"Cost: ${asset.cost_basis:,.2f}" if asset.cost_basis else "Cost: N/A"
            )
            summary += f"- {asset.asset}: {asset.total} units, ${asset.usdt_value:,.2f}, {roi_text}, {cost_basis_text}\n"

        return summary

    def _prepare_news_summary(self, market_news: List[Dict[str, Any]]) -> str:
        """Prepare market news for LLM analysis."""
        if not market_news:
            return "No recent market news available."

        summary = "Recent Market News:\n"
        for i, news in enumerate(market_news[:5], 1):  # Top 5 news items
            title = news.get("title", "No title")
            sentiment = news.get("sentiment", 0.5)
            summary += f"{i}. {title} (Sentiment: {sentiment:.2f})\n"

        return summary

    def _fallback_analysis(self, portfolio_data: PortfolioData) -> PortfolioAnalysis:
        """Fallback analysis when LLM fails."""
        return PortfolioAnalysis(
            total_value=portfolio_data.total_value_usdt,
            total_cost_basis=portfolio_data.total_cost_basis,
            total_roi_percentage=portfolio_data.total_roi_percentage,
            portfolio_risk_score=0.5,
            market_regime=MarketRegime.SIDEWAYS,
            top_performers=[],
            underperformers=[],
            diversification_score=0.5,
            liquidity_score=0.5,
            rebalancing_needed=False,
            risk_adjustment_needed=False,
        )

    def _fallback_recommendations(
        self, portfolio_data: PortfolioData
    ) -> List[Recommendation]:
        """Fallback recommendations when LLM fails."""
        recommendations = []

        for asset in portfolio_data.assets:
            if asset.roi_percentage and asset.roi_percentage > 20:
                recommendations.append(
                    Recommendation(
                        action_type=ActionType.TAKE_PROFIT,
                        asset=asset.asset,
                        percentage=10.0,
                        reason="High ROI position - consider taking some profits",
                        confidence_score=0.6,
                        risk_level=RiskLevel.MEDIUM,
                        expected_impact="Lock in profits while maintaining position",
                        personal_context=f"Your {asset.asset} position has {asset.roi_percentage:.1f}% ROI",
                        market_context="Consider market conditions for optimal timing",
                        execution_priority=2,
                    )
                )

        if not recommendations:
            recommendations.append(
                Recommendation(
                    action_type=ActionType.HOLD,
                    asset="PORTFOLIO",
                    reason="Maintain current positions and monitor market conditions",
                    confidence_score=0.7,
                    risk_level=RiskLevel.LOW,
                    expected_impact="Preserve capital while waiting for better opportunities",
                    personal_context="Portfolio is stable with mixed performance",
                    market_context="Market conditions are uncertain",
                    execution_priority=1,
                )
            )

        return recommendations

    def _generate_market_summary(
        self, analysis: PortfolioAnalysis, news: List[Dict[str, Any]]
    ) -> str:
        """Generate market summary from analysis and news."""
        summary = f"Market Analysis: {analysis.market_regime.value} market conditions detected. "
        summary += f"Portfolio risk score: {analysis.portfolio_risk_score:.2f}. "

        if analysis.top_performers:
            summary += f"Top performers: {', '.join(analysis.top_performers)}. "

        if analysis.underperformers:
            summary += f"Underperformers: {', '.join(analysis.underperformers)}. "

        if analysis.rebalancing_needed:
            summary += "Portfolio rebalancing recommended. "

        return summary

    def _generate_risk_assessment(
        self, analysis: PortfolioAnalysis, recommendations: List[Recommendation]
    ) -> str:
        """Generate risk assessment."""
        risk_summary = (
            f"Overall portfolio risk: {analysis.portfolio_risk_score:.2f}/1.0. "
        )

        high_risk_recs = [r for r in recommendations if r.risk_level == RiskLevel.HIGH]
        if high_risk_recs:
            risk_summary += f"High-risk recommendations: {len(high_risk_recs)}. "

        if analysis.risk_adjustment_needed:
            risk_summary += "Risk adjustment recommended. "

        return risk_summary

    def _generate_next_actions(
        self, recommendations: List[Recommendation]
    ) -> List[str]:
        """Generate list of next actions."""
        actions = []

        for rec in recommendations[:3]:  # Top 3 recommendations
            action_text = f"{rec.action_type.value} {rec.asset}"
            if rec.percentage:
                action_text += f" ({rec.percentage}%)"
            actions.append(action_text)

        return actions


# Global agent instance
agent_engine: Optional[AgentDecisionEngine] = None


def get_agent_engine() -> AgentDecisionEngine:
    """Get or create agent engine instance."""
    global agent_engine

    if agent_engine is None:
        agent_engine = AgentDecisionEngine()

    return agent_engine


async def generate_agent_analysis(
    portfolio_data: PortfolioData, symbols: List[str] = None
) -> AgentAnalysis:
    """Generate complete agent analysis using the global engine."""
    engine = get_agent_engine()
    return await engine.generate_complete_analysis(portfolio_data, symbols)
