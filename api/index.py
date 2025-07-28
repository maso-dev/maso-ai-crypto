#!/usr/bin/env python3
"""
Vercel serverless function entry point for FastAPI
"""
import sys
import os
from pathlib import Path

# Add parent directory to path so we can import from the root
sys.path.append(str(Path(__file__).parent.parent))

# Import the FastAPI app from main.py
from main import app

# Create a handler function for Vercel
def handler(request, context):
    """Vercel serverless function handler."""
    from mangum import Adapter
    adapter = Adapter(app)
    return adapter(request, context)

# Also export the app directly for compatibility
app_handler = app 
