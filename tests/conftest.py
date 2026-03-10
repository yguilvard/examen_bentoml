"""Shared pytest configuration for HTTP client tests."""

import os
import sys
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture(scope="module")
def api_config() -> dict[str, str | int]:
    """Return the target API configuration used by client-side tests."""
    port = int(os.getenv("TEST_API_PORT", "3000"))
    return {
        "port": port,
        "username": os.getenv("TEST_API_USERNAME", "admin"),
        "password": os.getenv("TEST_API_PASSWORD", "admin"),
        "base_url": f"http://localhost:{port}",
    }
