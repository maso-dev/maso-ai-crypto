#!/usr/bin/env python3
"""
News Ingestor - Phase 1 of Temporal Optimization
================================================

This script runs independently of the FastAPI application and is responsible for:
1. Fetching raw news data from NewsAPI and Tavily
2. Basic filtering and validation
3. Storing raw data in intermediate database
4. Running on a scheduled basis (Cron job)

This is the "market shopping" phase - we gather all ingredients before cooking.
"""

import asyncio
import json
import logging
import os
import sqlite3
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from utils.config import ConfigManager
    from utils.newsapi import fetch_news_articles
    from utils.tavily_search import TavilySearchClient
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure all dependencies are installed and the project structure is correct")
    sys.exit(1)
from utils.temporal_context import enhance_article_with_temporal_context

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class NewsIngestor:
    """
    Independent news collection service that runs on a schedule.
    
    This is the "collector" that stocks our kitchen with fresh ingredients
    without blocking customer orders (API requests).
    """
    
    def __init__(self, db_path: str = "data/raw_news.db"):
        self.config = ConfigManager()
        self.db_path = db_path
        self.tavily_client = TavilySearchClient()
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Initialize database
        self._init_database()
        
        # Default crypto symbols to track
        self.crypto_symbols = ["BTC", "ETH", "SOL", "ADA", "DOT", "LINK", "AVAX", "MATIC"]
        
    def _init_database(self) -> None:
        """Initialize the raw news database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS raw_articles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT NOT NULL,  -- 'newsapi' or 'tavily'
                    crypto_symbol TEXT NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT,
                    url TEXT UNIQUE NOT NULL,
                    source_name TEXT,
                    published_at TEXT NOT NULL,
                    collected_at TEXT NOT NULL,
                    raw_data TEXT,  -- JSON of original API response
                    processed BOOLEAN DEFAULT FALSE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_url ON raw_articles(url)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_processed ON raw_articles(processed)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_crypto_symbol ON raw_articles(crypto_symbol)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_published_at ON raw_articles(published_at)
            """)
            
            logger.info("Raw news database initialized")
    
    async def collect_newsapi_articles(self, hours_back: int = 24) -> int:
        """
        Collect articles from NewsAPI for all tracked crypto symbols.
        
        Returns:
            Number of new articles collected
        """
        logger.info(f"Starting NewsAPI collection for {len(self.crypto_symbols)} symbols")
        new_articles = 0
        
        try:
            # Collect articles for each crypto symbol
            for symbol in self.crypto_symbols:
                try:
                    logger.info(f"Fetching NewsAPI articles for {symbol}")
                    articles = await fetch_news_articles(
                        [symbol], 
                        hours_back=hours_back
                    )
                    
                    for article in articles:
                        if self._store_raw_article(
                            source='newsapi',
                            crypto_symbol=symbol,
                            article=article
                        ):
                            new_articles += 1
                    
                    logger.info(f"Collected {len(articles)} articles for {symbol}")
                    
                    # Small delay to respect rate limits
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Error collecting NewsAPI articles for {symbol}: {e}")
                    continue
            
            logger.info(f"NewsAPI collection completed. {new_articles} new articles")
            return new_articles
            
        except Exception as e:
            logger.error(f"NewsAPI collection failed: {e}")
            return 0
    
    async def collect_tavily_articles(self, hours_back: int = 24) -> int:
        """
        Collect articles from Tavily for all tracked crypto symbols.
        
        Returns:
            Number of new articles collected
        """
        logger.info(f"Starting Tavily collection for {len(self.crypto_symbols)} symbols")
        new_articles = 0
        
        try:
            # Collect articles for each crypto symbol
            for symbol in self.crypto_symbols:
                try:
                    logger.info(f"Fetching Tavily articles for {symbol}")
                    
                    # Search for recent news
                    query = f"{symbol} cryptocurrency news"
                    results = await self.tavily_client.search_news(
                        query=query,
                        max_results=20
                    )
                    
                    # Handle different response formats
                    if hasattr(results, '__iter__') and not isinstance(results, (str, bytes)):
                        result_list = list(results)
                    else:
                        result_list = results if isinstance(results, list) else []
                    
                    for result in result_list:
                        # Convert Tavily result to article format
                        article = {
                            'title': result.get('title', ''),
                            'content': result.get('content', ''),
                            'url': result.get('url', ''),
                            'source_name': result.get('domain', 'Tavily'),
                            'published_at': result.get('published_date', datetime.now(timezone.utc).isoformat()),
                            'crypto_topic': symbol
                        }
                        
                        # Add temporal context
                        article = enhance_article_with_temporal_context(article)
                        
                        # Only include recent articles
                        if article.get('hours_ago', 999) <= hours_back:
                            if self._store_raw_article(
                                source='tavily',
                                crypto_symbol=symbol,
                                article=article,
                                raw_data=result
                            ):
                                new_articles += 1
                    
                    logger.info(f"Collected articles for {symbol} from Tavily")
                    
                    # Small delay to respect rate limits
                    await asyncio.sleep(2)
                    
                except Exception as e:
                    logger.error(f"Error collecting Tavily articles for {symbol}: {e}")
                    continue
            
            logger.info(f"Tavily collection completed. {new_articles} new articles")
            return new_articles
            
        except Exception as e:
            logger.error(f"Tavily collection failed: {e}")
            return 0
    
    def _store_raw_article(
        self, 
        source: str, 
        crypto_symbol: str, 
        article: Dict[str, Any],
        raw_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Store a raw article in the intermediate database.
        
        Returns:
            True if article was stored (new), False if duplicate
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Check if article already exists
                cursor = conn.execute(
                    "SELECT id FROM raw_articles WHERE url = ?",
                    (article.get('url', ''),)
                )
                
                if cursor.fetchone():
                    return False  # Duplicate
                
                # Store the article
                conn.execute("""
                    INSERT INTO raw_articles (
                        source, crypto_symbol, title, content, url, 
                        source_name, published_at, collected_at, raw_data
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    source,
                    crypto_symbol,
                    article.get('title', ''),
                    article.get('content', ''),
                    article.get('url', ''),
                    article.get('source_name', ''),
                    article.get('published_at', datetime.now(timezone.utc).isoformat()),
                    datetime.now(timezone.utc).isoformat(),
                    json.dumps(raw_data or article)
                ))
                
                return True  # New article stored
                
        except Exception as e:
            logger.error(f"Error storing article: {e}")
            return False
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about collected articles."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Total articles
                cursor = conn.execute("SELECT COUNT(*) FROM raw_articles")
                total_articles = cursor.fetchone()[0]
                
                # Articles by source
                cursor = conn.execute("""
                    SELECT source, COUNT(*) 
                    FROM raw_articles 
                    GROUP BY source
                """)
                by_source = dict(cursor.fetchall())
                
                # Articles by crypto symbol
                cursor = conn.execute("""
                    SELECT crypto_symbol, COUNT(*) 
                    FROM raw_articles 
                    GROUP BY crypto_symbol 
                    ORDER BY COUNT(*) DESC
                """)
                by_crypto = dict(cursor.fetchall())
                
                # Processed vs unprocessed
                cursor = conn.execute("""
                    SELECT processed, COUNT(*) 
                    FROM raw_articles 
                    GROUP BY processed
                """)
                processing_status = dict(cursor.fetchall())
                
                # Recent articles (last 24 hours)
                cursor = conn.execute("""
                    SELECT COUNT(*) FROM raw_articles 
                    WHERE collected_at > datetime('now', '-24 hours')
                """)
                recent_articles = cursor.fetchone()[0]
                
                return {
                    'total_articles': total_articles,
                    'by_source': by_source,
                    'by_crypto': by_crypto,
                    'processing_status': processing_status,
                    'recent_articles': recent_articles,
                    'last_updated': datetime.now(timezone.utc).isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {}
    
    async def run_collection_cycle(self, hours_back: int = 24) -> Dict[str, Any]:
        """
        Run a complete collection cycle for all sources.
        
        This is the main method called by the Cron job.
        """
        logger.info("🚀 Starting news collection cycle")
        start_time = datetime.now(timezone.utc)
        
        results = {
            'start_time': start_time.isoformat(),
            'newsapi_articles': 0,
            'tavily_articles': 0,
            'total_new_articles': 0,
            'errors': []
        }
        
        try:
            # Collect from NewsAPI
            newsapi_count = await self.collect_newsapi_articles(hours_back)
            results['newsapi_articles'] = newsapi_count
            
            # Collect from Tavily
            tavily_count = await self.collect_tavily_articles(hours_back)
            results['tavily_articles'] = tavily_count
            
            results['total_new_articles'] = newsapi_count + tavily_count
            
        except Exception as e:
            error_msg = f"Collection cycle error: {e}"
            logger.error(error_msg)
            results['errors'].append(error_msg)
        
        end_time = datetime.now(timezone.utc)
        results['end_time'] = end_time.isoformat()
        results['duration_seconds'] = (end_time - start_time).total_seconds()
        
        # Get final stats
        results['stats'] = self.get_collection_stats()
        
        logger.info(f"✅ Collection cycle completed in {results['duration_seconds']:.1f}s")
        logger.info(f"📊 New articles: {results['total_new_articles']}")
        
        return results


async def main():
    """Main entry point for the news ingestor."""
    logger.info("🏗️ News Ingestor - Phase 1 Temporal Optimization")
    
    # Create ingestor
    ingestor = NewsIngestor()
    
    # Run collection cycle
    results = await ingestor.run_collection_cycle()
    
    # Print results
    print("\n" + "="*60)
    print("📊 COLLECTION RESULTS")
    print("="*60)
    print(f"🗞️  NewsAPI articles: {results['newsapi_articles']}")
    print(f"🔍 Tavily articles: {results['tavily_articles']}")
    print(f"📈 Total new articles: {results['total_new_articles']}")
    print(f"⏱️  Duration: {results['duration_seconds']:.1f}s")
    
    if results.get('stats'):
        stats = results['stats']
        print(f"\n📊 DATABASE STATS:")
        print(f"   Total articles: {stats.get('total_articles', 0)}")
        print(f"   Recent (24h): {stats.get('recent_articles', 0)}")
        
        if stats.get('by_source'):
            print(f"   By source: {stats['by_source']}")
        
        if stats.get('by_crypto'):
            top_crypto = list(stats['by_crypto'].items())[:5]
            print(f"   Top crypto: {dict(top_crypto)}")
    
    if results.get('errors'):
        print(f"\n⚠️  ERRORS:")
        for error in results['errors']:
            print(f"   - {error}")
    
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
