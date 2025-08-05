#!/usr/bin/env python3
"""
Real-time Data Integration System
Provides WebSocket connections for live crypto data and market updates.
"""

import asyncio
import json
import websockets
import aiohttp
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timezone
import os
from dataclasses import dataclass
from enum import Enum


class DataSource(Enum):
    BINANCE = "binance"
    COINGECKO = "coingecko"
    MOCK = "mock"
    LIVECOINWATCH = "livecoinwatch"


@dataclass
class CryptoPrice:
    symbol: str
    price: float
    change_24h: float
    volume_24h: float
    market_cap: float
    timestamp: datetime
    source: str


@dataclass
class MarketUpdate:
    type: str  # "price", "volume", "news", "alert"
    symbol: str
    data: Dict[str, Any]
    timestamp: datetime
    priority: str  # "low", "medium", "high", "critical"


class RealTimeDataManager:
    """
    Manages real-time data streams for crypto prices and market updates.
    """

    def __init__(self):
        self.websocket_connections: Dict[str, websockets.WebSocketServerProtocol] = {}
        self.price_cache: Dict[str, CryptoPrice] = {}
        self.subscribers: List[Callable] = []
        self.running = False
        self.data_sources = {
            DataSource.BINANCE: self._binance_websocket,
            DataSource.COINGECKO: self._coingecko_api,
            DataSource.MOCK: self._mock_data_stream,
            DataSource.LIVECOINWATCH: self._livecoinwatch_api,
        }

    async def start(self, source: DataSource = DataSource.MOCK):
        """Start the real-time data manager."""
        self.running = True
        print(f"🚀 Starting real-time data manager with source: {source.value}")

        # Start the data source in the background
        if source in self.data_sources:
            asyncio.create_task(self.data_sources[source]())
        else:
            print(f"⚠️ Unknown data source: {source}")

    async def stop(self):
        """Stop the real-time data manager."""
        self.running = False
        print("🛑 Stopping real-time data manager")

        # Close all WebSocket connections
        for ws in self.websocket_connections.values():
            await ws.close()
        self.websocket_connections.clear()

    async def _mock_data_stream(self):
        """Mock data stream for testing and development."""
        print("🎭 Starting mock data stream")

        symbols = ["BTC", "ETH", "ADA", "DOT", "LINK"]
        base_prices = {
            "BTC": 45000.0,
            "ETH": 3000.0,
            "ADA": 0.50,
            "DOT": 20.0,
            "LINK": 15.0,
        }

        while self.running:
            try:
                for symbol in symbols:
                    # Simulate price movements
                    import random

                    base_price = base_prices[symbol]
                    change_percent = random.uniform(-2.0, 2.0)
                    new_price = base_price * (1 + change_percent / 100)

                    # Update base price
                    base_prices[symbol] = new_price

                    # Create price update
                    price_update = CryptoPrice(
                        symbol=symbol,
                        price=new_price,
                        change_24h=change_percent,
                        volume_24h=random.uniform(1000000, 50000000),
                        market_cap=random.uniform(1000000000, 100000000000),
                        timestamp=datetime.now(timezone.utc),
                        source="mock",
                    )

                    # Cache the price
                    self.price_cache[symbol] = price_update

                    # Notify subscribers
                    await self._notify_subscribers(price_update)

                    # Create market update
                    if random.random() < 0.1:  # 10% chance of market update
                        market_update = MarketUpdate(
                            type="price_alert",
                            symbol=symbol,
                            data={
                                "price": new_price,
                                "change": change_percent,
                                "threshold": "significant_movement",
                            },
                            timestamp=datetime.now(timezone.utc),
                            priority="medium" if abs(change_percent) < 1 else "high",
                        )
                        await self._notify_subscribers(market_update)

                # Wait before next update
                await asyncio.sleep(5)  # Update every 5 seconds

            except Exception as e:
                print(f"❌ Error in mock data stream: {e}")
                await asyncio.sleep(10)

    async def _binance_websocket(self):
        """Connect to Binance WebSocket for real-time data."""
        print("🔗 Connecting to Binance WebSocket")

        # Note: This is a simplified version. In production, you'd need proper API keys
        symbols = ["btcusdt", "ethusdt", "adausdt", "dotusdt", "linkusdt"]

        try:
            # Connect to Binance WebSocket
            uri = "wss://stream.binance.com:9443/ws/"
            streams = "/".join([f"{symbol}@ticker" for symbol in symbols])

            async with websockets.connect(f"{uri}{streams}") as websocket:
                print(f"✅ Connected to Binance WebSocket: {streams}")

                while self.running:
                    try:
                        message = await websocket.recv()
                        data = json.loads(message)

                        # Parse Binance ticker data
                        if "s" in data:  # Symbol
                            symbol = data["s"].replace("USDT", "")
                            price_update = CryptoPrice(
                                symbol=symbol,
                                price=float(data["c"]),  # Close price
                                change_24h=float(data["P"]),  # Price change percent
                                volume_24h=float(data["v"]),  # Volume
                                market_cap=float(data["v"])
                                * float(data["c"]),  # Approximate
                                timestamp=datetime.now(timezone.utc),
                                source="binance",
                            )

                            self.price_cache[symbol] = price_update
                            await self._notify_subscribers(price_update)

                    except websockets.exceptions.ConnectionClosed:
                        print("⚠️ Binance WebSocket connection closed, reconnecting...")
                        break
                    except Exception as e:
                        print(f"❌ Error processing Binance data: {e}")
                        continue

        except Exception as e:
            print(f"❌ Failed to connect to Binance WebSocket: {e}")
            print("🔄 Falling back to mock data stream")
            await self._mock_data_stream()

    async def _coingecko_api(self):
        """Use CoinGecko API for price data (polling-based)."""
        print("🪙 Using CoinGecko API for price data")

        symbols = ["bitcoin", "ethereum", "cardano", "polkadot", "chainlink"]

        while self.running:
            try:
                async with aiohttp.ClientSession() as session:
                    # Get price data from CoinGecko
                    url = "https://api.coingecko.com/api/v3/simple/price"
                    params = {
                        "ids": ",".join(symbols),
                        "vs_currencies": "usd",
                        "include_24hr_change": "true",
                        "include_24hr_vol": "true",
                        "include_market_cap": "true",
                    }

                    async with session.get(url, params=params) as response:
                        if response.status == 200:
                            data = await response.json()

                            for symbol_id, price_data in data.items():
                                symbol = symbol_id.upper()
                                price_update = CryptoPrice(
                                    symbol=symbol,
                                    price=price_data["usd"],
                                    change_24h=price_data.get("usd_24h_change", 0),
                                    volume_24h=price_data.get("usd_24h_vol", 0),
                                    market_cap=price_data.get("usd_market_cap", 0),
                                    timestamp=datetime.now(timezone.utc),
                                    source="coingecko",
                                )

                                self.price_cache[symbol] = price_update
                                await self._notify_subscribers(price_update)

                # Wait before next poll
                await asyncio.sleep(30)  # Poll every 30 seconds

            except Exception as e:
                print(f"❌ Error fetching CoinGecko data: {e}")
                await asyncio.sleep(60)

    async def _livecoinwatch_api(self):
        """Use LiveCoinWatch API for price data (polling-based)."""
        print("🪙 Using LiveCoinWatch API for price data")

        api_key = os.getenv("LIVECOINEWATCH_API_KEY")
        if not api_key:
            print("❌ LiveCoinWatch API key not found, falling back to mock data")
            await self._mock_data_stream()
            return

        symbols = [
            "BTC",
            "ETH",
            "ADA",
            "DOT",
            "LINK",
            "SOL",
            "XRP",
            "DOGE",
            "AVAX",
            "MATIC",
        ]

        while self.running:
            try:
                timeout = aiohttp.ClientTimeout(total=10)
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    url = "https://api.livecoinwatch.com/coins/single"
                    headers = {"x-api-key": api_key, "Content-Type": "application/json"}

                    for symbol in symbols:
                        try:
                            payload = {"currency": "USD", "code": symbol, "meta": True}
                            async with session.post(
                                url, json=payload, headers=headers
                            ) as response:
                                if response.status == 200:
                                    data = await response.json()
                                    # LiveCoinWatch returns data directly, not wrapped in success/data
                                    if data and "rate" in data:
                                        price_update = CryptoPrice(
                                            symbol=symbol,
                                            price=float(data.get("rate", 0)),
                                            change_24h=float(
                                                data.get("delta", {}).get("day", 0)
                                            )
                                            * 100,  # Convert to percentage
                                            volume_24h=float(data.get("volume", 0)),
                                            market_cap=float(data.get("cap", 0)),
                                            timestamp=datetime.now(timezone.utc),
                                            source="livecoinwatch",
                                        )
                                        self.price_cache[symbol] = price_update
                                        await self._notify_subscribers(price_update)

                                        # Create market update for significant movements
                                        if abs(price_update.change_24h) > 1.0:
                                            market_update = MarketUpdate(
                                                type="price_alert",
                                                symbol=symbol,
                                                data={
                                                    "price": price_update.price,
                                                    "change": price_update.change_24h,
                                                    "threshold": "significant_movement",
                                                },
                                                timestamp=datetime.now(timezone.utc),
                                                priority="medium",
                                            )
                                            await self._notify_subscribers(
                                                market_update
                                            )
                                else:
                                    print(
                                        f"⚠️ LiveCoinWatch API returned status {response.status} for {symbol}"
                                    )
                        except Exception as e:
                            print(f"❌ Error fetching {symbol} from LiveCoinWatch: {e}")
                            continue

                # Wait before next poll
                await asyncio.sleep(30)  # Poll every 30 seconds

            except asyncio.TimeoutError:
                print(
                    "⏰ LiveCoinWatch API request timed out, falling back to mock data"
                )
                await self._mock_data_stream()
                break
            except Exception as e:
                print(f"❌ Error with LiveCoinWatch API: {e}")
                print("🔄 Falling back to mock data")
                await self._mock_data_stream()
                break

    async def _notify_subscribers(self, update: Any):
        """Notify all subscribers of a data update."""
        for subscriber in self.subscribers:
            try:
                if asyncio.iscoroutinefunction(subscriber):
                    await subscriber(update)
                else:
                    subscriber(update)
            except Exception as e:
                print(f"❌ Error notifying subscriber: {e}")

    def subscribe(self, callback: Callable):
        """Subscribe to real-time updates."""
        self.subscribers.append(callback)
        print(f"✅ Added subscriber, total: {len(self.subscribers)}")

    def unsubscribe(self, callback: Callable):
        """Unsubscribe from real-time updates."""
        if callback in self.subscribers:
            self.subscribers.remove(callback)
            print(f"✅ Removed subscriber, total: {len(self.subscribers)}")

    def get_current_prices(self) -> Dict[str, CryptoPrice]:
        """Get current cached prices."""
        return self.price_cache.copy()

    def get_price(self, symbol: str) -> Optional[CryptoPrice]:
        """Get current price for a specific symbol."""
        return self.price_cache.get(symbol.upper())

    async def add_websocket_client(self, websocket, client_id: str):
        """Add a WebSocket client for real-time data streaming."""
        self.websocket_connections[client_id] = websocket
        print(f"✅ Added WebSocket client: {client_id}")

        # Send current prices to new client
        current_prices = self.get_current_prices()
        if current_prices:
            await websocket.send_text(
                json.dumps(
                    {
                        "type": "initial_prices",
                        "data": {
                            symbol: {
                                "price": price.price,
                                "change_24h": price.change_24h,
                                "volume_24h": price.volume_24h,
                                "market_cap": price.market_cap,
                                "timestamp": price.timestamp.isoformat(),
                            }
                            for symbol, price in current_prices.items()
                        },
                    }
                )
            )

    async def remove_websocket_client(self, client_id: str):
        """Remove a WebSocket client."""
        if client_id in self.websocket_connections:
            await self.websocket_connections[client_id].close()
            del self.websocket_connections[client_id]
            print(f"✅ Removed WebSocket client: {client_id}")


# Global instance
realtime_manager = RealTimeDataManager()


# Convenience functions
async def start_realtime_data(source: DataSource = DataSource.MOCK):
    """Start the real-time data manager."""
    await realtime_manager.start(source)


async def stop_realtime_data():
    """Stop the real-time data manager."""
    await realtime_manager.stop()


def subscribe_to_updates(callback: Callable):
    """Subscribe to real-time updates."""
    realtime_manager.subscribe(callback)


def get_current_prices() -> Dict[str, CryptoPrice]:
    """Get current cached prices."""
    return realtime_manager.get_current_prices()


def get_price(symbol: str) -> Optional[CryptoPrice]:
    """Get current price for a specific symbol."""
    return realtime_manager.get_price(symbol)


# Test function
async def test_realtime_data():
    """Test the real-time data system."""
    print("🧠 Testing Real-time Data Integration")
    print("=" * 50)

    # Subscribe to updates
    def price_callback(update):
        if isinstance(update, CryptoPrice):
            print(
                f"💰 {update.symbol}: ${update.price:.2f} ({update.change_24h:+.2f}%)"
            )
        elif isinstance(update, MarketUpdate):
            print(f"📊 {update.type}: {update.symbol} - {update.data}")

    subscribe_to_updates(price_callback)

    # Start the data manager
    await start_realtime_data(DataSource.MOCK)

    # Let it run for a bit
    print("🔄 Running for 30 seconds...")
    await asyncio.sleep(30)

    # Stop
    await stop_realtime_data()

    # Show final prices
    final_prices = get_current_prices()
    print(f"\n📊 Final prices: {len(final_prices)} symbols")
    for symbol, price in final_prices.items():
        print(f"   {symbol}: ${price.price:.2f}")


if __name__ == "__main__":
    asyncio.run(test_realtime_data())
