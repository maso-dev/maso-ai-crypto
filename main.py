from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from typing import Dict, Any
from pathlib import Path
import os

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
        "message": "FastAPI is working on Vercel!",
        "timestamp": "2024",
        "status": "success"
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
    """Get alpha portfolio data (BTC, ETH, RIPPLE, SOL, DOGE)"""
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
    """Get today's alpha signals from our brotherhood"""
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
@app.get("/v1")
def dashboard_v1(request: Request):
    """Version 1 dashboard - current implementation"""
    try:
        return templates.TemplateResponse("dashboard.html", {"request": request})
    except Exception as e:
        # Fallback to simple HTML if template fails
        return HTMLResponse(content=f"""
        <html>
            <head><title>Portfolio Analyzer v1</title></head>
            <body>
                <h1>Portfolio Analyzer API v1</h1>
                <p>FastAPI is running on Vercel!</p>
                <p><a href="/">← Back to Welcome</a></p>
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
                "last_updated": portfolio_data.last_updated.isoformat()
            }
        else:
            return {"error": "No portfolio data available"}
    except Exception as e:
        return {"error": f"Portfolio data unavailable: {str(e)}", "status": "error"}

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
