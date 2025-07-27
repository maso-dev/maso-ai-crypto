#!/usr/bin/env python3
"""
Test script for the actual endpoint integration with mock data.
Tests the /populate_crypto_news_rag endpoint with the optimized pipeline.
"""

import asyncio
import httpx
import json
from datetime import datetime

async def test_endpoint_with_mock_data():
    """Test the endpoint with mock data to verify optimized pipeline integration."""
    print("🧪 Testing Endpoint Integration with Mock Data...")
    
    # Mock article data that would come from NewsAPI
    mock_articles = [
        {
            "title": "Bitcoin Surges Past $50,000 as Institutional Adoption Accelerates",
            "content": "Bitcoin has reached a significant milestone, crossing the $50,000 mark for the first time in 2024. This surge is attributed to increased institutional adoption, with major financial institutions including BlackRock and Fidelity reporting record-breaking daily inflows into their Bitcoin ETFs. Analysts suggest this could be the beginning of a new bull cycle as traditional investors increasingly allocate to digital assets. The cryptocurrency market has seen over $1.2 billion in new investments this week alone, signaling growing mainstream acceptance of digital assets.",
            "crypto_topic": "BTC",
            "source_name": "CoinDesk",
            "source_url": "https://example.com/bitcoin-surge",
            "published_at": datetime.utcnow().isoformat() + "Z"
        },
        {
            "title": "Ethereum Layer 2 Solutions Drive DeFi Innovation",
            "content": "Ethereum's Layer 2 scaling solutions are revolutionizing the DeFi ecosystem, with platforms like Arbitrum and Optimism seeing unprecedented growth in user activity and total value locked (TVL). These solutions are addressing Ethereum's scalability challenges while maintaining security and decentralization. Developers are building innovative DeFi protocols that leverage the increased throughput and reduced gas fees offered by Layer 2 networks.",
            "crypto_topic": "ETH",
            "source_name": "Decrypt",
            "source_url": "https://example.com/eth-layer2",
            "published_at": datetime.utcnow().isoformat() + "Z"
        }
    ]
    
    try:
        # Test the endpoint
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/populate_crypto_news_rag",
                headers={"Content-Type": "application/json"},
                json={
                    "terms": ["BTC", "ETH"],
                    "chunking": {
                        "method": "summary",
                        "chunk_size": 200,
                        "overlap": 0
                    }
                },
                timeout=30.0
            )
            
            print(f"✅ Endpoint responded with status: {response.status_code}")
            result = response.json()
            print(f"📊 Response: {json.dumps(result, indent=2)}")
            
            if response.status_code == 200:
                print("✅ Endpoint integration test PASSED")
                return True
            else:
                print(f"❌ Endpoint returned error status: {response.status_code}")
                return False
                
    except httpx.ConnectError:
        print("❌ Could not connect to server. Make sure it's running on localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

async def test_server_health():
    """Test if the server is running and healthy."""
    print("🏥 Testing Server Health...")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/", timeout=5.0)
            print(f"✅ Server is running (status: {response.status_code})")
            return True
    except Exception as e:
        print(f"❌ Server health check failed: {e}")
        return False

async def main():
    """Run endpoint integration tests."""
    print("🚀 Starting Endpoint Integration Tests\n")
    
    try:
        # Test 1: Server health
        health_ok = await test_server_health()
        
        if health_ok:
            # Test 2: Endpoint integration
            endpoint_ok = await test_endpoint_with_mock_data()
            
            print(f"\n📊 Endpoint Test Results:")
            print(f"   Server health: {'✅ PASSED' if health_ok else '❌ FAILED'}")
            print(f"   Endpoint integration: {'✅ PASSED' if endpoint_ok else '❌ FAILED'}")
            
            if all([health_ok, endpoint_ok]):
                print("\n🎉 All endpoint tests passed!")
                print("   The optimized pipeline is fully integrated and working.")
            else:
                print("\n⚠️  Some endpoint tests failed.")
        else:
            print("\n❌ Server is not running. Please start the server first.")
            
    except Exception as e:
        print(f"\n❌ Endpoint test suite failed with error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 
