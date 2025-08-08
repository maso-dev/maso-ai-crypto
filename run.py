#!/usr/bin/env python3
"""
Simple startup script for Replit deployment
"""

import os

def main():
    """Main startup function"""
    try:
        import uvicorn
    except ImportError:
        print("❌ uvicorn not found. Please install dependencies using Replit's package manager.")
        print("💡 In Replit, go to 'Packages' tab and install the required packages.")
        return
    
    # Get port from environment (Replit sets this)
    port = int(os.environ.get("PORT", 8000))
    
    print(f"🚀 Starting Masonic AI Crypto Broker on port {port}")
    
    # Run the FastAPI app
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()
