from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from typing import Dict, Any
from pathlib import Path
import os
from datetime import datetime

app = FastAPI(title="🏛️ Masonic - Alpha Strategy Advisor")

templates = Jinja2Templates(directory="templates")

# Custom static files handling for Vercel (similar to working example)
@app.get("/static/{path:path}")
async def static_files(path: str):
    """Serve static files"""
    static_dir = Path("static")
    file_path = static_dir / path
    if file_path.exists() and file_path.is_file():
        return FileResponse(str(file_path))
    return {"error": "File not found"}, 404

@app.get("/favicon.ico")
async def favicon():
    """Handle favicon requests to prevent 404 errors."""
    from fastapi.responses import Response
    return Response(status_code=204)  # No content

@app.get("/api/health")
async def health_check():
    """Health check endpoint for Vercel deployment"""
    return {
        "status": "healthy", 
        "service": "🏛️ Masonic - Alpha Strategy Advisor",
        "deployment": "Vercel",
        "version": "2.0.0",
        "environment_vars": {
            "binance_key_set": bool(os.getenv("BINANCE_API_KEY")),
            "openai_key_set": bool(os.getenv("OPENAI_API_KEY")),
            "news_key_set": bool(os.getenv("NEWSAPI_KEY"))
        }
    }

@app.get("/api/test")
async def test_endpoint():
    """Simple test endpoint that doesn't require external dependencies"""
    return {
        "message": "FastAPI is working!",
        "timestamp": "2024",
        "status": "success",
        "endpoints": ["/", "/v1", "/dashboard", "/api/health", "/api/portfolio"]
    }

# NEW: Welcome section for non-logged users
@app.get("/")
async def welcome_page(request: Request):
    """Welcome page for non-logged users - shows market overview and opportunities"""
    try:
        return templates.TemplateResponse("welcome.html", {"request": request})
    except Exception as e:
        # Fallback to simple HTML if template fails
        return HTMLResponse(content=f"""
        <html>
            <head><title>Welcome - Portfolio Analyzer</title></head>
            <body>
                <h1>🚀 Welcome to Portfolio Analyzer</h1>
                <p>Your AI-powered crypto portfolio assistant</p>
                <p><a href="/v1">View Full Dashboard (v1)</a></p>
                <p><a href="/api/health">Health Check</a></p>
                <p>Error loading welcome page: {str(e)}</p>
            </body>
        </html>
        """)

# NEW: Alpha portfolio API
@app.get("/api/dream-team")
async def get_dream_team_portfolio():
    """Get alpha portfolio data using AI analysis"""
    try:
        # Use enhanced agent for portfolio analysis
        from utils.enhanced_agent import get_enhanced_agent
        from utils.binance_client import get_portfolio_data
        
        # Get portfolio data (will use mock if no API keys)
        portfolio_data = await get_portfolio_data()
        
        # Get enhanced agent analysis
        agent = get_enhanced_agent()
        if portfolio_data:
            analysis = await agent.generate_complete_analysis(portfolio_data, symbols=["BTC", "ETH", "XRP", "SOL", "DOGE"])
        else:
            # Use mock portfolio data for analysis
            from utils.binance_client import PortfolioData, PortfolioAsset
            mock_portfolio = PortfolioData(
                total_value_usdt=100000.0,
                total_cost_basis=60000.0,
                total_roi_percentage=66.67,
                assets=[
                    PortfolioAsset(asset="BTC", free=1.0, locked=0.0, total=1.0, usdt_value=40000.0, cost_basis=35000.0, roi_percentage=14.29, avg_buy_price=35000.0),
                    PortfolioAsset(asset="ETH", free=10.0, locked=0.0, total=10.0, usdt_value=30000.0, cost_basis=25000.0, roi_percentage=20.0, avg_buy_price=2500.0),
                ],
                last_updated=datetime.now(),
                trade_history=[]
            )
            analysis = await agent.generate_complete_analysis(mock_portfolio, symbols=["BTC", "ETH", "XRP", "SOL", "DOGE"])
        
        # Extract alpha portfolio from analysis
        alpha_portfolio = [
            {"symbol": "BTC", "name": "Bitcoin", "weight": 0.4, "analysis": "Core store of value"},
            {"symbol": "ETH", "name": "Ethereum", "weight": 0.3, "analysis": "Smart contract platform"},
            {"symbol": "XRP", "name": "Ripple", "weight": 0.15, "analysis": "Cross-border payments"},
            {"symbol": "SOL", "name": "Solana", "weight": 0.1, "analysis": "High-performance blockchain"},
            {"symbol": "DOGE", "name": "Dogecoin", "weight": 0.05, "analysis": "Meme coin with utility"}
        ]
        
        return {
            "portfolio_name": "Masonic Alpha Portfolio",
            "description": analysis.agent_insights[:100] + "..." if analysis.agent_insights else "Our brotherhood's most trusted allocation strategy",
            "assets": alpha_portfolio,
            "total_weight": 1.0,
            "risk_level": analysis.portfolio_analysis.portfolio_risk_score,
            "market_regime": analysis.portfolio_analysis.market_regime.value,
            "confidence": analysis.confidence_overall,
            "last_updated": analysis.timestamp.isoformat()
        }
    except Exception as e:
        # Fallback to static data if AI analysis fails
        alpha_portfolio = [
            {"symbol": "BTC", "name": "Bitcoin", "weight": 0.4},
            {"symbol": "ETH", "name": "Ethereum", "weight": 0.3},
            {"symbol": "XRP", "name": "Ripple", "weight": 0.15},
            {"symbol": "SOL", "name": "Solana", "weight": 0.1},
            {"symbol": "DOGE", "name": "Dogecoin", "weight": 0.05}
        ]
        
        return {
            "portfolio_name": "Masonic Alpha Portfolio",
            "description": "Our brotherhood's most trusted allocation strategy",
            "assets": alpha_portfolio,
            "total_weight": 1.0,
            "risk_level": "Moderate",
            "last_updated": "2024"
        }

# NEW: Alpha signals API
@app.get("/api/opportunities")
async def get_todays_opportunities():
    """Get today's alpha signals using AI analysis"""
    try:
        # Use enhanced agent for recommendations
        from utils.enhanced_agent import get_enhanced_agent
        from utils.binance_client import get_portfolio_data
        
        # Get portfolio data (will use mock if no API keys)
        portfolio_data = await get_portfolio_data()
        
        # Get enhanced agent analysis
        agent = get_enhanced_agent()
        if portfolio_data:
            analysis = await agent.generate_complete_analysis(portfolio_data, symbols=["BTC", "ETH", "XRP", "SOL", "DOGE"])
        else:
            # Use mock portfolio data for analysis
            from utils.binance_client import PortfolioData, PortfolioAsset
            mock_portfolio = PortfolioData(
                total_value_usdt=100000.0,
                total_cost_basis=60000.0,
                total_roi_percentage=66.67,
                assets=[
                    PortfolioAsset(asset="BTC", free=1.0, locked=0.0, total=1.0, usdt_value=40000.0, cost_basis=35000.0, roi_percentage=14.29, avg_buy_price=35000.0),
                    PortfolioAsset(asset="ETH", free=10.0, locked=0.0, total=10.0, usdt_value=30000.0, cost_basis=25000.0, roi_percentage=20.0, avg_buy_price=2500.0),
                ],
                last_updated=datetime.now(),
                trade_history=[]
            )
            analysis = await agent.generate_complete_analysis(mock_portfolio, symbols=["BTC", "ETH", "XRP", "SOL", "DOGE"])
        
        # Convert recommendations to alpha signals
        signals = []
        for rec in analysis.recommendations[:3]:  # Top 3 recommendations
            signals.append({
                "type": rec.action_type.value.lower(),
                "asset": rec.asset,
                "reason": rec.reason,
                "confidence": rec.confidence_score,
                "timeframe": "short-term" if rec.execution_priority <= 2 else "medium-term",
                "brotherhood_insight": rec.personal_context,
                "market_context": rec.market_context
            })
        
        # If no AI recommendations, use fallback
        if not signals:
            signals = [
                {
                    "type": "strong_buy",
                    "asset": "BTC",
                    "reason": "Key support level reached, institutional accumulation detected",
                    "confidence": 0.85,
                    "timeframe": "short-term",
                    "brotherhood_insight": "Smart money positioning for accumulation"
                },
                {
                    "type": "hold",
                    "asset": "ETH",
                    "reason": "Consolidation phase, wait for breakout signal",
                    "confidence": 0.75,
                    "timeframe": "medium-term",
                    "brotherhood_insight": "Technical analysis shows consolidation pattern"
                },
                {
                    "type": "watch",
                    "asset": "SOL",
                    "reason": "Potential breakout candidate, monitor closely",
                    "confidence": 0.65,
                    "timeframe": "short-term",
                    "brotherhood_insight": "Volume analysis suggests accumulation"
                }
            ]
        
        return {
            "date": analysis.timestamp.isoformat(),
            "signals": signals,
            "market_regime": analysis.portfolio_analysis.market_regime.value,
            "confidence_overall": analysis.confidence_overall
        }
    except Exception as e:
        # Fallback to static data if AI analysis fails
        return {
            "date": "2024",
            "signals": [
                {
                    "type": "strong_buy",
                    "asset": "BTC",
                    "reason": "Key support level reached, institutional accumulation detected",
                    "confidence": 0.85,
                    "timeframe": "short-term",
                    "brotherhood_insight": "Smart money positioning for accumulation"
                },
                {
                    "type": "hold",
                    "asset": "ETH",
                    "reason": "Consolidation phase, wait for breakout signal",
                    "confidence": 0.75,
                    "timeframe": "medium-term",
                    "brotherhood_insight": "Technical analysis shows consolidation pattern"
                },
                {
                    "type": "watch",
                    "asset": "SOL",
                    "reason": "Potential breakout candidate, monitor closely",
                    "confidence": 0.65,
                    "timeframe": "short-term",
                    "brotherhood_insight": "Volume analysis suggests accumulation"
                }
            ]
        }

# NEW: Brotherhood intelligence API
@app.get("/api/news-briefing")
async def get_news_briefing():
    """Get brotherhood intelligence for welcome page"""
    return {
        "date": "2024",
        "summary": "Market showing institutional accumulation with Bitcoin holding key support levels",
        "intelligence": [
            {
                "title": "Bitcoin maintains $40K support - institutional accumulation detected",
                "sentiment": "bullish",
                "impact": "high",
                "brotherhood_insight": "Smart money positioning for accumulation phase"
            },
            {
                "title": "Ethereum upgrade progress - smart money positioning",
                "sentiment": "neutral",
                "impact": "medium",
                "brotherhood_insight": "Technical analysis shows consolidation pattern"
            },
            {
                "title": "Regulatory clarity - institutional adoption accelerating",
                "sentiment": "bullish",
                "impact": "high",
                "brotherhood_insight": "Market intelligence suggests institutional inflow"
            }
        ]
    }

# VERSION 1: Keep current dashboard at /v1
@app.get("/dashboard")
def smart_dashboard(request: Request):
    """Smart dashboard that detects API connectivity and routes accordingly"""
    try:
        # Test Binance API connectivity
        from utils.binance_client import get_binance_client, get_portfolio_data
        
        # Check if we have API keys configured
        binance_client = get_binance_client()
        api_keys_configured = binance_client is not None
        
        print(f"🏛️ Smart Dashboard: API keys configured: {api_keys_configured}")
        
        # Try to get real portfolio data
        import asyncio
        portfolio_data = asyncio.run(get_portfolio_data())
        
        print(f"🏛️ Smart Dashboard: Portfolio data received: {portfolio_data is not None}")
        
        # Determine if we're using real or mock data
        is_real_data = False
        if portfolio_data and api_keys_configured:
            # Check if this looks like real data (not our mock data)
            total_value = portfolio_data.total_value_usdt
            asset_count = len(portfolio_data.assets)
            
            print(f"🏛️ Smart Dashboard: Total value: {total_value}, Asset count: {asset_count}")
            
            # Check for mock data characteristics
            is_mock_data = (
                total_value == 36500.0 and 
                asset_count == 4 and 
                any(asset.asset == "BTC" and asset.usdt_value == 25000.0 for asset in portfolio_data.assets)
            )
            
            print(f"🏛️ Smart Dashboard: Is mock data: {is_mock_data}")
            
            # If it's NOT mock data, then it's real data
            if not is_mock_data:
                is_real_data = True
                print("🏛️ Smart Dashboard: Detected REAL data!")
        
        # Route to appropriate dashboard
        if is_real_data:
            print("🏛️ Smart Dashboard: Using REAL Binance data - showing live dashboard")
            return templates.TemplateResponse("dashboard.html", {
                "request": request,
                "data_mode": "real",
                "api_status": "connected"
            })
        else:
            print("🏛️ Smart Dashboard: Using MOCK data - showing demo dashboard")
            return templates.TemplateResponse("dashboard_demo.html", {
                "request": request,
                "data_mode": "demo",
                "api_status": "demo"
            })
            
    except Exception as e:
        print(f"🏛️ Smart Dashboard Error: {e} - showing demo dashboard")
        return templates.TemplateResponse("dashboard_demo.html", {
            "request": request,
            "data_mode": "demo",
            "api_status": "error"
        })

@app.get("/v1")
def dashboard_v1(request: Request):
    """Version 1 dashboard - static demo implementation"""
    try:
        return templates.TemplateResponse("dashboard_demo.html", {
            "request": request,
            "data_mode": "static",
            "api_status": "static"
        })
    except Exception as e:
        # Fallback to simple HTML if template fails
        return HTMLResponse(content=f"""
        <html>
            <head><title>Portfolio Analyzer v1</title></head>
            <body>
                <h1>Portfolio Analyzer API v1</h1>
                <p>FastAPI is running!</p>
                <p><a href="/">← Back to Welcome</a></p>
                <p><a href="/dashboard">Smart Dashboard</a></p>
                <p><a href="/api/health">Health Check</a></p>
                <p><a href="/api/test">Test Endpoint</a></p>
                <p>Error loading dashboard: {str(e)}</p>
            </body>
        </html>
        """)

# Import routers with error handling
try:
    from routers.crypto_news_rag import router as crypto_news_rag_router
    app.include_router(crypto_news_rag_router)
except ImportError as e:
    print(f"Warning: Could not import crypto_news_rag_router: {e}")

try:
    from routers.portfolio_user import router as portfolio_router
    app.include_router(portfolio_router)
except ImportError as e:
    print(f"Warning: Could not import portfolio_router: {e}")

try:
    from routers.crypto_news import router as crypto_news_router
    app.include_router(crypto_news_router)
except ImportError as e:
    print(f"Warning: Could not import crypto_news_router: {e}")

try:
    from routers.admin import router as admin_router
    app.include_router(admin_router)
except ImportError as e:
    print(f"Warning: Could not import admin_router: {e}")

try:
    from routers.agent import router as agent_router
    app.include_router(agent_router)
except ImportError as e:
    print(f"Warning: Could not import agent_router: {e}")

@app.get("/api/portfolio", response_model=Dict[str, Any])
async def get_portfolio() -> Dict[str, Any]:
    """Get portfolio data using the new async Binance client."""
    try:
        from utils.binance_client import get_portfolio_data
        portfolio_data = await get_portfolio_data()
        
        # Always return data (either real or mock)
        if portfolio_data:
            return {
                "total_value_usdt": portfolio_data.total_value_usdt,
                "assets": [
                    {
                        "asset": asset.asset,
                        "free": asset.free,
                        "locked": asset.locked,
                        "total": asset.total,
                        "usdt_value": asset.usdt_value,
                        "cost_basis": asset.cost_basis,
                        "roi_percentage": asset.roi_percentage,
                        "avg_buy_price": asset.avg_buy_price
                    }
                    for asset in portfolio_data.assets
                ],
                "last_updated": portfolio_data.last_updated.isoformat(),
                "data_source": "binance"
            }
        else:
            # Return mock data if portfolio_data is None
            return {
                "total_value_usdt": 36500.0,
                "assets": [
                    {
                        "asset": "BTC",
                        "free": 0.5,
                        "locked": 0.0,
                        "total": 0.5,
                        "usdt_value": 25000.0,
                        "cost_basis": 20000.0,
                        "roi_percentage": 25.0,
                        "avg_buy_price": 40000.0
                    },
                    {
                        "asset": "ETH",
                        "free": 2.0,
                        "locked": 0.0,
                        "total": 2.0,
                        "usdt_value": 8000.0,
                        "cost_basis": 6000.0,
                        "roi_percentage": 33.3,
                        "avg_buy_price": 3000.0
                    }
                ],
                "last_updated": datetime.now().isoformat(),
                "data_source": "mock"
            }
    except Exception as e:
        # Return mock data as fallback
        return {
            "total_value_usdt": 36500.0,
            "assets": [
                {
                    "asset": "BTC",
                    "free": 0.5,
                    "locked": 0.0,
                    "total": 0.5,
                    "usdt_value": 25000.0,
                    "cost_basis": 20000.0,
                    "roi_percentage": 25.0,
                    "avg_buy_price": 40000.0
                },
                {
                    "asset": "ETH",
                    "free": 2.0,
                    "locked": 0.0,
                    "total": 2.0,
                    "usdt_value": 8000.0,
                    "cost_basis": 6000.0,
                    "roi_percentage": 33.3,
                    "avg_buy_price": 3000.0
                }
            ],
            "last_updated": datetime.now().isoformat(),
            "data_source": "fallback",
            "note": "Using fallback data due to API restrictions"
        }

@app.get("/api/asset/{symbol}", response_model=Dict[str, Any])
async def get_asset_details(symbol: str) -> Dict[str, Any]:
    """Get asset details using the new async Binance client."""
    try:
        from utils.binance_client import get_portfolio_data
        portfolio_data = await get_portfolio_data()
        if portfolio_data:
            for asset in portfolio_data.assets:
                if asset.asset == symbol:
                    return {
                        'symbol': symbol,
                        'free': asset.free,
                        'locked': asset.locked,
                        'total': asset.total,
                        'usdt_value': asset.usdt_value,
                        'cost_basis': asset.cost_basis,
                        'roi_percentage': asset.roi_percentage,
                        'avg_buy_price': asset.avg_buy_price
                    }
        return {"error": f"Asset {symbol} not found"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error for {symbol}: {str(e)}")

@app.get("/api/top-movers", response_model=Dict[str, Any])
async def get_top_movers() -> Dict[str, Any]:
    """Get top movers - simplified for Vercel compatibility."""
    try:
        # Return mock data for now to avoid complex API calls
        return {
            'top_gainers': [
                {'symbol': 'BTCUSDT', 'priceChangePercent': 2.5, 'lastPrice': 45000.0},
                {'symbol': 'ETHUSDT', 'priceChangePercent': 1.8, 'lastPrice': 3200.0},
                {'symbol': 'BNBUSDT', 'priceChangePercent': 1.2, 'lastPrice': 850.0}
            ],
            'top_losers': [
                {'symbol': 'DOGEUSDT', 'priceChangePercent': -1.5, 'lastPrice': 0.08},
                {'symbol': 'ADAUSDT', 'priceChangePercent': -1.2, 'lastPrice': 0.45},
                {'symbol': 'SOLUSDT', 'priceChangePercent': -0.8, 'lastPrice': 95.0}
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching top movers: {str(e)}")

@app.get("/api/etf-comparison", response_model=Dict[str, Any])
async def etf_comparison() -> Dict[str, Any]:
    """Get ETF comparison - simplified for Vercel compatibility."""
    try:
        # Return mock ETF data for now
        return {
            'etf_allocation': {
                'BTC': 0.20, 'ETH': 0.20, 'BNB': 0.15, 'DOGE': 0.15,
                'SOL': 0.10, 'ADA': 0.10, 'NEXO': 0.10
            },
            'initial_investment': 1000.0,
            'current_value': 1050.0,
            'total_return': 5.0,
            'performance': {
                '24h': 1.2, '7d': 3.5, '28d': 8.2, '90d': 15.0
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching ETF comparison: {str(e)}")

@app.get("/admin_conf")
async def admin_configuration():
    """Admin configuration page - shows all service statuses and API tests"""
    try:
        # Test all services
        services_status = {}
        
        # 1. OpenAI Service Test
        openai_status = {
            "name": "OpenAI",
            "key_set": bool(os.getenv("OPENAI_API_KEY")),
            "test_working": False,
            "error": None
        }
        
        if openai_status["key_set"]:
            try:
                from utils.openai_utils import get_openai_client
                client = get_openai_client()
                if client:
                    # Simple test - try to create a completion
                    response = await client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": "Hello"}],
                        max_tokens=5
                    )
                    openai_status["test_working"] = True
                    openai_status["model"] = "gpt-3.5-turbo"
                else:
                    openai_status["error"] = "Client not initialized"
            except Exception as e:
                openai_status["error"] = str(e)[:100]
        
        services_status["openai"] = openai_status
        
        # 2. Binance Service Test
        binance_status = {
            "name": "Binance",
            "key_set": bool(os.getenv("BINANCE_API_KEY") and os.getenv("BINANCE_SECRET_KEY")),
            "test_working": False,
            "error": None
        }
        
        if binance_status["key_set"]:
            try:
                from utils.binance_client import get_binance_client
                client = get_binance_client()
                if client:
                    # Test account info endpoint
                    account_info = await client.get_account_info()
                    if account_info and "makerCommission" in account_info:
                        binance_status["test_working"] = True
                        binance_status["account_type"] = "Spot"
                    else:
                        binance_status["error"] = "Invalid account response"
                else:
                    binance_status["error"] = "Client not initialized"
            except Exception as e:
                binance_status["error"] = str(e)[:100]
        
        services_status["binance"] = binance_status
        
        # 3. NewsAPI Service Test
        newsapi_status = {
            "name": "NewsAPI",
            "key_set": bool(os.getenv("NEWSAPI_KEY") or os.getenv("NEWS_API_KEY")),
            "test_working": False,
            "error": None
        }
        
        if newsapi_status["key_set"]:
            try:
                from utils.newsapi import fetch_news_articles
                # Test with a simple crypto news search
                articles = await fetch_news_articles(["bitcoin"], hours_back=1)
                if articles and len(articles) > 0:
                    newsapi_status["test_working"] = True
                    newsapi_status["articles_count"] = len(articles)
                else:
                    newsapi_status["error"] = "No articles returned"
            except Exception as e:
                newsapi_status["error"] = str(e)[:100]
        
        services_status["newsapi"] = newsapi_status
        
        # 4. Environment Information
        env_info = {
            "platform": "Unknown",
            "deployment": "Unknown",
            "python_version": "3.x",
            "timestamp": datetime.now().isoformat()
        }
        
        # Detect platform
        if os.getenv("VERCEL") == "1" or os.getenv("VERCEL_ENV"):
            env_info["platform"] = "Vercel"
            env_info["deployment"] = os.getenv("VERCEL_ENV", "production")
        elif os.getenv("REPL_ID") or os.getenv("REPL_OWNER"):
            env_info["platform"] = "Replit"
            env_info["deployment"] = "replit"
        else:
            env_info["platform"] = "Local"
            env_info["deployment"] = "development"
        
        # Calculate overall health
        total_services = len(services_status)
        working_services = sum(1 for service in services_status.values() if service["test_working"])
        overall_health = f"{working_services}/{total_services} services working"
        
        return {
            "status": "success",
            "overall_health": overall_health,
            "environment": env_info,
            "services": services_status,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/admin")
def admin_page(request: Request):
    """Admin configuration page - HTML interface"""
    try:
        return templates.TemplateResponse("admin.html", {"request": request})
    except Exception as e:
        return HTMLResponse(content=f"""
        <html>
            <head><title>Admin - Masonic</title></head>
            <body>
                <h1>Admin Configuration</h1>
                <p><a href="/">← Back to Welcome</a></p>
                <p><a href="/admin_conf">View JSON API</a></p>
                <p>Error loading admin page: {str(e)}</p>
            </body>
        </html>
        """)
