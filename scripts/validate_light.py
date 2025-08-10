#!/usr/bin/env python3
"""
Lightweight validation for fast development cycles
Only checks essential functionality - no heavy AI/LLM calls
"""

import os
import sys
import subprocess
from pathlib import Path


def run_command(cmd, description):
    """Run a command and return success status."""
    print(f"🔍 {description}...")
    try:
        # Split command into list to avoid shell=True security issue
        if isinstance(cmd, str):
            cmd = cmd.split()

        result = subprocess.run(
            cmd, shell=False, capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            print(f"✅ {description} - PASSED")
            return True
        else:
            print(f"❌ {description} - FAILED")
            print(f"   Error: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} - TIMEOUT")
        return False
    except Exception as e:
        print(f"❌ {description} - ERROR: {e}")
        return False


def check_imports():
    """Check that main modules can be imported."""
    print("🔍 Checking critical imports...")
    try:
        # Add current directory to Python path
        import sys

        sys.path.insert(0, os.getcwd())

        # Test main app import
        import main

        print("✅ Main app imports successfully")

        # Test key utils (without heavy operations)
        from utils.binance_client import get_portfolio_data
        from utils.livecoinwatch_processor import LiveCoinWatchProcessor
        from utils.ai_agent import CryptoAIAgent, AgentTask

        print("✅ Key utils import successfully")

        return True
    except Exception as e:
        print(f"❌ Import check failed: {e}")
        return False


def check_syntax():
    """Check Python syntax without running heavy operations."""
    print("🔍 Checking Python syntax...")
    try:
        # Check main.py syntax
        with open("main.py", "r") as f:
            compile(f.read(), "main.py", "exec")
        print("✅ main.py syntax is valid")

        # Check key utils syntax
        key_files = [
            "utils/binance_client.py",
            "utils/livecoinwatch_processor.py",
            "utils/ai_agent.py",
        ]

        for file in key_files:
            if Path(file).exists():
                with open(file, "r") as f:
                    compile(f.read(), file, "exec")
                print(f"✅ {file} syntax is valid")

        return True
    except Exception as e:
        print(f"❌ Syntax check failed: {e}")
        return False


def check_env_vars():
    """Check essential environment variables."""
    print("🔍 Checking environment variables...")
    essential_vars = [
        "OPENAI_API_KEY",
        "BINANCE_API_KEY",
        "BINANCE_SECRET_KEY",
        "LIVECOINWATCH_API_KEY",
        "TAVILY_API_KEY",
    ]

    missing_vars = []
    for var in essential_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        print(f"⚠️  Missing optional vars: {missing_vars}")
    else:
        print("✅ All essential environment variables are set")

    return True  # Don't fail on missing vars


def check_git_status():
    """Check git status."""
    print("🔍 Checking git status...")
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            shell=False,
            capture_output=True,
            text=True,
        )
        if result.stdout.strip():
            print("⚠️  There are uncommitted changes")
        else:
            print("✅ Working directory is clean")
        return True
    except Exception as e:
        print(f"❌ Git check failed: {e}")
        return False


def main():
    """Run lightweight validation."""
    print("🚀 LIGHTWEIGHT VALIDATION - Fast Development Check")
    print("=" * 50)

    checks = [
        ("Syntax Check", check_syntax),
        ("Import Check", check_imports),
        ("Environment Variables", check_env_vars),
        ("Git Status", check_git_status),
    ]

    passed = 0
    total = len(checks)

    for name, check_func in checks:
        if check_func():
            passed += 1
        print()

    print("=" * 50)
    print(f"📊 LIGHTWEIGHT VALIDATION SUMMARY")
    print(f"Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")

    if passed == total:
        print("🎉 All lightweight checks passed! Ready for development.")
        return 0
    else:
        print("⚠️  Some checks failed. Review before proceeding.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
