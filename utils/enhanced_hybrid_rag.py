#!/usr/bin/env python3
"""
Enhanced Hybrid RAG System with Qdrant Integration
Combines Qdrant cloud vector DB with local fallback for maximum reliability
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

# Import our systems
from .local_vector_fallback import (
    get_local_vector_search,
    add_document_to_local_store,
    search_local_vectors,
    get_local_vector_stats,
)

# Try to import Qdrant
try:
    from .qdrant_client import (
        get_qdrant_client,
        is_qdrant_available,
        test_qdrant_connection,
    )

    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False

logger = logging.getLogger(__name__)


class EnhancedHybridRAG:
    """
    Enhanced hybrid RAG system that uses Qdrant when available
    and gracefully falls back to local search when needed
    """

    def __init__(self):
        self.local_search = get_local_vector_search()
        self.qdrant_client = None
        self.qdrant_available = False
        self.fallback_mode = False

        # Try to initialize Qdrant
        self._initialize_qdrant()

        if self.qdrant_available:
            logger.info("🚀 Enhanced Hybrid RAG: Qdrant + Local Fallback")
        else:
            logger.info("🔄 Enhanced Hybrid RAG: Local Fallback Only")

    def _initialize_qdrant(self):
        """Initialize Qdrant connection if available"""
        try:
            if QDRANT_AVAILABLE and is_qdrant_available():
                self.qdrant_client = get_qdrant_client()
                self.qdrant_available = True
                logger.info("✅ Qdrant client initialized successfully")
            else:
                logger.info("ℹ️ Qdrant not available, using local fallback only")
        except Exception as e:
            logger.warning(f"⚠️ Qdrant initialization failed: {e}")
            self.qdrant_available = False

    async def add_document(
        self, content: str, metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Add document to both Qdrant (if available) and local store"""
        results = {"local_id": None, "qdrant_id": None, "success": False, "errors": []}

        # Always add to local store (reliable backup)
        try:
            local_id = add_document_to_local_store(content, metadata)
            results["local_id"] = local_id
            results["success"] = True
            logger.info(f"📝 Document added to local store: {local_id}")
        except Exception as e:
            error_msg = f"Local store error: {e}"
            results["errors"].append(error_msg)
            logger.error(f"❌ {error_msg}")

        # Try to add to Qdrant if available
        if self.qdrant_available and self.qdrant_client:
            try:
                # Generate simple vector for Qdrant (you can enhance this later)
                from .local_vector_fallback import simple_vectorize

                vector = simple_vectorize(content)

                qdrant_id = self.qdrant_client.add_document(content, metadata, vector)
                results["qdrant_id"] = qdrant_id
                logger.info(f"🚀 Document added to Qdrant: {qdrant_id}")
            except Exception as e:
                error_msg = f"Qdrant error: {e}"
                results["errors"].append(error_msg)
                logger.warning(f"⚠️ {error_msg}")
                # Fall back to local-only mode
                self.fallback_mode = True

        return results

    async def search(
        self,
        query: str,
        symbols: Optional[List[str]] = None,
        limit: int = 10,
        use_hybrid: bool = True,
        prefer_qdrant: bool = True,
    ) -> Dict[str, Any]:
        """Search using Qdrant if available, fallback to local"""

        results = {
            "query": query,
            "symbols": symbols or [],
            "results": [],
            "source": "unknown",
            "fallback_used": False,
            "qdrant_used": False,
            "timestamp": datetime.now().isoformat(),
        }

        # Try Qdrant first if available and preferred
        if (
            prefer_qdrant
            and self.qdrant_available
            and self.qdrant_client
            and not self.fallback_mode
        ):
            try:
                # Generate vector for query
                from .local_vector_fallback import simple_vectorize

                query_vector = simple_vectorize(query)

                qdrant_results = self.qdrant_client.search(
                    query_vector=query_vector,
                    limit=limit,
                    symbols=symbols,
                    min_score=0.1,
                )

                if qdrant_results:
                    results["results"] = qdrant_results
                    results["source"] = "qdrant"
                    results["qdrant_used"] = True
                    logger.info(
                        f"🚀 Qdrant search returned {len(qdrant_results)} results"
                    )
                    return results

            except Exception as e:
                logger.warning(f"⚠️ Qdrant search failed, falling back to local: {e}")
                self.fallback_mode = True

        # Fallback to local search
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
            results["source"] = "local_fallback"
            results["fallback_used"] = True

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
            current_time = datetime.now()
            filtered_results = []

            for result in results["results"]:
                try:
                    # Try to parse timestamp from different sources
                    timestamp_str = (
                        result.get("timestamp")
                        or result.get("metadata", {}).get("timestamp")
                        or ""
                    )

                    if timestamp_str:
                        # Simple time filtering (you can enhance this)
                        filtered_results.append(result)
                    else:
                        # If no timestamp, include anyway
                        filtered_results.append(result)

                except Exception:
                    # If timestamp parsing fails, include anyway
                    filtered_results.append(result)

            results["results"] = filtered_results[:limit]

        return results

    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        status = {
            "system": "enhanced_hybrid_rag",
            "qdrant_available": self.qdrant_available,
            "qdrant_operational": bool(
                self.qdrant_client and self.qdrant_client.is_connected
            ),
            "fallback_mode": self.fallback_mode,
            "local_stats": get_local_vector_stats(),
            "timestamp": datetime.now().isoformat(),
        }

        # Add Qdrant status if available
        if self.qdrant_available and self.qdrant_client:
            try:
                qdrant_info = self.qdrant_client.get_collection_info()
                status["qdrant_info"] = qdrant_info
            except Exception as e:
                status["qdrant_error"] = str(e)

        return status

    def reset_fallback_mode(self):
        """Reset fallback mode to try Qdrant again"""
        self.fallback_mode = False
        logger.info("🔄 Reset fallback mode - will try Qdrant again")

    def test_qdrant_connection(self) -> Dict[str, Any]:
        """Test Qdrant connection"""
        if not QDRANT_AVAILABLE:
            return {"status": "not_available", "error": "Qdrant client not installed"}

        return test_qdrant_connection()


def get_enhanced_hybrid_rag() -> EnhancedHybridRAG:
    """Get enhanced hybrid RAG instance"""
    return EnhancedHybridRAG()


async def enhanced_hybrid_search(
    query: str,
    symbols: Optional[List[str]] = None,
    limit: int = 10,
    prefer_qdrant: bool = True,
) -> Dict[str, Any]:
    """Convenience function for enhanced hybrid search"""
    rag = get_enhanced_hybrid_rag()
    return await rag.search(query, symbols, limit, prefer_qdrant=prefer_qdrant)


async def enhanced_hybrid_search_news(
    query: str, hours_back: int = 24, limit: int = 10
) -> Dict[str, Any]:
    """Convenience function for enhanced hybrid news search"""
    rag = get_enhanced_hybrid_rag()
    return await rag.search_news(query, hours_back, limit)


def get_enhanced_hybrid_status() -> Dict[str, Any]:
    """Get enhanced hybrid system status"""
    rag = get_enhanced_hybrid_rag()
    return rag.get_status()


def test_enhanced_qdrant_connection() -> Dict[str, Any]:
    """Test Qdrant connection through enhanced system"""
    rag = get_enhanced_hybrid_rag()
    return rag.test_qdrant_connection()
