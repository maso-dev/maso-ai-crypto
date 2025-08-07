from binance.client import Client
from pathlib import Path
import os
import asyncio
from typing import Dict, Any, List
from datetime import datetime


def get_binance_client() -> Client:
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")

    if not api_key or not api_secret:
        raise ValueError("API key or secret missing in environment variables")

    return Client(api_key, api_secret)


async def get_portfolio_data() -> Dict[str, Any]:
    """
    Get portfolio data using LiveCoinWatch instead of Binance.
    This function replaces the old Binance portfolio data function.
    """
    try:
        from utils.livecoinwatch_processor import LiveCoinWatchProcessor
        
        # Initialize LiveCoinWatch processor
        processor = LiveCoinWatchProcessor()
        
        # Define default portfolio assets
        symbols = ["BTC", "ETH", "SOL", "XRP", "ADA"]
        
        # Get latest prices
        latest_prices = await processor.get_latest_prices(symbols)
        
        # Calculate portfolio value (mock portfolio with fixed quantities)
        portfolio_assets = []
        total_value = 0
        
        # Mock portfolio quantities
        quantities = {
            "BTC": 0.5,
            "ETH": 5.0,
            "SOL": 100.0,
            "XRP": 10000.0,
            "ADA": 5000.0
        }
        
        for symbol, price_data in latest_prices.items():
            if price_data:
                quantity = quantities.get(symbol, 0)
                asset_value = price_data.price_usd * quantity
                total_value += asset_value
                
                portfolio_assets.append({
                    "symbol": symbol,
                    "quantity": quantity,
                    "price_usd": price_data.price_usd,
                    "value_usd": asset_value,
                    "change_24h": price_data.change_24h,
                    "market_cap": price_data.market_cap,
                    "volume_24h": price_data.volume_24h
                })
        
        return {
            "total_value_usdt": total_value,
            "assets": portfolio_assets,
            "last_updated": datetime.now().isoformat(),
            "data_source": "LiveCoinWatch"
        }
        
    except Exception as e:
        # Fallback to mock data if LiveCoinWatch fails
        return {
            "total_value_usdt": 125000.0,
            "assets": [
                {
                    "symbol": "BTC",
                    "quantity": 0.5,
                    "price_usd": 115000.0,
                    "value_usd": 57500.0,
                    "change_24h": 2.1,
                    "market_cap": 2200000000000,
                    "volume_24h": 30000000000
                },
                {
                    "symbol": "ETH",
                    "quantity": 5.0,
                    "price_usd": 3950.0,
                    "value_usd": 19750.0,
                    "change_24h": 1.8,
                    "market_cap": 475000000000,
                    "volume_24h": 15000000000
                },
                {
                    "symbol": "SOL",
                    "quantity": 100.0,
                    "price_usd": 145.0,
                    "value_usd": 14500.0,
                    "change_24h": 4.2,
                    "market_cap": 65000000000,
                    "volume_24h": 5000000000
                }
            ],
            "last_updated": datetime.now().isoformat(),
            "data_source": "Mock (LiveCoinWatch unavailable)"
        }


# For backward compatibility
PortfolioData = Dict[str, Any]
