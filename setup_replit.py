#!/usr/bin/env python3
"""
Setup script for Replit environment
Run this first to install all dependencies
"""

import subprocess
import sys
import os

def main():
    print("🚀 Setting up Masonic AI Crypto Broker for Replit...")
    
    # Install dependencies
    print("📦 Installing Python dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False
    
    # Check if key packages are installed
    print("🔍 Verifying installation...")
    try:
        import fastapi
        import uvicorn
        import openai
        import langchain
        print("✅ All key packages installed!")
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        return False
    
    print("🎉 Setup complete! You can now run: python run.py")
    return True

if __name__ == "__main__":
    main()
