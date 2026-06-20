"""Global Pytest configuration and shared fixtures."""

import pytest


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    """Configure the asynchronous backend context for enterprise testing."""
    return "asyncio"
