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

# For Vercel serverless deployment - use mangum adapter
from mangum import Adapter

# Create ASGI adapter for AWS Lambda/Vercel
handler = Adapter(app) 
