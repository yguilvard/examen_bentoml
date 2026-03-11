"""Shared pytest configuration for HTTP client tests."""

import os

import pytest


@pytest.fixture(scope="module")
def api_config() -> dict[str, str | int]:
    """Return the target API configuration used by client-side tests."""
    port = int(os.getenv("TEST_API_PORT", "3000"))
    hostname = os.getenv("TEST_API_HOSTNAME", "localhost"),
    return {
        "port": int(os.getenv("TEST_API_PORT", "3000")),
        "username": os.getenv("TEST_API_USERNAME", "admin"),
        "password": os.getenv("TEST_API_PASSWORD", "admin"),
        "hostname": os.getenv("TEST_API_HOSTNAME", "localhost"),
        "base_url": f"http://{hostname}:{port}",
    }
