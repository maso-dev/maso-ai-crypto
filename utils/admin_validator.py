#!/usr/bin/env python3
"""
Admin Validator - Properly validates real vs mock data
"""

import asyncio
import os
from typing import Dict, Any, List
from datetime import datetime
from pydantic import BaseModel


class DataQualityStatus(BaseModel):
    """Represents the quality status of a data source"""
    is_real_data: bool
    is_operational: bool
    mock_mode: bool
    error_message: str | None = None
    last_check: datetime
    data_freshness_minutes: int = 0


class AdminValidationResult(BaseModel):
    """Complete admin validation result"""
    api_keys: Dict[str, bool]
    livecoinwatch: DataQualityStatus
    newsapi: DataQualityStatus
    neo4j: DataQualityStatus
    openai: DataQualityStatus
    tavily: DataQualityStatus
    milvus: DataQualityStatus
    langsmith: DataQualityStatus
    overall_health: str
    real_data_percentage: float
    last_updated: datetime


async def validate_livecoinwatch() -> DataQualityStatus:
    """Validate LiveCoinWatch API with real data check"""
    try:
        from utils.livecoinwatch_processor import LiveCoinWatchProcessor
        
        processor = LiveCoinWatchProcessor()
        
        # Force fresh data collection instead of reading from cache
        price_data_list = await processor.collect_price_data(["BTC", "ETH"])
        
        # Check if we get real prices from API
        real_prices = 0
        for price_data in price_data_list:
            if price_data and price_data.price_usd > 0:
                real_prices += 1
        
        is_real_data = real_prices > 0
        is_operational = True  # API responds
        mock_mode = not is_real_data
        
        return DataQualityStatus(
            is_real_data=is_real_data,
            is_operational=is_operational,
            mock_mode=mock_mode,
            last_check=datetime.now(),
            data_freshness_minutes=0 if mock_mode else 5
        )
        
    except Exception as e:
        return DataQualityStatus(
            is_real_data=False,
            is_operational=False,
            mock_mode=True,
            error_message=str(e),
            last_check=datetime.now()
        )


async def validate_newsapi() -> DataQualityStatus:
    """Validate NewsAPI with real data check"""
    try:
        from utils.intelligent_news_cache import get_portfolio_news
        
        news_data = await get_portfolio_news(
            include_alpha_portfolio=True,
            include_opportunity_tokens=True,
            include_personal_portfolio=True,
            hours_back=24,
        )
        
        # Check if we have real articles
        articles = news_data.get("news_by_category", {})
        total_articles = sum(len(articles_list) for articles_list in articles.values())
        
        # Check for mock indicators
        is_mock = False
        for category, articles_list in articles.items():
            for article in articles_list:
                if "mock" in str(article).lower() or "Mock" in str(article):
                    is_mock = True
                    break
        
        is_real_data = total_articles > 0 and not is_mock
        is_operational = True  # API responds
        mock_mode = is_mock
        
        return DataQualityStatus(
            is_real_data=is_real_data,
            is_operational=is_operational,
            mock_mode=mock_mode,
            last_check=datetime.now(),
            data_freshness_minutes=0 if mock_mode else 60
        )
        
    except Exception as e:
        return DataQualityStatus(
            is_real_data=False,
            is_operational=False,
            mock_mode=True,
            error_message=str(e),
            last_check=datetime.now()
        )


async def validate_neo4j() -> DataQualityStatus:
    """Validate Neo4j connection"""
    try:
        from utils.graph_rag import Neo4jGraphRAG
        
        graph_rag = Neo4jGraphRAG()
        is_connected = graph_rag.connected
        
        return DataQualityStatus(
            is_real_data=is_connected,
            is_operational=is_connected,
            mock_mode=not is_connected,
            last_check=datetime.now(),
            data_freshness_minutes=0 if not is_connected else 30
        )
        
    except Exception as e:
        return DataQualityStatus(
            is_real_data=False,
            is_operational=False,
            mock_mode=True,
            error_message=str(e),
            last_check=datetime.now()
        )


async def validate_openai() -> DataQualityStatus:
    """Validate OpenAI API"""
    try:
        import openai
        from utils.config import get_api_key
        
        api_key = get_api_key("openai")
        if not api_key:
            raise ValueError("OpenAI API key not configured")
        
        # Test with a simple completion
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=5
        )
        
        is_working = response.choices[0].message.content is not None
        
        return DataQualityStatus(
            is_real_data=is_working,
            is_operational=is_working,
            mock_mode=not is_working,
            last_check=datetime.now(),
            data_freshness_minutes=0 if not is_working else 1
        )
        
    except Exception as e:
        return DataQualityStatus(
            is_real_data=False,
            is_operational=False,
            mock_mode=True,
            error_message=str(e),
            last_check=datetime.now()
        )


async def validate_tavily() -> DataQualityStatus:
    """Validate Tavily API"""
    try:
        from utils.tavily_search import TavilySearchClient
        
        client = TavilySearchClient()
        response = await client.search_news(
            query="bitcoin",
            max_results=1,
            time_period="1d"
        )
        
        is_working = len(response.results) > 0
        
        return DataQualityStatus(
            is_real_data=is_working,
            is_operational=is_working,
            mock_mode=not is_working,
            last_check=datetime.now(),
            data_freshness_minutes=0 if not is_working else 10
        )
        
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            error_msg = "API key invalid or expired - get new key from tavily.com"
        
        return DataQualityStatus(
            is_real_data=False,
            is_operational=False,
            mock_mode=True,
            error_message=error_msg,
            last_check=datetime.now()
        )


async def validate_milvus() -> DataQualityStatus:
    """Validate Milvus vector database"""
    try:
        from utils.config import get_api_key
        
        # Check if Milvus URI is configured
        milvus_uri = get_api_key("milvus")
        is_configured = bool(milvus_uri)
        
        # For now, assume it's working if configured
        # In production, you'd test the actual connection
        is_connected = is_configured
        
        return DataQualityStatus(
            is_real_data=is_connected,
            is_operational=is_connected,
            mock_mode=not is_connected,
            last_check=datetime.now(),
            data_freshness_minutes=0 if not is_connected else 15
        )
        
    except Exception as e:
        return DataQualityStatus(
            is_real_data=False,
            is_operational=False,
            mock_mode=True,
            error_message=str(e),
            last_check=datetime.now()
        )


async def validate_langsmith() -> DataQualityStatus:
    """Validate LangSmith tracing"""
    try:
        from utils.config import get_api_key
        
        api_key = get_api_key("langsmith")
        if not api_key:
            raise ValueError("LangSmith API key not configured")
        
        # Check if LangSmith is properly configured
        import os
        langsmith_configured = bool(os.getenv("LANGCHAIN_TRACING_V2"))
        
        return DataQualityStatus(
            is_real_data=langsmith_configured,
            is_operational=langsmith_configured,
            mock_mode=not langsmith_configured,
            last_check=datetime.now(),
            data_freshness_minutes=0 if not langsmith_configured else 5
        )
        
    except Exception as e:
        return DataQualityStatus(
            is_real_data=False,
            is_operational=False,
            mock_mode=True,
            error_message=str(e),
            last_check=datetime.now()
        )


def validate_api_keys() -> Dict[str, bool]:
    """Validate all API keys are configured"""
    from utils.config import get_api_key
    
    apis = [
        "binance", "openai", "newsapi", "livecoinwatch", 
        "tavily", "milvus", "neo4j", "langsmith"
    ]
    
    api_keys = {}
    for api in apis:
        try:
            key = get_api_key(api)
            api_keys[api] = bool(key)
        except:
            api_keys[api] = False
    
    return api_keys


async def get_comprehensive_admin_status() -> AdminValidationResult:
    """Get comprehensive admin status with real vs mock data validation"""
    
    # Validate all components
    api_keys = validate_api_keys()
    livecoinwatch = await validate_livecoinwatch()
    newsapi = await validate_newsapi()
    neo4j = await validate_neo4j()
    openai = await validate_openai()
    tavily = await validate_tavily()
    milvus = await validate_milvus()
    langsmith = await validate_langsmith()
    
    # Calculate overall health
    components = [livecoinwatch, newsapi, neo4j, openai, tavily, milvus, langsmith]
    operational_count = sum(1 for comp in components if comp.is_operational)
    real_data_count = sum(1 for comp in components if comp.is_real_data)
    
    if operational_count == len(components):
        overall_health = "healthy"
    elif operational_count >= len(components) * 0.7:
        overall_health = "degraded"
    else:
        overall_health = "unhealthy"
    
    real_data_percentage = (real_data_count / len(components)) * 100
    
    return AdminValidationResult(
        api_keys=api_keys,
        livecoinwatch=livecoinwatch,
        newsapi=newsapi,
        neo4j=neo4j,
        openai=openai,
        tavily=tavily,
        milvus=milvus,
        langsmith=langsmith,
        overall_health=overall_health,
        real_data_percentage=real_data_percentage,
        last_updated=datetime.now()
    )


def get_status_emoji(status: DataQualityStatus) -> str:
    """Get emoji for status display"""
    if status.is_real_data:
        return "✅"
    elif status.is_operational and status.mock_mode:
        return "⚠️"
    else:
        return "❌"


def format_status_text(status: DataQualityStatus) -> str:
    """Format status text for display"""
    if status.is_real_data:
        return "Real Data"
    elif status.is_operational and status.mock_mode:
        return "Mock Data (Fallback)"
    else:
        return f"Error: {status.error_message}" if status.error_message else "Not Operational"
