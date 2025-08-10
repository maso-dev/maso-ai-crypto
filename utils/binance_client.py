from binance.client import Client
from pathlib import Path
import os
import asyncio
from typing import Dict, Any, List
from datetime import datetime
from pydantic import BaseModel


class PortfolioAsset(BaseModel):
    """Represents a single asset in the portfolio."""

    asset: str
    free: float
    locked: float
    total: float
    usdt_value: float
    cost_basis: float
    roi_percentage: float
    avg_buy_price: float


class PortfolioData(BaseModel):
    """Represents the complete portfolio data."""

    total_value_usdt: float
    total_cost_basis: float
    total_roi_percentage: float
    assets: List[PortfolioAsset]
    last_updated: datetime


def get_binance_client() -> Client:
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")

    if not api_key or not api_secret:
        raise ValueError("API key or secret missing in environment variables")

    return Client(api_key, api_secret)


# Function to create PortfolioData from LiveCoinWatch data
async def get_portfolio_data() -> PortfolioData:
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
        total_cost_basis = 0

        # Mock portfolio quantities and cost basis
        quantities = {
            "BTC": 0.5,
            "ETH": 5.0,
            "SOL": 100.0,
            "XRP": 10000.0,
            "ADA": 5000.0,
        }

        cost_basis = {
            "BTC": 40000.0,
            "ETH": 3000.0,
            "SOL": 100.0,
            "XRP": 0.5,
            "ADA": 0.4,
        }

        for symbol, price_data in latest_prices.items():
            if price_data:
                quantity = quantities.get(symbol, 0)
                asset_value = price_data.price_usd * quantity
                asset_cost = cost_basis.get(symbol, 0) * quantity
                total_value += asset_value
                total_cost_basis += asset_cost

                roi_percentage = (
                    ((asset_value - asset_cost) / asset_cost * 100)
                    if asset_cost > 0
                    else 0
                )

                portfolio_assets.append(
                    PortfolioAsset(
                        asset=symbol,
                        free=quantity,
                        locked=0.0,
                        total=quantity,
                        usdt_value=asset_value,
                        cost_basis=asset_cost,
                        roi_percentage=roi_percentage,
                        avg_buy_price=cost_basis.get(symbol, 0),
                    )
                )

        total_roi_percentage = (
            ((total_value - total_cost_basis) / total_cost_basis * 100)
            if total_cost_basis > 0
            else 0
        )

        return PortfolioData(
            total_value_usdt=total_value,
            total_cost_basis=total_cost_basis,
            total_roi_percentage=total_roi_percentage,
            assets=portfolio_assets,
            last_updated=datetime.now(),
        )

    except Exception as e:
        # Fallback to mock data if LiveCoinWatch fails
        mock_assets = [
            PortfolioAsset(
                asset="BTC",
                free=0.5,
                locked=0.0,
                total=0.5,
                usdt_value=57500.0,
                cost_basis=20000.0,
                roi_percentage=187.5,
                avg_buy_price=40000.0,
            ),
            PortfolioAsset(
                asset="ETH",
                free=5.0,
                locked=0.0,
                total=5.0,
                usdt_value=19750.0,
                cost_basis=15000.0,
                roi_percentage=31.67,
                avg_buy_price=3000.0,
            ),
            PortfolioAsset(
                asset="SOL",
                free=100.0,
                locked=0.0,
                total=100.0,
                usdt_value=14500.0,
                cost_basis=10000.0,
                roi_percentage=45.0,
                avg_buy_price=100.0,
            ),
        ]

        return PortfolioData(
            total_value_usdt=125000.0,
            total_cost_basis=45000.0,
            total_roi_percentage=177.78,
            assets=mock_assets,
            last_updated=datetime.now(),
        )
