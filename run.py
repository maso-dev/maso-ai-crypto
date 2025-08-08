#!/usr/bin/env python3
"""
Simple startup script for Replit deployment
"""

import uvicorn
import os

if __name__ == "__main__":
    # Get port from environment (Replit sets this)
    port = int(os.environ.get("PORT", 8000))
    
    # Run the FastAPI app
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
