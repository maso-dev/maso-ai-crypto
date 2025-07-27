#!/usr/bin/env python3
"""
Test script for the Agent Decision Engine
"""

import asyncio
import os
from datetime import datetime, timezone
from utils.simple_agent import SimpleAgentEngine, PortfolioData, PortfolioAsset
from utils.binance_client import PortfolioAsset as BinancePortfolioAsset

async def test_agent_engine():
    """Test the agent decision engine with mock data."""
    
    print("🧠 Testing Agent Decision Engine...")
    
    # Create mock portfolio data
    mock_assets = [
        BinancePortfolioAsset(
            asset="BTC",
            free=0.5,
            locked=0.0,
            total=0.5,
            usdt_value=25000.0,
            cost_basis=20000.0,
            roi_percentage=25.0,
            avg_buy_price=40000.0
        ),
        BinancePortfolioAsset(
            asset="ETH",
            free=2.0,
            locked=0.0,
            total=2.0,
            usdt_value=8000.0,
            cost_basis=6000.0,
            roi_percentage=33.3,
            avg_buy_price=3000.0
        ),
        BinancePortfolioAsset(
            asset="ADA",
            free=1000.0,
            locked=0.0,
            total=1000.0,
            usdt_value=500.0,
            cost_basis=800.0,
            roi_percentage=-37.5,
            avg_buy_price=0.8
        )
    ]
    
    mock_portfolio = PortfolioData(
        total_value_usdt=33500.0,
        total_cost_basis=26800.0,
        total_roi_percentage=25.0,
        assets=mock_assets,
        last_updated=datetime.now(timezone.utc),
        trade_history=[]
    )
    
    print(f"📊 Mock Portfolio Created:")
    print(f"   Total Value: ${mock_portfolio.total_value_usdt:,.2f}")
    print(f"   Total Cost Basis: ${mock_portfolio.total_cost_basis:,.2f}")
    print(f"   Total ROI: {mock_portfolio.total_roi_percentage:.2f}%")
    print(f"   Assets: {len(mock_portfolio.assets)}")
    
    try:
        # Initialize agent engine
        agent = SimpleAgentEngine()
        print("✅ Agent Engine initialized successfully")
        
        # Test portfolio analysis
        print("\n🔍 Testing Portfolio Analysis...")
        mock_news = [
            {
                "title": "Bitcoin reaches new highs",
                "sentiment": 0.8,
                "crypto_topic": "BTC"
            },
            {
                "title": "Ethereum upgrade successful",
                "sentiment": 0.7,
                "crypto_topic": "ETH"
            }
        ]
        
        analysis = agent.analyze_portfolio(mock_portfolio)
        print(f"✅ Portfolio Analysis Complete:")
        print(f"   Market Regime: {analysis.market_regime.value}")
        print(f"   Risk Score: {analysis.portfolio_risk_score:.2f}")
        print(f"   Diversification: {analysis.diversification_score:.2f}")
        print(f"   Rebalancing Needed: {analysis.rebalancing_needed}")
        
        # Test recommendation generation
        print("\n💡 Testing Recommendation Generation...")
        recommendations = agent.generate_recommendations(analysis, mock_portfolio)
        print(f"✅ Generated {len(recommendations)} recommendations:")
        
        for i, rec in enumerate(recommendations[:3], 1):
            print(f"   {i}. {rec.action_type.value} {rec.asset}")
            print(f"      Reason: {rec.reason[:100]}...")
            print(f"      Confidence: {rec.confidence_score:.2f}")
            print(f"      Risk: {rec.risk_level.value}")
            print(f"      Personal Context: {rec.personal_context[:80]}...")
            print()
        
        # Test complete analysis
        print("🎯 Testing Complete Agent Analysis...")
        complete_analysis = agent.generate_complete_analysis(mock_portfolio)
        print(f"✅ Complete Analysis Generated:")
        print(f"   Overall Confidence: {complete_analysis.confidence_overall:.2f}")
        print(f"   Market Summary: {complete_analysis.market_summary[:100]}...")
        print(f"   Risk Assessment: {complete_analysis.risk_assessment[:100]}...")
        print(f"   Next Actions: {complete_analysis.next_actions}")
        
        print("\n🎉 Agent Decision Engine Test PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Agent Decision Engine Test FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_agent_endpoints():
    """Test the agent API endpoints."""
    
    print("\n🌐 Testing Agent API Endpoints...")
    
    import httpx
    
    async with httpx.AsyncClient() as client:
        try:
            # Test insights endpoint
            response = await client.get("http://127.0.0.1:8000/agent/insights")
            if response.status_code == 200:
                data = response.json()
                print("✅ /agent/insights endpoint working")
                print(f"   Portfolio Performance: ${data['portfolio_performance']['total_value']:,.2f}")
                print(f"   Market Regime: {data['market_analysis']['regime']}")
                print(f"   Opportunities: {len(data['opportunities'])}")
                print(f"   Warnings: {len(data['warnings'])}")
            else:
                print(f"❌ /agent/insights failed: {response.status_code}")
            
            # Test recommendations endpoint
            response = await client.get("http://127.0.0.1:8000/agent/recommendations?limit=3")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ /agent/recommendations endpoint working: {len(data)} recommendations")
            else:
                print(f"❌ /agent/recommendations failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ API endpoint test failed: {str(e)}")

if __name__ == "__main__":
    # Set up environment
    os.environ.setdefault("OPENAI_API_KEY", "test-key")
    
    # Run tests
    asyncio.run(test_agent_engine())
    asyncio.run(test_agent_endpoints()) 
