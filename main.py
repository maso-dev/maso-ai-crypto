from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from typing import Dict, Any
from binance_client import get_binance_client
from binance.client import Client
from routers.crypto_news_rag import router as crypto_news_rag_router
from routers.portfolio_user import router as portfolio_router
from routers.crypto_news import router as crypto_news_router
from routers.admin import router as admin_router

app = FastAPI(title="Portfolio Analyzer API")

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(crypto_news_rag_router)
app.include_router(portfolio_router)
app.include_router(crypto_news_router)
app.include_router(admin_router)

@app.get("/")
def dashboard(request: Request):
    # Render the dashboard with Jinja2
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/api/portfolio", response_model=Dict[str, Any])
async def get_portfolio() -> Dict[str, Any]:
    try:
        import time
        from datetime import datetime, timedelta
        client = get_binance_client()
        account_info = client.get_account()
        balances = [b for b in account_info['balances'] if float(b['free']) > 0 or float(b['locked']) > 0]
        assets = []
        now = int(time.time() * 1000)
        periods = {
            '24h': 24 * 60 * 60 * 1000,
            '7d': 7 * 24 * 60 * 60 * 1000,
            '28d': 28 * 24 * 60 * 60 * 1000,
            '90d': 90 * 24 * 60 * 60 * 1000,
        }
        for b in balances:
            symbol = b['asset']
            if symbol == 'USDT':
                continue
            asset_data = {
                'asset': symbol,
                'free': float(b['free']),
                'locked': float(b['locked'])
            }
            try:
                # Current price
                ticker = client.get_symbol_ticker(symbol=f"{symbol}USDT")
                current_price = float(ticker['price'])
                asset_data['current_price'] = current_price
                # Cost basis (from trade history)
                trades = client.get_my_trades(symbol=f"{symbol}USDT")
                total_qty = 0.0
                total_cost = 0.0
                for t in trades:
                    qty = float(t['qty'])
                    price = float(t['price'])
                    if t['isBuyer']:
                        total_qty += qty
                        total_cost += qty * price
                    else:
                        total_qty -= qty
                        total_cost -= qty * price
                avg_cost = (total_cost / total_qty) if total_qty > 0 else 0.0
                asset_data['average_cost_basis'] = avg_cost
                # Historical ROI
                asset_data['roi'] = {}
                for label, ms_ago in periods.items():
                    start_time = now - ms_ago
                    klines = client.get_historical_klines(f"{symbol}USDT", Client.KLINE_INTERVAL_1DAY, start_str=start_time, end_str=now, limit=2)
                    if klines:
                        # Use the first kline's close as the historical price
                        historical_price = float(klines[0][4])
                        roi = ((current_price - historical_price) / historical_price * 100) if historical_price > 0 else None
                        asset_data['roi'][label] = roi
                        asset_data[f'price_{label}_ago'] = historical_price
                    else:
                        asset_data['roi'][label] = None
                        asset_data[f'price_{label}_ago'] = None
            except Exception as e:
                asset_data['error'] = str(e)
            assets.append(asset_data)
        portfolio = {'assets': assets}
        return portfolio
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/asset/{symbol}", response_model=Dict[str, Any])
async def get_asset_details(symbol: str) -> Dict[str, Any]:
    try:
        client = get_binance_client()
        # 1. Fetch trade history for the asset (spot trades)
        trades = client.get_my_trades(symbol=f"{symbol}USDT")
        # 2. Calculate average cost basis for current holdings
        total_qty = 0.0
        total_cost = 0.0
        for t in trades:
            qty = float(t['qty'])
            price = float(t['price'])
            if t['isBuyer']:
                total_qty += qty
                total_cost += qty * price
            else:
                total_qty -= qty
                total_cost -= qty * price
        avg_cost = (total_cost / total_qty) if total_qty > 0 else 0.0
        # 3. Fetch current market price
        ticker = client.get_symbol_ticker(symbol=f"{symbol}USDT")
        current_price = float(ticker['price'])
        # 4. Calculate ROI
        roi = ((current_price - avg_cost) / avg_cost * 100) if avg_cost > 0 else None
        return {
            'symbol': symbol,
            'trade_count': len(trades),
            'average_cost_basis': avg_cost,
            'current_price': current_price,
            'roi_percent': roi,
            'current_qty': total_qty,
            'trades': trades
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error for {symbol}: {str(e)}")

@app.get("/api/top-movers", response_model=Dict[str, Any])
async def get_top_movers() -> Dict[str, Any]:
    try:
        client = get_binance_client()
        tickers = client.get_ticker()
        # Only consider USDT pairs for relevance
        usdt_tickers = [t for t in tickers if t['symbol'].endswith('USDT')]
        # Sort by price change percent
        sorted_tickers = sorted(usdt_tickers, key=lambda t: float(t['priceChangePercent']), reverse=True)
        top_gainers = [
            {
                'symbol': t['symbol'],
                'priceChangePercent': float(t['priceChangePercent']),
                'lastPrice': float(t['lastPrice'])
            } for t in sorted_tickers[:5]
        ]
        top_losers = [
            {
                'symbol': t['symbol'],
                'priceChangePercent': float(t['priceChangePercent']),
                'lastPrice': float(t['lastPrice'])
            } for t in sorted_tickers[-5:][::-1]
        ]
        return {
            'top_gainers': top_gainers,
            'top_losers': top_losers
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching top movers: {str(e)}")

@app.get("/api/etf-comparison", response_model=Dict[str, Any])
async def etf_comparison() -> Dict[str, Any]:
    try:
        import time
        from binance.client import Client
        client = get_binance_client()
        now = int(time.time() * 1000)
        periods = {
            '24h': 24 * 60 * 60 * 1000,
            '7d': 7 * 24 * 60 * 60 * 1000,
            '28d': 28 * 24 * 60 * 60 * 1000,
            '90d': 90 * 24 * 60 * 60 * 1000,
        }
        # Example ETF allocation (can be customized)
        etf_allocation = {
            'BTC': 0.20,
            'ETH': 0.20,
            'BNB': 0.15,
            'DOGE': 0.15,
            'SOL': 0.10,
            'ADA': 0.10,
            'NEXO': 0.10
        }
        initial_investment = 1000.0
        etf_data = []
        etf_value_now = 0.0
        etf_value_periods = {k: 0.0 for k in periods}
        for symbol, weight in etf_allocation.items():
            asset = {'asset': symbol, 'weight': weight}
            try:
                ticker = client.get_symbol_ticker(symbol=f"{symbol}USDT")
                current_price = float(ticker['price'])
                asset['current_price'] = current_price
                # Amount of coin if invested at start
                coin_qty = (initial_investment * weight) / current_price
                asset['coin_qty'] = coin_qty
                asset['roi'] = {}
                for label, ms_ago in periods.items():
                    start_time = now - ms_ago
                    klines = client.get_historical_klines(f"{symbol}USDT", Client.KLINE_INTERVAL_1DAY, start_str=start_time, end_str=now, limit=2)
                    if klines:
                        historical_price = float(klines[0][4])
                        value_then = coin_qty * historical_price
                        value_now = coin_qty * current_price
                        roi = ((value_now - value_then) / value_then * 100) if value_then > 0 else None
                        asset['roi'][label] = roi
                        asset[f'price_{label}_ago'] = historical_price
                        etf_value_periods[label] += value_then
                    else:
                        asset['roi'][label] = None
                        asset[f'price_{label}_ago'] = None
                etf_value_now += coin_qty * current_price
            except Exception as e:
                asset['error'] = str(e)
            etf_data.append(asset)
        # Calculate ETF ROI for each period
        etf_roi = {label: ((etf_value_now - etf_value_periods[label]) / etf_value_periods[label] * 100) if etf_value_periods[label] > 0 else None for label in periods}
        return {
            'etf_allocation': etf_allocation,
            'initial_investment': initial_investment,
            'etf_value_now': etf_value_now,
            'etf_roi': etf_roi,
            'assets': etf_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ETF comparison error: {str(e)}")
