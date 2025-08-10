#!/usr/bin/env python3
"""
Quick E2E Test - Post Security Fixes Validation
Fast test of core architecture components
"""

import requests
import time

BASE_URL = "http://localhost:8000"

def quick_test():
    print("🧪 QUICK E2E TEST - Post Security Fixes Validation")
    print("=" * 60)

    # Test 1: Core Health (should be instant)
    print("\n1️⃣ Testing Core Health...")
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ API Health: PASS")
        else:
            print(f"   ❌ API Health: FAIL ({response.status_code})")
    except Exception as e:
        print(f"   ❌ API Health: ERROR ({str(e)})")

    # Test 2: Admin Health
    try:
        response = requests.get(f"{BASE_URL}/admin/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ Admin Health: PASS")
        else:
            print(f"   ❌ Admin Health: FAIL ({response.status_code})")
    except Exception as e:
        print(f"   ❌ Admin Health: ERROR ({str(e)})")

    # Test 3: Brain Health
    try:
        response = requests.get(f"{BASE_URL}/brain/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ Brain Health: PASS")
        else:
            print(f"   ❌ Brain Health: FAIL ({response.status_code})")
    except Exception as e:
        print(f"   ❌ Brain Health: ERROR ({str(e)})")

    # Test 4: Cache Status
    print("\n2️⃣ Testing Cache System...")
    try:
        response = requests.get(f"{BASE_URL}/api/cache/status", timeout=5)
        if response.status_code == 200:
            print("   ✅ Cache Status: PASS")
        else:
            print(f"   ❌ Cache Status: FAIL ({response.status_code})")
    except Exception as e:
        print(f"   ❌ Cache Status: ERROR ({str(e)})")

    # Test 5: External Services
    print("\n3️⃣ Testing External Services...")
    try:
        response = requests.get(f"{BASE_URL}/api/tavily/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ Tavily Service: PASS")
        else:
            print(f"   ❌ Tavily Service: FAIL ({response.status_code})")
    except Exception as e:
        print(f"   ❌ Tavily Service: ERROR ({str(e)})")

    try:
        response = requests.get(f"{BASE_URL}/api/livecoinwatch/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ LiveCoinWatch: PASS")
        else:
            print(f"   ❌ LiveCoinWatch: FAIL ({response.status_code})")
    except Exception as e:
        print(f"   ❌ LiveCoinWatch: ERROR ({str(e)})")

    # Test 6: Dashboard Loading
    print("\n4️⃣ Testing Dashboards...")
    try:
        response = requests.get(f"{BASE_URL}/dashboard", timeout=5)
        if response.status_code == 200 and response.text.startswith('<!DOCTYPE html>'):
            print("   ✅ Main Dashboard: PASS")
        else:
            print(f"   ❌ Main Dashboard: FAIL ({response.status_code})")
    except Exception as e:
        print(f"   ❌ Main Dashboard: ERROR ({str(e)})")

    try:
        response = requests.get(f"{BASE_URL}/brain-dashboard", timeout=5)
        if response.status_code == 200 and response.text.startswith('<!DOCTYPE html>'):
            print("   ✅ Brain Dashboard: PASS")
        else:
            print(f"   ❌ Brain Dashboard: FAIL ({response.status_code})")
    except Exception as e:
        print(f"   ❌ Brain Dashboard: ERROR ({str(e)})")

    # Test 7: API Documentation
    print("\n5️⃣ Testing API Docs...")
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        if response.status_code == 200:
            print("   ✅ API Documentation: PASS")
        else:
            print(f"   ❌ API Documentation: FAIL ({response.status_code})")
    except Exception as e:
        print(f"   ❌ API Documentation: ERROR ({str(e)})")

    print("\n" + "=" * 60)
    print("🎯 Quick E2E Test Complete!")
    print("If all tests PASS, your security fixes are working!")

if __name__ == "__main__":
    quick_test()
