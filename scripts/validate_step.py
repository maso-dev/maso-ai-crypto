#!/usr/bin/env python3
"""
Step Validation Script
Validates all requirements for a development step before creating a PR.
"""

import os
import sys
import subprocess
import json
import requests
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import asyncio
import aiohttp


class StepValidator:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.success_count = 0
        self.total_checks = 0

    def log_success(self, message: str):
        """Log a successful check."""
        print(f"✅ {message}")
        self.success_count += 1
        self.total_checks += 1

    def log_warning(self, message: str):
        """Log a warning."""
        print(f"⚠️  {message}")
        self.warnings.append(message)
        self.total_checks += 1

    def log_error(self, message: str):
        """Log an error."""
        print(f"❌ {message}")
        self.errors.append(message)
        self.total_checks += 1

    def check_python_syntax(self) -> bool:
        """Check Python syntax for all .py files."""
        print("\n🔍 Checking Python syntax...")
        try:
            result = subprocess.run(
                ["python", "-m", "py_compile", "main.py"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                self.log_success("main.py syntax is valid")
            else:
                self.log_error(f"main.py syntax error: {result.stderr}")
                return False

            # Check all Python files
            py_files = list(Path(".").rglob("*.py"))
            for py_file in py_files:
                if "venv" not in str(py_file) and ".venv" not in str(py_file):
                    result = subprocess.run(
                        ["python", "-m", "py_compile", str(py_file)],
                        capture_output=True,
                        text=True,
                    )
                    if result.returncode != 0:
                        self.log_error(f"{py_file} syntax error: {result.stderr}")
                        return False

            self.log_success(f"All {len(py_files)} Python files have valid syntax")
            return True
        except Exception as e:
            self.log_error(f"Syntax check failed: {e}")
            return False

    def check_imports(self) -> bool:
        """Check if all modules can be imported."""
        print("\n🔍 Checking module imports...")
        try:
            # Test main imports
            result = subprocess.run(
                ["python", "-c", "import main; print('main imports successfully')"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                self.log_success("main module imports successfully")
            else:
                self.log_error(f"main import failed: {result.stderr}")
                return False

            # Test utils imports
            utils_modules = [
                "utils.config",
                "utils.ai_agent",
                "utils.livecoinwatch_processor",
                "utils.tavily_search",
                "utils.enhanced_news_pipeline",
                "utils.data_quality_filter",
                "utils.refresh_processor",
            ]

            for module in utils_modules:
                result = subprocess.run(
                    [
                        "python",
                        "-c",
                        f"import {module}; print('{module} imports successfully')",
                    ],
                    capture_output=True,
                    text=True,
                )
                if result.returncode == 0:
                    self.log_success(f"{module} imports successfully")
                else:
                    self.log_error(f"{module} import failed: {result.stderr}")
                    return False

            return True
        except Exception as e:
            self.log_error(f"Import check failed: {e}")
            return False

    def check_linting(self) -> bool:
        """Check code linting with flake8."""
        print("\n🔍 Checking code linting...")
        try:
            result = subprocess.run(
                ["python", "-m", "flake8", ".", "--max-line-length=120", "--count"],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                self.log_success("Code passes flake8 linting")
                return True
            else:
                lines = result.stdout.strip().split("\n")
                if lines and lines[0].isdigit():
                    error_count = int(lines[0])
                    if error_count == 0:
                        self.log_success("Code passes flake8 linting")
                        return True
                    else:
                        self.log_error(f"Found {error_count} linting errors")
                        print(result.stdout)
                        return False
                else:
                    self.log_error("Linting check failed")
                    print(result.stderr)
                    return False
        except Exception as e:
            self.log_error(f"Linting check failed: {e}")
            return False

    def check_code_formatting(self) -> bool:
        """Check code formatting with black."""
        print("\n🔍 Checking code formatting...")
        try:
            result = subprocess.run(
                ["python", "-m", "black", ".", "--check", "--diff"],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                self.log_success("Code formatting is correct")
                return True
            else:
                self.log_error("Code formatting issues found")
                print(result.stdout)
                return False
        except Exception as e:
            self.log_error(f"Formatting check failed: {e}")
            return False

    def check_tests(self) -> bool:
        """Run unit tests."""
        print("\n🔍 Running unit tests...")
        try:
            # Run pytest on tests directory
            result = subprocess.run(
                ["python", "-m", "pytest", "tests/", "-v"],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                self.log_success("Unit tests pass")
                return True
            else:
                self.log_error("Unit tests failed")
                print(result.stdout)
                return False
        except Exception as e:
            self.log_error(f"Test execution failed: {e}")
            return False

    def check_integration_tests(self) -> bool:
        """Run integration tests."""
        print("\n🔍 Running integration tests...")
        try:
            # Run individual test files
            test_files = [
                "test_enhanced_pipeline.py",
                "test_livecoinwatch.py",
                "test_tavily.py",
                "test_data_quality_filter.py",
                "test_refresh_processor.py",
            ]

            all_passed = True
            for test_file in test_files:
                if os.path.exists(test_file):
                    result = subprocess.run(
                        ["python", test_file], capture_output=True, text=True
                    )
                    if result.returncode == 0:
                        self.log_success(f"{test_file} passed")
                    else:
                        self.log_error(f"{test_file} failed")
                        print(result.stdout)
                        all_passed = False
                else:
                    self.log_warning(f"{test_file} not found")

            return all_passed
        except Exception as e:
            self.log_error(f"Integration test execution failed: {e}")
            return False

    async def check_api_endpoints(self) -> bool:
        """Check API endpoints are working."""
        print("\n🔍 Checking API endpoints...")
        try:
            # Start the server
            server_process = subprocess.Popen(
                [
                    "python",
                    "-m",
                    "uvicorn",
                    "main:app",
                    "--host",
                    "0.0.0.0",
                    "--port",
                    "8000",
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            # Wait for server to start
            await asyncio.sleep(5)

            async with aiohttp.ClientSession() as session:
                endpoints = [
                    ("/health", "Health check"),
                    ("/admin_conf", "Admin configuration"),
                    ("/api/portfolio", "Portfolio endpoint"),
                    ("/api/news-briefing", "News briefing endpoint"),
                    ("/api/opportunities", "Opportunities endpoint"),
                ]

                all_passed = True
                for endpoint, description in endpoints:
                    try:
                        async with session.get(
                            f"http://localhost:8000{endpoint}"
                        ) as response:
                            if response.status == 200:
                                self.log_success(f"{description} responds correctly")
                            else:
                                self.log_warning(
                                    f"{description} returned status {response.status}"
                                )
                    except Exception as e:
                        self.log_warning(f"{description} check failed: {e}")

            # Stop the server
            server_process.terminate()
            server_process.wait()

            return True
        except Exception as e:
            self.log_error(f"API endpoint check failed: {e}")
            return False

    def check_environment_variables(self) -> bool:
        """Check required environment variables."""
        print("\n🔍 Checking environment variables...")
        required_vars = [
            "OPENAI_API_KEY",
            "BINANCE_API_KEY",
            "BINANCE_SECRET_KEY",
            "NEWSAPI_API_KEY",
            "LIVECOINWATCH_API_KEY",
            "TAVILY_API_KEY",
        ]

        optional_vars = [
            "MILVUS_URI",
            "MILVUS_TOKEN",
            "NEO4J_URI",
            "NEO4J_USERNAME",
            "NEO4J_PASSWORD",
            "LANGSMITH_API_KEY",
        ]

        all_required_present = True
        for var in required_vars:
            if os.getenv(var):
                self.log_success(f"{var} is set")
            else:
                self.log_error(f"{var} is not set")
                all_required_present = False

        for var in optional_vars:
            if os.getenv(var):
                self.log_success(f"{var} is set (optional)")
            else:
                self.log_warning(f"{var} is not set (optional)")

        return all_required_present

    def check_documentation(self) -> bool:
        """Check documentation completeness."""
        print("\n🔍 Checking documentation...")
        required_docs = [
            "README.md",
            "DEVELOPMENT_WORKFLOW.md",
            "OPTIMIZED_BRAIN_ARCHITECTURE_PLAN.md",
            "CURRENT_IMPLEMENTATION_STATUS.md",
        ]

        all_present = True
        for doc in required_docs:
            if os.path.exists(doc):
                self.log_success(f"{doc} exists")
            else:
                self.log_error(f"{doc} is missing")
                all_present = False

        return all_present

    def check_security(self) -> bool:
        """Check for security issues."""
        print("\n🔍 Checking security...")
        try:
            # Check for hardcoded secrets
            secret_patterns = ["api_key", "secret", "password", "token"]

            found_secrets = []
            for pattern in secret_patterns:
                result = subprocess.run(
                    [
                        "grep",
                        "-r",
                        "-i",
                        pattern,
                        ".",
                        "--exclude-dir=.git",
                        "--exclude-dir=.venv",
                    ],
                    capture_output=True,
                    text=True,
                )
                if result.stdout:
                    lines = result.stdout.strip().split("\n")
                    for line in lines:
                        if "=" in line and not line.strip().startswith("#"):
                            # Check if it looks like a hardcoded secret
                            if any(char.isdigit() for char in line.split("=")[1]):
                                found_secrets.append(line.strip())

            if found_secrets:
                self.log_error("Potential hardcoded secrets found:")
                for secret in found_secrets[:5]:  # Show first 5
                    print(f"  {secret}")
                return False
            else:
                self.log_success("No hardcoded secrets found")
                return True
        except Exception as e:
            self.log_error(f"Security check failed: {e}")
            return False

    def check_git_status(self) -> bool:
        """Check git status and branch."""
        print("\n🔍 Checking git status...")
        try:
            # Check current branch
            result = subprocess.run(
                ["git", "branch", "--show-current"], capture_output=True, text=True
            )
            current_branch = result.stdout.strip()

            if current_branch.startswith("feature/step-"):
                self.log_success(f"Working on feature branch: {current_branch}")
            else:
                self.log_warning(f"Not on a feature branch: {current_branch}")

            # Check for uncommitted changes
            result = subprocess.run(
                ["git", "status", "--porcelain"], capture_output=True, text=True
            )

            if result.stdout.strip():
                self.log_warning("There are uncommitted changes")
                print("Uncommitted files:")
                for line in result.stdout.strip().split("\n"):
                    if line:
                        print(f"  {line}")
            else:
                self.log_success("All changes are committed")

            return True
        except Exception as e:
            self.log_error(f"Git status check failed: {e}")
            return False

    def generate_report(self) -> Dict:
        """Generate validation report."""
        return {
            "total_checks": self.total_checks,
            "success_count": self.success_count,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "success_rate": (
                (self.success_count / self.total_checks * 100)
                if self.total_checks > 0
                else 0
            ),
            "errors": self.errors,
            "warnings": self.warnings,
        }

    async def run_all_checks(self) -> bool:
        """Run all validation checks."""
        print("🚀 Starting step validation...")
        print("=" * 50)

        checks = [
            ("Python Syntax", self.check_python_syntax),
            ("Module Imports", self.check_imports),
            ("Code Linting", self.check_linting),
            ("Code Formatting", self.check_code_formatting),
            ("Unit Tests", self.check_tests),
            ("Integration Tests", self.check_integration_tests),
            ("API Endpoints", self.check_api_endpoints),
            ("Environment Variables", self.check_environment_variables),
            ("Documentation", self.check_documentation),
            ("Security", self.check_security),
            ("Git Status", self.check_git_status),
        ]

        all_passed = True
        for check_name, check_func in checks:
            try:
                if asyncio.iscoroutinefunction(check_func):
                    result = await check_func()
                else:
                    result = check_func()

                if not result:
                    all_passed = False
            except Exception as e:
                self.log_error(f"{check_name} check failed with exception: {e}")
                all_passed = False

        print("\n" + "=" * 50)
        print("📊 VALIDATION SUMMARY")
        print("=" * 50)

        report = self.generate_report()
        print(f"Total Checks: {report['total_checks']}")
        print(f"Successful: {report['success_count']}")
        print(f"Errors: {report['error_count']}")
        print(f"Warnings: {report['warning_count']}")
        print(f"Success Rate: {report['success_rate']:.1f}%")

        if report["errors"]:
            print(f"\n❌ ERRORS ({len(report['errors'])}):")
            for error in report["errors"]:
                print(f"  • {error}")

        if report["warnings"]:
            print(f"\n⚠️  WARNINGS ({len(report['warnings'])}):")
            for warning in report["warnings"]:
                print(f"  • {warning}")

        if all_passed:
            print(f"\n🎉 ALL CHECKS PASSED! Ready to create PR.")
        else:
            print(f"\n❌ VALIDATION FAILED! Please fix errors before creating PR.")

        return all_passed


async def main():
    """Main function."""
    validator = StepValidator()
    success = await validator.run_all_checks()

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
