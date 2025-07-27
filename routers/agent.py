#!/usr/bin/env python3
"""
Agent API Endpoints
Provides agentic intelligence and personalized recommendations.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

# Import agent-specific utilities
from utils.simple_agent import generate_simple_agent_analysis, AgentAnalysis, Recommendation, ActionType, RiskLevel
from utils.binance_client import get_portfolio_data, PortfolioData

router = APIRouter(prefix="/agent", tags=["agent"])

class AgentAnalysisRequest(BaseModel):
    """Request model for agent analysis."""
    symbols: Optional[List[str]] = Field(default=None, description="Specific symbols to analyze")
    include_news: bool = Field(default=True, description="Include market news in analysis")
    risk_tolerance: str = Field(default="MEDIUM", description="User risk tolerance: LOW, MEDIUM, HIGH")

class AgentAnalysisResponse(BaseModel):
    """Response model for agent analysis."""
    portfolio_analysis: Dict[str, Any]
    recommendations: List[Dict[str, Any]]
    market_summary: str
    risk_assessment: str
    next_actions: List[str]
    confidence_overall: float
    timestamp: str
    agent_insights: str

class RecommendationAction(BaseModel):
    """Model for executing a recommendation."""
    recommendation_id: str
    action_type: str
    asset: str
    quantity: Optional[float] = None
    percentage: Optional[float] = None
    execute: bool = Field(default=False, description="Whether to execute the action")

class AgentInsightsResponse(BaseModel):
    """Response model for agent insights."""
    portfolio_performance: Dict[str, Any]
    market_analysis: Dict[str, Any]
    risk_metrics: Dict[str, Any]
    opportunities: List[str]
    warnings: List[str]
    timestamp: str

@router.post("/analyze", response_model=AgentAnalysisResponse)
async def get_agent_analysis(request: AgentAnalysisRequest) -> AgentAnalysisResponse:
    """Get comprehensive agent analysis with personalized recommendations."""
    try:
        # Get portfolio data
        portfolio_data = await get_portfolio_data()
        
        if not portfolio_data:
            raise HTTPException(status_code=404, detail="Portfolio data not available")
        
        # Generate agent analysis
        analysis = await generate_simple_agent_analysis(portfolio_data)
        
        # Generate agent insights
        agent_insights = _generate_agent_insights(analysis)
        
        return AgentAnalysisResponse(
            portfolio_analysis=analysis.portfolio_analysis.model_dump(),
            recommendations=[rec.model_dump() for rec in analysis.recommendations],
            market_summary=analysis.market_summary,
            risk_assessment=analysis.risk_assessment,
            next_actions=analysis.next_actions,
            confidence_overall=analysis.confidence_overall,
            timestamp=analysis.timestamp.isoformat(),
            agent_insights=agent_insights
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating agent analysis: {str(e)}")

@router.get("/recommendations", response_model=List[Dict[str, Any]])
async def get_recommendations(
    limit: int = 5,
    risk_level: Optional[str] = None,
    action_type: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Get filtered recommendations based on criteria."""
    try:
        # Get portfolio data
        portfolio_data = await get_portfolio_data()
        
        if not portfolio_data:
            # Create mock portfolio data when Binance is not configured
            from utils.binance_client import PortfolioAsset as BinancePortfolioAsset
            
            mock_assets = [
                BinancePortfolioAsset(
                    asset="BTC",
                    free=0.5,
                    locked=0.0,
                    total=0.5,
                    usdt_value=25000.0,
                    cost_basis=20000.0,
                    roi_percentage=25.0,
                    avg_buy_price=40000.0
                ),
                BinancePortfolioAsset(
                    asset="ETH",
                    free=2.0,
                    locked=0.0,
                    total=2.0,
                    usdt_value=8000.0,
                    cost_basis=6000.0,
                    roi_percentage=33.3,
                    avg_buy_price=3000.0
                ),
                BinancePortfolioAsset(
                    asset="ADA",
                    free=1000.0,
                    locked=0.0,
                    total=1000.0,
                    usdt_value=500.0,
                    cost_basis=400.0,
                    roi_percentage=25.0,
                    avg_buy_price=0.4
                )
            ]
            
            portfolio_data = PortfolioData(
                total_value_usdt=33500.0,
                total_cost_basis=26400.0,
                total_roi_percentage=26.9,
                assets=mock_assets,
                last_updated=datetime.now(timezone.utc),
                trade_history=[]
            )
        
        # Generate agent analysis
        analysis = await generate_simple_agent_analysis(portfolio_data)
        
        # Filter recommendations
        recommendations = analysis.recommendations
        
        if risk_level:
            recommendations = [r for r in recommendations if r.risk_level.value == risk_level.upper()]
        
        if action_type:
            recommendations = [r for r in recommendations if r.action_type.value == action_type.upper()]
        
        # Limit results
        recommendations = recommendations[:limit]
        
        return [rec.model_dump() for rec in recommendations]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting recommendations: {str(e)}")

@router.get("/insights", response_model=AgentInsightsResponse)
async def get_agent_insights() -> AgentInsightsResponse:
    """Get high-level agent insights and portfolio analysis."""
    try:
        # Get portfolio data
        portfolio_data = await get_portfolio_data()
        
        if not portfolio_data:
            # Create mock portfolio data when Binance is not configured
            from utils.binance_client import PortfolioAsset as BinancePortfolioAsset
            
            mock_assets = [
                BinancePortfolioAsset(
                    asset="BTC",
                    free=0.5,
                    locked=0.0,
                    total=0.5,
                    usdt_value=25000.0,
                    cost_basis=20000.0,
                    roi_percentage=25.0,
                    avg_buy_price=40000.0
                ),
                BinancePortfolioAsset(
                    asset="ETH",
                    free=2.0,
                    locked=0.0,
                    total=2.0,
                    usdt_value=8000.0,
                    cost_basis=6000.0,
                    roi_percentage=33.3,
                    avg_buy_price=3000.0
                ),
                BinancePortfolioAsset(
                    asset="ADA",
                    free=1000.0,
                    locked=0.0,
                    total=1000.0,
                    usdt_value=500.0,
                    cost_basis=400.0,
                    roi_percentage=25.0,
                    avg_buy_price=0.4
                )
            ]
            
            portfolio_data = PortfolioData(
                total_value_usdt=33500.0,
                total_cost_basis=26400.0,
                total_roi_percentage=26.9,
                assets=mock_assets,
                last_updated=datetime.now(timezone.utc),
                trade_history=[]
            )
        
        # Generate agent analysis
        analysis = await generate_simple_agent_analysis(portfolio_data)
        
        # Extract insights
        portfolio_performance = {
            "total_value": analysis.portfolio_analysis.total_value,
            "total_roi": analysis.portfolio_analysis.total_roi_percentage,
            "risk_score": analysis.portfolio_analysis.portfolio_risk_score,
            "diversification_score": analysis.portfolio_analysis.diversification_score,
            "market_regime": analysis.portfolio_analysis.market_regime.value
        }
        
        market_analysis = {
            "regime": analysis.portfolio_analysis.market_regime.value,
            "top_performers": analysis.portfolio_analysis.top_performers,
            "underperformers": analysis.portfolio_analysis.underperformers,
            "rebalancing_needed": analysis.portfolio_analysis.rebalancing_needed
        }
        
        risk_metrics = {
            "portfolio_risk": analysis.portfolio_analysis.portfolio_risk_score,
            "liquidity_score": analysis.portfolio_analysis.liquidity_score,
            "risk_adjustment_needed": analysis.portfolio_analysis.risk_adjustment_needed,
            "high_risk_recommendations": len([r for r in analysis.recommendations if r.risk_level == RiskLevel.HIGH])
        }
        
        # Generate opportunities and warnings
        opportunities = []
        warnings = []
        
        for rec in analysis.recommendations:
            if rec.confidence_score > 0.8:
                opportunities.append(f"{rec.action_type.value} {rec.asset}: {rec.reason}")
            elif rec.risk_level == RiskLevel.HIGH:
                warnings.append(f"High-risk action: {rec.action_type.value} {rec.asset}")
        
        return AgentInsightsResponse(
            portfolio_performance=portfolio_performance,
            market_analysis=market_analysis,
            risk_metrics=risk_metrics,
            opportunities=opportunities,
            warnings=warnings,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting agent insights: {str(e)}")

@router.post("/execute-recommendation")
async def execute_recommendation(action: RecommendationAction) -> Dict[str, Any]:
    """Execute a specific recommendation (simulation only)."""
    try:
        # This is a simulation - in a real implementation, this would execute trades
        if not action.execute:
            return {
                "status": "simulation",
                "message": f"Simulated {action.action_type} of {action.quantity or action.percentage}% {action.asset}",
                "recommendation_id": action.recommendation_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        # In a real implementation, this would:
        # 1. Validate the recommendation
        # 2. Check portfolio balance
        # 3. Execute the trade via Binance API
        # 4. Record the action
        # 5. Update the agent's learning model
        
        return {
            "status": "executed",
            "message": f"Executed {action.action_type} of {action.quantity or action.percentage}% {action.asset}",
            "recommendation_id": action.recommendation_id,
            "execution_price": "market_price",  # Would be actual execution price
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing recommendation: {str(e)}")

@router.get("/performance")
async def get_agent_performance() -> Dict[str, Any]:
    """Get agent performance metrics (placeholder for future implementation)."""
    try:
        # This would track historical recommendation accuracy
        # For now, return mock data
        return {
            "total_recommendations": 25,
            "successful_recommendations": 18,
            "accuracy_rate": 0.72,
            "average_roi_improvement": 0.045,
            "risk_adjustment_success": 0.85,
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting agent performance: {str(e)}")

@router.get("/market-sentiment")
async def get_market_sentiment() -> Dict[str, Any]:
    """Get current market sentiment analysis."""
    try:
        # Get portfolio data for context
        portfolio_data = await get_portfolio_data()
        
        if not portfolio_data:
            raise HTTPException(status_code=404, detail="Portfolio data not available")
        
        # Generate agent analysis
        analysis = await generate_simple_agent_analysis(portfolio_data)
        
        return {
            "market_regime": analysis.portfolio_analysis.market_regime.value,
            "overall_sentiment": _calculate_sentiment(analysis),
            "top_concerns": _extract_concerns(analysis),
            "positive_factors": _extract_positive_factors(analysis),
            "confidence_level": analysis.confidence_overall,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting market sentiment: {str(e)}")

def _generate_agent_insights(analysis: AgentAnalysis) -> str:
    """Generate human-readable agent insights."""
    insights = []
    
    # Portfolio performance insights
    if analysis.portfolio_analysis.total_roi_percentage > 10:
        insights.append(f"Your portfolio is performing well with {analysis.portfolio_analysis.total_roi_percentage:.1f}% ROI")
    elif analysis.portfolio_analysis.total_roi_percentage < -5:
        insights.append(f"Portfolio is down {abs(analysis.portfolio_analysis.total_roi_percentage):.1f}% - consider defensive positions")
    
    # Market regime insights
    regime = analysis.portfolio_analysis.market_regime.value
    if regime == "BULL":
        insights.append("Market is in bullish territory - good time for growth positions")
    elif regime == "BEAR":
        insights.append("Bear market detected - focus on capital preservation")
    elif regime == "VOLATILE":
        insights.append("High volatility - consider reducing position sizes")
    
    # Risk insights
    if analysis.portfolio_analysis.portfolio_risk_score > 0.7:
        insights.append("Portfolio risk is elevated - consider rebalancing")
    
    # Recommendation insights
    high_confidence_recs = [r for r in analysis.recommendations if r.confidence_score > 0.8]
    if high_confidence_recs:
        insights.append(f"Found {len(high_confidence_recs)} high-confidence opportunities")
    
    return ". ".join(insights) if insights else "Portfolio is stable with no immediate action required."

def _calculate_sentiment(analysis: AgentAnalysis) -> str:
    """Calculate overall market sentiment."""
    roi = analysis.portfolio_analysis.total_roi_percentage
    risk = analysis.portfolio_analysis.portfolio_risk_score
    regime = analysis.portfolio_analysis.market_regime.value
    
    if roi > 5 and risk < 0.5 and regime in ["BULL", "SIDEWAYS"]:
        return "POSITIVE"
    elif roi < -5 or risk > 0.7 or regime == "BEAR":
        return "NEGATIVE"
    else:
        return "NEUTRAL"

def _extract_concerns(analysis: AgentAnalysis) -> List[str]:
    """Extract market concerns from analysis."""
    concerns = []
    
    if analysis.portfolio_analysis.portfolio_risk_score > 0.7:
        concerns.append("Elevated portfolio risk")
    
    if analysis.portfolio_analysis.market_regime.value == "BEAR":
        concerns.append("Bear market conditions")
    
    high_risk_recs = [r for r in analysis.recommendations if r.risk_level == RiskLevel.HIGH]
    if high_risk_recs:
        concerns.append(f"{len(high_risk_recs)} high-risk recommendations")
    
    return concerns

def _extract_positive_factors(analysis: AgentAnalysis) -> List[str]:
    """Extract positive factors from analysis."""
    positives = []
    
    if analysis.portfolio_analysis.total_roi_percentage > 0:
        positives.append(f"Positive ROI: {analysis.portfolio_analysis.total_roi_percentage:.1f}%")
    
    if analysis.portfolio_analysis.diversification_score > 0.7:
        positives.append("Good portfolio diversification")
    
    if analysis.portfolio_analysis.market_regime.value == "BULL":
        positives.append("Bull market conditions")
    
    high_confidence_recs = [r for r in analysis.recommendations if r.confidence_score > 0.8]
    if high_confidence_recs:
        positives.append(f"{len(high_confidence_recs)} high-confidence opportunities")
    
    return positives 
