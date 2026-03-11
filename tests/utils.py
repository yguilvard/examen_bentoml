"""Shared HTTP test helpers."""

import requests

VALID_STUDENT = {
    "gre_score": 320.0,
    "toefl_score": 110.0,
    "rating": 4.0,
    "sop": 4.0,
    "lor": 4.0,
    "cgpa": 8.5,
    "research_xp": 1.0,
}

INVALID_STUDENT = {
    "gre": 320,
    "gpa": 3.5,
    "rank": 2,
}

OUT_OF_RANGE_STUDENT = {
    "gre_score": 500.0,
    "toefl_score": 110.0,
    "rating": 4.0,
    "sop": 4.0,
    "lor": 4.0,
    "cgpa": 8.5,
    "research_xp": 1.0,
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
