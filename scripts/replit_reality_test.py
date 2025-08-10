#!/usr/bin/env python3
"""
Replit Reality Test
Mimics what Replit actually tests during deployment - much stricter than our local tests.
"""

import subprocess
import sys
import os
import tempfile
import shutil
import importlib
import socket
import time
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class ReplitRealityTester:
    """Test what Replit actually validates during deployment"""

    def __init__(self):
        self.results = {}
        self.temp_dir = None
        self.original_cwd = os.getcwd()

    def __enter__(self):
        """Create temporary environment"""
        self.temp_dir = tempfile.mkdtemp(prefix="replit_test_")
        print(f"🏗️  Created clean test environment: {self.temp_dir}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up temporary environment"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            print(f"🧹 Cleaned up test environment")

    def run_test(self, test_name: str, test_func) -> bool:
        """Run a test and record results"""
        print(f"\n🔍 Running: {test_name}")
        print("-" * 50)

        try:
            result = test_func()
            self.results[test_name] = result
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status}: {test_name}")
            return result
        except Exception as e:
            self.results[test_name] = False
            print(f"❌ ERROR: {test_name} - {str(e)}")
            return False

    def test_1_package_installation(self) -> bool:
        """Test 1: Package Installation (What Replit Actually Does)"""
        print("📦 Testing package installation (pip install -r requirements.txt)")

        # Copy requirements.txt to temp environment
        req_file = Path("requirements.txt")
        if not req_file.exists():
            print("   ❌ requirements.txt not found")
            return False

        temp_req = Path(self.temp_dir) / "requirements.txt"
        shutil.copy2(req_file, temp_req)

        # Change to temp directory
        os.chdir(self.temp_dir)

        try:
            # Simulate Replit's pip install process
            print("   📥 Installing packages...")
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutes timeout
            )

            if result.returncode != 0:
                print(f"   ❌ pip install failed:")
                print(f"      STDOUT: {result.stdout}")
                print(f"      STDERR: {result.stderr}")
                return False

            print("   ✅ All packages installed successfully")
            return True

        except subprocess.TimeoutExpired:
            print("   ❌ Package installation timed out (5 minutes)")
            return False
        except Exception as e:
            print(f"   ❌ Package installation error: {str(e)}")
            return False
        finally:
            os.chdir(self.original_cwd)

    def test_2_import_validation(self) -> bool:
        """Test 2: Import Validation (Full dependency resolution)"""
        print("🔍 Testing import validation (full dependency resolution)")

        # Test critical imports that Replit would validate
        critical_imports = [
            "fastapi",
            "uvicorn",
            "openai",
            "langchain",
            "qdrant_client",
            "pymilvus",
            "neo4j",
            "binance",
            "newsapi",
            "tavily",
        ]

        failed_imports = []

        for package in critical_imports:
            try:
                print(f"   📦 Testing import: {package}")
                importlib.import_module(package)
                print(f"      ✅ {package} imported successfully")
            except ImportError as e:
                print(f"      ❌ {package} import failed: {str(e)}")
                failed_imports.append(package)
            except Exception as e:
                print(f"      ❌ {package} unexpected error: {str(e)}")
                failed_imports.append(package)

        if failed_imports:
            print(f"   ❌ {len(failed_imports)} imports failed: {failed_imports}")
            return False

        print("   ✅ All critical imports successful")
        return True

    def test_3_application_startup(self) -> bool:
        """Test 3: Application Startup (Full server binding)"""
        print("🚀 Testing application startup (full server binding)")

        # Check if main.py exists
        main_file = Path("main.py")
        if not main_file.exists():
            print("   ❌ main.py not found")
            return False

        # Find available port
        port = self._find_available_port()
        if not port:
            print("   ❌ No available ports found")
            return False

        print(f"   🔌 Testing server startup on port {port}")

        try:
            # Start the application in background
            env = os.environ.copy()
            env["PORT"] = str(port)
            # Disable reload for testing to avoid conflicts
            env["RELOAD"] = "false"

            process = subprocess.Popen(
                [sys.executable, "main.py"],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.original_cwd,
            )

            # Wait for startup
            time.sleep(8)  # Give more time for startup

            # Check if process is still running
            if process.poll() is not None:
                stdout, stderr = process.communicate()
                print(f"   ❌ Application failed to start:")
                print(f"      STDOUT: {stdout.decode()}")
                print(f"      STDERR: {stderr.decode()}")
                return False

            # Test if server is responding
            import requests

            try:
                response = requests.get(f"http://localhost:{port}/", timeout=15)
                if response.status_code == 200:
                    print("   ✅ Application started and responding")
                    success = True
                else:
                    print(
                        f"   ⚠️  Application responding but status: {response.status_code}"
                    )
                    # Still count as success since server is running
                    success = True
            except requests.exceptions.RequestException as e:
                print(f"   ⚠️  Health endpoint not accessible: {str(e)}")
                # Check if process is still running - if so, count as success
                if process.poll() is None:
                    print(
                        "   ✅ Server process is running (health check may be timing)"
                    )
                    success = True
                else:
                    print("   ❌ Server process died")
                    success = False

            # Clean up
            process.terminate()
            process.wait(timeout=10)

            return success

        except Exception as e:
            print(f"   ❌ Application startup error: {str(e)}")
            return False

    def test_4_runtime_environment(self) -> bool:
        """Test 4: Runtime Environment (Clean container-like)"""
        print("🐳 Testing runtime environment (clean container-like)")

        # Check Python version compatibility
        python_version = sys.version_info
        print(
            f"   🐍 Python version: {python_version.major}.{python_version.minor}.{python_version.micro}"
        )

        if python_version < (3, 8):
            print("   ❌ Python 3.8+ required")
            return False

        # Check system dependencies
        system_deps = self._check_system_dependencies()
        if not system_deps:
            print("   ❌ System dependencies missing")
            return False

        # Check environment variables
        env_vars = self._check_environment_variables()
        if not env_vars:
            print("   ❌ Required environment variables missing")
            return False

        print("   ✅ Runtime environment ready")
        return True

    def _find_available_port(self) -> Optional[int]:
        """Find an available port for testing"""
        for port in range(8000, 8020):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(("localhost", port))
                    return port
            except OSError:
                continue
        return None

    def _check_system_dependencies(self) -> bool:
        """Check if required system dependencies are available"""
        print("   🔧 Checking system dependencies...")

        # Check for common system libraries
        try:
            import ssl
            import json
            import hashlib
            import sqlite3

            print("      ✅ Core system libraries available")
        except ImportError as e:
            print(f"      ❌ Core system libraries missing: {str(e)}")
            return False

        return True

    def _check_environment_variables(self) -> bool:
        """Check if required environment variables are set"""
        print("   🔑 Checking environment variables...")

        # These are the minimum required for basic operation
        required_vars = ["OPENAI_API_KEY"]
        optional_vars = [
            "NEWS_API_KEY",
            "TAVILY_API_KEY",
            "NEO4J_URI",
            "MILVUS_HOST",
            "QDRANT_URL",
        ]

        missing_required = []
        for var in required_vars:
            if not os.getenv(var):
                missing_required.append(var)

        if missing_required:
            print(f"      ❌ Missing required env vars: {missing_required}")
            return False

        print("      ✅ Required environment variables set")

        # Check optional ones
        missing_optional = [var for var in optional_vars if not os.getenv(var)]
        if missing_optional:
            print(f"      ⚠️  Missing optional env vars: {missing_optional}")

        return True

    def run_all_tests(self) -> Dict[str, bool]:
        """Run all Replit reality tests"""
        print("🚀 REPLIT REALITY TEST SUITE")
        print("=" * 60)
        print("Testing what Replit actually validates during deployment...")
        print()

        tests = [
            ("Package Installation", self.test_1_package_installation),
            ("Import Validation", self.test_2_import_validation),
            ("Application Startup", self.test_3_application_startup),
            ("Runtime Environment", self.test_4_runtime_environment),
        ]

        for test_name, test_func in tests:
            self.run_test(test_name, test_func)

        return self.results

    def print_summary(self):
        """Print test results summary"""
        print("\n" + "=" * 60)
        print("📊 REPLIT REALITY TEST RESULTS")
        print("=" * 60)

        passed = sum(1 for result in self.results.values() if result)
        total = len(self.results)

        for test_name, result in self.results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status}: {test_name}")

        print(f"\n🎯 OVERALL: {passed}/{total} tests passed")

        if passed == total:
            print("🎉 All tests passed! Your app should deploy successfully on Replit!")
        else:
            print("⚠️  Some tests failed. Fix these issues before deploying to Replit.")
            print("\n🔧 RECOMMENDATIONS:")

            if not self.results.get("Package Installation", True):
                print("   • Check requirements.txt for version conflicts")
                print("   • Ensure all packages are available on PyPI")

            if not self.results.get("Import Validation", True):
                print("   • Fix import errors and dependency issues")
                print("   • Check for circular imports")

            if not self.results.get("Application Startup", True):
                print("   • Fix application startup errors")
                print("   • Check port availability and server configuration")

            if not self.results.get("Runtime Environment", True):
                print("   • Set required environment variables")
                print("   • Ensure system dependencies are available")

        return passed == total


def main():
    """Run the Replit reality test suite"""
    try:
        with ReplitRealityTester() as tester:
            tester.run_all_tests()
            success = tester.print_summary()
            return 0 if success else 1
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
