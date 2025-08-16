#!/usr/bin/env python3
"""
Replit-specific startup script for Masonic AI Crypto Broker
This ensures proper initialization and helps Replit detect the web app
"""

import os
import sys
import uvicorn
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))


def main():
    """Start the FastAPI application for Replit deployment."""

    # Set deployment mode for lightweight startup
    os.environ.setdefault("DEPLOYMENT_MODE", "lightweight")
    os.environ.setdefault("RELOAD", "false")
    os.environ.setdefault("PORT", "8000")

    print("🚀 Starting Masonic AI Crypto Broker for Replit...")
    print("📊 Phase 5: Cache Reader Implementation")
    print("⚡ NEW: Temporal Optimization (Prepped Kitchen Architecture)")
    print("   - Background news collection: collectors/news_ingestor.py")
    print("   - AI processing pipeline: collectors/analysis_pipeline.py")
    print("   - Fast serving router: /optimized-news")

    # Import the app after setting up environment
    try:
        from main import app

        print("✅ FastAPI app imported successfully")
        print(f"🌐 Server will be available at: http://0.0.0.0:8000")
        print("📚 Cache endpoints: /api/cache/*")
        print("🎓 Capstone dashboard: /dashboard")
        print("🔧 Admin panel: /admin")
        print("🧠 Brain dashboard: /brain-dashboard")
        print("📊 Status dashboard: /status-dashboard")

        # Start the server
        uvicorn.run(app, host="0.0.0.0", port=8000, reload=False, log_level="info")

    except ImportError as e:
        print(f"❌ Failed to import app: {e}")
        print("💡 Make sure all dependencies are installed")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
