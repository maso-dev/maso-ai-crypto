#!/usr/bin/env python3
"""
Vercel serverless function entry point for FastAPI
"""
import sys
import os
from pathlib import Path

# Add current directory to path so we can import from the root
sys.path.append(str(Path(__file__).parent))

# Import the main FastAPI app
from main import app

# Export the app for Vercel (FastAPI is ASGI compatible)
handler = app 
