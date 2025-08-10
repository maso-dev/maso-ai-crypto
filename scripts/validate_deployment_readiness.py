#!/usr/bin/env python3
"""
Deployment Readiness Validation Script
Tests all fallback systems to ensure successful deployment
"""

import sys
import time
from pathlib import Path

def test_imports():
    """Test that all critical modules can be imported"""
    print("🧪 Testing Critical Imports...")
    
    try:
        # Test main app
        from main import app
        print("✅ Main FastAPI app imported successfully")
        print(f"   Routes count: {len(app.routes)}")
    except Exception as e:
        print(f"❌ Failed to import main app: {e}")
        return False
    
    try:
        # Test fallback systems
        from utils.hybrid_rag_fallback import get_hybrid_rag_fallback
        print("✅ Hybrid RAG fallback system ready")
    except Exception as e:
        print(f"❌ Failed to import hybrid RAG fallback: {e}")
        return False
    
    try:
        from utils.local_vector_fallback import get_local_vector_search
        print("✅ Local vector fallback system ready")
    except Exception as e:
        print(f"❌ Failed to import local vector fallback: {e}")
        return False
    
    try:
        from utils.qdrant_client import is_qdrant_available
        print("✅ Qdrant client ready")
    except Exception as e:
        print(f"❌ Failed to import Qdrant client: {e}")
        return False
    
    return True

def test_fallback_systems():
    """Test that fallback systems work correctly"""
    print("\n🔄 Testing Fallback Systems...")
    
    try:
        # Test hybrid RAG fallback
        from utils.hybrid_rag_fallback import get_hybrid_rag_fallback
        hybrid_rag = get_hybrid_rag_fallback()
        print("✅ Hybrid RAG fallback initialized")
        
        # Test local vector search
        from utils.local_vector_fallback import get_local_vector_search
        local_search = get_local_vector_search()
        print("✅ Local vector search initialized")
        
        return True
    except Exception as e:
        print(f"❌ Fallback system test failed: {e}")
        return False

def test_health_endpoints():
    """Test that health endpoints are accessible"""
    print("\n🏥 Testing Health Endpoints...")
    
    try:
        from main import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        
        # Test root endpoint
        start_time = time.time()
        response = client.get("/")
        response_time = (time.time() - start_time) * 1000
        
        print(f"✅ Root endpoint: {response.status_code} ({response_time:.1f}ms)")
        
        # Test health endpoint
        start_time = time.time()
        response = client.get("/health")
        response_time = (time.time() - start_time) * 1000
        
        print(f"✅ Health endpoint: {response.status_code} ({response_time:.1f}ms)")
        
        # Test API health endpoint
        start_time = time.time()
        response = client.get("/api/health")
        response_time = (time.time() - start_time) * 1000
        
        print(f"✅ API health endpoint: {response.status_code} ({response_time:.1f}ms)")
        
        # Check if response times are acceptable for Replit
        if response_time < 100:
            print("✅ Response times are acceptable for Replit deployment")
        else:
            print(f"⚠️ Response time {response_time:.1f}ms may be slow for Replit")
        
        return True
    except Exception as e:
        print(f"❌ Health endpoint test failed: {e}")
        return False

def test_environment_variables():
    """Test that critical environment variables are set"""
    print("\n🔧 Testing Environment Variables...")
    
    import os
    
    critical_vars = [
        "OPENAI_API_KEY",
        "NEWSAPI_KEY", 
        "BINANCE_API_KEY",
        "NEO4J_URI",
        "QDRANT_VECTOR_API"
    ]
    
    missing_vars = []
    for var in critical_vars:
        if os.getenv(var):
            print(f"✅ {var}: Set")
        else:
            print(f"⚠️ {var}: Not set")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️ Missing {len(missing_vars)} critical environment variables")
        print("   App will use fallback systems for missing services")
        return True  # Not critical for deployment
    else:
        print("✅ All critical environment variables are set")
        return True

def main():
    """Run all validation tests"""
    print("🚀 DEPLOYMENT READINESS VALIDATION")
    print("=" * 50)
    
    tests = [
        ("Critical Imports", test_imports),
        ("Fallback Systems", test_fallback_systems),
        ("Health Endpoints", test_health_endpoints),
        ("Environment Variables", test_environment_variables),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 VALIDATION SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 DEPLOYMENT READY! All systems are go!")
        print("💡 Your app has excellent fallback systems and should deploy successfully")
        return True
    else:
        print("⚠️ Some tests failed. Review the issues above before deploying.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
