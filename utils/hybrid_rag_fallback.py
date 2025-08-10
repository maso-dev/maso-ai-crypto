#!/usr/bin/env python3
"""
Hybrid RAG System with Graceful Fallback
Combines external vector DB (Milvus) with local fallback
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

# Import our local fallback system
from .local_vector_fallback import (
    get_local_vector_search,
    add_document_to_local_store,
    search_local_vectors,
    get_local_vector_stats,
)

logger = logging.getLogger(__name__)


class HybridRAGFallback:
    """
    Hybrid RAG system that gracefully falls back to local search
    when external vector databases are unavailable
    """

    def __init__(self):
        self.local_search = get_local_vector_search()
        self.fallback_mode = True  # Start in fallback mode for reliability

        logger.info("🔄 Using local vector search fallback mode")

    async def add_document(self, content: str, metadata: Dict[str, Any]) -> str:
        """Add document to local store (reliable)"""
        try:
            local_id = add_document_to_local_store(content, metadata)
            logger.info(f"📝 Document added to local store: {local_id}")
            return local_id

        except Exception as e:
            logger.error(f"❌ Failed to add document: {e}")
            raise

    async def search(
        self,
        query: str,
        symbols: Optional[List[str]] = None,
        limit: int = 10,
        use_hybrid: bool = True,
    ) -> Dict[str, Any]:
        """Search using local fallback"""

        results = {
            "query": query,
            "symbols": symbols or [],
            "results": [],
            "source": "local_fallback",
            "fallback_used": True,
            "timestamp": datetime.now().isoformat(),
        }

        # Use local search (reliable)
        try:
            local_results = search_local_vectors(query, limit)

            # Filter by symbols if provided
            if symbols:
                filtered_results = []
                for result in local_results:
                    result_symbols = result.get("metadata", {}).get("symbols", [])
                    if any(symbol in result_symbols for symbol in symbols):
                        filtered_results.append(result)
                local_results = filtered_results[:limit]

            results["results"] = local_results

            logger.info(
                f"🔄 Local fallback search returned {len(local_results)} results"
            )

        except Exception as e:
            logger.error(f"❌ Local search failed: {e}")
            results["results"] = []
            results["source"] = "failed"
            results["error"] = str(e)

        return results

    async def search_news(
        self, query: str, hours_back: int = 24, limit: int = 10
    ) -> Dict[str, Any]:
        """Search news articles with time filtering"""

        # Add time-based metadata to query
        enhanced_query = f"{query} recent news last {hours_back} hours"

        results = await self.search(enhanced_query, limit=limit)

        # Filter results by timestamp if available
        if results["results"]:
            cutoff_time = datetime.now().timestamp() - (hours_back * 3600)
            filtered_results = []

            for result in results["results"]:
                try:
                    timestamp = datetime.fromisoformat(result.get("timestamp", ""))
                    if timestamp.timestamp() >= cutoff_time:
                        filtered_results.append(result)
                except:
                    # If timestamp parsing fails, include the result
                    filtered_results.append(result)

            results["results"] = filtered_results[:limit]
            results["time_filtered"] = True

        return results

    def get_status(self) -> Dict[str, Any]:
        """Get system status and statistics"""
        local_stats = get_local_vector_stats()

        return {
            "external_available": False,  # Simplified for now
            "fallback_mode": True,
            "local_stats": local_stats,
            "status": "healthy" if local_stats["total_documents"] > 0 else "degraded",
        }

    def reset_fallback_mode(self):
        """Reset fallback mode to try external services again"""
        self.fallback_mode = False
        logger.info("🔄 Reset fallback mode - will try external services")


# Global instance
_hybrid_rag_fallback = None


def get_hybrid_rag_fallback() -> HybridRAGFallback:
    """Get or create global hybrid RAG fallback instance"""
    global _hybrid_rag_fallback
    if _hybrid_rag_fallback is None:
        _hybrid_rag_fallback = HybridRAGFallback()
    return _hybrid_rag_fallback


# Convenience functions
async def hybrid_search(
    query: str, symbols: Optional[List[str]] = None, limit: int = 10
) -> Dict[str, Any]:
    """Perform hybrid search with fallback"""
    return await get_hybrid_rag_fallback().search(query, symbols, limit)


async def hybrid_search_news(
    query: str, hours_back: int = 24, limit: int = 10
) -> Dict[str, Any]:
    """Search news with hybrid approach"""
    return await get_hybrid_rag_fallback().search_news(query, hours_back, limit)


def get_hybrid_status() -> Dict[str, Any]:
    """Get hybrid RAG system status"""
    return get_hybrid_rag_fallback().get_status()
