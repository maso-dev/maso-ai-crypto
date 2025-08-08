#!/usr/bin/env python3
"""Test LiveCoinWatch processor directly"""

import asyncio
import os

async def test_livecoinwatch_processor():
    """Test LiveCoinWatch processor"""
    os.environ['LIVECOINWATCH_API_KEY'] = "474dbae9-72de-4691-81bc-430db59ed5e3"  # Set the key
    
    from utils.livecoinwatch_processor import LiveCoinWatchProcessor
    
    processor = LiveCoinWatchProcessor()
    print(f"Processor initialized with API key: {processor.api_key[:15] if processor.api_key else 'None'}...")
    
    try:
        # Test collect_price_data first
        print("\n1. Testing collect_price_data:")
        price_data_list = await processor.collect_price_data(["BTC", "ETH"])
        print(f"Collected {len(price_data_list)} price data entries")
        
        for price_data in price_data_list:
            print(f"  {price_data.symbol}: ${price_data.price_usd}")
        
        # Now test get_latest_prices after collecting data
        print("\n2. Testing get_latest_prices after collection:")
        latest_prices = await processor.get_latest_prices(["BTC", "ETH"])
        print(f"Got {len(latest_prices)} price entries from database")
        
        for symbol, price_data in latest_prices.items():
            if price_data:
                print(f"  {symbol}: ${price_data.price_usd}")
            else:
                print(f"  {symbol}: No data")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_livecoinwatch_processor())
