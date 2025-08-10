#!/usr/bin/env python3
"""
Cron Scheduler - Temporal Optimization Orchestrator
===================================================

This script orchestrates the temporal optimization pipeline:
1. Runs news collection (Phase 1)
2. Runs analysis pipeline (Phase 2)
3. Manages scheduling and logging
4. Provides status monitoring

This is the "restaurant manager" that coordinates the kitchen operations.
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from collectors.news_ingestor import NewsIngestor
from collectors.analysis_pipeline import AnalysisPipeline

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class TemporalScheduler:
    """
    Orchestrates the temporal optimization pipeline.

    This manages the entire "prepped kitchen" workflow.
    """

    def __init__(self, log_dir: str = "data/logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.news_ingestor = NewsIngestor()
        self.analysis_pipeline = AnalysisPipeline()

    def save_run_log(self, run_type: str, results: Dict[str, Any]) -> None:
        """Save run results to log file."""
        try:
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            log_file = self.log_dir / f"{run_type}_{timestamp}.json"

            with open(log_file, "w") as f:
                json.dump(results, f, indent=2, default=str)

            logger.info(f"Run log saved: {log_file}")

        except Exception as e:
            logger.error(f"Error saving run log: {e}")

    async def run_collection_only(self, hours_back: int = 24) -> Dict[str, Any]:
        """Run only the news collection phase."""
        logger.info("🚀 Running collection-only cycle")

        results = await self.news_ingestor.run_collection_cycle(hours_back)
        self.save_run_log("collection", results)

        return results

    async def run_analysis_only(self, batch_size: int = 50) -> Dict[str, Any]:
        """Run only the analysis pipeline phase."""
        logger.info("🧠 Running analysis-only cycle")

        results = await self.analysis_pipeline.run_analysis_cycle(batch_size)
        self.save_run_log("analysis", results)

        return results

    async def run_full_cycle(
        self, hours_back: int = 24, batch_size: int = 50
    ) -> Dict[str, Any]:
        """Run the complete temporal optimization cycle."""
        logger.info("🏗️ Running FULL temporal optimization cycle")
        start_time = datetime.now(timezone.utc)

        full_results = {
            "start_time": start_time.isoformat(),
            "collection_results": {},
            "analysis_results": {},
            "total_duration_seconds": 0,
            "success": False,
        }

        try:
            # Phase 1: Collect news
            logger.info("📡 Phase 1: News Collection")
            collection_results = await self.news_ingestor.run_collection_cycle(
                hours_back
            )
            full_results["collection_results"] = collection_results

            # Small delay between phases
            await asyncio.sleep(5)

            # Phase 2: Analysis pipeline
            logger.info("🧠 Phase 2: Analysis Pipeline")
            analysis_results = await self.analysis_pipeline.run_analysis_cycle(
                batch_size
            )
            full_results["analysis_results"] = analysis_results

            full_results["success"] = True

        except Exception as e:
            logger.error(f"Full cycle error: {e}")
            full_results["error"] = str(e)

        end_time = datetime.now(timezone.utc)
        full_results["end_time"] = end_time.isoformat()
        full_results["total_duration_seconds"] = (end_time - start_time).total_seconds()

        # Save combined log
        self.save_run_log("full_cycle", full_results)

        logger.info(
            f"✅ Full cycle completed in {full_results['total_duration_seconds']:.1f}s"
        )

        return full_results

    def get_recent_logs(
        self, run_type: Optional[str] = None, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get recent run logs."""
        try:
            log_files = []

            for log_file in self.log_dir.glob("*.json"):
                if run_type and not log_file.name.startswith(run_type):
                    continue

                log_files.append(log_file)

            # Sort by modification time (newest first)
            log_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)

            logs = []
            for log_file in log_files[:limit]:
                try:
                    with open(log_file) as f:
                        log_data = json.load(f)
                        log_data["log_file"] = log_file.name
                        logs.append(log_data)
                except Exception as e:
                    logger.error(f"Error reading log file {log_file}: {e}")

            return logs

        except Exception as e:
            logger.error(f"Error getting recent logs: {e}")
            return []

    def print_status_summary(self) -> None:
        """Print a summary of recent activity."""
        print("\n" + "=" * 80)
        print("🏗️ TEMPORAL OPTIMIZATION STATUS")
        print("=" * 80)

        # Get recent logs
        recent_full = self.get_recent_logs("full_cycle", 3)
        recent_collection = self.get_recent_logs("collection", 3)
        recent_analysis = self.get_recent_logs("analysis", 3)

        if recent_full:
            print("\n📊 RECENT FULL CYCLES:")
            for i, log in enumerate(recent_full[:3]):
                status = "✅" if log.get("success") else "❌"
                duration = log.get("total_duration_seconds", 0)
                collection_articles = log.get("collection_results", {}).get(
                    "total_new_articles", 0
                )
                processed_articles = log.get("analysis_results", {}).get(
                    "total_processed", 0
                )

                print(
                    f"   {i+1}. {status} {log.get('start_time', 'Unknown')} "
                    f"({duration:.1f}s) - Collected: {collection_articles}, Processed: {processed_articles}"
                )

        # Database stats
        stats = self.news_ingestor.get_collection_stats()
        if stats:
            print(f"\n💾 DATABASE STATUS:")
            print(f"   Total articles: {stats.get('total_articles', 0)}")
            print(f"   Recent (24h): {stats.get('recent_articles', 0)}")

            unprocessed = stats.get("processing_status", {}).get(
                0, 0
            )  # 0 = False = unprocessed
            processed = stats.get("processing_status", {}).get(
                1, 0
            )  # 1 = True = processed

            print(f"   Processed: {processed}")
            print(f"   Pending: {unprocessed}")

            if stats.get("by_source"):
                print(f"   By source: {stats['by_source']}")

        print("=" * 80)


async def main():
    """Main entry point for the scheduler."""
    import argparse

    parser = argparse.ArgumentParser(description="Temporal Optimization Scheduler")
    parser.add_argument(
        "--mode",
        choices=["collect", "analyze", "full", "status"],
        default="full",
        help="Operation mode",
    )
    parser.add_argument(
        "--hours-back",
        type=int,
        default=24,
        help="Hours back to collect news (default: 24)",
    )
    parser.add_argument(
        "--batch-size", type=int, default=50, help="Analysis batch size (default: 50)"
    )

    args = parser.parse_args()

    scheduler = TemporalScheduler()

    if args.mode == "status":
        scheduler.print_status_summary()
        return

    logger.info(f"🏗️ Temporal Scheduler - Mode: {args.mode}")

    if args.mode == "collect":
        results = await scheduler.run_collection_only(args.hours_back)
        print(
            f"\n✅ Collection completed: {results['total_new_articles']} new articles"
        )

    elif args.mode == "analyze":
        results = await scheduler.run_analysis_only(args.batch_size)
        print(
            f"\n✅ Analysis completed: {results['total_processed']} articles processed"
        )

    elif args.mode == "full":
        results = await scheduler.run_full_cycle(args.hours_back, args.batch_size)

        collection = results.get("collection_results", {})
        analysis = results.get("analysis_results", {})

        print(f"\n✅ Full cycle completed in {results['total_duration_seconds']:.1f}s")
        print(f"📡 Collected: {collection.get('total_new_articles', 0)} new articles")
        print(f"🧠 Processed: {analysis.get('total_processed', 0)} articles")
        print(f"💾 Vector DB: {analysis.get('total_stored_vector', 0)} stored")
        print(f"🕸️  Graph DB: {analysis.get('total_stored_graph', 0)} stored")

    # Show final status
    scheduler.print_status_summary()


if __name__ == "__main__":
    asyncio.run(main())
