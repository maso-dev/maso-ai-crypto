#!/usr/bin/env python3
"""
Simplified temporal optimization runner for Replit.
Replaces the complex cron_jobs.sh with a Python script.
"""

import asyncio
import os
import sys
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def run_temporal_cycle(mode="collect", hours_back=168):
    """Run temporal optimization cycle."""
    print(f"🏗️ Running temporal optimization: {mode}")
    print(f"📅 Time window: {hours_back} hours back")
    print("=" * 50)
    
    if mode in ["collect", "full"]:
        print("📡 Phase 1: News Collection")
        try:
            from collectors.news_ingestor import NewsIngestor
            ingestor = NewsIngestor()
            results = await ingestor.run_collection_cycle(hours_back=hours_back)
            
            print(f"✅ Collection completed:")
            print(f"   📰 NewsAPI: {results['newsapi_articles']} articles")
            print(f"   🔍 Tavily: {results['tavily_articles']} articles")
            print(f"   📊 Total: {results['total_new_articles']} new articles")
            print(f"   ⏱️  Duration: {results['duration_seconds']:.1f}s")
            
        except Exception as e:
            print(f"❌ Collection failed: {e}")
            return False
    
    if mode in ["analyze", "full"]:
        print("\n🧠 Phase 2: Analysis Pipeline")
        try:
            from collectors.analysis_pipeline import AnalysisPipeline
            pipeline = AnalysisPipeline()
            results = await pipeline.run_analysis_cycle()
            
            print(f"✅ Analysis completed:")
            print(f"   🧠 Processed: {results['processed_articles']} articles")
            print(f"   💾 Vector DB: {results.get('vector_stored', 0)} stored")
            print(f"   🕸️  Graph DB: {results.get('graph_stored', 0)} stored")
            print(f"   ⏱️  Duration: {results['duration_seconds']:.1f}s")
            
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            return False
    
    print("\n✅ Temporal optimization cycle completed!")
    return True

async def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run temporal optimization cycle")
    parser.add_argument("--mode", choices=["collect", "analyze", "full"], 
                       default="collect", help="Operation mode")
    parser.add_argument("--hours-back", type=int, default=168, 
                       help="Hours back to collect (default: 168 = 1 week)")
    
    args = parser.parse_args()
    
    success = await run_temporal_cycle(args.mode, args.hours_back)
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
