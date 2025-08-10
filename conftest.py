"""
Pytest configuration for async test support
"""

import pytest

# Configure pytest-asyncio
pytest_plugins = ["pytest_asyncio"]


# Mark all tests in tests/api/ as asyncio tests
def pytest_collection_modifyitems(config, items):
    for item in items:
        if "tests/api/" in str(item.fspath):
            item.add_marker(pytest.mark.asyncio)
