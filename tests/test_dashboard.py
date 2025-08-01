#!/usr/bin/env python3
"""
Test dashboard functionality with Agent Decision Engine
"""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_dashboard_loads():
    """Test that the welcome page loads successfully."""
    response = client.get("/")
    assert response.status_code == 200
    assert "Masonic" in response.text
    assert "Alpha Strategy Advisor" in response.text

def test_agent_insights_endpoint():
    """Test that agent insights endpoint returns valid data."""
    response = client.get("/agent/insights")
    assert response.status_code == 200
    data = response.json()
    
    # Check required fields
    assert "portfolio_performance" in data
    assert "market_analysis" in data
    assert "risk_metrics" in data
    assert "opportunities" in data
    assert "warnings" in data
    assert "timestamp" in data
    
    # Check portfolio performance structure
    perf = data["portfolio_performance"]
    assert "total_value" in perf
    assert "total_roi" in perf
    assert "risk_score" in perf
    assert "diversification_score" in perf
    assert "market_regime" in perf
    
    # Check market analysis structure
    market = data["market_analysis"]
    assert "regime" in market
    assert "top_performers" in market
    assert "underperformers" in market
    assert "rebalancing_needed" in market

def test_agent_recommendations_endpoint():
    """Test that agent recommendations endpoint returns valid data."""
    response = client.get("/agent/recommendations")
    assert response.status_code == 200
    data = response.json()
    
    # Should return a list of recommendations
    assert isinstance(data, list)
    
    if len(data) > 0:
        rec = data[0]
        # Check recommendation structure
        assert "action_type" in rec
        assert "asset" in rec
        assert "reason" in rec
        assert "confidence_score" in rec
        assert "risk_level" in rec
        assert "expected_impact" in rec
        assert "personal_context" in rec
        assert "market_context" in rec
        assert "execution_priority" in rec

def test_portfolio_assets_endpoint():
    """Test that portfolio assets endpoint works with agent integration."""
    response = client.get("/portfolio/assets")
    assert response.status_code == 200
    data = response.json()
    
    assert "total_value_usdt" in data
    assert "assets" in data
    assert "last_updated" in data
    assert isinstance(data["assets"], list)

def test_market_summary_endpoint():
    """Test that market summary endpoint works."""
    response = client.post("/portfolio/market_summary", json={
        "symbols": ["BTC", "ETH"],
        "limit": 5,
        "always_include_base_coins": True
    })
    assert response.status_code == 200
    data = response.json()
    
    assert "summary" in data
    assert "recommendations" in data
    assert "news" in data
    assert "timestamp" in data
    assert "symbols_analyzed" in data

def test_admin_status_endpoint():
    """Test that admin status endpoint works."""
    response = client.get("/admin/status")
    assert response.status_code == 200
    data = response.json()
    
    assert "status" in data
    assert "timestamp" in data
    assert "services" in data
    assert "database" in data
    assert "api_keys" in data 
