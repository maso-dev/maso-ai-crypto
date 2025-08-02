#!/usr/bin/env python3
"""
Enhanced Vector Database Integration with LangSmith Tracing
Provides intelligent knowledge retrieval with ReAct agent patterns.
"""

import os
import asyncio
import httpx
from typing import List, Dict, Tuple, Optional, Any
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass
from enum import Enum

# LangSmith imports
from langsmith import Client
from langchain_core.tracers import LangChainTracer
from langchain_core.runnables import RunnableConfig

# Local imports
from .milvus import MILVUS_URI, MILVUS_TOKEN, MILVUS_COLLECTION_NAME

# LangSmith configuration
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "true")
LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT", "masonic-brain")
LANGCHAIN_ORGANIZATION = os.getenv("LANGCHAIN_ORGANIZATION", "703f12b7-8da7-455d-9870-c0dd95d12d7d")

class QueryType(Enum):
    """Types of queries supported by the enhanced vector database."""
    SEMANTIC_SEARCH = "semantic_search"
    KEYWORD_SEARCH = "keyword_search"
    HYBRID_SEARCH = "hybrid_search"
    TEMPORAL_SEARCH = "temporal_search"
    SENTIMENT_SEARCH = "sentiment_search"
    REACT_AGENT = "react_agent"

@dataclass
class VectorQuery:
    """Structured query for vector database operations."""
    query_text: str
    query_type: QueryType
    symbols: Optional[List[str]] = None
    time_range_hours: Optional[int] = None
    sentiment_filter: Optional[str] = None
    limit: int = 20
    similarity_threshold: float = 0.7
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class VectorResult:
    """Structured result from vector database operations."""
    content: str
    metadata: Dict[str, Any]
    similarity_score: float
    source_url: str
    published_at: datetime
    crypto_topic: str
    title: str
    sentiment_score: Optional[float] = None
    relevance_score: Optional[float] = None

class EnhancedVectorDB:
    """
    Enhanced vector database with LangSmith tracing and ReAct agent patterns.
    """
    
    def __init__(self):
        self.milvus_uri = MILVUS_URI
        self.milvus_token = MILVUS_TOKEN
        self.collection_name = MILVUS_COLLECTION_NAME
        
        # LangSmith setup
        self.langsmith_client = None
        self.tracer = None
        if LANGSMITH_API_KEY:
            self.langsmith_client = Client(api_key=LANGSMITH_API_KEY)
            self.tracer = LangChainTracer(
                project_name=LANGCHAIN_PROJECT,
                tags=["vector_db", "enhanced", "masonic"]
            )
    
    async def intelligent_search(
        self, 
        query: VectorQuery,
        config: Optional[RunnableConfig] = None
    ) -> List[VectorResult]:
        """
        Perform intelligent search using ReAct agent patterns with LangSmith tracing.
        """
        if config is None:
            config = {}
        
        # Add LangSmith metadata
        if self.tracer:
            config["tags"] = config.get("tags", []) + ["intelligent_search", query.query_type.value]
            config["metadata"] = {
                **config.get("metadata", {}),
                "query_type": query.query_type.value,
                "symbols": query.symbols,
                "time_range": query.time_range_hours,
                "sentiment_filter": query.sentiment_filter
            }
        
        try:
            if query.query_type == QueryType.REACT_AGENT:
                return await self._react_agent_search(query, config)
            elif query.query_type == QueryType.HYBRID_SEARCH:
                return await self._hybrid_search(query, config)
            elif query.query_type == QueryType.TEMPORAL_SEARCH:
                return await self._temporal_search(query, config)
            elif query.query_type == QueryType.SENTIMENT_SEARCH:
                return await self._sentiment_search(query, config)
            else:
                return await self._semantic_search(query, config)
                
        except Exception as e:
            if self.tracer:
                print(f"Vector DB error: {e}")
            raise
    
    async def _react_agent_search(
        self, 
        query: VectorQuery, 
        config: RunnableConfig
    ) -> List[VectorResult]:
        """
        ReAct agent-based search that reasons about the query and performs multiple searches.
        """
        # Step 1: Analyze the query to determine search strategy
        analysis_prompt = f"""
        Analyze this crypto query and determine the best search strategy:
        Query: {query.query_text}
        Symbols: {query.symbols}
        Time range: {query.time_range_hours} hours
        
        Determine:
        1. What type of information is being sought?
        2. Which symbols are most relevant?
        3. What time range is appropriate?
        4. What sentiment or market context is important?
        
        Return a JSON with search strategy.
        """
        
        # For now, implement a simplified ReAct pattern
        # In full implementation, this would use LangChain's create_react_agent
        
        # Step 2: Perform initial semantic search
        initial_results = await self._semantic_search(query, config)
        
        # Step 3: Refine search based on initial results
        if initial_results:
            # Extract key topics from initial results
            key_topics = self._extract_key_topics(initial_results)
            
            # Perform refined search
            refined_query = VectorQuery(
                query_text=f"{query.query_text} {' '.join(key_topics)}",
                query_type=QueryType.SEMANTIC_SEARCH,
                symbols=query.symbols,
                time_range_hours=query.time_range_hours,
                limit=query.limit
            )
            
            refined_results = await self._semantic_search(refined_query, config)
            
            # Combine and rank results
            combined_results = self._combine_and_rank_results(initial_results, refined_results)
            return combined_results[:query.limit]
        
        return initial_results
    
    async def _semantic_search(
        self, 
        query: VectorQuery, 
        config: RunnableConfig
    ) -> List[VectorResult]:
        """
        Perform semantic search using vector embeddings.
        """
        # Get embeddings for query
        query_embedding = await get_embeddings([query.query_text])
        
        # Build search payload
        search_payload = {
            "collectionName": self.collection_name,
            "vector": query_embedding[0],
            "limit": query.limit,
            "outputFields": [
                "chunk_text", "crypto_topic", "title", "source_url", 
                "published_at", "sentiment_score", "relevance_score"
            ],
            "metricType": "COSINE",
            "params": {"nprobe": 10}
        }
        
        # Add filters if specified
        if query.symbols:
            filter_expr = " or ".join([f"crypto_topic == '{symbol}'" for symbol in query.symbols])
            search_payload["filter"] = filter_expr
        
        # Perform search
        headers = {"Content-Type": "application/json"}
        if self.milvus_token:
            headers["Authorization"] = f"Bearer {self.milvus_token}"
        
        url = f"{self.milvus_uri}/v1/vector/search"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=search_payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json().get("data", [])
                return [self._parse_vector_result(item) for item in data]
            else:
                print(f"Semantic search error: {response.status_code} {response.text}")
                return []
    
    async def _hybrid_search(
        self, 
        query: VectorQuery, 
        config: RunnableConfig
    ) -> List[VectorResult]:
        """
        Perform hybrid search combining semantic and keyword matching.
        """
        # Perform both semantic and keyword searches
        semantic_results = await self._semantic_search(query, config)
        
        # For keyword search, we'd implement BM25 or similar
        # For now, return semantic results
        return semantic_results
    
    async def _temporal_search(
        self, 
        query: VectorQuery, 
        config: RunnableConfig
    ) -> List[VectorResult]:
        """
        Perform temporal search with time-based filtering.
        """
        if not query.time_range_hours:
            return await self._semantic_search(query, config)
        
        # Add temporal filter
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=query.time_range_hours)
        metadata = query.metadata or {}
        metadata["temporal_filter"] = cutoff_time.isoformat()
        
        temporal_query = VectorQuery(
            query_text=query.query_text,
            query_type=QueryType.SEMANTIC_SEARCH,
            symbols=query.symbols,
            limit=query.limit,
            metadata=metadata
        )
        
        return await self._semantic_search(temporal_query, config)
    
    async def _sentiment_search(
        self, 
        query: VectorQuery, 
        config: RunnableConfig
    ) -> List[VectorResult]:
        """
        Perform sentiment-aware search.
        """
        # Add sentiment filter to search
        sentiment_query = VectorQuery(
            query_text=query.query_text,
            query_type=QueryType.SEMANTIC_SEARCH,
            symbols=query.symbols,
            limit=query.limit,
            sentiment_filter=query.sentiment_filter
        )
        
        return await self._semantic_search(sentiment_query, config)
    
    def _parse_vector_result(self, item: Dict) -> VectorResult:
        """Parse raw vector result into structured format."""
        return VectorResult(
            content=item.get("chunk_text", ""),
            metadata=item.get("metadata", {}),
            similarity_score=item.get("score", 0.0),
            source_url=item.get("source_url", ""),
            published_at=datetime.fromisoformat(item.get("published_at", datetime.now().isoformat())),
            crypto_topic=item.get("crypto_topic", ""),
            title=item.get("title", ""),
            sentiment_score=item.get("sentiment_score"),
            relevance_score=item.get("relevance_score")
        )
    
    def _extract_key_topics(self, results: List[VectorResult]) -> List[str]:
        """Extract key topics from search results for refinement."""
        topics = []
        for result in results[:5]:  # Use top 5 results
            # Simple keyword extraction - in production, use NLP
            words = result.content.split()[:20]  # First 20 words
            topics.extend([word.lower() for word in words if len(word) > 3])
        
        # Return most common topics
        from collections import Counter
        return [topic for topic, _ in Counter(topics).most_common(5)]
    
    def _combine_and_rank_results(
        self, 
        results1: List[VectorResult], 
        results2: List[VectorResult]
    ) -> List[VectorResult]:
        """Combine and rank results from multiple searches."""
        # Create a map of unique results by source_url
        unique_results = {}
        
        for result in results1 + results2:
            if result.source_url not in unique_results:
                unique_results[result.source_url] = result
            else:
                # If duplicate, keep the one with higher similarity score
                if result.similarity_score > unique_results[result.source_url].similarity_score:
                    unique_results[result.source_url] = result
        
        # Sort by similarity score
        return sorted(
            unique_results.values(), 
            key=lambda x: x.similarity_score, 
            reverse=True
        )
    
    async def insert_enhanced_news(
        self, 
        news_items: List[Dict], 
        config: Optional[RunnableConfig] = None
    ) -> Tuple[int, int, List[str]]:
        """
        Insert enhanced news items with LangSmith tracing.
        """
        if config is None:
            config = {}
        
        # Add LangSmith metadata
        if self.tracer:
            config["tags"] = config.get("tags", []) + ["vector_insert", "enhanced_news"]
            config["metadata"] = {
                **config.get("metadata", {}),
                "news_count": len(news_items),
                "collection": self.collection_name
            }
        
        try:
            # Process news items for insertion
            processed_items = []
            for item in news_items:
                # Get embeddings
                embedding = await get_embeddings([item.get("content", "")])
                
                processed_item = {
                    "chunk_text": item.get("content", ""),
                    "crypto_topic": item.get("crypto_topic", ""),
                    "source_url": item.get("source_url", ""),
                    "published_at": item.get("published_at", datetime.now().isoformat()),
                    "title": item.get("title", ""),
                    "vector": embedding[0],
                    "sentiment_score": item.get("sentiment_score"),
                    "relevance_score": item.get("relevance_score"),
                    "metadata": item.get("metadata", {})
                }
                processed_items.append(processed_item)
            
            # Insert into Milvus
            from .milvus import insert_news_chunks
            return await insert_news_chunks(processed_items)
            
        except Exception as e:
            if self.tracer:
                self.tracer.log_error(
                    error=e,
                    metadata={"news_count": len(news_items)}
                )
            raise

# Global instance
enhanced_vector_db = EnhancedVectorDB()

# Convenience functions
async def intelligent_search(
    query_text: str,
    query_type: QueryType = QueryType.SEMANTIC_SEARCH,
    symbols: Optional[List[str]] = None,
    time_range_hours: Optional[int] = None,
    limit: int = 20
) -> List[VectorResult]:
    """Convenience function for intelligent search."""
    query = VectorQuery(
        query_text=query_text,
        query_type=query_type,
        symbols=symbols,
        time_range_hours=time_range_hours,
        limit=limit
    )
    return await enhanced_vector_db.intelligent_search(query)

async def insert_enhanced_news_batch(
    news_items: List[Dict],
    config: Optional[RunnableConfig] = None
) -> Tuple[int, int, List[str]]:
    """Convenience function for batch news insertion."""
    return await enhanced_vector_db.insert_enhanced_news(news_items, config) 
