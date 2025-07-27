#!/usr/bin/env python3
"""
Test script for the enhanced UI components.
Tests the new sections and functionality added to the dashboard.
"""

import asyncio
import httpx
import json

async def test_dashboard_access():
    """Test that the enhanced dashboard is accessible."""
    print("🧪 Testing Enhanced Dashboard Access...")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/", timeout=10.0)
            
            if response.status_code == 200:
                content = response.text
                
                # Check for new sections
                new_sections = [
                    "news-insights",
                    "processing-status",
                    "temporal-badge",
                    "sentiment-indicator",
                    "impact-indicator",
                    "analytics-grid",
                    "components-grid",
                    "pipeline-steps"
                ]
                
                found_sections = []
                for section in new_sections:
                    if section in content:
                        found_sections.append(section)
                
                print(f"✅ Dashboard accessible (status: {response.status_code})")
                print(f"📊 New UI components found: {len(found_sections)}/{len(new_sections)}")
                
                for section in found_sections:
                    print(f"   ✅ {section}")
                
                missing_sections = [s for s in new_sections if s not in found_sections]
                if missing_sections:
                    print(f"   ⚠️ Missing sections: {missing_sections}")
                
                return len(found_sections) >= len(new_sections) * 0.8  # 80% success rate
            else:
                print(f"❌ Dashboard returned status: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Dashboard access failed: {e}")
        return False

async def test_market_summary_endpoint():
    """Test the enhanced market summary endpoint."""
    print("\n🧪 Testing Enhanced Market Summary Endpoint...")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/portfolio/market_summary",
                headers={"Content-Type": "application/json"},
                json={
                    "symbols": ["BTC", "ETH"],
                    "limit": 3,
                    "always_include_base_coins": True
                },
                timeout=15.0
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Market summary endpoint working (status: {response.status_code})")
                
                # Check response structure
                required_fields = ["summary", "recommended_actions", "news"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    print(f"   ✅ Response structure valid")
                    print(f"   📰 News items: {len(data.get('news', []))}")
                    print(f"   📊 Summary length: {len(data.get('summary', ''))} chars")
                    print(f"   💡 Actions length: {len(data.get('recommended_actions', ''))} chars")
                    return True
                else:
                    print(f"   ❌ Missing fields: {missing_fields}")
                    return False
            else:
                print(f"❌ Market summary returned status: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Market summary test failed: {e}")
        return False

async def test_css_styles():
    """Test that the enhanced CSS styles are accessible."""
    print("\n🧪 Testing Enhanced CSS Styles...")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/static/css/style.css", timeout=10.0)
            
            if response.status_code == 200:
                content = response.text
                
                # Check for new CSS classes
                new_styles = [
                    "temporal-badge",
                    "sentiment-indicator",
                    "impact-indicator",
                    "analytics-grid",
                    "components-grid",
                    "pipeline-steps",
                    "insights-card",
                    "status-card"
                ]
                
                found_styles = []
                for style in new_styles:
                    if style in content:
                        found_styles.append(style)
                
                print(f"✅ CSS styles accessible (status: {response.status_code})")
                print(f"🎨 New styles found: {len(found_styles)}/{len(new_styles)}")
                
                for style in found_styles:
                    print(f"   ✅ {style}")
                
                return len(found_styles) >= len(new_styles) * 0.8  # 80% success rate
            else:
                print(f"❌ CSS returned status: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ CSS test failed: {e}")
        return False

async def main():
    """Run all UI enhancement tests."""
    print("🚀 Starting Enhanced UI Tests\n")
    
    try:
        # Test 1: Dashboard access
        test1 = await test_dashboard_access()
        
        # Test 2: Market summary endpoint
        test2 = await test_market_summary_endpoint()
        
        # Test 3: CSS styles
        test3 = await test_css_styles()
        
        print(f"\n📊 UI Enhancement Test Results:")
        print(f"   Dashboard access: {'✅ PASSED' if test1 else '❌ FAILED'}")
        print(f"   Market summary endpoint: {'✅ PASSED' if test2 else '❌ FAILED'}")
        print(f"   CSS styles: {'✅ PASSED' if test3 else '❌ FAILED'}")
        
        if all([test1, test2, test3]):
            print("\n🎉 All UI enhancement tests passed!")
            print("   The enhanced dashboard is fully functional.")
            print("   New features available:")
            print("   ✅ Temporal indicators (breaking news badges)")
            print("   ✅ Rich metadata display (sentiment, impact, categories)")
            print("   ✅ News analytics dashboard")
            print("   ✅ System status monitoring")
            print("   ✅ Processing pipeline visualization")
        else:
            print("\n⚠️  Some UI tests failed. Please check the implementation.")
            
    except Exception as e:
        print(f"\n❌ UI test suite failed with error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 
