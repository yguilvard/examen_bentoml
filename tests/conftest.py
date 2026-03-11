"""Shared pytest configuration for HTTP client tests."""

import os

import pytest


@pytest.fixture(scope="module")
def api_config() -> dict[str, str | int]:
    """Return the target API configuration used by client-side tests."""
    port = int(os.getenv("TEST_API_PORT", "3000"))
    hostname = os.getenv("TEST_API_HOSTNAME", "localhost")
    return {
        "port": port,
        "username": os.getenv("TEST_API_USERNAME", "admin"),
        "password": os.getenv("TEST_API_PASSWORD", "admin"),
        "hostname": hostname,
        "base_url": f"http://{hostname}:{port}",
    }


@pytest.fixture(scope="module")
def jwt_secret_key() -> str:
    """Return the shared JWT secret required by tests that encode/decode tokens."""
    secret = os.getenv("JWT_SECRET_KEY", "").strip()
    assert secret, (
        "JWT_SECRET_KEY must be set for API tests. "
        "Export the same secret used to start the service."
    )
    return secret
