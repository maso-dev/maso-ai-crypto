"""
Optimized LangChain Pipeline for Crypto News Processing

This module creates a LangChain pipeline that:
1. Enriches articles with temporal context
2. Creates summary-focused chunks
3. Prepares data for both vector and graph storage
4. Optimizes for query performance
"""

from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import JsonOutputParser
from typing import Dict, List, Any, Optional
from utils.enrichment import get_enrichment_chain
from utils.temporal_context import enhance_article_with_temporal_context
from utils.optimized_embedding import process_article_for_optimized_storage
import asyncio

class OptimizedNewsPipeline:
    """
    LangChain pipeline for optimized crypto news processing.
    """
    
    def __init__(self):
        self.enrichment_chain = get_enrichment_chain()
        
    async def process_single_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single article through the optimized pipeline.
        
        Steps:
        1. Enhance with temporal context
        2. Enrich with AI metadata
        3. Create summary-focused chunk
        4. Prepare for vector and graph storage
        """
        
        print(f"🔄 Processing article: {article.get('title', '')[:50]}...")
        
        # Step 1: Enhance with temporal context
        article = enhance_article_with_temporal_context(article)
        print(f"   ✅ Enhanced with temporal context")
        
        # Step 2: Enrich with AI metadata
        enrichment_input = {
            "title": article.get('title', ''),
            "content": article.get('content', ''),
            "source_name": article.get('source_name', ''),
            "published_at": article.get('published_at', '')
        }
        
        try:
            enrichment_result = await self.enrichment_chain.ainvoke(enrichment_input)
            print(f"   ✅ Enriched with AI metadata")
        except Exception as e:
            print(f"   ⚠️ Enrichment failed: {e}")
            # Fallback enrichment data
            enrichment_result = {
                "sentiment": 0.5,
                "trust": 0.5,
                "categories": ["Cryptocurrency"],
                "macro_category": "Finance",
                "summary": article.get('content', '')[:200] + "...",
                "urgency_score": 0.5,
                "market_impact": "medium",
                "time_relevance": "recent"
            }
        
        # Step 3: Process for optimized storage
        processed_data = await process_article_for_optimized_storage(article, enrichment_result)
        print(f"   ✅ Prepared for vector and graph storage")
        
        return processed_data
    
    async def process_articles_batch(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process a batch of articles through the optimized pipeline.
        """
        print(f"🚀 Processing {len(articles)} articles through optimized pipeline...")
        
        processed_articles = []
        
        for i, article in enumerate(articles):
            try:
                processed = await self.process_single_article(article)
                processed_articles.append(processed)
                print(f"   ✅ Article {i+1}/{len(articles)} processed successfully")
            except Exception as e:
                print(f"   ❌ Article {i+1}/{len(articles)} failed: {e}")
                continue
        
        print(f"🎉 Pipeline completed: {len(processed_articles)}/{len(articles)} articles processed")
        return processed_articles
    
    def get_vector_data_batch(self, processed_articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract vector data for batch insertion into Milvus.
        """
        vector_data = []
        for article in processed_articles:
            vector_data.append(article["vector_data"])
        return vector_data
    
    def get_graph_data_batch(self, processed_articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract graph data for batch insertion into Neo4j.
        """
        graph_data = []
        for article in processed_articles:
            graph_data.append(article["graph_data"])
        return graph_data
    
    def get_processing_summary(self, processed_articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a summary of the processing results.
        """
        if not processed_articles:
            return {"total_processed": 0}
        
        # Extract metadata for analysis
        metadata_list = [article["metadata"] for article in processed_articles]
        
        # Calculate statistics
        total_processed = len(processed_articles)
        breaking_news = sum(1 for m in metadata_list if m.get('is_breaking', False))
        recent_news = sum(1 for m in metadata_list if m.get('is_recent', False))
        
        # Sentiment analysis
        sentiments = [m.get('sentiment', 0.5) for m in metadata_list]
        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0.5
        
        # Market impact distribution
        market_impacts = {}
        for m in metadata_list:
            impact = m.get('market_impact', 'medium')
            market_impacts[impact] = market_impacts.get(impact, 0) + 1
        
        # Category distribution
        all_categories = []
        for m in metadata_list:
            all_categories.extend(m.get('categories', []))
        
        category_counts = {}
        for category in all_categories:
            category_counts[category] = category_counts.get(category, 0) + 1
        
        return {
            "total_processed": total_processed,
            "breaking_news": breaking_news,
            "recent_news": recent_news,
            "avg_sentiment": round(avg_sentiment, 3),
            "market_impact_distribution": market_impacts,
            "top_categories": sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:5],
            "processing_stats": {
                "summary_focused_chunks": total_processed,
                "vector_ready": total_processed,
                "graph_ready": total_processed
            }
        }

# Convenience function for easy pipeline usage
async def run_optimized_pipeline(articles: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Run the complete optimized pipeline on a list of articles.
    
    Returns:
        Dict containing:
        - processed_articles: List of processed articles
        - vector_data: Data ready for Milvus insertion
        - graph_data: Data ready for Neo4j insertion
        - summary: Processing statistics
    """
    
    pipeline = OptimizedNewsPipeline()
    
    # Process articles
    processed_articles = await pipeline.process_articles_batch(articles)
    
    # Extract data for different storage systems
    vector_data = pipeline.get_vector_data_batch(processed_articles)
    graph_data = pipeline.get_graph_data_batch(processed_articles)
    
    # Generate summary
    summary = pipeline.get_processing_summary(processed_articles)
    
    return {
        "processed_articles": processed_articles,
        "vector_data": vector_data,
        "graph_data": graph_data,
        "summary": summary
    } 
