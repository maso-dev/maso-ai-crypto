#!/usr/bin/env python3
"""
Test script to verify Replit setup for Masonic AI Crypto Broker
Run this to check if the app can start properly in Replit environment
"""

import os
import sys
from pathlib import Path


def test_replit_environment():
    """Test Replit environment setup."""
    print("🧪 Testing Replit Environment Setup")
    print("=" * 50)

    # Test 1: Python path
    print("📁 Python Path:")
    for path in sys.path[:5]:  # Show first 5 paths
        print(f"   {path}")

    # Test 2: Current working directory
    print(f"\n📂 Current Directory: {os.getcwd()}")

    # Test 3: Check if main.py exists
    main_py = Path("main.py")
    if main_py.exists():
        print(f"✅ main.py found: {main_py.absolute()}")
    else:
        print(f"❌ main.py not found")

    # Test 4: Check if replit_startup.py exists
    startup_py = Path("replit_startup.py")
    if startup_py.exists():
        print(f"✅ replit_startup.py found: {startup_py.absolute()}")
    else:
        print(f"❌ replit_startup.py not found")

    # Test 5: Environment variables
    print(f"\n🔧 Environment Variables:")
    print(f"   PORT: {os.getenv('PORT', 'Not set')}")
    print(f"   RELOAD: {os.getenv('RELOAD', 'Not set')}")
    print(f"   PYTHONPATH: {os.getenv('PYTHONPATH', 'Not set')}")

    # Test 6: Try to import the app
    print(f"\n📦 Import Test:")
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from main import app

        print("✅ FastAPI app imported successfully")
        print(f"   App title: {app.title}")
        print(f"   Routes count: {len(app.routes)}")
    except ImportError as e:
        print(f"❌ Failed to import app: {e}")
    except Exception as e:
        print(f"⚠️ Import error: {e}")

    print("\n" + "=" * 50)
    print("🎯 Replit Setup Test Complete!")

    return True


if __name__ == "__main__":
    test_replit_environment()
