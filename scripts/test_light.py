#!/usr/bin/env python3
"""
Lightweight tests for fast development cycles
Only tests essential functionality - no heavy AI/LLM calls
"""

import sys
import os
import pytest
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, os.getcwd())


def test_app_imports():
    """Test that the app imports correctly."""
    import main

    assert main.app is not None
    assert hasattr(main.app, "routes")
    print("✅ App imports successfully")


def test_key_utils_import():
    """Test that key utilities can be imported."""
    from utils.binance_client import get_portfolio_data
    from utils.livecoinwatch_processor import LiveCoinWatchProcessor
    from utils.ai_agent import CryptoAIAgent, AgentTask

    print("✅ Key utils import successfully")


def test_app_structure():
    """Test basic app structure."""
    import main

    assert main.app.title == "🏛️ Masonic - Alpha Strategy Advisor"
    assert len(main.app.routes) > 0
    print("✅ App structure is correct")


def test_env_vars():
    """Test that essential environment variables are available."""
    essential_vars = [
        "OPENAI_API_KEY",
        "BINANCE_API_KEY",
        "BINANCE_SECRET_KEY",
        "LIVECOINWATCH_API_KEY",
        "TAVILY_API_KEY",
    ]

    for var in essential_vars:
        assert os.getenv(var) is not None, f"Missing environment variable: {var}"
    print("✅ Environment variables are set")


def main():
    """Run lightweight tests."""
    print("🚀 LIGHTWEIGHT TESTS - Fast Development Testing")
    print("=" * 50)

    tests = [
        test_app_imports,
        test_key_utils_import,
        test_app_structure,
        test_env_vars,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"❌ {test.__name__} failed: {e}")

    print("=" * 50)
    print(f"📊 LIGHTWEIGHT TEST SUMMARY")
    print(f"Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")

    if passed == total:
        print("🎉 All lightweight tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
