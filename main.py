from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from typing import Dict, Any
from pathlib import Path
import os

app = FastAPI(title="Portfolio Analyzer API")

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
        "service": "Portfolio Analyzer API",
        "deployment": "Vercel",
        "version": "1.0.0",
        "environment_vars": {
            "binance_key_set": bool(os.getenv("BINANCE_API_KEY")),
            "openai_key_set": bool(os.getenv("OPENAI_API_KEY")),
            "news_key_set": bool(os.getenv("NEWS_API_KEY"))
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

@app.get("/")
def dashboard(request: Request):
    # Render the dashboard with Jinja2
    try:
        return templates.TemplateResponse("dashboard.html", {"request": request})
    except Exception as e:
        # Fallback to simple HTML if template fails
        from fastapi.responses import HTMLResponse
        return HTMLResponse(content=f"""
        <html>
            <head><title>Portfolio Analyzer</title></head>
            <body>
                <h1>Portfolio Analyzer API</h1>
                <p>FastAPI is running on Vercel!</p>
                <p><a href="/api/health">Health Check</a></p>
                <p><a href="/api/test">Test Endpoint</a></p>
                <p>Error loading dashboard: {str(e)}</p>
            </body>
        </html>
        """)

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
