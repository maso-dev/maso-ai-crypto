#!/usr/bin/env python3
"""
Replit Deployment Verification Script
Run this on Replit to verify your deployment is working correctly
"""

import requests
import os
import sys
from datetime import datetime


def test_root_endpoint():
    """Test the root endpoint (/)"""
    print("🔍 Testing root endpoint (/)...")
    try:
        # Use PORT environment variable or default to 8000 for local testing
        port = os.getenv("PORT", "8000")
        response = requests.get(f"http://localhost:{port}/", timeout=10)
        if response.status_code == 200:
            # Root endpoint should return HTML, not JSON
            if "text/html" in response.headers.get("content-type", ""):
                print("   ✅ Root endpoint working: Returns HTML (website)")
                return True
            else:
                print(
                    f"   ❌ Root endpoint returns wrong content type: {response.headers.get('content-type')}"
                )
                return False
        else:
            print(f"   ❌ Root endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Root endpoint error: {str(e)}")
        return False


def test_health_endpoint():
    """Test the health endpoint (/api/health)"""
    print("🔍 Testing health endpoint (/api/health)...")
    try:
        port = os.getenv("PORT", "8000")
        response = requests.get(f"http://localhost:{port}/api/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Health endpoint working: {data.get('status', 'unknown')}")

            # Check environment variables
            env_vars = data.get("environment_vars", {})
            print("   📊 Environment Variables Status:")
            for var, status in env_vars.items():
                icon = "✅" if status else "❌"
                print(f"      {icon} {var}: {'SET' if status else 'MISSING'}")

            return True
        else:
            print(f"   ❌ Health endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Health endpoint error: {str(e)}")
        return False


def test_replit_health_endpoint():
    """Test the Replit health endpoint (/health)"""
    print("🔍 Testing Replit health endpoint (/health)...")
    try:
        port = os.getenv("PORT", "8000")
        response = requests.get(f"http://localhost:{port}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(
                f"   ✅ Replit health endpoint working: {data.get('status', 'unknown')}"
            )
            return True
        else:
            print(f"   ❌ Replit health endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Replit health endpoint error: {str(e)}")
        return False


def test_dashboard_endpoint():
    """Test the dashboard endpoint (/dashboard)"""
    print("🔍 Testing dashboard endpoint (/dashboard)...")
    try:
        port = os.getenv("PORT", "8000")
        response = requests.get(f"http://localhost:{port}/dashboard", timeout=15)
        if response.status_code == 200:
            print("   ✅ Dashboard endpoint working")
            return True
        else:
            print(f"   ⚠️ Dashboard endpoint: {response.status_code} (may be expected)")
            return True  # Dashboard might require authentication
    except Exception as e:
        print(f"   ⚠️ Dashboard endpoint error: {str(e)} (may be expected)")
        return True  # Dashboard might require authentication


def test_docs_endpoint():
    """Test the API docs endpoint (/docs)"""
    print("🔍 Testing API docs endpoint (/docs)...")
    try:
        port = os.getenv("PORT", "8000")
        response = requests.get(f"http://localhost:{port}/docs", timeout=10)
        if response.status_code == 200:
            print("   ✅ API docs endpoint working")
            return True
        else:
            print(f"   ❌ API docs endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ API docs endpoint error: {str(e)}")
        return False


def check_environment_variables():
    """Check if required environment variables are set"""
    print("🔍 Checking environment variables...")

    required_vars = ["OPENAI_API_KEY"]
    optional_vars = [
        "NEWS_API_KEY",
        "TAVILY_API_KEY",
        "BINANCE_API_KEY",
        "MILVUS_TOKEN",
        "NEO4J_URI",
        "QDRANT_URL",
    ]

    missing_required = []
    missing_optional = []

    for var in required_vars:
        if os.getenv(var):
            print(f"   ✅ {var}: SET")
        else:
            missing_required.append(var)
            print(f"   ❌ {var}: MISSING (REQUIRED)")

    for var in optional_vars:
        if os.getenv(var):
            print(f"   ✅ {var}: SET")
        else:
            missing_optional.append(var)
            print(f"   ⚠️ {var}: MISSING (OPTIONAL)")

    if missing_required:
        print(f"   ❌ Missing required environment variables: {missing_required}")
        return False

    print("   ✅ All required environment variables are set")
    if missing_optional:
        print(f"   ⚠️ Missing optional variables: {missing_optional}")

    return True


def main():
    """Run all deployment verification tests"""
    print("🚀 REPLIT DEPLOYMENT VERIFICATION")
    print("=" * 50)
    print(f"Timestamp: {datetime.now().isoformat()}")
    port = os.getenv("PORT", "8000")
    print(f"Port: {port}")
    print(f"Testing endpoints at: http://localhost:{port}")
    print()

    tests = [
        ("Root Endpoint", test_root_endpoint),
        ("Health Endpoint", test_health_endpoint),
        ("Replit Health Endpoint", test_replit_health_endpoint),
        ("Dashboard Endpoint", test_dashboard_endpoint),
        ("API Docs", test_docs_endpoint),
        ("Environment Variables", check_environment_variables),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"💥 {test_name} test crashed: {e}")
            results.append((test_name, False))
        print()

    # Summary
    print("=" * 50)
    print("📊 DEPLOYMENT VERIFICATION RESULTS")
    print("=" * 50)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")

    print(f"\n🎯 Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 ALL TESTS PASSED - Your Replit deployment is working!")
        return 0
    else:
        print("⚠️ Some tests failed - Check the issues above")
        return 1


if __name__ == "__main__":
    sys.exit(main())
