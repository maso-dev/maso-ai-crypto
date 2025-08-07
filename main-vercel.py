from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse, HTMLResponse
from typing import Dict, Any
from pathlib import Path
import os
from datetime import datetime, timedelta

app = FastAPI(title="🏛️ Masonic - Alpha Strategy Advisor (Vercel)")

templates = Jinja2Templates(directory="templates")


# Custom static files handling for Vercel
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
            "news_key_set": bool(os.getenv("NEWSAPI_KEY")),
        },
    }


@app.get("/api/test")
async def test_endpoint():
    """Simple test endpoint that doesn't require external dependencies"""
    return {
        "message": "FastAPI is working on Vercel!",
        "timestamp": datetime.now().isoformat(),
        "status": "success",
        "endpoints": ["/", "/dashboard", "/api/health", "/api/portfolio"],
    }


@app.get("/")
async def welcome_page(request: Request):
    """Welcome page for non-logged users - shows market overview and opportunities"""
    try:
        return templates.TemplateResponse("welcome.html", {"request": request})
    except Exception:
        # Fallback to simple HTML if template fails
        return HTMLResponse(
            content="""
        <html>
            <head><title>Welcome - Portfolio Analyzer</title></head>
            <body>
                <h1>🚀 Welcome to Portfolio Analyzer</h1>
                <p>Your AI-powered crypto portfolio assistant</p>
                <p><a href="/dashboard">View Full Dashboard</a></p>
                <p><a href="/api/health">Health Check</a></p>
            </body>
        </html>
        """
        )


@app.get("/dashboard")
def dashboard(request: Request):
    """Main dashboard"""
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/api/portfolio")
async def get_portfolio():
    """Simplified portfolio endpoint for Vercel"""
    try:
        # Try to get real data if possible
        from utils.binance_client import get_portfolio_data
        portfolio_data = await get_portfolio_data()
        
        return {
            "portfolio": {
                "total_value_usdt": portfolio_data.total_value_usdt,
                "total_cost_basis": portfolio_data.total_cost_basis,
                "total_roi_percentage": portfolio_data.total_roi_percentage,
                "assets": [
                    {
                        "asset": asset.asset,
                        "free": asset.free,
                        "locked": asset.locked,
                        "total": asset.total,
                        "usdt_value": asset.usdt_value,
                        "cost_basis": asset.cost_basis,
                        "roi_percentage": asset.roi_percentage,
                        "avg_buy_price": asset.avg_buy_price,
                    }
                    for asset in portfolio_data.assets
                ],
                "last_updated": portfolio_data.last_updated.isoformat(),
                "data_source": "livecoinwatch",
            },
            "status": "success",
        }
    except Exception as e:
        # Fallback to mock data
        return {
            "portfolio": {
                "total_value_usdt": 125000.0,
                "total_cost_basis": 45000.0,
                "total_roi_percentage": 177.78,
                "assets": [
                    {
                        "asset": "BTC",
                        "free": 0.5,
                        "locked": 0.0,
                        "total": 0.5,
                        "usdt_value": 57500.0,
                        "cost_basis": 20000.0,
                        "roi_percentage": 187.5,
                        "avg_buy_price": 40000.0,
                    },
                    {
                        "asset": "ETH",
                        "free": 5.0,
                        "locked": 0.0,
                        "total": 5.0,
                        "usdt_value": 19750.0,
                        "cost_basis": 15000.0,
                        "roi_percentage": 31.67,
                        "avg_buy_price": 3000.0,
                    },
                ],
                "last_updated": datetime.now().isoformat(),
                "data_source": "mock",
            },
            "status": "fallback",
            "error": str(e),
        }


@app.get("/api/opportunities")
async def get_opportunities():
    """Simplified opportunities endpoint for Vercel"""
    try:
        from utils.livecoinwatch_processor import LiveCoinWatchProcessor
        
        processor = LiveCoinWatchProcessor()
        symbols = ["BTC", "ETH", "SOL", "XRP", "DOGE"]
        latest_prices = await processor.get_latest_prices(symbols)
        
        opportunities = []
        for symbol, price_data in latest_prices.items():
            if price_data:
                # Simple opportunity scoring based on 24h change
                change_24h = price_data.change_24h
                if change_24h > 5:
                    opportunity_type = "BUY"
                    score = 0.7
                elif change_24h < -5:
                    opportunity_type = "SELL"
                    score = 0.6
                else:
                    opportunity_type = "HOLD"
                    score = 0.3
                
                opportunities.append({
                    "symbol": symbol,
                    "type": opportunity_type,
                    "score": score,
                    "price": price_data.price_usd,
                    "change_24h": change_24h,
                    "volume_24h": price_data.volume_24h,
                    "market_cap": price_data.market_cap,
                })
        
        return {
            "opportunities": opportunities,
            "status": "success",
            "last_updated": datetime.now().isoformat(),
        }
    except Exception as e:
        return {
            "opportunities": [],
            "status": "fallback",
            "error": str(e),
            "last_updated": datetime.now().isoformat(),
        }


@app.get("/api/news-briefing")
async def get_news():
    """Simplified news endpoint for Vercel"""
    try:
        from utils.intelligent_news_cache import get_portfolio_news
        
        news_data = await get_portfolio_news(
            include_alpha_portfolio=True,
            include_opportunity_tokens=True,
            include_personal_portfolio=True,
            hours_back=24,
        )
        
        return {
            "news": news_data.get("news_by_category", {}),
            "status": "success",
            "last_updated": datetime.now().isoformat(),
        }
    except Exception as e:
        return {
            "news": {},
            "status": "fallback",
            "error": str(e),
            "last_updated": datetime.now().isoformat(),
        }


# Server startup for development
if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Masonic AI Vercel Server...")
    print("🌐 Server will be available at: http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
