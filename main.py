from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse, HTMLResponse
from typing import Dict, Any
from pathlib import Path
import os
from datetime import datetime

app = FastAPI(title="🏛️ Masonic - Alpha Strategy Advisor")

templates = Jinja2Templates(directory="templates")


# Custom static files handling for Vercel (similar to working example)
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
        "message": "FastAPI is working!",
        "timestamp": "2024",
        "status": "success",
        "endpoints": ["/", "/dashboard", "/api/health", "/api/portfolio"],
    }


# NEW: Welcome section for non-logged users
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


# NEW: Alpha portfolio API
@app.get("/api/dream-team")
async def get_dream_team_portfolio():
    """Get alpha portfolio data using AI analysis"""
    try:
        # Use enhanced agent for portfolio analysis (with fallback for missing LangChain)
        try:
            from utils.enhanced_agent import get_enhanced_agent
            from utils.binance_client import get_portfolio_data

            # Get portfolio data (will use mock if no API keys)
            portfolio_data = await get_portfolio_data()

            # Get enhanced agent analysis
            agent = get_enhanced_agent()
            if portfolio_data:
                analysis = await agent.generate_complete_analysis(
                    portfolio_data, symbols=["BTC", "ETH", "XRP", "SOL", "DOGE"]
                )
            else:
                # Use mock portfolio data for analysis
                from utils.binance_client import PortfolioData, PortfolioAsset

                mock_portfolio = PortfolioData(
                    total_value_usdt=100000.0,
                    total_cost_basis=60000.0,
                    total_roi_percentage=66.67,
                    assets=[
                        PortfolioAsset(
                            asset="BTC",
                            free=1.0,
                            locked=0.0,
                            total=1.0,
                            usdt_value=50000.0,
                            cost_basis=40000.0,
                            roi_percentage=25.0,
                            avg_buy_price=40000.0,
                        ),
                        PortfolioAsset(
                            asset="ETH",
                            free=5.0,
                            locked=0.0,
                            total=5.0,
                            usdt_value=25000.0,
                            cost_basis=20000.0,
                            roi_percentage=25.0,
                            avg_buy_price=4000.0,
                        ),
                    ],
                    last_updated=datetime.now(),
                )
                analysis = await agent.generate_complete_analysis(
                    mock_portfolio, symbols=["BTC", "ETH", "XRP", "SOL", "DOGE"]
                )

            return {
                "portfolio": analysis.portfolio_analysis if analysis else None,
                "market_analysis": analysis.market_analysis if analysis else None,
                "recommendations": analysis.recommendations if analysis else [],
                "risk_assessment": analysis.risk_assessment if analysis else {},
                "last_updated": datetime.now().isoformat(),
            }
        except Exception:
            # Fallback to static data
            return {
                "portfolio": {
                    "total_value": 100000.0,
                    "total_roi": 66.67,
                    "assets": ["BTC", "ETH", "XRP", "SOL", "DOGE"],
                },
                "market_analysis": {
                    "trend": "bullish",
                    "confidence": 0.75,
                    "key_levels": {"BTC": 40000, "ETH": 3000},
                },
                "recommendations": [
                    {
                        "action": "HOLD",
                        "asset": "BTC",
                        "reason": "Strong support at $40K",
                    },
                    {"action": "BUY", "asset": "ETH", "reason": "Breakout potential"},
                ],
                "risk_assessment": {"overall_risk": "medium", "volatility": "high"},
                "last_updated": datetime.now().isoformat(),
            }
    except Exception:
        return {"error": "Portfolio analysis failed"}


# NEW: Alpha signals API
@app.get("/api/opportunities")
async def get_enhanced_opportunities():
    """Enhanced opportunities using existing AI agent and technical analysis."""
    try:
        # Import existing systems
        from utils.enhanced_context_rag import get_symbol_context
        from utils.livecoinwatch_processor import LiveCoinWatchProcessor
        from utils.ai_agent import CryptoAIAgent, AgentTask

        # Initialize systems
        livecoinwatch_processor = LiveCoinWatchProcessor()
        ai_agent = CryptoAIAgent()  # Uses LangGraph + LangSmith

        # 1. Get symbol context for major tokens
        symbols = ["BTC", "ETH", "SOL", "XRP", "DOGE", "ADA", "DOT", "LINK"]
        opportunities = []

        for symbol in symbols:
            try:
                # Get symbol context (existing system)
                await get_symbol_context(symbol)

                # Get LiveCoinWatch data
                latest_prices = await livecoinwatch_processor.get_latest_prices(
                    [symbol]
                )
                price_data = latest_prices.get(symbol)

                # Get technical indicators
                indicators = (
                    await livecoinwatch_processor.calculate_technical_indicators(symbol)
                )

                # Generate opportunity using LangGraph agent
                ai_analysis = await ai_agent.execute_task(
                    AgentTask.TRADING_SIGNAL,
                    query=f"Analyze {symbol} for trading opportunities",
                    symbols=[symbol],
                )

                if ai_analysis and ai_analysis.recommendations:
                    for rec in ai_analysis.recommendations:
                        opportunities.append(
                            {
                                "symbol": symbol,
                                "type": rec.get("action", "HOLD"),
                                "reason": rec.get("reasoning", "No specific reason"),
                                "confidence": rec.get("confidence", 0.5),
                                "price": price_data.price_usd if price_data else 0,
                                "change_24h": (
                                    price_data.change_24h if price_data else 0
                                ),
                                "technical_indicators": indicators,
                                "ai_insights": rec.get("insights", []),
                            }
                        )
            except Exception as e:
                print(f"Opportunity analysis failed for {symbol}: {e}")
                continue

        # Sort by confidence
        opportunities.sort(key=lambda x: x["confidence"], reverse=True)

        return {
            "opportunities": opportunities[:5],  # Top 5
            "total_analyzed": len(symbols),
            "last_updated": datetime.now().isoformat(),
            "status": "success",
        }
    except Exception as e:
        print(f"Opportunities API error: {e}")
        return {
            "opportunities": [],
            "total_analyzed": 0,
            "last_updated": datetime.now().isoformat(),
            "status": "fallback",
            "error": str(e),
        }


# NEW: Brotherhood intelligence API
@app.get("/api/news-briefing")
async def get_enhanced_news():
    """Enhanced news using existing intelligent cache and hybrid RAG systems."""
    try:
        # Import existing systems
        from utils.intelligent_news_cache import (
            get_portfolio_news,
            get_cache_statistics,
        )
        from utils.hybrid_rag import HybridRAGSystem, HybridQuery, HybridQueryType
        from utils.ai_agent import CryptoAIAgent, AgentTask

        # Initialize systems
        hybrid_rag = HybridRAGSystem()
        ai_agent = CryptoAIAgent()  # Uses LangGraph + LangSmith

        # 1. Get portfolio-aware news (existing system)
        news_data = await get_portfolio_news(
            include_alpha_portfolio=True,
            include_opportunity_tokens=True,
            include_personal_portfolio=True,
            hours_back=24,
        )

        # 2. Use hybrid RAG for enhanced search
        hybrid_query = HybridQuery(
            query_text="crypto market news analysis",
            query_type=HybridQueryType.SENTIMENT_ANALYSIS,
            symbols=["BTC", "ETH", "SOL", "XRP", "DOGE"],
            time_range_hours=24,
            limit=15,
        )

        hybrid_results = await hybrid_rag.hybrid_search(hybrid_query)

        # 3. Combine with existing news data
        combined_news = []

        # Add cached news
        for category, articles in news_data.get("news_by_category", {}).items():
            combined_news.extend(articles[:5])  # Top 5 per category

        # Add hybrid RAG results
        for result in hybrid_results:
            combined_news.append(
                {
                    "title": result.title,
                    "content": result.content,
                    "source_url": result.source_url,
                    "published_at": result.published_at.isoformat(),
                    "sentiment_score": result.sentiment_score,
                    "relevance_score": result.relevance_score,
                    "source": "hybrid_rag",
                }
            )

        # 4. Get AI sentiment analysis using LangGraph agent
        sentiment_analysis = await ai_agent.execute_task(
            AgentTask.NEWS_SENTIMENT_ANALYSIS,
            query="Analyze overall crypto market sentiment",
            symbols=["BTC", "ETH", "SOL", "XRP", "DOGE"],
        )

        return {
            "news": combined_news[:20],  # Top 20 for MVP
            "sentiment": (
                sentiment_analysis.analysis_results
                if sentiment_analysis
                else {"overall": "neutral", "score": 0.5}
            ),
            "sources": ["newsapi", "tavily", "hybrid_rag"],
            "total_articles": len(combined_news),
            "cache_stats": get_cache_statistics(),
            "last_updated": datetime.now().isoformat(),
            "status": "success",
        }
    except Exception as e:
        print(f"News API error: {e}")
        return {
            "news": [],
            "sentiment": {"overall": "neutral", "score": 0.5},
            "sources": [],
            "total_articles": 0,
            "cache_stats": {},
            "last_updated": datetime.now().isoformat(),
            "status": "fallback",
            "error": str(e),
        }


@app.get("/dashboard")
def smart_dashboard(request: Request):
    """Smart dashboard that detects API connectivity and routes accordingly"""
    try:
        # Test Binance API connectivity
        from utils.binance_client import get_binance_client, get_portfolio_data

        # Check if we have API keys configured
        binance_client = get_binance_client()
        api_keys_configured = binance_client is not None

        print(f"🏛️ Smart Dashboard: API keys configured: {api_keys_configured}")

        # Try to get real portfolio data
        import asyncio

        portfolio_data = asyncio.run(get_portfolio_data())

        print(
            f"🏛️ Smart Dashboard: Portfolio data received: {portfolio_data is not None}"
        )

        # Determine if we're using real or mock data
        is_real_data = False
        if portfolio_data and api_keys_configured:
            # Check if this looks like real data (not our mock data)
            total_value = portfolio_data.total_value_usdt
            asset_count = len(portfolio_data.assets)

            print(
                f"🏛️ Smart Dashboard: Total value: {total_value}, Asset count: {asset_count}"
            )

            # Check for mock data characteristics
            is_mock_data = (
                total_value == 36500.0
                and asset_count == 4
                and any(
                    asset.asset == "BTC" and asset.usdt_value == 25000.0
                    for asset in portfolio_data.assets
                )
            )

            print(f"🏛️ Smart Dashboard: Is mock data: {is_mock_data}")

            # If it's NOT mock data, then it's real data
            if not is_mock_data:
                is_real_data = True
                print("🏛️ Smart Dashboard: Detected REAL data!")

        # Always show the main dashboard with appropriate data mode
        data_mode = "real" if is_real_data else "mock"
        api_status = "connected" if is_real_data else "demo"

        print(
            f"🏛️ Smart Dashboard: Using {data_mode.upper()} data - showing main dashboard"
        )
        return templates.TemplateResponse(
            "dashboard.html",
            {"request": request, "data_mode": data_mode, "api_status": api_status},
        )

    except Exception as e:
        print(f"🏛️ Smart Dashboard Error: {e} - showing main dashboard with error mode")
        return templates.TemplateResponse(
            "dashboard.html",
            {"request": request, "data_mode": "error", "api_status": "error"},
        )


# Import routers with error handling
try:
    from routers.crypto_news_rag import router as crypto_news_rag_router

    app.include_router(crypto_news_rag_router)
except ImportError as e:
    print(f"Warning: Could not import crypto_news_rag_router: {e}")

try:
    from routers.portfolio_user import router as portfolio_router

    app.include_router(portfolio_router)
except ImportError as e:
    print(f"Warning: Could not import portfolio_router: {e}")

try:
    from routers.agent import router as agent_router

    app.include_router(agent_router)
except ImportError as e:
    print(f"Warning: Could not import agent_router: {e}")

try:
    from routers.cost_tracking import router as cost_tracking_router

    app.include_router(cost_tracking_router)
except ImportError as e:
    print(f"Warning: Could not import cost_tracking_router: {e}")

try:
    from routers.admin import router as admin_router

    app.include_router(admin_router)
except ImportError as e:
    print(f"Warning: Could not import admin_router: {e}")

try:
    from routers.brain_enhanced import router as brain_enhanced_router

    app.include_router(brain_enhanced_router)
except ImportError as e:
    print(f"Warning: Could not import brain_enhanced_router: {e}")

try:
    from routers.brain_simple import router as brain_simple_router

    app.include_router(brain_simple_router)
except ImportError as e:
    print(f"Warning: Could not import brain_simple_router: {e}")


@app.get("/api/portfolio", response_model=Dict[str, Any])
async def get_enhanced_portfolio() -> Dict[str, Any]:
    """Enhanced portfolio using existing systems - Hybrid RAG, AI Agent, LiveCoinWatch."""
    try:
        # Import all existing systems
        from utils.binance_client import get_portfolio_data
        from utils.enhanced_context_rag import get_portfolio_context
        from utils.livecoinwatch_processor import LiveCoinWatchProcessor
        from utils.ai_agent import CryptoAIAgent, AgentTask

        # Initialize systems
        livecoinwatch_processor = LiveCoinWatchProcessor()
        ai_agent = CryptoAIAgent()  # Uses LangGraph + LangSmith

        # 1. Get portfolio context (existing enhanced system)
        context = await get_portfolio_context(
            include_news=True, include_analysis=True, include_opportunities=True
        )

        # 2. Get portfolio data (existing)
        portfolio_data = await get_portfolio_data()

        # 3. Add LiveCoinWatch real-time prices
        livecoinwatch_data = {}
        if portfolio_data and portfolio_data.assets:
            symbols = [asset.asset for asset in portfolio_data.assets]
            try:
                latest_prices = await livecoinwatch_processor.get_latest_prices(symbols)
                for symbol, price_data in latest_prices.items():
                    livecoinwatch_data[symbol] = {
                        "price": price_data.price_usd,
                        "change_24h": price_data.change_24h,
                        "volume_24h": price_data.volume_24h,
                        "market_cap": price_data.market_cap,
                        "timestamp": price_data.timestamp.isoformat(),
                    }
            except Exception as e:
                print(f"LiveCoinWatch failed: {e}")

        # 4. Add technical indicators
        technical_indicators = {}
        if portfolio_data and portfolio_data.assets:
            for asset in portfolio_data.assets:
                try:
                    indicators = (
                        await livecoinwatch_processor.calculate_technical_indicators(
                            asset.asset
                        )
                    )
                    technical_indicators[asset.asset] = indicators
                except Exception as e:
                    print(f"Technical indicators failed for {asset.asset}: {e}")
                    continue

        # 5. Get AI market analysis using LangGraph agent
        ai_analysis = None
        if portfolio_data and portfolio_data.assets:
            try:
                symbols = [asset.asset for asset in portfolio_data.assets]
                ai_analysis = await ai_agent.execute_task(
                    AgentTask.MARKET_ANALYSIS,
                    query="Analyze portfolio performance and market conditions",
                    symbols=symbols,
                )
            except Exception as e:
                print(f"AI analysis failed: {e}")

        # 6. Prepare enhanced response
        if portfolio_data:
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
                    "data_source": "binance",
                },
                "insights": context.get("portfolio_insights", []),
                "opportunities": context.get("trading_opportunities", []),
                "risk_assessment": context.get("risk_assessment", {}),
                "live_prices": livecoinwatch_data,
                "technical_indicators": technical_indicators,
                "ai_analysis": ai_analysis.analysis_results if ai_analysis else None,
                "last_updated": datetime.now().isoformat(),
                "status": "success",
            }
        else:
            # Return enhanced mock data
            return {
                "portfolio": {
                    "total_value_usdt": 36500.0,
                    "total_cost_basis": 22000.0,
                    "total_roi_percentage": 66.67,
                    "assets": [
                        {
                            "asset": "BTC",
                            "free": 0.5,
                            "locked": 0.0,
                            "total": 0.5,
                            "usdt_value": 25000.0,
                            "cost_basis": 20000.0,
                            "roi_percentage": 25.0,
                            "avg_buy_price": 40000.0,
                        },
                        {
                            "asset": "ETH",
                            "free": 2.0,
                            "locked": 0.0,
                            "total": 2.0,
                            "usdt_value": 8000.0,
                            "cost_basis": 6000.0,
                            "roi_percentage": 33.3,
                            "avg_buy_price": 3000.0,
                        },
                    ],
                    "last_updated": datetime.now().isoformat(),
                    "data_source": "mock",
                },
                "insights": context.get("portfolio_insights", []),
                "opportunities": context.get("trading_opportunities", []),
                "risk_assessment": context.get("risk_assessment", {}),
                "live_prices": livecoinwatch_data,
                "technical_indicators": technical_indicators,
                "ai_analysis": ai_analysis.analysis_results if ai_analysis else None,
                "last_updated": datetime.now().isoformat(),
                "status": "success",
            }
    except Exception as e:
        print(f"Portfolio API error: {e}")
        # Return enhanced fallback data
        return {
            "portfolio": {
                "total_value_usdt": 36500.0,
                "total_cost_basis": 22000.0,
                "total_roi_percentage": 66.67,
                "assets": [
                    {
                        "asset": "BTC",
                        "free": 0.5,
                        "locked": 0.0,
                        "total": 0.5,
                        "usdt_value": 25000.0,
                        "cost_basis": 20000.0,
                        "roi_percentage": 25.0,
                        "avg_buy_price": 40000.0,
                    },
                    {
                        "asset": "ETH",
                        "free": 2.0,
                        "locked": 0.0,
                        "total": 2.0,
                        "usdt_value": 8000.0,
                        "cost_basis": 6000.0,
                        "roi_percentage": 33.3,
                        "avg_buy_price": 3000.0,
                    },
                ],
                "last_updated": datetime.now().isoformat(),
                "data_source": "fallback",
            },
            "insights": [],
            "opportunities": [],
            "risk_assessment": {},
            "live_prices": {},
            "technical_indicators": {},
            "ai_analysis": None,
            "last_updated": datetime.now().isoformat(),
            "status": "fallback",
            "error": str(e),
        }


@app.get("/api/asset/{symbol}", response_model=Dict[str, Any])
async def get_asset_details(symbol: str) -> Dict[str, Any]:
    """Get asset details using the new async Binance client."""
    try:
        from utils.binance_client import get_portfolio_data

        portfolio_data = await get_portfolio_data()
        if portfolio_data:
            for asset in portfolio_data.assets:
                if asset.asset == symbol:
                    return {
                        "symbol": symbol,
                        "free": asset.free,
                        "locked": asset.locked,
                        "total": asset.total,
                        "usdt_value": asset.usdt_value,
                        "cost_basis": asset.cost_basis,
                        "roi_percentage": asset.roi_percentage,
                        "avg_buy_price": asset.avg_buy_price,
                    }
        return {"error": f"Asset {symbol} not found"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error for {symbol}: {str(e)}")


@app.get("/api/top-movers", response_model=Dict[str, Any])
async def get_top_movers() -> Dict[str, Any]:
    """Get top movers using LiveCoinWatch data."""
    try:
        from utils.livecoinwatch_processor import LiveCoinWatchProcessor

        processor = LiveCoinWatchProcessor()
        latest_prices = await processor.get_latest_prices()
        return {"top_movers": list(latest_prices.values())[:10]}
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/etf-comparison", response_model=Dict[str, Any])
async def etf_comparison() -> Dict[str, Any]:
    """Get ETF comparison data."""
    return {
        "etfs": [
            {"name": "BITO", "performance": "+15.2%", "volume": "2.1B"},
            {"name": "BITX", "performance": "+12.8%", "volume": "1.8B"},
        ]
    }


@app.get("/admin_conf")
async def admin_configuration():
    """Admin configuration endpoint for API status and settings."""
    try:
        from utils.config import get_api_key

        # Get API configurations
        api_configs = {
            "binance": {
                "key_set": bool(get_api_key("binance")),
                "status": "configured" if get_api_key("binance") else "not_configured",
            },
            "openai": {
                "key_set": bool(get_api_key("openai")),
                "status": "configured" if get_api_key("openai") else "not_configured",
            },
            "newsapi": {
                "key_set": bool(get_api_key("newsapi")),
                "status": "configured" if get_api_key("newsapi") else "not_configured",
            },
            "livecoinwatch": {
                "key_set": bool(get_api_key("livecoinwatch")),
                "status": (
                    "configured" if get_api_key("livecoinwatch") else "not_configured"
                ),
            },
            "tavily": {
                "key_set": bool(get_api_key("tavily")),
                "status": "configured" if get_api_key("tavily") else "not_configured",
            },
            "milvus": {
                "key_set": bool(get_api_key("milvus")),
                "status": "configured" if get_api_key("milvus") else "not_configured",
            },
            "neo4j": {
                "key_set": bool(get_api_key("neo4j")),
                "status": "configured" if get_api_key("neo4j") else "not_configured",
            },
            "langsmith": {
                "key_set": bool(get_api_key("langsmith")),
                "status": (
                    "configured" if get_api_key("langsmith") else "not_configured"
                ),
            },
        }

        # Check overall configuration
        configured_apis = sum(1 for config in api_configs.values() if config["key_set"])
        api_keys_configured = configured_apis >= 2  # At least 2 keys needed

        return {
            "api_configurations": api_configs,
            "api_keys_configured": api_keys_configured,
            "configured_count": configured_apis,
            "total_apis": len(api_configs),
            "status": "ready" if api_keys_configured else "needs_configuration",
            "last_updated": datetime.now().isoformat(),
        }
    except Exception as e:
        return {
            "error": str(e),
            "status": "error",
            "last_updated": datetime.now().isoformat(),
        }


# Import routers with error handling
try:
    from routers.crypto_news_rag import router as crypto_news_rag_router

    app.include_router(crypto_news_rag_router)
except ImportError as e:
    print(f"Warning: Could not import crypto_news_rag_router: {e}")

try:
    from routers.portfolio_user import router as portfolio_router

    app.include_router(portfolio_router)
except ImportError as e:
    print(f"Warning: Could not import portfolio_router: {e}")

try:
    from routers.agent import router as agent_router

    app.include_router(agent_router)
except ImportError as e:
    print(f"Warning: Could not import agent_router: {e}")

try:
    from routers.cost_tracking import router as cost_tracking_router

    app.include_router(cost_tracking_router)
except ImportError as e:
    print(f"Warning: Could not import cost_tracking_router: {e}")

try:
    from routers.admin import router as admin_router

    app.include_router(admin_router)
except ImportError as e:
    print(f"Warning: Could not import admin_router: {e}")

try:
    from routers.brain_enhanced import router as brain_enhanced_router

    app.include_router(brain_enhanced_router)
except ImportError as e:
    print(f"Warning: Could not import brain_enhanced_router: {e}")

try:
    from routers.brain_simple import router as brain_simple_router

    app.include_router(brain_simple_router)
except ImportError as e:
    print(f"Warning: Could not import brain_simple_router: {e}")


@app.get("/admin")
def admin_page(request: Request):
    """Admin dashboard for system monitoring and configuration."""
    return templates.TemplateResponse("admin.html", {"request": request})


@app.get("/brain-dashboard")
def brain_dashboard(request: Request):
    """Brain dashboard for AI system monitoring."""
    return templates.TemplateResponse("brain_dashboard.html", {"request": request})


@app.get("/status-dashboard")
def status_dashboard(request: Request):
    """Status dashboard for system health monitoring."""
    return templates.TemplateResponse("status_dashboard.html", {"request": request})
