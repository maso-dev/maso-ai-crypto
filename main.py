from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from typing import Dict, Any
from binance_client import get_binance_client

app = FastAPI(title="Portfolio Analyzer API")

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def dashboard(request: Request):
    # Render the dashboard with Jinja2
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/api/portfolio", response_model=Dict[str, Any])
async def get_portfolio() -> Dict[str, Any]:
    try:
        client = get_binance_client()
        account_info = client.get_account()
        balances = [b for b in account_info['balances'] if float(b['free']) > 0 or float(b['locked']) > 0]
        portfolio = {
            'assets': [
                {
                    'asset': b['asset'],
                    'free': float(b['free']),
                    'locked': float(b['locked'])
                } for b in balances
            ]
        }
        return portfolio
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/asset/{symbol}", response_model=Dict[str, Any])
async def get_asset_details(symbol: str) -> Dict[str, Any]:
    # TODO: Implement logic to fetch trade history, cost basis, price, ROI, and use cache
    return {"message": f"Details for asset {symbol} will be here."}
