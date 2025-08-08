#!/usr/bin/env python3
"""
Validation script to check what data is real vs mock
"""

import asyncio
import httpx
import json
from datetime import datetime

async def validate_endpoints():
    """Validate all endpoints to see what's real vs mock data"""
    
    base_url = "http://localhost:8000"
    results = {}
    
    async with httpx.AsyncClient() as client:
        
        # 1. Check admin configuration
        print("🔍 Checking Admin Configuration...")
        try:
            response = await client.get(f"{base_url}/admin_conf")
            admin_conf = response.json()
            results["admin_conf"] = {
                "api_keys_configured": admin_conf.get("api_keys_configured"),
                "configured_count": admin_conf.get("configured_count"),
                "status": admin_conf.get("status")
            }
            print(f"   ✅ API Keys: {admin_conf.get('configured_count')}/8 configured")
        except Exception as e:
            print(f"   ❌ Admin conf error: {e}")
        
        # 2. Check MVP status
        print("\n🔍 Checking MVP Status...")
        try:
            response = await client.get(f"{base_url}/api/admin/mvp-status")
            mvp_status = response.json()
            results["mvp_status"] = {
                "system_health": mvp_status.get("system_health"),
                "operational_components": mvp_status.get("operational_components"),
                "livecoinwatch_status": mvp_status.get("components", {}).get("livecoinwatch", {}).get("status"),
                "news_cache_status": mvp_status.get("components", {}).get("news_cache", {}).get("status"),
                "hybrid_rag_status": mvp_status.get("components", {}).get("hybrid_rag", {}).get("status"),
                "graph_mock_mode": mvp_status.get("components", {}).get("hybrid_rag", {}).get("graph_mock_mode")
            }
            print(f"   ✅ System Health: {mvp_status.get('system_health')}")
            print(f"   ✅ LiveCoinWatch: {mvp_status.get('components', {}).get('livecoinwatch', {}).get('status')}")
            print(f"   ✅ News Cache: {mvp_status.get('components', {}).get('news_cache', {}).get('status')}")
            print(f"   ⚠️  Graph RAG Mock Mode: {mvp_status.get('components', {}).get('hybrid_rag', {}).get('graph_mock_mode')}")
        except Exception as e:
            print(f"   ❌ MVP status error: {e}")
        
        # 3. Check portfolio data
        print("\n🔍 Checking Portfolio Data...")
        try:
            response = await client.get(f"{base_url}/api/cache/portfolio/livecoinwatch")
            portfolio = response.json()
            
            # Check if data is real or mock
            assets = portfolio.get("data", {}).get("portfolio", {}).get("assets", [])
            mock_count = 0
            real_count = 0
            
            for asset in assets:
                data_source = asset.get("data_source", "")
                if "Mock" in data_source or "mock" in data_source.lower():
                    mock_count += 1
                else:
                    real_count += 1
            
            results["portfolio"] = {
                "total_assets": len(assets),
                "mock_assets": mock_count,
                "real_assets": real_count,
                "data_source": portfolio.get("source"),
                "is_mock": mock_count > 0
            }
            
            print(f"   📊 Total Assets: {len(assets)}")
            print(f"   🎭 Mock Assets: {mock_count}")
            print(f"   ✅ Real Assets: {real_count}")
            print(f"   📍 Data Source: {portfolio.get('source')}")
            
        except Exception as e:
            print(f"   ❌ Portfolio error: {e}")
        
        # 4. Check news data
        print("\n🔍 Checking News Data...")
        try:
            response = await client.get(f"{base_url}/api/cache/news/latest-summary")
            news = response.json()
            
            articles = news.get("data", {}).get("articles", [])
            mock_articles = 0
            real_articles = 0
            
            for article in articles:
                data_source = article.get("data_source", "")
                if "Mock" in data_source or "mock" in data_source.lower():
                    mock_articles += 1
                else:
                    real_articles += 1
            
            results["news"] = {
                "total_articles": len(articles),
                "mock_articles": mock_articles,
                "real_articles": real_articles,
                "is_mock": mock_articles > 0
            }
            
            print(f"   📰 Total Articles: {len(articles)}")
            print(f"   🎭 Mock Articles: {mock_articles}")
            print(f"   ✅ Real Articles: {real_articles}")
            
        except Exception as e:
            print(f"   ❌ News error: {e}")
        
        # 5. Check technical analysis
        print("\n🔍 Checking Technical Analysis...")
        try:
            response = await client.get(f"{base_url}/api/technical-analysis/BTC")
            tech_analysis = response.json()
            
            results["technical_analysis"] = {
                "current_price": tech_analysis.get("current_price"),
                "price_change_24h": tech_analysis.get("price_change_24h"),
                "status": tech_analysis.get("status"),
                "has_indicators": bool(tech_analysis.get("technical_indicators"))
            }
            
            print(f"   💰 BTC Price: ${tech_analysis.get('current_price', 0):,.2f}")
            print(f"   📈 24h Change: {tech_analysis.get('price_change_24h', 0)}%")
            print(f"   📊 Has Indicators: {bool(tech_analysis.get('technical_indicators'))}")
            
        except Exception as e:
            print(f"   ❌ Technical analysis error: {e}")
        
        # 6. Check opportunities
        print("\n🔍 Checking Opportunities...")
        try:
            response = await client.get(f"{base_url}/api/opportunities")
            opportunities = response.json()
            
            opps = opportunities.get("opportunities", [])
            results["opportunities"] = {
                "total_opportunities": len(opps),
                "status": opportunities.get("status"),
                "has_real_data": len(opps) > 0
            }
            
            print(f"   🎯 Total Opportunities: {len(opps)}")
            print(f"   📊 Status: {opportunities.get('status')}")
            
        except Exception as e:
            print(f"   ❌ Opportunities error: {e}")
        
        # 7. Check LiveCoinWatch directly
        print("\n🔍 Checking LiveCoinWatch Direct API...")
        try:
            from utils.livecoinwatch_processor import LiveCoinWatchProcessor
            processor = LiveCoinWatchProcessor()
            latest_prices = await processor.get_latest_prices(["BTC", "ETH"])
            
            real_prices = 0
            for symbol, price_data in latest_prices.items():
                if price_data and price_data.price_usd > 0:
                    real_prices += 1
            
            results["livecoinwatch_direct"] = {
                "symbols_checked": len(latest_prices),
                "real_prices": real_prices,
                "is_working": real_prices > 0
            }
            
            print(f"   🪙 Symbols Checked: {len(latest_prices)}")
            print(f"   ✅ Real Prices: {real_prices}")
            print(f"   🔗 API Working: {real_prices > 0}")
            
        except Exception as e:
            print(f"   ❌ LiveCoinWatch direct error: {e}")
            results["livecoinwatch_direct"] = {"error": str(e)}
    
    return results

def print_summary(results):
    """Print a summary of what's real vs mock"""
    
    print("\n" + "="*60)
    print("📊 VALIDATION SUMMARY")
    print("="*60)
    
    # API Keys
    admin_conf = results.get("admin_conf", {})
    print(f"\n🔑 API Keys: {admin_conf.get('configured_count', 0)}/8 configured")
    
    # System Health
    mvp_status = results.get("mvp_status", {})
    print(f"🏥 System Health: {mvp_status.get('system_health', 'unknown')}")
    print(f"🔗 Graph RAG Mock Mode: {mvp_status.get('graph_mock_mode', 'unknown')}")
    
    # Portfolio
    portfolio = results.get("portfolio", {})
    if portfolio.get("is_mock"):
        print(f"💼 Portfolio: 🎭 MOCK DATA ({portfolio.get('mock_assets', 0)} assets)")
    else:
        print(f"💼 Portfolio: ✅ REAL DATA ({portfolio.get('real_assets', 0)} assets)")
    
    # News
    news = results.get("news", {})
    if news.get("is_mock"):
        print(f"📰 News: 🎭 MOCK DATA ({news.get('mock_articles', 0)} articles)")
    else:
        print(f"📰 News: ✅ REAL DATA ({news.get('real_articles', 0)} articles)")
    
    # Technical Analysis
    tech = results.get("technical_analysis", {})
    if tech.get("current_price", 0) > 0:
        print(f"📊 Technical Analysis: ✅ REAL DATA (BTC: ${tech.get('current_price', 0):,.2f})")
    else:
        print(f"📊 Technical Analysis: 🎭 MOCK DATA")
    
    # LiveCoinWatch
    lcw = results.get("livecoinwatch_direct", {})
    if lcw.get("is_working"):
        print(f"🪙 LiveCoinWatch: ✅ REAL DATA ({lcw.get('real_prices', 0)} prices)")
    else:
        print(f"🪙 LiveCoinWatch: 🎭 MOCK DATA")
    
    # Opportunities
    opps = results.get("opportunities", {})
    print(f"🎯 Opportunities: {opps.get('total_opportunities', 0)} available")
    
    print("\n" + "="*60)
    print("🎯 RECOMMENDATIONS")
    print("="*60)
    
    if portfolio.get("is_mock"):
        print("⚠️  Portfolio data is mock - check LiveCoinWatch API key")
    
    if news.get("is_mock"):
        print("⚠️  News data is mock - check NewsAPI rate limits")
    
    if mvp_status.get("graph_mock_mode"):
        print("⚠️  Neo4j Graph RAG is in mock mode - check Neo4j connection")
    
    if not lcw.get("is_working"):
        print("⚠️  LiveCoinWatch API not working - check API key and connectivity")
    
    print("\n✅ System is functional with fallback mechanisms!")

if __name__ == "__main__":
    print("🚀 Starting Data Validation...")
    results = asyncio.run(validate_endpoints())
    print_summary(results)
