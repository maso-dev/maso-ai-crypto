#!/usr/bin/env python3
"""
Vercel serverless function entry point for FastAPI
"""
import sys
import os
from pathlib import Path

# Add current directory to path so we can import from the root
sys.path.append(str(Path(__file__).parent))

# Create a minimal FastAPI app for testing
from fastapi import FastAPI

app = FastAPI(title="Test API")

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/test")
async def test():
    return {"status": "ok", "message": "Test endpoint working"}

# Export the app for Vercel (FastAPI is ASGI compatible)
handler = app 
