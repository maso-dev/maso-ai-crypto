#!/usr/bin/env python3
"""
Simple test for the Agent Decision Engine
"""

import pytest
import asyncio
from datetime import datetime, timezone
from utils.simple_agent import SimpleAgentEngine, PortfolioData, PortfolioAsset
from utils.binance_client import PortfolioAsset as BinancePortfolioAsset

@pytest.fixture
def mock_portfolio():
    """Create mock portfolio data for testing."""
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
        )
    ]
    
    return PortfolioData(
        total_value_usdt=33000.0,
        total_cost_basis=26000.0,
        total_roi_percentage=26.9,
        assets=mock_assets,
        last_updated=datetime.now(timezone.utc),
        trade_history=[]
    )

def test_agent_initialization():
    """Test that the agent can be initialized."""
    agent = SimpleAgentEngine()
    assert agent is not None

def test_portfolio_analysis(mock_portfolio):
    """Test portfolio analysis functionality."""
    agent = SimpleAgentEngine()
    analysis = agent.analyze_portfolio(mock_portfolio)
    
    assert analysis.total_value == 33000.0
    assert analysis.total_cost_basis == 26000.0
    assert analysis.total_roi_percentage == 26.9
    assert analysis.market_regime.value in ["BULL", "BEAR", "SIDEWAYS", "VOLATILE"]
    assert 0 <= analysis.portfolio_risk_score <= 1

def test_recommendation_generation(mock_portfolio):
    """Test recommendation generation."""
    agent = SimpleAgentEngine()
    analysis = agent.analyze_portfolio(mock_portfolio)
    recommendations = agent.generate_recommendations(analysis, mock_portfolio)
    
    assert len(recommendations) > 0
    for rec in recommendations:
        assert rec.action_type.value in ["HOLD", "BUY", "SELL", "REBALANCE", "TAKE_PROFIT", "STOP_LOSS"]
        assert 0 <= rec.confidence_score <= 1
        assert rec.risk_level.value in ["LOW", "MEDIUM", "HIGH"]

def test_complete_analysis(mock_portfolio):
    """Test complete agent analysis."""
    agent = SimpleAgentEngine()
    complete_analysis = agent.generate_complete_analysis(mock_portfolio)
    
    assert complete_analysis.portfolio_analysis is not None
    assert len(complete_analysis.recommendations) > 0
    assert complete_analysis.market_summary is not None
    assert complete_analysis.risk_assessment is not None
    assert len(complete_analysis.next_actions) > 0
    assert 0 <= complete_analysis.confidence_overall <= 1

@pytest.mark.asyncio
async def test_async_agent_analysis(mock_portfolio):
    """Test async agent analysis function."""
    from utils.simple_agent import generate_simple_agent_analysis
    
    analysis = await generate_simple_agent_analysis(mock_portfolio)
    assert analysis is not None
    assert analysis.portfolio_analysis is not None 
