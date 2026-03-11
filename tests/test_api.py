# Python imports
import os
import requests
from jwt import decode as jwt_decode

# Constants
JWT_ALGORITHM = "HS256"
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "")


def test_login_returns_valid_jwt_for_valid_credentials(api_config: dict[str, str | int]) -> None:
    """Valid credentials should yield a decodable JWT."""
    assert JWT_SECRET_KEY, "JWT_SECRET_KEY must be set for API tests."
    response = requests.post(
        f"{api_config['base_url']}/login",
        json={
            "username": api_config["username"],
            "password": api_config["password"],
        },
        timeout=10,
    )

    assert response.status_code == 200, (
        f"Login failed: [{response.status_code}] {response.text}"
    )

    token = response.json().get("access_token")
    assert token, "No access token returned by /login."

    payload = jwt_decode(
        token,
        JWT_SECRET_KEY,
        algorithms=[JWT_ALGORITHM],
    )
    assert payload["sub"] == api_config["username"]
    assert "exp" in payload


def test_login_returns_401_for_invalid_credentials(api_config: dict[str, str | int]) -> None:
    """Invalid credentials should be rejected by /login."""
    response = requests.post(
        f"{api_config['base_url']}/login",
        json={
            "username": api_config["username"],
            "password": "wrong-password",
        },
        timeout=10,
    )

    assert response.status_code == 401, (
        f"Unexpected response: [{response.status_code}] {response.text}"
    )
