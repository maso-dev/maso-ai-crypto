"""
Optimized Embedding Module for Crypto News RAG

This module focuses on summary-based chunking and rich metadata for:
- Better vector search performance
- Enhanced graph schema preparation
- Improved query relevance
"""

import os
from typing import Dict, List, Any, Optional
import openai
from sklearn.feature_extraction.text import TfidfVectorizer
from datetime import datetime

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

def create_summary_focused_chunk(article: Dict[str, Any], summary: str) -> Dict[str, Any]:
    """
    Create a summary-focused chunk with rich metadata for optimal vector search.
    
    Strategy:
    - Use AI-generated summary as primary content for embedding
    - Include key metadata as searchable fields
    - Structure for both vector and graph storage
    """
    
    # Create a rich, searchable text representation
    searchable_text = f"""
Title: {article.get('title', '')}
Summary: {summary}
Crypto Topic: {article.get('crypto_topic', '')}
Source: {article.get('source_name', '')}
Categories: {', '.join(article.get('categories', []))}
Market Impact: {article.get('market_impact', 'medium')}
Time Relevance: {article.get('time_relevance', 'recent')}
    """.strip()
    
    # Create metadata for vector indexing and graph schema
    metadata = {
        # Core article info
        "article_id": f"{article.get('crypto_topic', '')}_{article.get('published_at', '')}_{hash(article.get('title', ''))}",
        "title": article.get('title', ''),
        "crypto_topic": article.get('crypto_topic', ''),
        "source_name": article.get('source_name', ''),
        "source_url": article.get('source_url', ''),
        "published_at": article.get('published_at', ''),
        
        # Temporal context (for indexing)
        "hours_ago": article.get('hours_ago', 0),
        "is_breaking": article.get('is_breaking', False),
        "is_recent": article.get('is_recent', False),
        "time_category": article.get('time_category', 'historical'),
        "temporal_relevance_score": article.get('temporal_relevance_score', 0),
        
        # AI enrichment (for filtering and ranking)
        "sentiment": article.get('sentiment', 0.5),
        "trust": article.get('trust', 0.5),
        "urgency_score": article.get('urgency_score', 0.5),
        "market_impact": article.get('market_impact', 'medium'),
        "time_relevance": article.get('time_relevance', 'recent'),
        "macro_category": article.get('macro_category', ''),
        
        # Categories for graph relationships
        "categories": article.get('categories', []),
        
        # Summary for semantic search
        "summary": summary,
        
        # Original content for reference
        "original_content": article.get('content', '')[:500],  # Truncated for storage
        
        # Processing metadata
        "processed_at": datetime.utcnow().isoformat(),
        "chunk_type": "summary_focused"
    }
    
    return {
        "searchable_text": searchable_text,
        "metadata": metadata,
        "summary": summary
    }

async def embed_summary_focused_chunk(chunk_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create embeddings for summary-focused chunks with optimized text representation.
    """
    if not client:
        return chunk_data
    
    try:
        # Embed the searchable text (summary + metadata)
        resp = await client.embeddings.create(
            model="text-embedding-ada-002",
            input=chunk_data["searchable_text"]
        )
        
        chunk_data["dense_vector"] = resp.data[0].embedding
        
        # Create sparse vector from searchable text
        chunk_data["sparse_vector"] = compute_sparse_vectors(chunk_data["searchable_text"])
        
        return chunk_data
        
    except Exception as e:
        print(f"Error getting embedding: {e}")
        return chunk_data

def compute_sparse_vectors(text: str) -> Dict[str, float]:
    """Compute TF-IDF sparse vectors for the searchable text."""
    vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
    X = vectorizer.fit_transform([text])
    tfidf = X.toarray()[0]  # type: ignore
    return {str(i): float(tfidf[i]) for i in range(len(tfidf)) if tfidf[i] > 0}

async def process_article_for_optimized_storage(article: Dict[str, Any], enrichment_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process a single article for optimized vector and graph storage.
    
    This function:
    1. Creates summary-focused chunks
    2. Adds rich metadata for indexing
    3. Prepares data for both vector and graph storage
    """
    
    # Merge enrichment data with article
    article.update(enrichment_data)
    
    # Create summary-focused chunk
    chunk_data = create_summary_focused_chunk(article, enrichment_data.get('summary', ''))
    
    # Generate embeddings
    chunk_data = await embed_summary_focused_chunk(chunk_data)
    
    # Convert published_at to Unix timestamp for Milvus
    published_at = chunk_data["metadata"]["published_at"]
    if isinstance(published_at, str):
        try:
            dt = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
            published_timestamp = int(dt.timestamp())
        except (ValueError, TypeError):
            published_timestamp = int(datetime.utcnow().timestamp())
    else:
        published_timestamp = published_at
    
    # Prepare for vector storage
    vector_data = {
        "chunk_text": chunk_data["searchable_text"],
        "vector": chunk_data["dense_vector"],
        "sparse_vector": chunk_data["sparse_vector"],
        **chunk_data["metadata"]  # All metadata for indexing
    }
    
    # Override published_at with timestamp for Milvus compatibility
    vector_data["published_at"] = published_timestamp
    
    # Prepare for graph storage
    graph_data = {
        "node_id": chunk_data["metadata"]["article_id"],
        "node_type": "news_article",
        "properties": {
            "title": chunk_data["metadata"]["title"],
            "summary": chunk_data["summary"],
            "crypto_topic": chunk_data["metadata"]["crypto_topic"],
            "source_name": chunk_data["metadata"]["source_name"],
            "sentiment": chunk_data["metadata"]["sentiment"],
            "trust": chunk_data["metadata"]["trust"],
            "market_impact": chunk_data["metadata"]["market_impact"],
            "time_relevance": chunk_data["metadata"]["time_relevance"],
            "macro_category": chunk_data["metadata"]["macro_category"],
            "categories": chunk_data["metadata"]["categories"],
            "published_at": chunk_data["metadata"]["published_at"],
            "is_breaking": chunk_data["metadata"]["is_breaking"],
            "temporal_relevance_score": chunk_data["metadata"]["temporal_relevance_score"]
        },
        "relationships": {
            "mentions": chunk_data["metadata"]["crypto_topic"],
            "categorized_as": chunk_data["metadata"]["categories"],
            "published_by": chunk_data["metadata"]["source_name"],
            "has_impact": chunk_data["metadata"]["market_impact"],
            "time_period": chunk_data["metadata"]["time_relevance"]
        }
    }
    
    return {
        "vector_data": vector_data,
        "graph_data": graph_data,
        "metadata": chunk_data["metadata"]
    }

def create_search_optimized_query(query: str, filters: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Create an optimized query structure for vector search with metadata filtering.
    
    Args:
        query: User's search query
        filters: Optional filters for metadata fields
    
    Returns:
        Optimized query structure for vector search
    """
    
    # Enhance query with context for better semantic matching
    enhanced_query = f"""
Search Query: {query}
Context: Looking for relevant crypto news articles with recent market impact.
    """.strip()
    
    # Build filter expression for metadata
    filter_expr = ""
    if filters:
        filter_parts = []
        
        if filters.get('crypto_topic'):
            filter_parts.append(f"crypto_topic == '{filters['crypto_topic']}'")
        
        if filters.get('time_relevance'):
            filter_parts.append(f"time_relevance == '{filters['time_relevance']}'")
        
        if filters.get('market_impact'):
            filter_parts.append(f"market_impact == '{filters['market_impact']}'")
        
        if filters.get('is_breaking'):
            filter_parts.append(f"is_breaking == {filters['is_breaking']}")
        
        if filters.get('min_sentiment'):
            filter_parts.append(f"sentiment >= {filters['min_sentiment']}")
        
        if filter_parts:
            filter_expr = " and ".join(filter_parts)
    
    return {
        "query_text": enhanced_query,
        "filter_expr": filter_expr,
        "metadata_filters": filters or {},
        "search_fields": ["summary", "title", "categories", "macro_category"]
    } 
