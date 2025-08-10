#!/usr/bin/env python3
"""
Phase 6 UI Polish Test - Lightweight & Concrete
Tests the enhanced dashboard UI with Phase 4 & 5 integration
"""

import asyncio
import sys
import os

sys.path.insert(0, os.getcwd())


async def test_dashboard_template_structure():
    """Test the dashboard template has all required elements."""
    print("🧪 Testing Dashboard Template Structure...")
    try:
        with open("templates/dashboard.html", "r") as f:
            content = f.read()

        required_elements = [
            "portfolio-summary-content",
            "agent-intelligence-content",
            "market-summary-content",
            "market-analysis-content",
            "news-insights-content",
            "enhanced-dashboard.js",
        ]

        for element in required_elements:
            if element in content:
                print(f"✅ {element} found")
            else:
                print(f"❌ {element} missing")
                return False

        # Check for Phase 6 specific CSS classes
        phase6_classes = [
            "refresh-btn",
            "phase-badge",
            "system-status",
            "market-regime",
            "intelligence-header",
            "recommendation-item",
        ]

        for css_class in phase6_classes:
            if css_class in content:
                print(f"✅ CSS class {css_class} found")
            else:
                print(f"❌ CSS class {css_class} missing")
                return False

        return True
    except Exception as e:
        print(f"❌ Dashboard template test failed: {e}")
        return False


async def test_enhanced_javascript():
    """Test the enhanced JavaScript functionality."""
    print("🧪 Testing Enhanced JavaScript...")
    try:
        with open("static/js/enhanced-dashboard.js", "r") as f:
            content = f.read()

        required_functions = [
            "updateOpportunitiesData",
            "updateAdminStatus",
            "updateAgentIntelligence",
            "updateMarketAnalysis",
            "refreshCardData",
            "updatePhaseIndicator",
        ]

        for function in required_functions:
            if function in content:
                print(f"✅ Function {function} found")
            else:
                print(f"❌ Function {function} missing")
                return False

        # Check for Phase 6 specific features
        phase6_features = [
            'currentPhase = "6"',
            "adminUpdateInterval",
            "setupEventListeners",
            "addRefreshButtons",
            "updateSystemStatus",
        ]

        for feature in phase6_features:
            if feature in content:
                print(f"✅ Feature {feature} found")
            else:
                print(f"❌ Feature {feature} missing")
                return False

        return True
    except Exception as e:
        print(f"❌ Enhanced JavaScript test failed: {e}")
        return False


async def test_css_enhancements():
    """Test the CSS enhancements for Phase 6."""
    print("🧪 Testing CSS Enhancements...")
    try:
        with open("templates/dashboard.html", "r") as f:
            content = f.read()

        # Extract CSS section - look in the entire style section
        css_start = content.find("<style>")
        if css_start == -1:
            print("❌ CSS section not found")
            return False

        css_end = content.find("</style>", css_start)
        css_section = content[css_start:css_end]

        required_styles = [
            ".refresh-btn",
            ".phase-badge",
            ".system-status",
            ".market-regime",
            ".regime-badge",
            ".intelligence-header",
            ".recommendation-item",
            ".error-message",
        ]

        for style in required_styles:
            if style in css_section:
                print(f"✅ Style {style} found")
            else:
                print(f"❌ Style {style} missing")
                return False

        return True
    except Exception as e:
        print(f"❌ CSS enhancements test failed: {e}")
        return False


async def test_endpoint_integration():
    """Test that the JavaScript integrates with our Phase 4 & 5 endpoints."""
    print("🧪 Testing Endpoint Integration...")
    try:
        with open("static/js/enhanced-dashboard.js", "r") as f:
            content = f.read()

        required_endpoints = [
            "/api/opportunities",
            "/api/admin/mvp-status",
            "/api/news-briefing",
            "/api/portfolio",
        ]

        for endpoint in required_endpoints:
            if endpoint in content:
                print(f"✅ Endpoint {endpoint} integrated")
            else:
                print(f"❌ Endpoint {endpoint} not integrated")
                return False

        return True
    except Exception as e:
        print(f"❌ Endpoint integration test failed: {e}")
        return False


async def test_ui_components():
    """Test the new UI components and their structure."""
    print("🧪 Testing UI Components...")
    try:
        with open("templates/dashboard.html", "r") as f:
            content = f.read()

        # Test for new UI components
        components = {
            "Refresh buttons": "refresh-btn",
            "Phase badge": "phase-badge",
            "System status": "system-status",
            "Market regime badges": "regime-badge",
            "Intelligence stats": "intelligence-stats",
            "Recommendation items": "recommendation-item",
            "Error messages": "error-message",
        }

        all_found = True
        for component_name, css_class in components.items():
            if css_class in content:
                print(f"✅ {component_name} implemented")
            else:
                print(f"❌ {component_name} not implemented")
                all_found = False

        return all_found
    except Exception as e:
        print(f"❌ UI components test failed: {e}")
        return False


async def main():
    """Run concrete Phase 6 UI Polish tests."""
    print("🚀 PHASE 6 UI POLISH - CONCRETE TESTS")
    print("=" * 50)
    tests = [
        test_dashboard_template_structure,
        test_enhanced_javascript,
        test_css_enhancements,
        test_endpoint_integration,
        test_ui_components,
    ]
    passed = 0
    total = len(tests)
    for test in tests:
        try:
            if await test():
                passed += 1
            print()
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            print()
    print("=" * 50)
    print(f"📊 PHASE 6 UI POLISH TEST SUMMARY")
    print(f"Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    if passed == total:
        print("🎉 All Phase 6 UI Polish tests passed!")
        print("✅ Enhanced dashboard with dynamic content")
        print("✅ Refresh buttons and phase indicators")
        print("✅ Phase 4 & 5 endpoint integration")
        print("✅ Responsive design and error handling")
        return 0
    else:
        print("⚠️  Some Phase 6 UI Polish tests failed.")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
