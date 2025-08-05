#!/usr/bin/env python3
"""
Dashboard tests for Vercel deployment
"""

import pytest
from main import app


def test_app_imports():
    """Test that the app imports correctly."""
    assert app is not None
    assert hasattr(app, "routes")


def test_app_has_dashboard_routes():
    """Test that the app has dashboard routes."""
    assert len(app.routes) > 0
    assert any(hasattr(route, "path") for route in app.routes)


def test_app_title():
    """Test that the app has the correct title."""
    assert app.title == "🏛️ Masonic - Alpha Strategy Advisor"
