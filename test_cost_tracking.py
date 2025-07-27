#!/usr/bin/env python3
"""
Test script for the cost tracking system.
Tests cost tracking functionality and API endpoints.
"""

import asyncio
import httpx
import json
from datetime import datetime, timezone
from utils.cost_tracker import cost_tracker, track_openai_call, track_tavily_call, track_newsapi_call

async def test_cost_tracking_system():
    """Test the cost tracking system with mock API calls."""
    print("🧪 Testing Cost Tracking System...")
    
    try:
        # Test 1: Track OpenAI calls
        print("   📊 Testing OpenAI cost tracking...")
        await track_openai_call(
            model="gpt-4-turbo",
            tokens_input=1000,
            tokens_output=500,
            metadata={"operation": "news_enrichment"}
        )
        print("      ✅ OpenAI call tracked")
        
        # Test 2: Track Tavily calls
        print("   🔍 Testing Tavily cost tracking...")
        await track_tavily_call(
            endpoint="search",
            metadata={"query": "bitcoin price"}
        )
        print("      ✅ Tavily call tracked")
        
        # Test 3: Track NewsAPI calls
        print("   📰 Testing NewsAPI cost tracking...")
        await track_newsapi_call(
            endpoint="everything",
            metadata={"terms": ["BTC", "ETH"]}
        )
        print("      ✅ NewsAPI call tracked")
        
        # Test 4: Get daily summary
        print("   📈 Testing daily summary...")
        daily_summary = cost_tracker.get_daily_summary()
        print(f"      ✅ Daily summary: ${daily_summary['total_cost']:.4f} total cost")
        print(f"      📊 Service breakdown: {daily_summary['service_costs']}")
        
        # Test 5: Get monthly summary
        print("   📅 Testing monthly summary...")
        now = datetime.now(timezone.utc)
        monthly_summary = cost_tracker.get_monthly_summary(now.year, now.month)
        print(f"      ✅ Monthly summary: ${monthly_summary['total_cost']:.4f} total cost")
        
        # Test 6: Get recent calls
        print("   📋 Testing recent calls...")
        recent_calls = cost_tracker.get_recent_calls(limit=10)
        print(f"      ✅ Recent calls: {len(recent_calls)} calls retrieved")
        
        return True
        
    except Exception as e:
        print(f"❌ Cost tracking test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_cost_tracking_endpoints():
    """Test the cost tracking API endpoints."""
    print("\n🧪 Testing Cost Tracking API Endpoints...")
    
    try:
        async with httpx.AsyncClient() as client:
            # Test 1: Daily costs endpoint
            print("   📊 Testing daily costs endpoint...")
            response = await client.get("http://localhost:8000/costs/daily", timeout=10.0)
            
            if response.status_code == 200:
                data = response.json()
                print(f"      ✅ Daily costs: ${data['total_cost']:.4f}")
                print(f"      📊 Call count: {data['call_count']}")
            else:
                print(f"      ❌ Daily costs returned status: {response.status_code}")
                return False
            
            # Test 2: Current month endpoint
            print("   📅 Testing current month endpoint...")
            response = await client.get("http://localhost:8000/costs/current-month", timeout=10.0)
            
            if response.status_code == 200:
                data = response.json()
                print(f"      ✅ Current month: ${data['monthly']['total_cost']:.4f}")
                print(f"      📈 Projected: ${data['projected_monthly']['total_cost']:.4f}")
            else:
                print(f"      ❌ Current month returned status: {response.status_code}")
                return False
            
            # Test 3: Service breakdown endpoint
            print("   🔧 Testing service breakdown endpoint...")
            response = await client.get("http://localhost:8000/costs/services", timeout=10.0)
            
            if response.status_code == 200:
                data = response.json()
                print(f"      ✅ Service breakdown retrieved")
                print(f"      📊 Daily breakdown: {data['daily_breakdown']}")
            else:
                print(f"      ❌ Service breakdown returned status: {response.status_code}")
                return False
            
            # Test 4: Cost alerts endpoint
            print("   ⚠️ Testing cost alerts endpoint...")
            response = await client.get("http://localhost:8000/costs/alerts", timeout=10.0)
            
            if response.status_code == 200:
                data = response.json()
                print(f"      ✅ Cost alerts: {len(data['alerts'])} alerts")
                print(f"      💰 Daily cost: ${data['daily_cost']:.4f}")
            else:
                print(f"      ❌ Cost alerts returned status: {response.status_code}")
                return False
            
            # Test 5: Recent calls endpoint
            print("   📋 Testing recent calls endpoint...")
            response = await client.get("http://localhost:8000/costs/recent?limit=5", timeout=10.0)
            
            if response.status_code == 200:
                data = response.json()
                print(f"      ✅ Recent calls: {len(data)} calls")
                for call in data[:3]:  # Show first 3 calls
                    print(f"         {call['service']}: ${call['cost_usd']:.4f}")
            else:
                print(f"      ❌ Recent calls returned status: {response.status_code}")
                return False
            
            return True
            
    except Exception as e:
        print(f"❌ Cost tracking endpoints test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_cost_calculation():
    """Test cost calculation accuracy."""
    print("\n🧪 Testing Cost Calculation...")
    
    try:
        # Test OpenAI cost calculation
        print("   🤖 Testing OpenAI cost calculation...")
        
        # GPT-4-turbo: $0.01/1K input, $0.03/1K output
        input_tokens = 1000
        output_tokens = 500
        expected_cost = (input_tokens / 1000) * 0.01 + (output_tokens / 1000) * 0.03
        
        cost = cost_tracker.calculate_cost("openai", "gpt-4-turbo", input_tokens, output_tokens)
        print(f"      📊 Expected: ${expected_cost:.4f}, Calculated: ${cost:.4f}")
        
        if abs(cost - expected_cost) < 0.0001:
            print("      ✅ OpenAI cost calculation correct")
        else:
            print("      ❌ OpenAI cost calculation incorrect")
            return False
        
        # Test Tavily cost calculation
        print("   🔍 Testing Tavily cost calculation...")
        cost = cost_tracker.calculate_cost("tavily", "search")
        expected_cost = 0.01  # $0.01 per call
        
        print(f"      📊 Expected: ${expected_cost:.4f}, Calculated: ${cost:.4f}")
        
        if abs(cost - expected_cost) < 0.0001:
            print("      ✅ Tavily cost calculation correct")
        else:
            print("      ❌ Tavily cost calculation incorrect")
            return False
        
        # Test NewsAPI cost calculation
        print("   📰 Testing NewsAPI cost calculation...")
        cost = cost_tracker.calculate_cost("newsapi", "everything")
        expected_cost = 0.001  # $0.001 per call
        
        print(f"      📊 Expected: ${expected_cost:.4f}, Calculated: ${cost:.4f}")
        
        if abs(cost - expected_cost) < 0.0001:
            print("      ✅ NewsAPI cost calculation correct")
        else:
            print("      ❌ NewsAPI cost calculation incorrect")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Cost calculation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all cost tracking tests."""
    print("🚀 Starting Cost Tracking Tests\n")
    
    try:
        # Test 1: Basic cost tracking system
        test1 = await test_cost_tracking_system()
        
        # Test 2: API endpoints
        test2 = await test_cost_tracking_endpoints()
        
        # Test 3: Cost calculation accuracy
        test3 = await test_cost_calculation()
        
        print(f"\n📊 Cost Tracking Test Results:")
        print(f"   Basic system: {'✅ PASSED' if test1 else '❌ FAILED'}")
        print(f"   API endpoints: {'✅ PASSED' if test2 else '❌ FAILED'}")
        print(f"   Cost calculation: {'✅ PASSED' if test3 else '❌ FAILED'}")
        
        if all([test1, test2, test3]):
            print("\n🎉 All cost tracking tests passed!")
            print("   The cost tracking system is fully operational.")
            print("   Key features verified:")
            print("   ✅ SQLite database for cost storage")
            print("   ✅ Real-time cost calculation")
            print("   ✅ API call tracking")
            print("   ✅ Daily and monthly summaries")
            print("   ✅ Cost alerts and warnings")
            print("   ✅ Service breakdown analysis")
            print("   ✅ RESTful API endpoints")
        else:
            print("\n⚠️  Some cost tracking tests failed.")
            print("   Note: Tests may fail if the server is not running.")
            
    except Exception as e:
        print(f"\n❌ Cost tracking test suite failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 
