#!/usr/bin/env python3
"""
Simple API tests for Vercel deployment
"""

import pytest
from main import app


def test_app_imports():
    """Test that the app imports correctly."""
    assert app is not None
    assert hasattr(app, "routes")


def test_app_has_routes():
    """Test that the app has routes."""
    assert len(app.routes) > 0
    assert any(hasattr(route, "path") for route in app.routes)


def test_app_title():
    """Test that the app has the correct title."""
    assert app.title == "🏛️ Masonic - Alpha Strategy Advisor"


def test_app_version():
    """Test that the app has a version."""
    assert hasattr(app, "version")


def test_app_openapi():
    """Test that the app has OpenAPI schema."""
    assert hasattr(app, "openapi")
