#!/usr/bin/env python3
"""
Enhanced Hybrid RAG Router
Provides endpoints for the enhanced hybrid RAG system with Qdrant integration
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
import logging

from utils.enhanced_hybrid_rag import (
    get_enhanced_hybrid_rag,
    enhanced_hybrid_search,
    enhanced_hybrid_search_news,
    get_enhanced_hybrid_status,
    test_enhanced_qdrant_connection,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/enhanced-hybrid", tags=["enhanced-hybrid-rag"])


@router.get("/status")
async def get_status() -> Dict[str, Any]:
    """Get enhanced hybrid RAG system status"""
    try:
        return get_enhanced_hybrid_status()
    except Exception as e:
        logger.error(f"Failed to get enhanced hybrid status: {e}")
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")


@router.get("/search")
async def search_documents(
    query: str = Query(..., description="Search query"),
    symbols: Optional[List[str]] = Query(
        None, description="Filter by cryptocurrency symbols"
    ),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of results"),
    prefer_qdrant: bool = Query(True, description="Prefer Qdrant over local fallback"),
) -> Dict[str, Any]:
    """Search documents using enhanced hybrid RAG system"""
    try:
        result = await enhanced_hybrid_search(
            query=query, symbols=symbols, limit=limit, prefer_qdrant=prefer_qdrant
        )
        return result
    except Exception as e:
        logger.error(f"Enhanced hybrid search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/search-news")
async def search_news(
    query: str = Query(..., description="News search query"),
    hours_back: int = Query(24, ge=1, le=168, description="Hours to look back"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of results"),
) -> Dict[str, Any]:
    """Search news articles using enhanced hybrid RAG system"""
    try:
        result = await enhanced_hybrid_search_news(
            query=query, hours_back=hours_back, limit=limit
        )
        return result
    except Exception as e:
        logger.error(f"Enhanced hybrid news search failed: {e}")
        raise HTTPException(status_code=500, detail=f"News search failed: {str(e)}")


@router.post("/add-document")
async def add_document(
    content: str = Query(..., description="Document content"),
    symbols: List[str] = Query(..., description="Cryptocurrency symbols"),
    category: str = Query("crypto_news", description="Document category"),
    sentiment: str = Query("neutral", description="Document sentiment"),
) -> Dict[str, Any]:
    """Add document to enhanced hybrid RAG system"""
    try:
        metadata = {
            "symbols": symbols,
            "category": category,
            "sentiment": sentiment,
            "timestamp": "2025-08-09T22:00:00.000000",  # You can enhance this
        }

        rag = get_enhanced_hybrid_rag()
        result = await rag.add_document(content, metadata)
        return result
    except Exception as e:
        logger.error(f"Failed to add document: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to add document: {str(e)}")


@router.get("/test-qdrant")
async def test_qdrant_connection() -> Dict[str, Any]:
    """Test Qdrant connection"""
    try:
        return test_enhanced_qdrant_connection()
    except Exception as e:
        logger.error(f"Qdrant connection test failed: {e}")
        raise HTTPException(status_code=500, detail=f"Qdrant test failed: {str(e)}")


@router.post("/reset-fallback")
async def reset_fallback_mode() -> Dict[str, Any]:
    """Reset fallback mode to try Qdrant again"""
    try:
        rag = get_enhanced_hybrid_rag()
        rag.reset_fallback_mode()
        return {
            "message": "Fallback mode reset successfully",
            "status": "reset",
            "timestamp": "2025-08-09T22:00:00.000000",
        }
    except Exception as e:
        logger.error(f"Failed to reset fallback mode: {e}")
        raise HTTPException(status_code=500, detail=f"Reset failed: {str(e)}")


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check for enhanced hybrid RAG system"""
    try:
        status = get_enhanced_hybrid_status()
        return {
            "status": (
                "healthy"
                if status.get("qdrant_operational")
                or status.get("local_stats", {}).get("total_documents", 0) > 0
                else "degraded"
            ),
            "qdrant_available": status.get("qdrant_available", False),
            "local_documents": status.get("local_stats", {}).get("total_documents", 0),
            "fallback_mode": status.get("fallback_mode", False),
            "timestamp": status.get("timestamp", "unknown"),
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "error": str(e), "timestamp": "unknown"}
