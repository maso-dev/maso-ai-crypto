#!/usr/bin/env python3
"""
Phase 2 Technical Analysis Test
Tests the enhanced portfolio and technical analysis endpoints
"""

import asyncio
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.getcwd())


async def test_technical_analysis():
    """Test the technical analysis functionality."""
    print("🧪 Testing Phase 2 Technical Analysis...")

    try:
        # Test the technical sentiment analysis function
        from main import _analyze_technical_sentiment

        # Test with mock indicators
        mock_indicators = {
            "rsi_14": 65.2,
            "macd": {"macd": 1250.5, "signal": 1200.0, "histogram": 50.5},
            "bollinger_bands": {"upper": 45000, "middle": 42000, "lower": 39000},
            "moving_averages": {"sma_20": 41500, "sma_50": 40000, "ema_12": 41800},
            "volatility": 0.045,
        }

        sentiment = _analyze_technical_sentiment("BTC", mock_indicators)
        print(f"✅ Technical sentiment analysis: {sentiment}")

        # Test with oversold RSI
        oversold_indicators = {
            "rsi_14": 25.0,
            "macd": {"macd": 1000.0, "signal": 1100.0, "histogram": -100.0},
            "volatility": 0.06,
        }

        oversold_sentiment = _analyze_technical_sentiment("ETH", oversold_indicators)
        print(f"✅ Oversold sentiment analysis: {oversold_sentiment}")

        return True

    except Exception as e:
        print(f"❌ Technical analysis test failed: {e}")
        return False


async def test_livecoinwatch_integration():
    """Test LiveCoinWatch integration."""
    print("🧪 Testing LiveCoinWatch Integration...")

    try:
        from utils.livecoinwatch_processor import LiveCoinWatchProcessor

        processor = LiveCoinWatchProcessor()

        # Test getting latest prices
        latest_prices = await processor.get_latest_prices(["BTC", "ETH"])
        print(f"✅ Latest prices retrieved: {len(latest_prices)} symbols")

        # Test technical indicators (this might take a moment)
        print("🔄 Calculating technical indicators for BTC...")
        indicators = await processor.calculate_technical_indicators("BTC", days=7)
        print(f"✅ Technical indicators calculated: {list(indicators.keys())}")

        return True

    except Exception as e:
        print(f"❌ LiveCoinWatch integration test failed: {e}")
        return False


async def main():
    """Run all Phase 2 tests."""
    print("🚀 PHASE 2 TECHNICAL ANALYSIS TESTS")
    print("=" * 50)

    tests = [test_technical_analysis, test_livecoinwatch_integration]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if await test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")

    print("=" * 50)
    print(f"📊 PHASE 2 TEST SUMMARY")
    print(f"Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")

    if passed == total:
        print("🎉 All Phase 2 tests passed!")
        return 0
    else:
        print("⚠️  Some Phase 2 tests failed.")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
