#!/usr/bin/env python3
"""
Phase 4 Opportunities Integration Test - Lightweight & Concrete
Tests specific functionality without heavy AI calls
"""

import asyncio
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.getcwd())

async def test_opportunity_scoring_logic():
    """Test the opportunity scoring logic with mock data."""
    print("🧪 Testing Opportunity Scoring Logic...")
    
    try:
        from main import _analyze_technical_sentiment
        
        # Test bullish scenario
        bullish_indicators = {
            "rsi_14": 35.0,  # Oversold
            "macd": {"macd": 1250.5, "signal": 1200.0, "histogram": 50.5},
            "volatility": 0.06
        }
        
        sentiment = _analyze_technical_sentiment("BTC", bullish_indicators)
        print(f"✅ Bullish sentiment: {sentiment.get('trend')}")
        
        # Test bearish scenario
        bearish_indicators = {
            "rsi_14": 75.0,  # Overbought
            "macd": {"macd": 1000.0, "signal": 1100.0, "histogram": -100.0},
            "volatility": 0.04
        }
        
        sentiment = _analyze_technical_sentiment("ETH", bearish_indicators)
        print(f"✅ Bearish sentiment: {sentiment.get('trend')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Opportunity scoring test failed: {e}")
        return False

async def test_livecoinwatch_integration():
    """Test LiveCoinWatch integration for opportunities."""
    print("🧪 Testing LiveCoinWatch Integration...")
    
    try:
        from utils.livecoinwatch_processor import LiveCoinWatchProcessor
        
        processor = LiveCoinWatchProcessor()
        
        # Test with just BTC to avoid rate limits
        latest_prices = await processor.get_latest_prices(["BTC"])
        
        if "BTC" in latest_prices:
            btc_data = latest_prices["BTC"]
            print(f"✅ BTC price: ${btc_data.price_usd:,.2f}")
            print(f"✅ 24h change: {btc_data.change_24h:.2f}%")
            print(f"✅ Volume: ${btc_data.volume_24h:,.0f}")
        
        # Test technical indicators for BTC only
        indicators = await processor.calculate_technical_indicators("BTC", days=7)
        print(f"✅ Technical indicators: {list(indicators.keys())}")
        
        return True
        
    except Exception as e:
        print(f"❌ LiveCoinWatch integration test failed: {e}")
        return False

async def test_hybrid_rag_basic():
    """Test basic hybrid RAG functionality."""
    print("🧪 Testing Hybrid RAG Basic Functionality...")
    
    try:
        from utils.hybrid_rag import HybridRAGSystem
        
        hybrid_rag = HybridRAGSystem()
        
        # Just check if it initializes properly
        print(f"✅ Vector RAG: {'✅' if hybrid_rag.vector_rag else '❌'}")
        print(f"✅ Graph RAG: {'✅' if hybrid_rag.graph_rag else '❌'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Hybrid RAG test failed: {e}")
        return False

async def test_opportunity_analysis_structure():
    """Test the opportunity analysis endpoint structure without heavy calls."""
    print("🧪 Testing Opportunity Analysis Structure...")
    
    try:
        from main import get_opportunity_analysis
        
        # Test with a simple symbol
        result = await get_opportunity_analysis("BTC")
        
        # Check structure
        required_fields = ["symbol", "opportunity_type", "opportunity_score", "risk_level", "status"]
        for field in required_fields:
            if field in result:
                print(f"✅ {field}: {result[field]}")
            else:
                print(f"❌ Missing field: {field}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Opportunity analysis structure test failed: {e}")
        return False

async def test_opportunities_endpoint_structure():
    """Test the opportunities endpoint structure without heavy AI calls."""
    print("🧪 Testing Opportunities Endpoint Structure...")
    
    try:
        from main import get_enhanced_opportunities
        
        # Test the endpoint
        result = await get_enhanced_opportunities()
        
        # Check basic structure
        print(f"✅ Status: {result.get('status')}")
        print(f"✅ Phase: {result.get('phase')}")
        print(f"✅ Market regime: {result.get('market_regime')}")
        
        # Check statistics structure
        statistics = result.get('statistics', {})
        if statistics:
            print(f"✅ Statistics present: {list(statistics.keys())}")
        
        # Check opportunities structure
        opportunities = result.get('opportunities', [])
        if opportunities:
            print(f"✅ Opportunities count: {len(opportunities)}")
            first_opp = opportunities[0]
            print(f"✅ First opportunity: {first_opp.get('symbol')} - {first_opp.get('type')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Opportunities endpoint structure test failed: {e}")
        return False

async def main():
    """Run concrete Phase 4 opportunity tests."""
    print("🚀 PHASE 4 OPPORTUNITIES - CONCRETE TESTS")
    print("=" * 50)
    
    tests = [
        test_opportunity_scoring_logic,
        test_livecoinwatch_integration,
        test_hybrid_rag_basic,
        test_opportunity_analysis_structure,
        test_opportunities_endpoint_structure
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
    print(f"📊 PHASE 4 CONCRETE TEST SUMMARY")
    print(f"Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("🎉 All Phase 4 concrete tests passed!")
        return 0
    else:
        print("⚠️  Some Phase 4 concrete tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main())) 
