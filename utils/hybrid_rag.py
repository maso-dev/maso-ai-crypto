#!/usr/bin/env python3
"""
Hybrid RAG System - Vector + Graph Database Integration
Combines Milvus vector search with Neo4j graph relationships for comprehensive knowledge retrieval.
"""

import asyncio
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone
from dataclasses import dataclass
from enum import Enum

# Local imports
from .vector_rag import (
    EnhancedVectorRAG,
    VectorQuery,
    QueryType,
    intelligent_search,
    insert_enhanced_news_batch,
)
from .graph_rag import Neo4jGraphRAG, GraphQuery, search_graph, insert_news_to_graph
from .enrichment import enrich_news_articles


class HybridQueryType(Enum):
    """Types of hybrid queries."""

    VECTOR_ONLY = "vector_only"
    GRAPH_ONLY = "graph_only"
    HYBRID = "hybrid"
    REACT_HYBRID = "react_hybrid"
    ENTITY_NETWORK = "entity_network"
    SENTIMENT_ANALYSIS = "sentiment_analysis"


@dataclass
class HybridQuery:
    """Represents a hybrid RAG query."""

    query_text: str
    query_type: HybridQueryType
    symbols: Optional[List[str]] = None
    time_range_hours: Optional[int] = 24
    limit: int = 10
    vector_weight: float = 0.6
    graph_weight: float = 0.4


@dataclass
class HybridResult:
    """Represents a hybrid search result."""

    content: str
    title: str
    source_url: str
    crypto_topic: str
    published_at: datetime
    similarity_score: float
    sentiment_score: float
    relevance_score: float
    graph_relationships: List[Dict[str, Any]]
    entity_mentions: List[str]
    confidence_score: float


class HybridRAGSystem:
    """
    Hybrid RAG system combining vector and graph databases.
    Provides comprehensive knowledge retrieval with relationship analysis.
    """

    def __init__(self):
        self.vector_rag = EnhancedVectorRAG()
        self.graph_rag = Neo4jGraphRAG()
        print("🔗 Initialized Hybrid RAG System")
        print(f"   Vector RAG: {'✅' if self.vector_rag else '❌'}")
        print(
            f"   Graph RAG: {'✅' if self.graph_rag.connected else '❌ (using mock)'}"
        )

    async def hybrid_search(self, query: HybridQuery) -> List[HybridResult]:
        """Perform hybrid search combining vector and graph results."""
        print(f"🔍 Hybrid Search: {query.query_type.value}")

        try:
            if query.query_type == HybridQueryType.VECTOR_ONLY:
                return await self._vector_only_search(query)
            elif query.query_type == HybridQueryType.GRAPH_ONLY:
                return await self._graph_only_search(query)
            elif query.query_type == HybridQueryType.HYBRID:
                return await self._hybrid_search(query)
            elif query.query_type == HybridQueryType.REACT_HYBRID:
                return await self._react_hybrid_search(query)
            elif query.query_type == HybridQueryType.ENTITY_NETWORK:
                return await self._entity_network_search(query)
            elif query.query_type == HybridQueryType.SENTIMENT_ANALYSIS:
                return await self._sentiment_analysis_search(query)
            else:
                return await self._hybrid_search(query)

        except Exception as e:
            print(f"❌ Hybrid search failed: {e}")
            return []

    async def _vector_only_search(self, query: HybridQuery) -> List[HybridResult]:
        """Vector-only search using Milvus."""
        print("   📊 Vector search...")

        vector_results = await intelligent_search(
            query_text=query.query_text,
            query_type=QueryType.SEMANTIC_SEARCH,
            symbols=query.symbols,
            time_range_hours=query.time_range_hours,
            limit=query.limit,
        )

        # Convert to hybrid results
        hybrid_results = []
        for result in vector_results:
            hybrid_result = HybridResult(
                content=result.content,
                title=result.title,
                source_url=result.source_url,
                crypto_topic=result.crypto_topic,
                published_at=result.published_at,
                similarity_score=result.similarity_score,
                sentiment_score=result.sentiment_score,
                relevance_score=result.relevance_score,
                graph_relationships=[],
                entity_mentions=[],
                confidence_score=result.similarity_score,
            )
            hybrid_results.append(hybrid_result)

        return hybrid_results

    async def _graph_only_search(self, query: HybridQuery) -> List[HybridResult]:
        """Graph-only search using Neo4j."""
        print("   🕸️ Graph search...")

        # Determine graph query type based on symbols
        if query.symbols:
            graph_query = GraphQuery(
                query_type="related_articles",
                parameters={"symbols": query.symbols},
                limit=query.limit,
            )
        else:
            graph_query = GraphQuery(
                query_type="general",
                parameters={"search_term": query.query_text},
                limit=query.limit,
            )

        graph_results = await self.graph_rag.graph_search(graph_query)

        # Convert to hybrid results
        hybrid_results = []
        for result in graph_results:
            # Parse datetime
            published_at = datetime.now(timezone.utc)
            if result.get("published_at"):
                try:
                    published_at = datetime.fromisoformat(
                        result["published_at"].replace("Z", "+00:00")
                    )
                except:
                    pass

            hybrid_result = HybridResult(
                content=result.get("content", ""),
                title=result.get("title", ""),
                source_url=result.get("source_url", ""),
                crypto_topic=result.get("crypto_topic", ""),
                published_at=published_at,
                similarity_score=0.8,  # Default for graph results
                sentiment_score=result.get("sentiment_score", 0.0),
                relevance_score=0.8,  # Default for graph results
                graph_relationships=[],
                entity_mentions=result.get("entities", []),
                confidence_score=0.8,
            )
            hybrid_results.append(hybrid_result)

        return hybrid_results

    async def _hybrid_search(self, query: HybridQuery) -> List[HybridResult]:
        """Combined vector and graph search."""
        print("   🔗 Hybrid search...")

        # Run both searches in parallel
        vector_task = self._vector_only_search(query)
        graph_task = self._graph_only_search(query)

        vector_results, graph_results = await asyncio.gather(
            vector_task, graph_task, return_exceptions=True
        )

        # Handle exceptions
        if isinstance(vector_results, Exception):
            print(f"   ⚠️ Vector search failed: {vector_results}")
            vector_results = []
        if isinstance(graph_results, Exception):
            print(f"   ⚠️ Graph search failed: {graph_results}")
            graph_results = []

        # Combine and rank results
        combined_results = await self._combine_and_rank_results(
            vector_results, graph_results, query
        )

        return combined_results

    async def _react_hybrid_search(self, query: HybridQuery) -> List[HybridResult]:
        """ReAct agent with hybrid search capabilities."""
        print("   🤖 ReAct hybrid search...")

        # First, use ReAct agent to understand the query
        react_query = VectorQuery(
            query_text=query.query_text,
            query_type=QueryType.REACT_AGENT,
            symbols=query.symbols,
            time_range_hours=query.time_range_hours,
            limit=query.limit,
        )

        react_results = await self.vector_rag.search(react_query)

        # Then, use graph search to find relationships
        if query.symbols:
            graph_query = GraphQuery(
                query_type="entity_network",
                parameters={"entity_name": query.symbols[0], "depth": 2},
                limit=5,
            )
            graph_results = await self.graph_rag.graph_search(graph_query)
        else:
            graph_results = []

        # Combine results
        hybrid_results = []
        for result in react_results:
            hybrid_result = HybridResult(
                content=result.content,
                title=result.title,
                source_url=result.source_url,
                crypto_topic=result.crypto_topic,
                published_at=result.published_at,
                similarity_score=result.similarity_score,
                sentiment_score=result.sentiment_score,
                relevance_score=result.relevance_score,
                graph_relationships=graph_results,
                entity_mentions=[],
                confidence_score=result.similarity_score
                * 0.9,  # Slightly lower for hybrid
            )
            hybrid_results.append(hybrid_result)

        return hybrid_results

    async def _entity_network_search(self, query: HybridQuery) -> List[HybridResult]:
        """Search for entity relationships and networks."""
        print("   🕸️ Entity network search...")

        if not query.symbols:
            return []

        # Search for entity networks
        graph_query = GraphQuery(
            query_type="entity_network",
            parameters={"entity_name": query.symbols[0], "depth": 3},
            limit=query.limit,
        )

        graph_results = await self.graph_rag.graph_search(graph_query)

        # Convert to hybrid results
        hybrid_results = []
        for result in graph_results:
            hybrid_result = HybridResult(
                content=f"Entity: {result.get('name', 'Unknown')}",
                title=f"Entity Network - {result.get('name', 'Unknown')}",
                source_url="",
                crypto_topic="",
                published_at=datetime.now(timezone.utc),
                similarity_score=0.8,
                sentiment_score=0.0,
                relevance_score=0.8,
                graph_relationships=[result],
                entity_mentions=[result.get("name", "Unknown")],
                confidence_score=0.8,
            )
            hybrid_results.append(hybrid_result)

        return hybrid_results

    async def _sentiment_analysis_search(
        self, query: HybridQuery
    ) -> List[HybridResult]:
        """Search for sentiment patterns and analysis."""
        print("   😊 Sentiment analysis search...")

        if not query.symbols:
            return []

        # Search for sentiment patterns
        graph_query = GraphQuery(
            query_type="sentiment_analysis",
            parameters={
                "symbols": query.symbols,
                "time_range_hours": query.time_range_hours,
            },
            limit=query.limit,
        )

        graph_results = await self.graph_rag.graph_search(graph_query)

        # Convert to hybrid results
        hybrid_results = []
        for result in graph_results:
            hybrid_result = HybridResult(
                content=f"Sentiment analysis for {result.get('symbol', 'Unknown')}: {result.get('sentiment', 'neutral')}",
                title=f"Sentiment Analysis - {result.get('symbol', 'Unknown')}",
                source_url="",
                crypto_topic=result.get("symbol", ""),
                published_at=datetime.now(timezone.utc),
                similarity_score=0.8,
                sentiment_score=result.get("avg_sentiment", 0.0),
                relevance_score=0.8,
                graph_relationships=[result],
                entity_mentions=[result.get("symbol", "Unknown")],
                confidence_score=0.8,
            )
            hybrid_results.append(hybrid_result)

        return hybrid_results

    async def _combine_and_rank_results(
        self,
        vector_results: List[HybridResult],
        graph_results: List[HybridResult],
        query: HybridQuery,
    ) -> List[HybridResult]:
        """Combine and rank vector and graph results."""

        # Create a combined list
        combined = []

        # Add vector results with weight
        for result in vector_results:
            result.confidence_score *= query.vector_weight
            combined.append(("vector", result))

        # Add graph results with weight
        for result in graph_results:
            result.confidence_score *= query.graph_weight
            combined.append(("graph", result))

        # Remove duplicates based on source_url
        seen_urls = set()
        unique_results = []

        for source, result in combined:
            if result.source_url not in seen_urls:
                seen_urls.add(result.source_url)
                unique_results.append(result)
            else:
                # If duplicate, boost confidence
                for existing_result in unique_results:
                    if existing_result.source_url == result.source_url:
                        existing_result.confidence_score = max(
                            existing_result.confidence_score, result.confidence_score
                        )
                        break

        # Sort by confidence score
        unique_results.sort(key=lambda x: x.confidence_score, reverse=True)

        return unique_results[: query.limit]

    async def insert_hybrid_news(
        self,
        article_data: Dict[str, Any],
        entities: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        """Insert news article into both vector and graph databases."""
        print(f"📝 Inserting hybrid news: {article_data.get('title', 'Unknown')}")

        try:
            # Insert into vector database
            vector_id = await self.vector_rag.insert_enhanced_news(article_data)

            # Insert into graph database
            graph_id = await insert_news_to_graph(article_data, entities)

            print(f"   ✅ Vector ID: {vector_id}")
            print(f"   ✅ Graph ID: {graph_id}")

            return f"hybrid_{vector_id}_{graph_id}"

        except Exception as e:
            print(f"❌ Hybrid insert failed: {e}")
            return None

    async def get_hybrid_stats(self) -> Dict[str, Any]:
        """Get statistics from both vector and graph databases."""
        try:
            vector_stats = await self.vector_rag.get_stats()
            graph_stats = await self.graph_rag.get_graph_stats()

            return {
                "vector_rag": vector_stats,
                "graph_rag": graph_stats,
                "hybrid_system": {
                    "status": "operational",
                    "vector_connected": bool(vector_stats),
                    "graph_connected": graph_stats.get("connected", False),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
            }
        except Exception as e:
            return {
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }


# Global instance
hybrid_rag = HybridRAGSystem()


# Convenience functions
async def hybrid_search(
    query_text: str,
    query_type: HybridQueryType = HybridQueryType.HYBRID,
    symbols: Optional[List[str]] = None,
    time_range_hours: int = 24,
    limit: int = 10,
) -> List[HybridResult]:
    """Convenience function for hybrid search."""
    query = HybridQuery(
        query_text=query_text,
        query_type=query_type,
        symbols=symbols,
        time_range_hours=time_range_hours,
        limit=limit,
    )
    return await hybrid_rag.hybrid_search(query)


async def insert_hybrid_news_article(
    article_data: Dict[str, Any], entities: Optional[List[Dict[str, Any]]] = None
) -> str:
    """Convenience function for inserting hybrid news."""
    return await hybrid_rag.insert_hybrid_news(article_data, entities)


async def get_hybrid_statistics() -> Dict[str, Any]:
    """Convenience function for getting hybrid statistics."""
    return await hybrid_rag.get_hybrid_stats()
