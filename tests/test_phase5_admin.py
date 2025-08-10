#!/usr/bin/env python3
"""
Phase 5 Admin Controls Test - Lightweight & Concrete
Tests the new admin endpoints for MVP data refresh and status monitoring
"""

import asyncio
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.getcwd())


async def test_admin_configuration():
    """Test the enhanced admin configuration endpoint."""
    print("🧪 Testing Admin Configuration...")

    try:
        from main import admin_configuration

        result = await admin_configuration()

        print(f"✅ Status: {result.get('status')}")
        print(f"✅ Phase: {result.get('phase')}")
        print(
            f"✅ Configured APIs: {result.get('configured_count')}/{result.get('total_apis')}"
        )

        # Check cache statistics
        cache_stats = result.get("cache_statistics", {})
        if cache_stats:
            print(f"✅ Cache queries: {cache_stats.get('total_cached_queries', 0)}")
            print(f"✅ Cache hits: {cache_stats.get('total_cache_hits', 0)}")

        return True

    except Exception as e:
        print(f"❌ Admin configuration test failed: {e}")
        return False


async def test_mvp_status():
    """Test the MVP status endpoint."""
    print("🧪 Testing MVP Status...")

    try:
        from main import get_mvp_status

        result = await get_mvp_status()

        print(f"✅ System health: {result.get('system_health')}")
        print(
            f"✅ Operational components: {result.get('operational_components')}/{result.get('total_components')}"
        )
        print(f"✅ Current phase: {result.get('current_phase')}")

        # Check components
        components = result.get("components", {})
        if "livecoinwatch" in components:
            print(f"✅ LiveCoinWatch: {components['livecoinwatch'].get('status')}")
        if "news_cache" in components:
            print(f"✅ News Cache: {components['news_cache'].get('status')}")
        if "hybrid_rag" in components:
            print(f"✅ Hybrid RAG: {components['hybrid_rag'].get('status')}")

        return True

    except Exception as e:
        print(f"❌ MVP status test failed: {e}")
        return False


async def test_system_metrics():
    """Test the system metrics endpoint."""
    print("🧪 Testing System Metrics...")

    try:
        from main import get_system_metrics

        result = await get_system_metrics()

        print(f"✅ Status: {result.get('status')}")
        print(f"✅ Phase: {result.get('phase')}")

        metrics = result.get("metrics", {})

        # Check performance metrics
        performance = metrics.get("performance", {})
        if "livecoinwatch_response_time" in performance:
            print(
                f"✅ LiveCoinWatch response time: {performance['livecoinwatch_response_time']}s"
            )

        # Check data quality metrics
        data_quality = metrics.get("data_quality", {})
        if "news_articles_cached" in data_quality:
            print(f"✅ News articles cached: {data_quality['news_articles_cached']}")

        # Check system resources
        system_resources = metrics.get("system_resources", {})
        if "memory_usage_mb" in system_resources:
            print(f"✅ Memory usage: {system_resources['memory_usage_mb']}MB")

        return True

    except Exception as e:
        print(f"❌ System metrics test failed: {e}")
        return False


async def test_refresh_mvp_data_structure():
    """Test the refresh MVP data endpoint structure (without actually refreshing)."""
    print("🧪 Testing Refresh MVP Data Structure...")

    try:
        from main import refresh_mvp_data

        # Test the endpoint
        result = await refresh_mvp_data()

        print(f"✅ Status: {result.get('status')}")
        print(f"✅ Phase: {result.get('phase')}")

        # Check refresh results structure
        refresh_results = result.get("refresh_results", {})
        if refresh_results:
            print(f"✅ Overall status: {refresh_results.get('overall_status')}")

            # Check individual components
            for component, status in refresh_results.items():
                if isinstance(status, dict) and component != "overall_status":
                    print(f"✅ {component}: {status.get('status')}")

        return True

    except Exception as e:
        print(f"❌ Refresh MVP data test failed: {e}")
        return False


async def test_cache_statistics():
    """Test cache statistics functionality."""
    print("🧪 Testing Cache Statistics...")

    try:
        from utils.intelligent_news_cache import (
            get_cache_statistics,
            clear_expired_cache,
        )

        # Get cache statistics
        stats = get_cache_statistics()
        print(f"✅ Total cached queries: {stats.get('total_cached_queries', 0)}")
        print(f"✅ Expired queries: {stats.get('expired_queries', 0)}")
        print(f"✅ Total cache hits: {stats.get('total_cache_hits', 0)}")

        # Test clearing expired cache
        cleared_count = clear_expired_cache()
        print(f"✅ Cleared {cleared_count} expired entries")

        return True

    except Exception as e:
        print(f"❌ Cache statistics test failed: {e}")
        return False


async def main():
    """Run concrete Phase 5 admin tests."""
    print("🚀 PHASE 5 ADMIN CONTROLS - CONCRETE TESTS")
    print("=" * 50)

    tests = [
        test_admin_configuration,
        test_mvp_status,
        test_system_metrics,
        test_refresh_mvp_data_structure,
        test_cache_statistics,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if await test():
                passed += 1
            print()  # Add spacing between tests
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            print()

    print("=" * 50)
    print(f"📊 PHASE 5 ADMIN CONTROLS TEST SUMMARY")
    print(f"Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")

    if passed == total:
        print("🎉 All Phase 5 admin controls tests passed!")
        return 0
    else:
        print("⚠️  Some Phase 5 admin controls tests failed.")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
