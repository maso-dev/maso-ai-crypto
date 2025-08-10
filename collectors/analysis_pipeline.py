#!/usr/bin/env python3
"""
Analysis Pipeline - Phase 2 of Temporal Optimization
====================================================

This script runs after the news ingestor and is responsible for:
1. Reading raw articles from intermediate database
2. Performing expensive AI operations (OpenAI, embeddings)
3. Enriching articles with sentiment, entities, categories
4. Storing processed data in final search-optimized databases
5. Running on a scheduled basis after data collection

This is the "prep work" phase - we do all the expensive cooking before service.
"""

import asyncio
import json
import logging
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from utils.config import ConfigManager
except ImportError:
    ConfigManager = None

try:
    from utils.enrichment import get_enrichment_chain
except ImportError:
    get_enrichment_chain = None

try:
    from utils.optimized_embedding import OptimizedEmbeddingClient
except ImportError:
    OptimizedEmbeddingClient = None

try:
    from utils.milvus import EnhancedVectorRAG
except ImportError:
    EnhancedVectorRAG = None

try:
    from utils.graph_rag import Neo4jGraphRAG
except ImportError:
    Neo4jGraphRAG = None
from utils.temporal_context import (
    enhance_article_with_temporal_context,
    sort_articles_by_temporal_relevance,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class AnalysisPipeline:
    """
    Intelligent analysis pipeline that processes raw news data.

    This is the "prep kitchen" that transforms raw ingredients into
    ready-to-serve dishes before customers arrive.
    """

    def __init__(self, raw_db_path: str = "data/raw_news.db"):
        self.config = ConfigManager() if ConfigManager else None
        self.raw_db_path = raw_db_path

        # Initialize AI components (with fallbacks)
        self.enrichment_chain = get_enrichment_chain() if get_enrichment_chain else None
        self.embedding_client = (
            OptimizedEmbeddingClient() if OptimizedEmbeddingClient else None
        )

        # Initialize storage systems
        self.vector_rag = None
        self.graph_rag = None

        # Initialize storage systems (with error handling)
        try:
            self.vector_rag = EnhancedVectorRAG() if EnhancedVectorRAG else None
            if self.vector_rag:
                logger.info("✅ Vector RAG initialized")
            else:
                logger.warning("⚠️ Vector RAG not available")
        except Exception as e:
            logger.warning(f"⚠️ Vector RAG unavailable: {e}")

        try:
            self.graph_rag = Neo4jGraphRAG() if Neo4jGraphRAG else None
            if self.graph_rag:
                logger.info("✅ Graph RAG initialized")
            else:
                logger.warning("⚠️ Graph RAG not available")
        except Exception as e:
            logger.warning(f"⚠️ Graph RAG unavailable: {e}")

    async def get_unprocessed_articles(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get unprocessed articles from raw database."""
        try:
            with sqlite3.connect(self.raw_db_path) as conn:
                conn.row_factory = sqlite3.Row  # Enable dict-like access

                cursor = conn.execute(
                    """
                    SELECT * FROM raw_articles 
                    WHERE processed = FALSE 
                    ORDER BY published_at DESC 
                    LIMIT ?
                """,
                    (limit,),
                )

                articles = []
                for row in cursor.fetchall():
                    article = dict(row)
                    # Parse raw_data JSON
                    if article["raw_data"]:
                        try:
                            article["raw_data"] = json.loads(article["raw_data"])
                        except json.JSONDecodeError:
                            article["raw_data"] = {}

                    articles.append(article)

                logger.info(f"Retrieved {len(articles)} unprocessed articles")
                return articles

        except Exception as e:
            logger.error(f"Error retrieving unprocessed articles: {e}")
            return []

    async def enrich_article(self, article: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Enrich a single article with AI analysis.

        This performs the expensive OpenAI operations that we want to
        do once and cache, rather than on every user request.
        """
        try:
            logger.debug(f"Enriching article: {article['title'][:50]}...")

            # Prepare enrichment input
            enrichment_input = {
                "title": article["title"],
                "content": article["content"] or article["title"],
                "source_name": article["source_name"],
                "published_at": article["published_at"],
            }

            # Run enrichment chain
            if self.enrichment_chain:
                enrichment_result = await asyncio.to_thread(
                    self.enrichment_chain.invoke, enrichment_input
                )
            else:
                # Fallback enrichment result
                from types import SimpleNamespace

                enrichment_result = SimpleNamespace(
                    sentiment="neutral",
                    sentiment_score=0.5,
                    category="general",
                    entities=[],
                    key_topics=[],
                    market_impact="medium",
                    urgency_score=0.5,
                    time_relevance="recent",
                )

            # Add temporal context
            temporal_article = enhance_article_with_temporal_context(
                {
                    "title": article["title"],
                    "content": article["content"],
                    "published_at": article["published_at"],
                    "url": article["url"],
                    "source_name": article["source_name"],
                }
            )

            # Create enriched article
            enriched = {
                # Original data
                "id": article["id"],
                "source": article["source"],
                "crypto_symbol": article["crypto_symbol"],
                "title": article["title"],
                "content": article["content"],
                "url": article["url"],
                "source_name": article["source_name"],
                "published_at": article["published_at"],
                "collected_at": article["collected_at"],
                # AI Enrichment
                "sentiment": enrichment_result.sentiment,
                "sentiment_score": enrichment_result.sentiment_score,
                "category": enrichment_result.category,
                "entities": enrichment_result.entities,
                "key_topics": enrichment_result.key_topics,
                "market_impact": getattr(enrichment_result, "market_impact", "medium"),
                "urgency_score": getattr(enrichment_result, "urgency_score", 0.5),
                "time_relevance": getattr(
                    enrichment_result, "time_relevance", "recent"
                ),
                # Temporal Context
                "hours_ago": temporal_article.get("hours_ago"),
                "is_breaking": temporal_article.get("is_breaking", False),
                "is_recent": temporal_article.get("is_recent", False),
                "recency_score": temporal_article.get("recency_score", 0.5),
                "urgency_score_temporal": temporal_article.get("urgency_score", 0.5),
                "time_category": temporal_article.get("time_category", "recent"),
                # Processing metadata
                "processed_at": datetime.now(timezone.utc).isoformat(),
                "embedding_created": False,
            }

            return enriched

        except Exception as e:
            logger.error(f"Error enriching article {article['id']}: {e}")
            return None

    async def create_embeddings(
        self, enriched_article: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Create embeddings for the enriched article."""
        try:
            # Prepare text for embedding
            embedding_text = (
                f"{enriched_article['title']}\n\n{enriched_article['content'] or ''}"
            )

            # Create embedding
            embedding = await self.embedding_client.create_embedding(embedding_text)

            if embedding:
                enriched_article["embedding"] = embedding
                enriched_article["embedding_created"] = True
                logger.debug(f"Created embedding for article {enriched_article['id']}")

            return enriched_article

        except Exception as e:
            logger.error(
                f"Error creating embedding for article {enriched_article['id']}: {e}"
            )
            return enriched_article

    async def store_in_vector_db(self, enriched_article: Dict[str, Any]) -> bool:
        """Store enriched article in vector database."""
        if not self.vector_rag or not enriched_article.get("embedding"):
            return False

        try:
            # Prepare vector data
            vector_data = {
                "id": f"article_{enriched_article['id']}",
                "vector": enriched_article["embedding"],
                "metadata": {
                    "title": enriched_article["title"],
                    "content": enriched_article["content"],
                    "url": enriched_article["url"],
                    "source": enriched_article["source"],
                    "crypto_symbol": enriched_article["crypto_symbol"],
                    "sentiment": enriched_article["sentiment"],
                    "sentiment_score": enriched_article["sentiment_score"],
                    "category": enriched_article["category"],
                    "market_impact": enriched_article["market_impact"],
                    "is_breaking": enriched_article["is_breaking"],
                    "is_recent": enriched_article["is_recent"],
                    "recency_score": enriched_article["recency_score"],
                    "urgency_score": enriched_article["urgency_score"],
                    "published_at": enriched_article["published_at"],
                    "processed_at": enriched_article["processed_at"],
                },
            }

            # Store in Milvus
            await self.vector_rag.store_vectors([vector_data])
            logger.debug(f"Stored article {enriched_article['id']} in vector DB")
            return True

        except Exception as e:
            logger.error(
                f"Error storing article {enriched_article['id']} in vector DB: {e}"
            )
            return False

    async def store_in_graph_db(self, enriched_article: Dict[str, Any]) -> bool:
        """Store enriched article in graph database."""
        if not self.graph_rag:
            return False

        try:
            # Store in graph database (simplified version)
            # Note: Actual implementation depends on Neo4jGraphRAG interface
            try:
                if hasattr(self.graph_rag, "create_article_node"):
                    await self.graph_rag.create_article_node(
                        article_id=f"article_{enriched_article['id']}",
                        title=enriched_article["title"],
                        content=enriched_article["content"],
                        metadata={
                            "url": enriched_article["url"],
                            "source": enriched_article["source_name"],
                            "published_at": enriched_article["published_at"],
                            "sentiment": enriched_article["sentiment"],
                            "category": enriched_article["category"],
                            "crypto_symbol": enriched_article["crypto_symbol"],
                        },
                    )
                else:
                    # Fallback: use generic storage method
                    await self.graph_rag.store_article(enriched_article)
            except AttributeError:
                # Graph RAG interface not fully implemented yet
                logger.warning("Graph RAG storage interface not available")

            logger.debug(f"Stored article {enriched_article['id']} in graph DB")
            return True

        except Exception as e:
            logger.error(
                f"Error storing article {enriched_article['id']} in graph DB: {e}"
            )
            return False

    def mark_article_processed(self, article_id: int, success: bool = True) -> None:
        """Mark an article as processed in the raw database."""
        try:
            with sqlite3.connect(self.raw_db_path) as conn:
                conn.execute(
                    """
                    UPDATE raw_articles 
                    SET processed = ?, processed_at = ?
                    WHERE id = ?
                """,
                    (success, datetime.now(timezone.utc).isoformat(), article_id),
                )

        except Exception as e:
            logger.error(f"Error marking article {article_id} as processed: {e}")

    async def process_article_batch(
        self, articles: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """Process a batch of articles through the full pipeline."""
        results = {
            "processed": 0,
            "enriched": 0,
            "embedded": 0,
            "stored_vector": 0,
            "stored_graph": 0,
            "errors": 0,
        }

        for article in articles:
            try:
                logger.info(
                    f"Processing article {article['id']}: {article['title'][:50]}..."
                )

                # Step 1: Enrich with AI
                enriched = await self.enrich_article(article)
                if not enriched:
                    results["errors"] += 1
                    self.mark_article_processed(article["id"], success=False)
                    continue

                results["enriched"] += 1

                # Step 2: Create embeddings
                if enriched:
                    enriched = await self.create_embeddings(enriched)
                    if enriched and enriched.get("embedding_created"):
                        results["embedded"] += 1

                    # Step 3: Store in vector database
                    if enriched and await self.store_in_vector_db(enriched):
                        results["stored_vector"] += 1

                    # Step 4: Store in graph database
                    if enriched and await self.store_in_graph_db(enriched):
                        results["stored_graph"] += 1

                # Mark as processed
                self.mark_article_processed(article["id"], success=True)
                results["processed"] += 1

                # Small delay to prevent overwhelming APIs
                await asyncio.sleep(0.5)

            except Exception as e:
                logger.error(f"Error processing article {article['id']}: {e}")
                results["errors"] += 1
                self.mark_article_processed(article["id"], success=False)

        return results

    async def run_analysis_cycle(self, batch_size: int = 50) -> Dict[str, Any]:
        """
        Run a complete analysis cycle.

        This is the main method called by the Cron job after data collection.
        """
        logger.info("🧠 Starting analysis pipeline cycle")
        start_time = datetime.now(timezone.utc)

        cycle_results = {
            "start_time": start_time.isoformat(),
            "batches_processed": 0,
            "total_processed": 0,
            "total_enriched": 0,
            "total_embedded": 0,
            "total_stored_vector": 0,
            "total_stored_graph": 0,
            "total_errors": 0,
            "errors": [],
        }

        try:
            # Process articles in batches
            while True:
                # Get next batch of unprocessed articles
                articles = await self.get_unprocessed_articles(batch_size)

                if not articles:
                    logger.info("No more unprocessed articles")
                    break

                logger.info(f"Processing batch of {len(articles)} articles")

                # Process the batch
                batch_results = await self.process_article_batch(articles)

                # Update totals
                cycle_results["batches_processed"] += 1
                cycle_results["total_processed"] += batch_results["processed"]
                cycle_results["total_enriched"] += batch_results["enriched"]
                cycle_results["total_embedded"] += batch_results["embedded"]
                cycle_results["total_stored_vector"] += batch_results["stored_vector"]
                cycle_results["total_stored_graph"] += batch_results["stored_graph"]
                cycle_results["total_errors"] += batch_results["errors"]

                logger.info(
                    f"Batch completed: {batch_results['processed']}/{len(articles)} processed"
                )

                # Break if we processed fewer articles than batch size (last batch)
                if len(articles) < batch_size:
                    break

        except Exception as e:
            error_msg = f"Analysis cycle error: {e}"
            logger.error(error_msg)
            cycle_results["errors"].append(error_msg)

        end_time = datetime.now(timezone.utc)
        cycle_results["end_time"] = end_time.isoformat()
        cycle_results["duration_seconds"] = (end_time - start_time).total_seconds()

        logger.info(
            f"✅ Analysis cycle completed in {cycle_results['duration_seconds']:.1f}s"
        )
        logger.info(f"📊 Processed: {cycle_results['total_processed']} articles")

        return cycle_results


async def main():
    """Main entry point for the analysis pipeline."""
    logger.info("🧠 Analysis Pipeline - Phase 2 Temporal Optimization")

    # Create pipeline
    pipeline = AnalysisPipeline()

    # Run analysis cycle
    results = await pipeline.run_analysis_cycle()

    # Print results
    print("\n" + "=" * 60)
    print("🧠 ANALYSIS RESULTS")
    print("=" * 60)
    print(f"📊 Batches processed: {results['batches_processed']}")
    print(f"✅ Articles processed: {results['total_processed']}")
    print(f"🎯 Articles enriched: {results['total_enriched']}")
    print(f"🔢 Embeddings created: {results['total_embedded']}")
    print(f"💾 Stored in vector DB: {results['total_stored_vector']}")
    print(f"🕸️  Stored in graph DB: {results['total_stored_graph']}")
    print(f"⏱️  Duration: {results['duration_seconds']:.1f}s")

    if results["total_errors"] > 0:
        print(f"⚠️  Errors: {results['total_errors']}")

    if results.get("errors"):
        print(f"\n⚠️  ERROR DETAILS:")
        for error in results["errors"]:
            print(f"   - {error}")

    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
