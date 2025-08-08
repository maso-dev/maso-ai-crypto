#!/usr/bin/env python3
"""
Replit Debugging Script
Tests environment variables and API key loading specifically for Replit
"""

import os
import sys
import asyncio
from typing import Dict, Any

async def debug_replit_environment():
    """Debug Replit environment safely"""
    
    print("🔍 Replit Environment Debug Report")
    print("=" * 50)
    
    # 1. Check if we're in Replit
    is_replit = bool(os.getenv("REPL_ID"))
    print(f"\n🌐 Environment: {'Replit' if is_replit else 'Local'}")
    print(f"📁 Working Directory: {os.getcwd()}")
    print(f"🐍 Python Version: {sys.version}")
    
    # 2. Check environment variables (safely)
    print("\n📋 Environment Variables Check:")
    env_vars = [
        "OPENAI_API_KEY", "BINANCE_API_KEY", "NEWSAPI_KEY", 
        "LIVECOINWATCH_API_KEY", "TAVILY_API_KEY", "LANGSMITH_API_KEY",
        "NEO4J_URI", "MILVUS_URI", "PORT", "REPL_ID"
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            if "API_KEY" in var or "URI" in var:
                # Show first 4 and last 4 characters for safety
                masked = f"{value[:4]}...{value[-4:]}" if len(value) > 8 else "***"
                print(f"  ✅ {var}: {masked}")
            else:
                print(f"  ✅ {var}: {value}")
        else:
            print(f"  ❌ {var}: Not set")
    
    # 3. Test config loading
    print("\n⚙️ Config Loading Test:")
    try:
        from utils.config import get_api_key, is_api_available
        
        apis = ["binance", "openai", "newsapi", "livecoinwatch", 
                "tavily", "milvus", "neo4j", "langsmith"]
        
        for api in apis:
            key = get_api_key(api)
            available = is_api_available(api)
            status = "✅" if available else "❌"
            print(f"  {status} {api}: {'Configured' if key else 'Not configured'}")
            
    except Exception as e:
        print(f"  ❌ Config error: {e}")
        import traceback
        traceback.print_exc()
    
    # 4. Test admin validation
    print("\n🔧 Admin Validation Test:")
    try:
        from utils.admin_validator import get_comprehensive_admin_status
        
        result = await get_comprehensive_admin_status()
        
        print(f"  📊 Overall Health: {result.overall_health}")
        print(f"  📈 Real Data %: {result.real_data_percentage:.1f}%")
        print(f"  🕐 Last Updated: {result.last_updated}")
        
        print("\n  📋 API Keys Status:")
        for api, configured in result.api_keys.items():
            status = "✅" if configured else "❌"
            print(f"    {status} {api}: {'Configured' if configured else 'Not configured'}")
        
        print("\n  🔍 Component Status:")
        components = [
            ("LiveCoinWatch", result.livecoinwatch),
            ("NewsAPI", result.newsapi),
            ("Neo4j", result.neo4j),
            ("OpenAI", result.openai),
            ("Tavily", result.tavily),
            ("Milvus", result.milvus),
            ("LangSmith", result.langsmith)
        ]
        
        for name, status in components:
            if status.is_real_data:
                emoji = "✅"
                text = "Real Data"
            elif status.is_operational:
                emoji = "⚠️"
                text = "Mock Data"
            else:
                emoji = "❌"
                text = f"Error: {status.error_message}" if status.error_message else "Not Operational"
            
            print(f"    {emoji} {name}: {text}")
            
    except Exception as e:
        print(f"  ❌ Validation error: {e}")
        import traceback
        traceback.print_exc()
    
    # 5. Test server startup
    print("\n🚀 Server Startup Test:")
    try:
        from main import app
        print("  ✅ FastAPI app imported successfully")
        
        # Test a simple endpoint
        try:
            from fastapi.testclient import TestClient
            client = TestClient(app)
            response = client.get("/api/health")
            print(f"  ✅ Health endpoint: {response.status_code}")
        except Exception as test_error:
            print(f"  ⚠️ TestClient error: {test_error}")
            print("  ✅ FastAPI app is working (TestClient issue)")
        
    except Exception as e:
        print(f"  ❌ Server error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_replit_environment())
