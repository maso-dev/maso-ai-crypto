#!/usr/bin/env python3
"""
Test script for LiveCoinWatchProcessor
"""

import asyncio
import os
from utils.livecoinwatch_processor import (
    collect_price_data,
    collect_historical_data,
    calculate_technical_indicators,
    get_latest_prices
)

async def test_livecoinwatch():
    """Test LiveCoinWatch functionality."""
    print("🧪 Testing LiveCoinWatchProcessor...")
    
    # Test symbols
    symbols = ["BTC", "ETH", "SOL"]
    
    # 1. Test price data collection
    print("\n📊 Testing price data collection...")
    try:
        price_data = await collect_price_data(symbols)
        print(f"✅ Collected price data for {len(price_data)} symbols")
        
        for data in price_data:
            print(f"   {data.symbol}: ${data.price_usd:,.2f} (24h: {data.change_24h:+.2f}%)")
            
    except Exception as e:
        print(f"❌ Price data collection failed: {e}")
    
    # 2. Test historical data collection
    print("\n📈 Testing historical data collection...")
    try:
        historical_data = await collect_historical_data("BTC", days=7)
        print(f"✅ Collected {len(historical_data)} days of historical data for BTC")
        
        if historical_data:
            latest = historical_data[-1]
            print(f"   Latest BTC: ${latest.close_price:,.2f} (Volume: ${latest.volume:,.0f})")
            
    except Exception as e:
        print(f"❌ Historical data collection failed: {e}")
    
    # 3. Test technical indicators
    print("\n📊 Testing technical indicators...")
    try:
        indicators = await calculate_technical_indicators("BTC", days=30)
        print(f"✅ Calculated technical indicators for BTC")
        
        if indicators:
            print(f"   RSI: {indicators.get('rsi_14', 0):.2f}")
            print(f"   Volatility: {indicators.get('volatility', 0):.2f}%")
            
            bollinger = indicators.get('bollinger_bands', {})
            if bollinger:
                print(f"   Bollinger Bands: ${bollinger.get('lower', 0):,.0f} - ${bollinger.get('upper', 0):,.0f}")
                
    except Exception as e:
        print(f"❌ Technical indicators calculation failed: {e}")
    
    # 4. Test latest prices retrieval
    print("\n💾 Testing latest prices retrieval...")
    try:
        latest_prices = await get_latest_prices(symbols)
        print(f"✅ Retrieved latest prices for {len(latest_prices)} symbols")
        
        for symbol, price_data in latest_prices.items():
            print(f"   {symbol}: ${price_data.price_usd:,.2f} (Market Cap: ${price_data.market_cap:,.0f})")
            
    except Exception as e:
        print(f"❌ Latest prices retrieval failed: {e}")
    
    print("\n🎉 LiveCoinWatchProcessor test completed!")

if __name__ == "__main__":
    # Check if API key is available
    if not os.getenv("LIVECOINWATCH_API_KEY"):
        print("⚠️  LIVECOINWATCH_API_KEY not found. Some tests may fail.")
        print("   Set the environment variable to test with real data.")
    
    asyncio.run(test_livecoinwatch()) 
