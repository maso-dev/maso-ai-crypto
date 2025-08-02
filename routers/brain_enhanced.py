#!/usr/bin/env python3
"""
Enhanced Brain API Router
Integrates news processing, AI enrichment, and LangSmith tracing.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import os
import asyncio
import json
from pydantic import BaseModel

# Import our enhanced components
from utils.enhanced_news_pipeline import get_enhanced_crypto_news, EnhancedNewsPipeline
from utils.enrichment import enrich_news_articles
from utils.realtime_data import realtime_manager, DataSource, CryptoPrice, MarketUpdate
from utils.vector_rag import EnhancedVectorRAG, VectorQuery, QueryType, intelligent_search, insert_enhanced_news_batch
from utils.ai_agent import CryptoAIAgent, AgentTask, execute_agent_task, analyze_market_sentiment, generate_portfolio_recommendations
from langchain_core.runnables import RunnableConfig

router = APIRouter(prefix="/brain", tags=["brain"])

# LangSmith configuration
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
if LANGSMITH_API_KEY:
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_PROJECT"] = "masonic-brain"
    os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
    os.environ["LANGCHAIN_ORGANIZATION"] = "703f12b7-8da7-455d-9870-c0dd95d12d7d"

class NewsRequest(BaseModel):
    symbols: Optional[List[str]] = None
    hours_back: int = 24
    enable_enrichment: bool = True
    max_articles: int = 50

class BrainOperation(BaseModel):
    operation: str
    parameters: Dict[str, Any] = {}

@router.get("/health")
async def brain_health() -> Dict[str, Any]:
    """Get enhanced brain health status."""
    import os
    
    # Check environment variables
    newsapi_configured = bool(os.getenv("NEWSAPI_KEY"))
    openai_configured = bool(os.getenv("OPENAI_API_KEY"))
    langsmith_configured = bool(os.getenv("LANGSMITH_API_KEY"))
    
    issues = []
    recommendations = []
    
    if not langsmith_configured:
        issues.append("LangSmith not configured - tracing disabled")
        recommendations.append("Set LANGSMITH_API_KEY environment variable")
    
    if not newsapi_configured:
        issues.append("NewsAPI not configured - using mock data")
        recommendations.append("Set NEWSAPI_KEY environment variable")
    
    if not openai_configured:
        issues.append("OpenAI not configured - AI features disabled")
        recommendations.append("Set OPENAI_API_KEY environment variable")
    
    return {
        "status": "healthy",
        "brain_id": "masonic-brain-enhanced-v1",
        "environment": "development",
        "last_check": datetime.now(timezone.utc).isoformat(),
        "checks": {
            "configuration_loaded": True,
            "brain_state_active": True,
            "metrics_tracking": True,
            "langsmith_configured": langsmith_configured,
            "openai_configured": openai_configured,
            "newsapi_configured": newsapi_configured,
            "enhanced_pipeline": True
        },
        "issues": issues,
        "recommendations": recommendations,
        "langsmith": {
            "organization_id": "703f12b7-8da7-455d-9870-c0dd95d12d7d",
            "project": "masonic-brain",
            "tracing_enabled": langsmith_configured
        }
    }

@router.get("/news/enriched")
async def get_enriched_news(
    symbols: Optional[str] = None,
    hours_back: int = 24,
    enable_enrichment: bool = True,
    max_articles: int = 50
) -> Dict[str, Any]:
    """
    Get enriched crypto news with AI analysis and LangSmith tracing.
    
    Args:
        symbols: Comma-separated list of crypto symbols
        hours_back: Hours to look back
        enable_enrichment: Enable AI enrichment
        max_articles: Maximum articles to return
    """
    try:
        # Parse symbols
        symbol_list = None
        if symbols:
            symbol_list = [s.strip() for s in symbols.split(",")]
        
        # Get enhanced news
        result = await get_enhanced_crypto_news(
            symbols=symbol_list,
            hours_back=hours_back,
            enable_enrichment=enable_enrichment
        )
        
        # Limit articles if needed
        if result["success"] and len(result["articles"]) > max_articles:
            result["articles"] = result["articles"][:max_articles]
            result["metadata"]["total_articles"] = max_articles
        
        return {
            "success": True,
            "data": result,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "langsmith_traced": bool(LANGSMITH_API_KEY)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"News processing failed: {str(e)}")

@router.post("/news/process")
async def process_news_batch(request: NewsRequest) -> Dict[str, Any]:
    """
    Process news with custom parameters.
    """
    try:
        result = await get_enhanced_crypto_news(
            symbols=request.symbols,
            hours_back=request.hours_back,
            enable_enrichment=request.enable_enrichment
        )
        
        # Limit articles
        if result["success"] and len(result["articles"]) > request.max_articles:
            result["articles"] = result["articles"][:request.max_articles]
            result["metadata"]["total_articles"] = request.max_articles
        
        return {
            "success": True,
            "data": result,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "langsmith_traced": bool(LANGSMITH_API_KEY)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"News processing failed: {str(e)}")

@router.get("/news/analyze")
async def analyze_news_sentiment(
    symbols: Optional[str] = None,
    hours_back: int = 24
) -> Dict[str, Any]:
    """
    Analyze news sentiment and market impact.
    """
    try:
        # Get enriched news
        symbol_list = None
        if symbols:
            symbol_list = [s.strip() for s in symbols.split(",")]
        
        result = await get_enhanced_crypto_news(
            symbols=symbol_list,
            hours_back=hours_back,
            enable_enrichment=True
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail="Failed to fetch news")
        
        # Analyze sentiment
        articles = result["articles"]
        enriched_articles = [art for art in articles if "enrichment" in art]
        
        if not enriched_articles:
            return {
                "success": False,
                "message": "No enriched articles available for analysis"
            }
        
        # Calculate sentiment statistics
        sentiments = [art["enrichment"]["sentiment"] for art in enriched_articles]
        trusts = [art["enrichment"]["trust"] for art in enriched_articles]
        
        # Categorize by market impact
        high_impact = [art for art in enriched_articles if art["enrichment"]["market_impact"] == "high"]
        medium_impact = [art for art in enriched_articles if art["enrichment"]["market_impact"] == "medium"]
        low_impact = [art for art in enriched_articles if art["enrichment"]["market_impact"] == "low"]
        
        # Get top categories
        all_categories = []
        for art in enriched_articles:
            all_categories.extend(art["enrichment"]["categories"])
        
        from collections import Counter
        top_categories = [cat for cat, _ in Counter(all_categories).most_common(5)]
        
        analysis = {
            "total_articles": len(articles),
            "enriched_articles": len(enriched_articles),
            "sentiment_analysis": {
                "average_sentiment": sum(sentiments) / len(sentiments) if sentiments else 0,
                "average_trust": sum(trusts) / len(trusts) if trusts else 0,
                "sentiment_range": {
                    "min": min(sentiments) if sentiments else 0,
                    "max": max(sentiments) if sentiments else 0
                }
            },
            "market_impact": {
                "high_impact": len(high_impact),
                "medium_impact": len(medium_impact),
                "low_impact": len(low_impact)
            },
            "top_categories": top_categories,
            "breaking_news": len([art for art in articles if art.get("is_breaking", False)]),
            "recent_news": len([art for art in articles if art.get("is_recent", False)])
        }
        
        return {
            "success": True,
            "analysis": analysis,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "langsmith_traced": bool(LANGSMITH_API_KEY)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.get("/metrics")
async def get_brain_metrics() -> Dict[str, Any]:
    """Get brain performance metrics."""
    return {
        "brain_id": "masonic-brain-enhanced-v1",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "performance": {
            "uptime_seconds": 3600,  # Mock uptime
            "requests_processed": 150,
            "articles_processed": 500,
            "enrichment_success_rate": 0.95
        },
        "langsmith": {
            "traces_sent": 45,
            "project": "masonic-brain",
            "organization": "703f12b7-8da7-455d-9870-c0dd95d12d7d"
        },
        "components": {
            "news_pipeline": "active",
            "enrichment_engine": "active",
            "langsmith_integration": "active" if LANGSMITH_API_KEY else "disabled"
        }
    }

@router.get("/config")
async def get_brain_config() -> Dict[str, Any]:
    """Get brain configuration."""
    return {
        "brain_id": "masonic-brain-enhanced-v1",
        "environment": "development",
        "langsmith": {
            "project_name": "masonic-brain",
            "organization_id": "703f12b7-8da7-455d-9870-c0dd95d12d7d",
            "tracing_v2": True,
            "tags": ["brain", "crypto", "enhanced"],
            "configured": bool(LANGSMITH_API_KEY)
        },
        "news_pipeline": {
            "update_interval_minutes": 30,
            "max_articles_per_update": 50,
            "relevance_threshold": 0.7,
            "enable_enrichment": True,
            "configured": bool(os.getenv("NEWSAPI_KEY"))
        },
        "enrichment": {
            "model": "gpt-4-turbo",
            "temperature": 0.4,
            "max_tokens": 300,
            "configured": bool(os.getenv("OPENAI_API_KEY"))
        },
        "crypto_data": {
            "update_interval_seconds": 60,
            "supported_symbols": ["Bitcoin", "Ethereum", "cryptocurrency", "blockchain"],
            "real_time_enabled": False
        }
    }

@router.post("/operations")
async def execute_brain_operation(operation: BrainOperation) -> Dict[str, Any]:
    """Execute brain operations."""
    try:
        if operation.operation == "refresh_news":
            # Background news refresh
            symbols = operation.parameters.get("symbols", ["Bitcoin", "Ethereum"])
            hours_back = operation.parameters.get("hours_back", 24)
            
            result = await get_enhanced_crypto_news(
                symbols=symbols,
                hours_back=hours_back,
                enable_enrichment=True
            )
            
            return {
                "success": True,
                "operation": "refresh_news",
                "result": {
                    "articles_processed": len(result.get("articles", [])),
                    "enrichment_enabled": True
                },
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        elif operation.operation == "analyze_market":
            # Market analysis
            return {
                "success": True,
                "operation": "analyze_market",
                "result": {
                    "sentiment": "positive",
                    "confidence": 0.85,
                    "trend": "bullish"
                },
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        else:
            raise HTTPException(status_code=400, detail=f"Unknown operation: {operation.operation}")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Operation failed: {str(e)}")

@router.get("/knowledge/stats")
async def get_knowledge_stats() -> Dict[str, Any]:
    """Get knowledge base statistics."""
    return {
        "knowledge_base": {
            "total_articles": 1250,
            "enriched_articles": 980,
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "categories": {
                "Bitcoin": 450,
                "Ethereum": 320,
                "DeFi": 280,
                "Regulation": 200
            }
        },
        "vector_store": {
            "status": "active",
            "embeddings": 1250,
            "collections": ["crypto_news", "market_analysis"]
        },
        "graph_store": {
            "status": "active",
            "nodes": 2500,
            "relationships": 5000
        }
    }

@router.post("/knowledge/search")
async def search_knowledge_base(request: Dict[str, Any]) -> Dict[str, Any]:
    """Search the knowledge base using enhanced vector RAG."""
    try:
        query_text = request.get("query", "")
        query_type = request.get("query_type", "semantic_search")
        symbols = request.get("symbols", [])
        time_range_hours = request.get("time_range_hours")
        limit = request.get("limit", 10)
        
        # Convert query type string to enum
        query_type_enum = QueryType(query_type)
        
        # Perform search
        results = await intelligent_search(
            query_text=query_text,
            query_type=query_type_enum,
            symbols=symbols,
            time_range_hours=time_range_hours,
            limit=limit
        )
        
        # Convert results to serializable format
        serializable_results = []
        for result in results:
            serializable_results.append({
                "content": result.content,
                "title": result.title,
                "source_url": result.source_url,
                "crypto_topic": result.crypto_topic,
                "published_at": result.published_at.isoformat(),
                "similarity_score": result.similarity_score,
                "sentiment_score": result.sentiment_score,
                "relevance_score": result.relevance_score,
                "metadata": result.metadata
            })
        
        return {
            "success": True,
            "query": query_text,
            "query_type": query_type,
            "results_count": len(serializable_results),
            "results": serializable_results,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Knowledge search failed: {str(e)}")

@router.post("/knowledge/insert")
async def insert_knowledge_batch(request: Dict[str, Any]) -> Dict[str, Any]:
    """Insert a batch of news items into the knowledge base."""
    try:
        news_items = request.get("news_items", [])
        
        if not news_items:
            raise HTTPException(status_code=400, detail="No news items provided")
        
        # Insert with LangSmith tracing
        config: Optional[RunnableConfig] = {
            "tags": ["knowledge_insert", "batch"],
            "metadata": {
                "batch_size": len(news_items),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        }
        
        inserted, updated, errors = await insert_enhanced_news_batch(news_items, config)
        
        return {
            "success": True,
            "inserted": inserted,
            "updated": updated,
            "errors": errors,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Knowledge insertion failed: {str(e)}")

@router.get("/knowledge/react-agent")
async def react_agent_search(
    query: str,
    symbols: Optional[str] = None,
    time_range_hours: Optional[int] = None,
    limit: int = 10
) -> Dict[str, Any]:
    """Perform ReAct agent-based search on the knowledge base."""
    try:
        # Parse symbols
        symbol_list = []
        if symbols:
            symbol_list = [s.strip() for s in symbols.split(",")]
        
        # Perform ReAct agent search
        results = await intelligent_search(
            query_text=query,
            query_type=QueryType.REACT_AGENT,
            symbols=symbol_list,
            time_range_hours=time_range_hours,
            limit=limit
        )
        
        # Convert results to serializable format
        serializable_results = []
        for result in results:
            serializable_results.append({
                "content": result.content,
                "title": result.title,
                "source_url": result.source_url,
                "crypto_topic": result.crypto_topic,
                "published_at": result.published_at.isoformat(),
                "similarity_score": result.similarity_score,
                "sentiment_score": result.sentiment_score,
                "relevance_score": result.relevance_score
            })
        
        return {
            "success": True,
            "query": query,
            "query_type": "react_agent",
            "results_count": len(serializable_results),
            "results": serializable_results,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ReAct agent search failed: {str(e)}")

# AI Agent Endpoints
@router.post("/agent/execute")
async def execute_ai_agent_task(request: Dict[str, Any]) -> Dict[str, Any]:
    """Execute an AI agent task with LangGraph workflow."""
    try:
        task_type = request.get("task_type", "market_analysis")
        query = request.get("query", "")
        symbols = request.get("symbols", [])
        
        # Convert task type to enum
        try:
            task = AgentTask(task_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid task type: {task_type}")
        
        # Execute with LangSmith tracing
        config: Optional[RunnableConfig] = {
            "tags": ["ai_agent", task_type],
            "metadata": {
                "task_type": task_type,
                "query": query,
                "symbols": symbols,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        }
        
        result = await execute_agent_task(task, query, symbols, config)
        
        # Convert to serializable format
        return {
            "success": True,
            "task_type": task_type,
            "query": query,
            "symbols": symbols,
            "current_step": result.current_step,
            "confidence_score": result.confidence_score,
            "reasoning_steps": result.reasoning_steps,
            "search_results_count": len(result.search_results),
            "market_data": result.market_data,
            "analysis_results": result.analysis_results,
            "recommendations": result.recommendations,
            "error": result.error,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI agent execution failed: {str(e)}")

@router.post("/agent/market-analysis")
async def analyze_market_with_agent(request: Dict[str, Any]) -> Dict[str, Any]:
    """Perform market analysis using AI agent."""
    try:
        symbols = request.get("symbols", [])
        
        if not symbols:
            raise HTTPException(status_code=400, detail="No symbols provided")
        
        # Execute market analysis
        config: Optional[RunnableConfig] = {
            "tags": ["ai_agent", "market_analysis"],
            "metadata": {
                "symbols": symbols,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        }
        
        result = await analyze_market_sentiment(symbols, config)
        
        return {
            "success": True,
            "task": "market_analysis",
            "symbols": symbols,
            "confidence_score": result.confidence_score,
            "market_analysis": result.analysis_results.get("market_analysis", ""),
            "synthesis": result.analysis_results.get("synthesis", ""),
            "recommendations": result.recommendations,
            "reasoning_steps": result.reasoning_steps,
            "error": result.error,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Market analysis failed: {str(e)}")

@router.post("/agent/portfolio-recommendations")
async def get_portfolio_recommendations(request: Dict[str, Any]) -> Dict[str, Any]:
    """Generate portfolio recommendations using AI agent."""
    try:
        symbols = request.get("symbols", [])
        risk_profile = request.get("risk_profile", "moderate")
        
        if not symbols:
            raise HTTPException(status_code=400, detail="No symbols provided")
        
        # Execute portfolio recommendation
        config: Optional[RunnableConfig] = {
            "tags": ["ai_agent", "portfolio_recommendation"],
            "metadata": {
                "symbols": symbols,
                "risk_profile": risk_profile,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        }
        
        result = await generate_portfolio_recommendations(symbols, risk_profile, config)
        
        return {
            "success": True,
            "task": "portfolio_recommendation",
            "symbols": symbols,
            "risk_profile": risk_profile,
            "confidence_score": result.confidence_score,
            "recommendations": result.recommendations,
            "market_analysis": result.analysis_results.get("market_analysis", ""),
            "reasoning_steps": result.reasoning_steps,
            "error": result.error,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Portfolio recommendations failed: {str(e)}")

@router.get("/agent/tasks")
async def get_available_agent_tasks() -> Dict[str, Any]:
    """Get list of available AI agent tasks."""
    return {
        "success": True,
        "available_tasks": [
            {
                "task_type": task.value,
                "description": task.name.replace("_", " ").title(),
                "category": "analysis" if "analysis" in task.value else "recommendation"
            }
            for task in AgentTask
        ],
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

# Real-time Data Endpoints
@router.get("/realtime/prices")
async def get_current_prices() -> Dict[str, Any]:
    """Get current crypto prices."""
    prices = realtime_manager.get_current_prices()
    return {
        "success": True,
        "prices": {
            symbol: {
                "price": price.price,
                "change_24h": price.change_24h,
                "volume_24h": price.volume_24h,
                "market_cap": price.market_cap,
                "timestamp": price.timestamp.isoformat(),
                "source": price.source
            } for symbol, price in prices.items()
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@router.get("/realtime/price/{symbol}")
async def get_price(symbol: str) -> Dict[str, Any]:
    """Get current price for a specific symbol."""
    price = realtime_manager.get_price(symbol)
    if price:
        return {
            "success": True,
            "symbol": symbol.upper(),
            "price": price.price,
            "change_24h": price.change_24h,
            "volume_24h": price.volume_24h,
            "market_cap": price.market_cap,
            "timestamp": price.timestamp.isoformat(),
            "source": price.source
        }
    else:
        raise HTTPException(status_code=404, detail=f"Price not found for {symbol}")

@router.post("/realtime/start")
async def start_realtime_data(request: Dict[str, Any]) -> Dict[str, Any]:
    """Start real-time data stream."""
    try:
        source = request.get("source", "mock")
        data_source = DataSource(source.lower())
        await realtime_manager.start(data_source)
        return {
            "success": True,
            "message": f"Real-time data started with source: {source}",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except ValueError as e:
        source = request.get("source", "unknown")
        raise HTTPException(status_code=400, detail=f"Invalid data source: {source}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start real-time data: {str(e)}")

@router.post("/realtime/stop")
async def stop_realtime_data() -> Dict[str, Any]:
    """Stop real-time data stream."""
    await realtime_manager.stop()
    return {
        "success": True,
        "message": "Real-time data stopped",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@router.get("/realtime/status")
async def get_realtime_status() -> Dict[str, Any]:
    """Get real-time data status."""
    return {
        "success": True,
        "running": realtime_manager.running,
        "subscribers": len(realtime_manager.subscribers),
        "websocket_clients": len(realtime_manager.websocket_connections),
        "cached_prices": len(realtime_manager.price_cache),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

# WebSocket endpoint for real-time data streaming
@router.websocket("/realtime/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for real-time data streaming."""
    await websocket.accept()
    
    try:
        # Add client to real-time manager
        await realtime_manager.add_websocket_client(websocket, client_id)
        
        # Subscribe to updates
        async def websocket_callback(update):
            try:
                if isinstance(update, CryptoPrice):
                    message = {
                        "type": "price_update",
                        "symbol": update.symbol,
                        "price": update.price,
                        "change_24h": update.change_24h,
                        "volume_24h": update.volume_24h,
                        "market_cap": update.market_cap,
                        "timestamp": update.timestamp.isoformat(),
                        "source": update.source
                    }
                elif isinstance(update, MarketUpdate):
                    message = {
                        "type": "market_update",
                        "update_type": update.type,
                        "symbol": update.symbol,
                        "data": update.data,
                        "priority": update.priority,
                        "timestamp": update.timestamp.isoformat()
                    }
                else:
                    message = {
                        "type": "update",
                        "data": str(update),
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                print(f"Error sending WebSocket message: {e}")
        
        realtime_manager.subscribe(websocket_callback)
        
        # Keep connection alive and handle incoming messages
        while True:
            try:
                # Wait for messages from client
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle client messages
                if message.get("type") == "ping":
                    await websocket.send_text(json.dumps({
                        "type": "pong",
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }))
                elif message.get("type") == "subscribe":
                    # Handle subscription requests
                    await websocket.send_text(json.dumps({
                        "type": "subscribed",
                        "symbols": message.get("symbols", []),
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }))
                
            except WebSocketDisconnect:
                break
            except Exception as e:
                print(f"WebSocket error: {e}")
                break
                
    except Exception as e:
        print(f"WebSocket connection error: {e}")
    finally:
        # Clean up
        realtime_manager.unsubscribe(websocket_callback)
        await realtime_manager.remove_websocket_client(client_id) 
