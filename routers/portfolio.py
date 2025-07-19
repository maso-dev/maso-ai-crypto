from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from utils.milvus import query_news_for_symbols
from utils.openai_utils import get_market_summary

router = APIRouter()

class MarketSummaryRequest(BaseModel):
    symbols: List[str] = Field(..., description="Portfolio coin symbols, e.g. ['BTC', 'ETH', 'BITO']")
    limit: int = Field(10, description="Number of news items to return")

class NewsItem(BaseModel):
    title: str
    chunk_text: str
    crypto_topic: str
    source_url: str
    published_at: int

class MarketSummaryResponse(BaseModel):
    summary: str
    recommended_actions: str
    news: List[NewsItem]

@router.post("/portfolio/market_summary", response_model=MarketSummaryResponse)
async def portfolio_market_summary(req: MarketSummaryRequest = Body(...)) -> MarketSummaryResponse:
    try:
        news = await query_news_for_symbols(req.symbols, limit=req.limit)
        news_items = [
            NewsItem(
                title=item.get("title", ""),
                chunk_text=item.get("chunk_text", ""),
                crypto_topic=item.get("crypto_topic", ""),
                source_url=item.get("source_url", ""),
                published_at=item.get("published_at", 0)
            )
            for item in news
        ]
        summary, actions = await get_market_summary(news, req.symbols)
        return MarketSummaryResponse(
            summary=summary,
            recommended_actions=actions,
            news=news_items
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
