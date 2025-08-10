#!/usr/bin/env python3
"""
Replit Deployment Test Script
Mimics what Replit actually validates during deployment
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_package_installation():
    """Test 1: Package installation (what Replit does first)"""
    print("📦 Test 1: Package Installation")
    print("=" * 40)
    
    try:
        # Check if requirements.txt exists
        if not Path("requirements.txt").exists():
            print("❌ requirements.txt not found")
            return False
        
        # Check if key packages are importable
        required_packages = [
            "fastapi",
            "uvicorn", 
            "qdrant_client",
            "openai",
            "langchain"
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package)
                print(f"✅ {package} - OK")
            except ImportError:
                missing_packages.append(package)
                print(f"❌ {package} - MISSING")
        
        if missing_packages:
            print(f"❌ Missing packages: {missing_packages}")
            return False
        
        print("✅ All required packages available")
        return True
        
    except Exception as e:
        print(f"❌ Package test failed: {e}")
        return False


def test_imports():
    """Test 2: Import validation (what Replit does second)"""
    print("\n📚 Test 2: Import Validation")
    print("=" * 40)
    
    try:
        # Test critical imports
        critical_imports = [
            "main",
            "utils.qdrant_client",
            "utils.enhanced_hybrid_rag",
            "routers.enhanced_hybrid_router"
        ]
        
        failed_imports = []
        for module in critical_imports:
            try:
                __import__(module)
                print(f"✅ {module} - OK")
            except ImportError as e:
                failed_imports.append(module)
                print(f"❌ {module} - FAILED: {e}")
        
        if failed_imports:
            print(f"❌ Failed imports: {failed_imports}")
            return False
        
        print("✅ All critical imports successful")
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False


def test_application_startup():
    """Test 3: Application startup (what Replit does third)"""
    print("\n🚀 Test 3: Application Startup")
    print("=" * 40)
    
    try:
        # Check if main.py exists and is valid
        if not Path("main.py").exists():
            print("❌ main.py not found")
            return False
        
        # Try to start the app in background
        print("   Starting application...")
        process = subprocess.Popen(
            [sys.executable, "main.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a bit for startup
        time.sleep(5)
        
        # Check if process is still running
        if process.poll() is None:
            print("✅ Application started successfully")
            
            # Try to connect to health endpoint
            try:
                response = requests.get("http://localhost:8000/", timeout=10)
                if response.status_code == 200:
                    print("✅ Health endpoint responding")
                    success = True
                else:
                    print(f"⚠️ Health endpoint returned {response.status_code}")
                    success = True  # Still counts as startup success
            except requests.exceptions.RequestException:
                print("⚠️ Health endpoint not accessible yet (normal during startup)")
                success = True
            
            # Clean up
            process.terminate()
            process.wait()
            return success
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Application failed to start")
            print(f"   Exit code: {process.returncode}")
            if stderr:
                print(f"   Error: {stderr[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ Startup test failed: {e}")
        return False


def test_environment_variables():
    """Test 4: Environment variables (what Replit validates)"""
    print("\n🔑 Test 4: Environment Variables")
    print("=" * 40)
    
    required_vars = [
        "OPENAI_API_KEY",
        "QDRANT_VECTOR_API"
    ]
    
    optional_vars = [
        "NEO4J_URI",
        "NEO4J_USER", 
        "NEO4J_PASSWORD",
        "NEWS_API_KEY",
        "TAVILY_API_KEY"
    ]
    
    missing_required = []
    missing_optional = []
    
    for var in required_vars:
        if os.getenv(var):
            print(f"✅ {var} - SET")
        else:
            missing_required.append(var)
            print(f"❌ {var} - MISSING (REQUIRED)")
    
    for var in optional_vars:
        if os.getenv(var):
            print(f"✅ {var} - SET")
        else:
            missing_optional.append(var)
            print(f"⚠️ {var} - MISSING (OPTIONAL)")
    
    if missing_required:
        print(f"❌ Missing required environment variables: {missing_required}")
        return False
    
    print("✅ All required environment variables set")
    if missing_optional:
        print(f"⚠️ Optional variables missing: {missing_optional}")
    
    return True


def test_file_structure():
    """Test 5: File structure validation"""
    print("\n📁 Test 5: File Structure")
    print("=" * 40)
    
    required_files = [
        "main.py",
        "requirements.txt",
        "utils/qdrant_client.py",
        "utils/enhanced_hybrid_rag.py",
        "routers/enhanced_hybrid_router.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path} - EXISTS")
        else:
            missing_files.append(file_path)
            print(f"❌ {file_path} - MISSING")
    
    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        return False
    
    print("✅ All required files present")
    return True


def main():
    """Run all deployment tests"""
    print("🚀 Replit Deployment Validation Test")
    print("=" * 50)
    print("This test mimics what Replit validates during deployment")
    print()
    
    tests = [
        ("Package Installation", test_package_installation),
        ("Import Validation", test_imports),
        ("File Structure", test_file_structure),
        ("Environment Variables", test_environment_variables),
        ("Application Startup", test_application_startup)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"💥 {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 DEPLOYMENT TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - Ready for Replit deployment!")
        return True
    else:
        print("⚠️ Some tests failed - Fix issues before deploying")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
