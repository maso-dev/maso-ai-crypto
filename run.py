#!/usr/bin/env python3
"""
Simple startup script for Replit deployment
"""

import os
import sys
import subprocess

def install_dependencies():
    """Install required dependencies if not already installed"""
    try:
        import uvicorn
        print("✅ uvicorn already installed")
    except ImportError:
        print("📦 Installing dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed")

def main():
    """Main startup function"""
    # Install dependencies if needed
    install_dependencies()
    
    # Import uvicorn after ensuring it's installed
    import uvicorn
    
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
