"""Shared HTTP test helpers."""

import requests

VALID_STUDENT = {
    "gre_score": 0.95,
    "toefl_score": 0.9,
    "rating": 0.8,
    "sop": 0.8,
    "lor": 0.8,
    "cgpa": 0.85,
    "research_xp": 1.0,
}

INVALID_STUDENT = {
    "gre": 320,
    "gpa": 3.5,
    "rank": 2,
}


def get_random_student() -> tuple[dict[str, float], float]:
    """Return a valid prediction payload used by HTTP tests."""
    return VALID_STUDENT, 0.0


def get_access_token(api_config: dict[str, str | int]) -> str:
    """Authenticate against /login and return a bearer token."""
    login_response = requests.post(
        f"{api_config['base_url']}/login",
        json={
            "username": api_config["username"],
            "password": api_config["password"],
        },
        timeout=10,
    )
    assert login_response.status_code == 200, (
        f"Login failed: [{login_response.status_code}] {login_response.text}"
    )

    token = login_response.json().get("access_token")
    assert token, "No access token returned by /login."
    return token
