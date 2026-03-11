"""JWT authentication tests for the protected prediction endpoint."""

import os
from datetime import datetime, timedelta, timezone

import requests
from jwt import encode as jwt_encode

from utils import get_random_student


JWT_ALGORITHM = "HS256"


def test_predict_with_expired_token_returns_401(
    api_config: dict[str, str | int],
    jwt_secret_key: str,
) -> None:
    """Expired JWTs must not allow prediction calls."""
    X, _ = get_random_student()
    expired_token = jwt_encode(
        {
            "sub": api_config["username"],
            "exp": datetime.now(timezone.utc) - timedelta(minutes=5),
            "jti": "expired-test-token",
        },
        jwt_secret_key,
        algorithm=JWT_ALGORITHM,
    )

    response = requests.post(
        f"{api_config['base_url']}/predict",
        json={"request": X},
        headers={"Authorization": f"Bearer {expired_token}"},
        timeout=10,
    )

    assert response.status_code == 401, (
        f"Unexpected response: [{response.status_code}] {response.text}"
    )
