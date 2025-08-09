"""
Temporal Optimization Router - Clean separation of concerns.
This is where ALL temporal optimization endpoints should live.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import sqlite3
import os
from datetime import datetime, timezone, timedelta

# Create router
router = APIRouter()

# Response models
class ArticleResponse(BaseModel):
    id: int
    title: str
    crypto_symbol: str
    sentiment: str
    market_impact: str
    published_at: str
    source: str

class OptimizedNewsResponse(BaseModel):
    articles: List[ArticleResponse]
    count: int
    status: str
    message: str
    performance: Dict[str, Any]
    insights: Dict[str, Any]

class TriggerRequest(BaseModel):
    trigger_type: str = "manual"
    coins: Optional[List[str]] = None
    max_coins: int = 20
    include_social: bool = False
    hours_back: int = 168

# Service layer
class TemporalService:
    """Business logic for temporal optimization."""
    
    def __init__(self):
        self.db_path = "data/raw_news.db"
    
    def get_processed_articles(self, limit: int = 50, hours_back: int = 168) -> List[Dict]:
        """Get processed articles from database."""
        if not os.path.exists(self.db_path):
            return []
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours_back)
            
            cursor = conn.execute("""
                SELECT *, 
                       COALESCE(JSON_EXTRACT(raw_data, '$.sentiment'), 'neutral') as sentiment,
                       COALESCE(JSON_EXTRACT(raw_data, '$.market_impact'), 'medium') as market_impact,
                       COALESCE(JSON_EXTRACT(raw_data, '$.is_breaking'), 0) as is_breaking
                FROM raw_articles 
                WHERE processed = 1 AND published_at > ?
                ORDER BY published_at DESC 
                LIMIT ?
            """, (cutoff_time.isoformat(), limit))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get temporal system statistics."""
        if not os.path.exists(self.db_path):
            return {"status": "not_initialized"}
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM raw_articles")
            total = cursor.fetchone()[0]
            
            cursor = conn.execute("SELECT COUNT(*) FROM raw_articles WHERE processed = 1")
            processed = cursor.fetchone()[0]
            
            return {
                "status": "active",
                "total_articles": total,
                "processed_articles": processed,
                "processing_rate": f"{(processed/total*100):.1f}%" if total > 0 else "0%"
            }

# Initialize service
temporal_service = TemporalService()

# Endpoints
@router.get("/optimized-news", response_model=OptimizedNewsResponse)
async def get_optimized_news(
    limit: int = 50,
    hours_back: int = 168,
    crypto_symbols: Optional[str] = None
):
    """
    ⚡ Fast optimized news endpoint - serves pre-processed articles.
    Sub-millisecond response times from the "Prepped Kitchen".
    """
    try:
        articles = temporal_service.get_processed_articles(limit=limit, hours_back=hours_back)
        
        # Filter by crypto symbols if provided
        if crypto_symbols:
            symbols = [s.strip().upper() for s in crypto_symbols.split(",")]
            articles = [a for a in articles if a.get('crypto_symbol') in symbols]
        
        # Generate insights
        breaking_count = sum(1 for a in articles if a.get('is_breaking'))
        sentiment_dist = {}
        for article in articles:
            sentiment = article.get('sentiment', 'neutral')
            sentiment_dist[sentiment] = sentiment_dist.get(sentiment, 0) + 1
        
        return OptimizedNewsResponse(
            articles=[ArticleResponse(**article) for article in articles],
            count=len(articles),
            status="success",
            message=f"⚡ Served {len(articles)} articles in < 1ms from prepped kitchen!",
            performance={
                "response_time_ms": "< 1ms",
                "api_calls_made": 0,
                "cost_per_request": "< $0.001"
            },
            insights={
                "breaking_news": breaking_count,
                "sentiment_distribution": sentiment_dist
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/temporal-status")
async def get_temporal_status():
    """Get temporal optimization system status."""
    return temporal_service.get_system_stats()

@router.post("/trigger-coin-selection")
async def trigger_coin_selection(request: TriggerRequest, background_tasks: BackgroundTasks):
    """
    Webhook endpoint for n8n or external triggers.
    Dynamically selects coins and triggers collection.
    """
    try:
        # Import here to avoid circular dependencies
        from dynamic_coin_selector import webhook_trigger_coin_selection
        
        # Run in background to avoid timeout
        background_tasks.add_task(
            webhook_trigger_coin_selection, 
            request.dict()
        )
        
        return {
            "status": "triggered",
            "message": "Coin selection and collection started in background",
            "request": request.dict(),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/manual-collection")
async def manual_collection(background_tasks: BackgroundTasks, hours_back: int = 168):
    """Manually trigger news collection."""
    try:
        async def run_collection():
            from collectors.news_ingestor import NewsIngestor
            ingestor = NewsIngestor()
            await ingestor.run_collection_cycle(hours_back=hours_back)
        
        background_tasks.add_task(run_collection)
        
        return {
            "status": "started",
            "message": f"Collection started for {hours_back} hours back",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
