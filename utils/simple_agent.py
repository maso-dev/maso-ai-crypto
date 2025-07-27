#!/usr/bin/env python3
"""
Simple Agent Decision Engine
A simplified version that provides personalized recommendations without complex dependencies.
"""

import os
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field
from enum import Enum

# Local imports
from utils.binance_client import PortfolioData, PortfolioAsset

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

class PortfolioAnalysis(BaseModel):
    """Analysis of portfolio performance and risk."""
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

class Recommendation(BaseModel):
    """Individual recommendation with confidence and context."""
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

class AgentAnalysis(BaseModel):
    """Complete agent analysis and recommendations."""
    portfolio_analysis: PortfolioAnalysis
    recommendations: List[Recommendation]
    market_summary: str
    risk_assessment: str
    next_actions: List[str]
    confidence_overall: float
    timestamp: datetime

class SimpleAgentEngine:
    """Simple agent that provides rule-based recommendations."""
    
    def __init__(self):
        pass
    
    def analyze_portfolio(self, portfolio_data: PortfolioData) -> PortfolioAnalysis:
        """Analyze portfolio using simple rules."""
        
        # Calculate basic metrics
        total_value = portfolio_data.total_value_usdt
        total_cost_basis = portfolio_data.total_cost_basis
        total_roi = portfolio_data.total_roi_percentage
        
        # Determine market regime based on overall performance
        if total_roi > 10:
            market_regime = MarketRegime.BULL
        elif total_roi < -10:
            market_regime = MarketRegime.BEAR
        else:
            market_regime = MarketRegime.SIDEWAYS
        
        # Calculate risk score based on volatility and concentration
        risk_score = self._calculate_risk_score(portfolio_data)
        
        # Identify top and under performers
        top_performers = []
        underperformers = []
        
        for asset in portfolio_data.assets:
            if asset.roi_percentage and asset.roi_percentage > 20:
                top_performers.append(asset.asset)
            elif asset.roi_percentage and asset.roi_percentage < -20:
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
            liquidity_score=0.7,  # Assume good liquidity
            rebalancing_needed=rebalancing_needed,
            risk_adjustment_needed=risk_score > 0.7
        )
    
    def generate_recommendations(self, analysis: PortfolioAnalysis, portfolio_data: PortfolioData) -> List[Recommendation]:
        """Generate recommendations based on analysis."""
        recommendations = []
        
        # High ROI positions - consider taking profits
        for asset in portfolio_data.assets:
            if asset.roi_percentage and asset.roi_percentage > 30:
                recommendations.append(Recommendation(
                    action_type=ActionType.TAKE_PROFIT,
                    asset=asset.asset,
                    percentage=20.0,
                    reason=f"High ROI position ({asset.roi_percentage:.1f}%) - consider taking some profits",
                    confidence_score=0.8,
                    risk_level=RiskLevel.LOW,
                    expected_impact="Lock in profits while maintaining position",
                    personal_context=f"Your {asset.asset} position has {asset.roi_percentage:.1f}% ROI with cost basis ${asset.cost_basis:,.2f}",
                    market_context="Strong performance suggests good timing for profit taking",
                    execution_priority=1
                ))
        
        # Underperforming positions - consider averaging down or cutting losses
        for asset in portfolio_data.assets:
            if asset.roi_percentage and asset.roi_percentage < -30:
                recommendations.append(Recommendation(
                    action_type=ActionType.SELL,
                    asset=asset.asset,
                    percentage=50.0,
                    reason=f"Significant losses ({asset.roi_percentage:.1f}%) - consider cutting losses",
                    confidence_score=0.7,
                    risk_level=RiskLevel.MEDIUM,
                    expected_impact="Reduce exposure to underperforming asset",
                    personal_context=f"Your {asset.asset} position is down {abs(asset.roi_percentage):.1f}% from cost basis ${asset.cost_basis:,.2f}",
                    market_context="Poor performance suggests fundamental issues",
                    execution_priority=2
                ))
        
        # Diversification recommendations
        if analysis.diversification_score < 0.5:
            recommendations.append(Recommendation(
                action_type=ActionType.REBALANCE,
                asset="PORTFOLIO",
                reason="Low diversification - consider rebalancing portfolio",
                confidence_score=0.6,
                risk_level=RiskLevel.MEDIUM,
                expected_impact="Improve portfolio diversification and reduce concentration risk",
                personal_context="Your portfolio is concentrated in few assets",
                market_context="Diversification helps manage risk in volatile markets",
                execution_priority=3
            ))
        
        # If no specific recommendations, suggest holding
        if not recommendations:
            recommendations.append(Recommendation(
                action_type=ActionType.HOLD,
                asset="PORTFOLIO",
                reason="Portfolio is performing well - maintain current positions",
                confidence_score=0.7,
                risk_level=RiskLevel.LOW,
                expected_impact="Preserve capital and maintain current strategy",
                personal_context="Your portfolio shows stable performance",
                market_context="Market conditions are favorable for current positions",
                execution_priority=1
            ))
        
        return recommendations
    
    def generate_complete_analysis(self, portfolio_data: PortfolioData) -> AgentAnalysis:
        """Generate complete agent analysis."""
        
        # Analyze portfolio
        analysis = self.analyze_portfolio(portfolio_data)
        
        # Generate recommendations
        recommendations = self.generate_recommendations(analysis, portfolio_data)
        
        # Generate market summary
        market_summary = self._generate_market_summary(analysis)
        
        # Generate risk assessment
        risk_assessment = self._generate_risk_assessment(analysis, recommendations)
        
        # Generate next actions
        next_actions = self._generate_next_actions(recommendations)
        
        # Calculate overall confidence
        overall_confidence = sum(rec.confidence_score for rec in recommendations) / len(recommendations) if recommendations else 0.0
        
        return AgentAnalysis(
            portfolio_analysis=analysis,
            recommendations=recommendations,
            market_summary=market_summary,
            risk_assessment=risk_assessment,
            next_actions=next_actions,
            confidence_overall=overall_confidence,
            timestamp=datetime.now(timezone.utc)
        )
    
    def _calculate_risk_score(self, portfolio_data: PortfolioData) -> float:
        """Calculate portfolio risk score."""
        # Simple risk calculation based on ROI volatility
        if portfolio_data.total_roi_percentage > 20:
            return 0.3  # Low risk for high performers
        elif portfolio_data.total_roi_percentage < -20:
            return 0.8  # High risk for poor performers
        else:
            return 0.5  # Medium risk for neutral performance
    
    def _calculate_diversification_score(self, portfolio_data: PortfolioData) -> float:
        """Calculate portfolio diversification score."""
        # Simple diversification based on number of assets
        num_assets = len(portfolio_data.assets)
        if num_assets >= 5:
            return 0.9
        elif num_assets >= 3:
            return 0.7
        elif num_assets >= 2:
            return 0.5
        else:
            return 0.2
    
    def _generate_market_summary(self, analysis: PortfolioAnalysis) -> str:
        """Generate market summary."""
        summary = f"Market Analysis: {analysis.market_regime.value} market conditions. "
        summary += f"Portfolio ROI: {analysis.total_roi_percentage:.1f}%. "
        
        if analysis.top_performers:
            summary += f"Top performers: {', '.join(analysis.top_performers)}. "
        
        if analysis.underperformers:
            summary += f"Underperformers: {', '.join(analysis.underperformers)}. "
        
        if analysis.rebalancing_needed:
            summary += "Portfolio rebalancing recommended. "
        
        return summary
    
    def _generate_risk_assessment(self, analysis: PortfolioAnalysis, recommendations: List[Recommendation]) -> str:
        """Generate risk assessment."""
        risk_summary = f"Portfolio risk: {analysis.portfolio_risk_score:.2f}/1.0. "
        
        high_risk_recs = [r for r in recommendations if r.risk_level == RiskLevel.HIGH]
        if high_risk_recs:
            risk_summary += f"High-risk recommendations: {len(high_risk_recs)}. "
        
        if analysis.risk_adjustment_needed:
            risk_summary += "Risk adjustment recommended. "
        
        return risk_summary
    
    def _generate_next_actions(self, recommendations: List[Recommendation]) -> List[str]:
        """Generate list of next actions."""
        actions = []
        
        for rec in recommendations[:3]:  # Top 3 recommendations
            action_text = f"{rec.action_type.value} {rec.asset}"
            if rec.percentage:
                action_text += f" ({rec.percentage}%)"
            actions.append(action_text)
        
        return actions

# Global agent instance
simple_agent: Optional[SimpleAgentEngine] = None

def get_simple_agent() -> SimpleAgentEngine:
    """Get or create simple agent instance."""
    global simple_agent
    
    if simple_agent is None:
        simple_agent = SimpleAgentEngine()
    
    return simple_agent

async def generate_simple_agent_analysis(portfolio_data: PortfolioData) -> AgentAnalysis:
    """Generate complete agent analysis using the simple engine."""
    agent = get_simple_agent()
    return agent.generate_complete_analysis(portfolio_data) 
