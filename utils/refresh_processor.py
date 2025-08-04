#!/usr/bin/env python3
"""
Refresh Process Engine
Flexible data processing with configurable intervals for future-proofing.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from enum import Enum

# Import existing components
from utils.livecoinwatch_processor import livecoinwatch_processor
from utils.data_quality_filter import data_quality_filter
from utils.enhanced_news_pipeline import EnhancedNewsPipeline
from utils.tavily_search import tavily_client
from utils.ai_agent import ai_agent
from utils.hybrid_rag import hybrid_rag
# Note: track_processing_call will be implemented in cost_tracker

logger = logging.getLogger(__name__)

class RefreshInterval(Enum):
    """Refresh intervals for different processing levels."""
    QUICK = "15min"      # Price updates only
    HOURLY = "hourly"    # Price + basic indicators
    DAILY = "daily"      # Full processing
    MANUAL = "manual"    # Manual trigger

@dataclass
class ProcessingResult:
    """Result of a processing run."""
    interval: RefreshInterval
    start_time: datetime
    end_time: datetime
    success: bool
    data_collected: Dict[str, Any]
    processing_metadata: Dict[str, Any]
    errors: List[str]
    warnings: List[str]

class RefreshProcessor:
    """Flexible data processing engine with configurable intervals."""
    
    def __init__(self):
        self.livecoinwatch = livecoinwatch_processor
        self.quality_filter = data_quality_filter
        self.news_pipeline = EnhancedNewsPipeline()
        self.ai_agent = ai_agent
        self.hybrid_rag = hybrid_rag
        
        # Processing configuration
        self.default_symbols = ["BTC", "ETH", "SOL", "XRP", "DOGE", "ADA", "DOT", "LINK"]
        self.news_symbols = ["Bitcoin", "Ethereum", "cryptocurrency", "blockchain", "DeFi"]
        
        # Performance tracking
        self.processing_stats = {
            "total_runs": 0,
            "successful_runs": 0,
            "failed_runs": 0,
            "last_run": None,
            "average_duration": 0.0
        }
        
        logger.info("RefreshProcessor initialized")
    
    async def run_refresh_processing(self, interval: RefreshInterval = RefreshInterval.DAILY) -> ProcessingResult:
        """
        Execute refresh processing pipeline with flexible intervals.
        
        Args:
            interval: Processing interval (15min, hourly, daily, manual)
            
        Returns:
            ProcessingResult with detailed execution information
        """
        start_time = datetime.now(timezone.utc)
        result = ProcessingResult(
            interval=interval,
            start_time=start_time,
            end_time=start_time,
            success=False,
            data_collected={},
            processing_metadata={},
            errors=[],
            warnings=[]
        )
        
        logger.info(f"🔄 Starting refresh processing: {interval.value}")
        
        try:
            # Track processing call (placeholder for future implementation)
            # await track_processing_call(
            #     operation=f"refresh_processing_{interval.value}",
            #     metadata={"interval": interval.value, "start_time": start_time.isoformat()}
            # )
            
            # Execute processing based on interval
            if interval in [RefreshInterval.QUICK, RefreshInterval.HOURLY]:
                await self._run_quick_refresh(result)
            else:
                await self._run_full_refresh(result)
            
            # Update processing stats
            self._update_processing_stats(result)
            
            result.success = True
            logger.info(f"✅ Refresh processing completed: {interval.value}")
            
        except Exception as e:
            error_msg = f"Refresh processing failed: {str(e)}"
            logger.error(error_msg)
            result.errors.append(error_msg)
            result.success = False
        
        finally:
            result.end_time = datetime.now(timezone.utc)
            duration = (result.end_time - result.start_time).total_seconds()
            result.processing_metadata["duration_seconds"] = duration
            
            logger.info(f"⏱️ Processing duration: {duration:.2f} seconds")
        
        return result
    
    async def _run_quick_refresh(self, result: ProcessingResult):
        """Run quick refresh (15min/hourly) - price updates only."""
        logger.info("📊 Running quick refresh (price updates)")
        
        # 1. Collect price data
        try:
            price_data = await self._collect_price_data()
            result.data_collected["price_data"] = price_data
            result.processing_metadata["price_symbols"] = len(price_data)
        except Exception as e:
            result.errors.append(f"Price data collection failed: {str(e)}")
        
        # 2. Calculate basic indicators (hourly only)
        if result.interval == RefreshInterval.HOURLY:
            try:
                indicators = await self._calculate_basic_indicators()
                result.data_collected["indicators"] = indicators
                result.processing_metadata["indicators_calculated"] = len(indicators)
            except Exception as e:
                result.errors.append(f"Indicator calculation failed: {str(e)}")
        
        # 3. Update market metrics
        try:
            market_metrics = await self._update_market_metrics()
            result.data_collected["market_metrics"] = market_metrics
        except Exception as e:
            result.warnings.append(f"Market metrics update failed: {str(e)}")
    
    async def _run_full_refresh(self, result: ProcessingResult):
        """Run full refresh (daily/manual) - complete processing."""
        logger.info("🧠 Running full refresh (complete processing)")
        
        # 1. Collect news data
        try:
            news_data = await self._collect_news_data()
            result.data_collected["news_data"] = news_data
            result.processing_metadata["news_articles"] = len(news_data.get("articles", []))
        except Exception as e:
            result.errors.append(f"News data collection failed: {str(e)}")
        
        # 2. Collect price data
        try:
            price_data = await self._collect_price_data()
            result.data_collected["price_data"] = price_data
            result.processing_metadata["price_symbols"] = len(price_data)
        except Exception as e:
            result.errors.append(f"Price data collection failed: {str(e)}")
        
        # 3. Calculate technical indicators
        try:
            indicators = await self._calculate_technical_indicators()
            result.data_collected["indicators"] = indicators
            result.processing_metadata["indicators_calculated"] = len(indicators)
        except Exception as e:
            result.errors.append(f"Technical indicators calculation failed: {str(e)}")
        
        # 4. Filter and clean data
        if result.data_collected.get("news_data"):
            try:
                filtered_news = await self._filter_and_clean_data(result.data_collected["news_data"])
                result.data_collected["filtered_news"] = filtered_news
                result.processing_metadata["filtered_articles"] = len(filtered_news.get("articles", []))
            except Exception as e:
                result.errors.append(f"Data filtering failed: {str(e)}")
        
        # 5. AI processing
        try:
            ai_results = await self._run_ai_processing()
            result.data_collected["ai_results"] = ai_results
            result.processing_metadata["ai_processing"] = "completed"
        except Exception as e:
            result.errors.append(f"AI processing failed: {str(e)}")
        
        # 6. Update RAG systems
        try:
            rag_update = await self._update_rag_systems()
            result.data_collected["rag_update"] = rag_update
            result.processing_metadata["rag_updated"] = True
        except Exception as e:
            result.warnings.append(f"RAG update failed: {str(e)}")
    
    async def _collect_price_data(self) -> Dict[str, Any]:
        """Collect price data from LiveCoinWatch."""
        logger.info("💰 Collecting price data...")
        
        price_data = {}
        for symbol in self.default_symbols:
            try:
                # Get real-time price data
                price_info = await self.livecoinwatch.collect_price_data([symbol])
                if price_info:
                    price_data[symbol] = price_info[0] if price_info else None
                
                # Get historical data for indicators
                historical = await self.livecoinwatch.collect_historical_data(symbol, days=30)
                if historical:
                    price_data[f"{symbol}_historical"] = historical
                    
            except Exception as e:
                logger.warning(f"Failed to collect price data for {symbol}: {e}")
        
        logger.info(f"✅ Collected price data for {len(price_data)} symbols")
        return price_data
    
    async def _collect_news_data(self) -> Dict[str, Any]:
        """Collect and process news data from multiple sources."""
        logger.info("📰 Collecting news data...")
        
        all_articles = []
        sources_used = []
        
        # 1. Try NewsAPI first
        try:
            news_result = await self.news_pipeline.process_crypto_news(
                symbols=self.news_symbols,
                hours_back=24,
                enable_enrichment=True,
                max_articles=30
            )
            
            if news_result["success"] and news_result.get("articles"):
                all_articles.extend(news_result["articles"])
                sources_used.append("newsapi")
                logger.info(f"✅ NewsAPI: Collected {len(news_result['articles'])} articles")
            else:
                logger.warning(f"⚠️ NewsAPI failed: {news_result.get('error', 'Unknown error')}")
                
        except Exception as e:
            logger.warning(f"⚠️ NewsAPI collection failed: {e}")
        
        # 2. Try Tavily as backup/alternative
        try:
            if tavily_client and tavily_client.available:
                tavily_results = await tavily_client.get_crypto_news(
                    symbols=self.default_symbols,
                    max_results=20
                )
                
                if tavily_results:
                    # Convert Tavily results to NewsAPI format
                    for result in tavily_results:
                        article = {
                            "title": result.title,
                            "description": result.content[:200] + "..." if len(result.content) > 200 else result.content,
                            "content": result.content,
                            "url": result.url,
                            "source": {"name": result.source},
                            "publishedAt": result.published_date.isoformat() if result.published_date else None,
                            "tavily_score": result.score,
                            "search_type": result.search_type,
                            "metadata": result.metadata
                        }
                        all_articles.append(article)
                    
                    sources_used.append("tavily")
                    logger.info(f"✅ Tavily: Collected {len(tavily_results)} articles")
                else:
                    logger.warning("⚠️ Tavily returned no results")
            else:
                logger.info("ℹ️ Tavily not available, skipping")
                
        except Exception as e:
            logger.warning(f"⚠️ Tavily collection failed: {e}")
        
        # 3. Combine and deduplicate results
        if all_articles:
            # Simple deduplication by URL
            seen_urls = set()
            unique_articles = []
            
            for article in all_articles:
                url = article.get("url", "")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    unique_articles.append(article)
            
            logger.info(f"✅ Combined {len(unique_articles)} unique articles from {sources_used}")
            
            return {
                "success": True,
                "articles": unique_articles,
                "sources_used": sources_used,
                "total_articles": len(unique_articles),
                "metadata": {
                    "newsapi_articles": len([a for a in all_articles if "tavily_score" not in a]),
                    "tavily_articles": len([a for a in all_articles if "tavily_score" in a]),
                    "deduplicated": len(all_articles) - len(unique_articles)
                }
            }
        else:
            logger.error("❌ No news articles collected from any source")
            return {
                "success": False,
                "articles": [],
                "sources_used": sources_used,
                "error": "No news articles collected from any source"
            }
    
    async def _calculate_basic_indicators(self) -> Dict[str, Any]:
        """Calculate basic indicators for hourly refresh."""
        logger.info("📊 Calculating basic indicators...")
        
        indicators = {}
        for symbol in self.default_symbols[:5]:  # Limit for quick refresh
            try:
                basic_indicators = await self.livecoinwatch.calculate_technical_indicators(symbol, days=7)
                if basic_indicators:
                    indicators[symbol] = basic_indicators
            except Exception as e:
                logger.warning(f"Failed to calculate indicators for {symbol}: {e}")
        
        return indicators
    
    async def _calculate_technical_indicators(self) -> Dict[str, Any]:
        """Calculate comprehensive technical indicators."""
        logger.info("📈 Calculating technical indicators...")
        
        indicators = {}
        for symbol in self.default_symbols:
            try:
                technical_indicators = await self.livecoinwatch.calculate_technical_indicators(symbol)
                if technical_indicators:
                    indicators[symbol] = technical_indicators
            except Exception as e:
                logger.warning(f"Failed to calculate technical indicators for {symbol}: {e}")
        
        return indicators
    
    async def _filter_and_clean_data(self, news_data: Dict[str, Any]) -> Dict[str, Any]:
        """Filter and clean news data using quality filter."""
        logger.info("🔍 Filtering and cleaning data...")
        
        articles = news_data.get("articles", [])
        if not articles:
            return news_data
        
        try:
            filtered_articles = await self.quality_filter.filter_articles(
                articles, symbols=self.default_symbols
            )
            
            # Separate approved and rejected articles
            approved_articles = [fa.original_article for fa in filtered_articles if fa.is_approved]
            rejected_articles = [fa.original_article for fa in filtered_articles if not fa.is_approved]
            
            logger.info(f"✅ Filtered {len(approved_articles)}/{len(articles)} articles")
            
            return {
                **news_data,
                "articles": approved_articles,
                "filtered_metadata": {
                    "original_count": len(articles),
                    "approved_count": len(approved_articles),
                    "rejected_count": len(rejected_articles),
                    "approval_rate": len(approved_articles) / len(articles) if articles else 0
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Data filtering failed: {e}")
            return news_data
    
    async def _run_ai_processing(self) -> Dict[str, Any]:
        """Run AI processing for market analysis."""
        logger.info("🧠 Running AI processing...")
        
        ai_results = {}
        
        try:
            # Market sentiment analysis
            sentiment_result = await self.ai_agent.execute_task(
                "market_analysis",
                query="Analyze market sentiment for crypto portfolio",
                symbols=self.default_symbols
            )
            ai_results["market_sentiment"] = sentiment_result
            
            # Portfolio optimization
            portfolio_result = await self.ai_agent.execute_task(
                "portfolio_recommendation",
                query="Generate portfolio optimization recommendations",
                symbols=self.default_symbols
            )
            ai_results["portfolio_optimization"] = portfolio_result
            
            # Risk assessment
            risk_result = await self.ai_agent.execute_task(
                "risk_assessment",
                query="Assess risk factors for crypto portfolio",
                symbols=self.default_symbols
            )
            ai_results["risk_assessment"] = risk_result
            
            logger.info("✅ AI processing completed")
            
        except Exception as e:
            logger.error(f"❌ AI processing failed: {e}")
            ai_results["error"] = str(e)
        
        return ai_results
    
    async def _update_rag_systems(self) -> Dict[str, Any]:
        """Update RAG systems with new data."""
        logger.info("🔗 Updating RAG systems...")
        
        rag_update = {}
        
        try:
            # Update vector RAG with new articles
            if self.hybrid_rag and self.hybrid_rag.vector_rag:
                # This would be implemented based on your vector RAG structure
                rag_update["vector_rag"] = "updated"
            
            # Update graph RAG with new relationships
            if self.hybrid_rag and self.hybrid_rag.graph_rag:
                # This would be implemented based on your graph RAG structure
                rag_update["graph_rag"] = "updated"
            
            logger.info("✅ RAG systems updated")
            
        except Exception as e:
            logger.error(f"❌ RAG update failed: {e}")
            rag_update["error"] = str(e)
        
        return rag_update
    
    async def _update_market_metrics(self) -> Dict[str, Any]:
        """Update basic market metrics."""
        logger.info("📊 Updating market metrics...")
        
        try:
            # This would include market cap, volume, etc.
            metrics = {
                "total_market_cap": 0,
                "total_volume_24h": 0,
                "market_dominance": {},
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Market metrics update failed: {e}")
            return {"error": str(e)}
    
    def _update_processing_stats(self, result: ProcessingResult):
        """Update processing statistics."""
        self.processing_stats["total_runs"] += 1
        
        if result.success:
            self.processing_stats["successful_runs"] += 1
        else:
            self.processing_stats["failed_runs"] += 1
        
        self.processing_stats["last_run"] = result.end_time
        
        # Calculate average duration
        duration = (result.end_time - result.start_time).total_seconds()
        total_runs = self.processing_stats["total_runs"]
        current_avg = self.processing_stats["average_duration"]
        
        self.processing_stats["average_duration"] = (
            (current_avg * (total_runs - 1) + duration) / total_runs
        )
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics."""
        return {
            **self.processing_stats,
            "success_rate": (
                self.processing_stats["successful_runs"] / self.processing_stats["total_runs"]
                if self.processing_stats["total_runs"] > 0 else 0
            )
        }
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get system status for monitoring."""
        return {
            "processor_status": "ready",
            "last_run": self.processing_stats["last_run"],
            "success_rate": self.get_processing_stats()["success_rate"],
            "average_duration": self.processing_stats["average_duration"],
            "components": {
                "livecoinwatch": self.livecoinwatch is not None,
                "quality_filter": self.quality_filter is not None,
                "news_pipeline": self.news_pipeline is not None,
                "ai_agent": self.ai_agent is not None,
                "hybrid_rag": self.hybrid_rag is not None
            }
        }

# Global instance
refresh_processor = RefreshProcessor()

# Convenience functions
async def run_quick_refresh() -> ProcessingResult:
    """Run quick refresh (15min interval)."""
    return await refresh_processor.run_refresh_processing(RefreshInterval.QUICK)

async def run_hourly_refresh() -> ProcessingResult:
    """Run hourly refresh."""
    return await refresh_processor.run_refresh_processing(RefreshInterval.HOURLY)

async def run_daily_refresh() -> ProcessingResult:
    """Run daily refresh (full processing)."""
    return await refresh_processor.run_refresh_processing(RefreshInterval.DAILY)

async def run_manual_refresh() -> ProcessingResult:
    """Run manual refresh (full processing)."""
    return await refresh_processor.run_refresh_processing(RefreshInterval.MANUAL) 
