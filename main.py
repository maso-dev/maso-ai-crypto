from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from typing import Dict, Any
from utils.binance_client import get_portfolio_data
from routers.crypto_news_rag import router as crypto_news_rag_router
from routers.portfolio_user import router as portfolio_router
from routers.crypto_news import router as crypto_news_router
from routers.admin import router as admin_router
from routers.agent import router as agent_router

app = FastAPI(title="Portfolio Analyzer API")

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(crypto_news_rag_router)
app.include_router(portfolio_router)
app.include_router(crypto_news_router)
app.include_router(admin_router)
app.include_router(agent_router)

@app.get("/")
def dashboard(request: Request):
    # Render the dashboard with Jinja2
    return templates.TemplateResponse("dashboard.html", {"request": request})

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
        raise HTTPException(status_code=500, detail=str(e))

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
