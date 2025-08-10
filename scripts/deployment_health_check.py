#!/usr/bin/env python3
"""
Deployment Health Check Script
Validates that all critical endpoints are working after deployment
"""

import requests
import sys
import time

def check_endpoint(url: str, description: str) -> bool:
    """Check if an endpoint is responding correctly"""
    try:
        print(f"🔍 Checking {description}...")
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            print(f"   ✅ {description}: PASS (Status: {response.status_code})")
            return True
        else:
            print(f"   ❌ {description}: FAIL (Status: {response.status_code})")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ {description}: ERROR ({str(e)})")
        return False

def main():
    """Run deployment health checks"""
    print("🏥 DEPLOYMENT HEALTH CHECK")
    print("=" * 50)
    
    # Get base URL from command line or use default
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:3000"
    
    print(f"📍 Testing deployment at: {base_url}")
    print()
    
    # Critical endpoints to check
    endpoints = [
        ("/", "Root Health Check"),
        ("/api/health", "API Health Check"),
        ("/docs", "API Documentation"),
        ("/dashboard", "Main Dashboard"),
    ]
    
    passed = 0
    total = len(endpoints)
    
    for path, description in endpoints:
        url = f"{base_url}{path}"
        if check_endpoint(url, description):
            passed += 1
        print()
        time.sleep(1)  # Small delay between checks
    
    print("=" * 50)
    print(f"📊 RESULTS: {passed}/{total} endpoints passed")
    
    if passed == total:
        print("🎉 All health checks passed! Deployment is healthy!")
        return 0
    else:
        print("⚠️  Some health checks failed. Please investigate.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
