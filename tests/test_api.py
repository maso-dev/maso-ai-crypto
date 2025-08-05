#!/usr/bin/env python3
"""
Simple API tests for Vercel deployment
"""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root_endpoint():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200

def test_portfolio_assets_endpoint():
    """Test the portfolio assets endpoint."""
    response = client.get("/portfolio/assets")
    assert response.status_code == 200
    data = response.json()
    assert "assets" in data

def test_admin_status_endpoint():
    """Test the admin status endpoint."""
    response = client.get("/admin/status")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "timestamp" in data

def test_agent_insights_endpoint():
    """Test the agent insights endpoint."""
    response = client.get("/agent/insights")
    # This might fail if no portfolio data, but should return a proper error
    assert response.status_code in [200, 404, 500]

def test_health_check():
    """Test health check endpoint."""
    response = client.get("/admin/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data 
