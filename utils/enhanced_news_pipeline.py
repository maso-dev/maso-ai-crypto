#!/usr/bin/env python3
"""
Enhanced News Processing Pipeline
Integrates NewsAPI fetching with AI enrichment and LangSmith tracing.
"""

import os
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, timezone
from utils.newsapi import fetch_news_articles
from utils.enrichment import enrich_news_articles
from utils.cost_tracker import track_newsapi_call, track_openai_call

# LangSmith configuration
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
if LANGSMITH_API_KEY:
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_PROJECT"] = "masonic-news-pipeline"
    os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
    os.environ["LANGCHAIN_ORGANIZATION"] = "703f12b7-8da7-455d-9870-c0dd95d12d7d"

class EnhancedNewsPipeline:
    """
    Enhanced news processing pipeline with AI enrichment and LangSmith integration.
    """
    
    def __init__(self):
        self.newsapi_key = os.getenv("NEWSAPI_KEY")
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.langsmith_key = LANGSMITH_API_KEY
        
    async def process_crypto_news(
        self, 
        symbols: Optional[List[str]] = None,
        hours_back: int = 24,
        enable_enrichment: bool = True,
        max_articles: int = 50
    ) -> Dict[str, Any]:
        """
        Process crypto news with optional AI enrichment.
        
        Args:
            symbols: List of crypto symbols to search for
            hours_back: How many hours back to search
            enable_enrichment: Whether to enable AI enrichment
            max_articles: Maximum number of articles to process
            
        Returns:
            Dictionary with processed news data and metadata
        """
        if symbols is None:
            symbols = ["Bitcoin", "Ethereum", "cryptocurrency", "blockchain"]
        
        print(f"🔍 Processing crypto news for: {', '.join(symbols)}")
        print(f"   Time range: {hours_back} hours back")
        print(f"   Enrichment: {'Enabled' if enable_enrichment else 'Disabled'}")
        print(f"   LangSmith: {'Enabled' if self.langsmith_key else 'Disabled'}")
        
        # Step 1: Fetch news articles
        try:
            print("\n📰 Fetching news articles...")
            articles = await fetch_news_articles(symbols, hours_back=hours_back)
            
            # Track NewsAPI usage
            await track_newsapi_call(
                endpoint="everything",
                metadata={
                    "symbols": symbols,
                    "hours_back": hours_back,
                    "articles_fetched": len(articles)
                }
            )
            
            print(f"   ✅ Fetched {len(articles)} articles")
            
        except Exception as e:
            print(f"   ❌ Failed to fetch news: {e}")
            return {
                "success": False,
                "error": f"News fetching failed: {str(e)}",
                "articles": [],
                "metadata": {}
            }
        
        # Step 2: Filter and limit articles
        if len(articles) > max_articles:
            articles = articles[:max_articles]
            print(f"   📊 Limited to {max_articles} articles")
        
        # Step 3: AI Enrichment (if enabled)
        if enable_enrichment and self.openai_key:
            try:
                print("\n🧠 Enriching articles with AI...")
                enriched_articles = await enrich_news_articles(articles)
                
                # Track OpenAI usage
                await track_openai_call(
                    model="gpt-4-turbo",
                    metadata={
                        "operation": "news_enrichment",
                        "articles_enriched": len(enriched_articles),
                        "symbols": symbols
                    }
                )
                
                print(f"   ✅ Enriched {len(enriched_articles)} articles")
                articles = enriched_articles
                
            except Exception as e:
                print(f"   ⚠️ Enrichment failed: {e}")
                print("   Continuing with unenriched articles...")
        
        # Step 4: Analyze and summarize
        metadata = self._analyze_articles(articles)
        
        return {
            "success": True,
            "articles": articles,
            "metadata": metadata,
            "processing_info": {
                "symbols_searched": symbols,
                "hours_back": hours_back,
                "enrichment_enabled": enable_enrichment,
                "langsmith_enabled": bool(self.langsmith_key),
                "processing_time": datetime.now(timezone.utc).isoformat()
            }
        }
    
    def _analyze_articles(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze articles and extract metadata."""
        if not articles:
            return {}
        
        # Basic statistics
        total_articles = len(articles)
        sources = list(set(art.get("source_name", "Unknown") for art in articles))
        
        # Enrichment statistics (if available)
        enrichment_stats = {}
        if any("enrichment" in art for art in articles):
            sentiments = [art["enrichment"]["sentiment"] for art in articles if "enrichment" in art]
            trusts = [art["enrichment"]["trust"] for art in articles if "enrichment" in art]
            categories = []
            for art in articles:
                if "enrichment" in art:
                    categories.extend(art["enrichment"]["categories"])
            
            enrichment_stats = {
                "avg_sentiment": sum(sentiments) / len(sentiments) if sentiments else 0,
                "avg_trust": sum(trusts) / len(trusts) if trusts else 0,
                "top_categories": self._get_top_categories(categories),
                "enriched_count": len([art for art in articles if "enrichment" in art])
            }
        
        # Temporal analysis
        breaking_news = len([art for art in articles if art.get("is_breaking", False)])
        recent_news = len([art for art in articles if art.get("is_recent", False)])
        
        return {
            "total_articles": total_articles,
            "unique_sources": len(sources),
            "sources": sources[:10],  # Top 10 sources
            "breaking_news": breaking_news,
            "recent_news": recent_news,
            "enrichment_stats": enrichment_stats
        }
    
    def _get_top_categories(self, categories: List[str], top_n: int = 5) -> List[str]:
        """Get top categories by frequency."""
        from collections import Counter
        category_counts = Counter(categories)
        return [cat for cat, _ in category_counts.most_common(top_n)]

# Convenience function for quick news processing
async def get_enhanced_crypto_news(
    symbols: Optional[List[str]] = None,
    hours_back: int = 24,
    enable_enrichment: bool = True
) -> Dict[str, Any]:
    """
    Quick function to get enhanced crypto news.
    
    Args:
        symbols: List of crypto symbols
        hours_back: Hours to look back
        enable_enrichment: Enable AI enrichment
        
    Returns:
        Processed news data
    """
    pipeline = EnhancedNewsPipeline()
    return await pipeline.process_crypto_news(
        symbols=symbols,
        hours_back=hours_back,
        enable_enrichment=enable_enrichment
    )

# Test function
async def test_enhanced_pipeline():
    """Test the enhanced news pipeline."""
    print("🧠 Testing Enhanced News Pipeline")
    print("=" * 50)
    
    pipeline = EnhancedNewsPipeline()
    
    # Test with basic symbols
    result = await pipeline.process_crypto_news(
        symbols=["Bitcoin", "Ethereum"],
        hours_back=6,
        enable_enrichment=True,
        max_articles=5
    )
    
    if result["success"]:
        print("✅ Pipeline test successful!")
        print(f"   Articles processed: {len(result['articles'])}")
        print(f"   Metadata: {result['metadata']}")
        
        # Show sample enriched article
        if result['articles']:
            sample = result['articles'][0]
            print(f"\n📰 Sample article:")
            print(f"   Title: {sample.get('title', 'N/A')}")
            if 'enrichment' in sample:
                print(f"   Sentiment: {sample['enrichment'].get('sentiment', 'N/A')}")
                print(f"   Categories: {sample['enrichment'].get('categories', [])}")
    else:
        print(f"❌ Pipeline test failed: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    asyncio.run(test_enhanced_pipeline()) 
