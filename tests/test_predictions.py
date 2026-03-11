"""Prediction endpoint behavior tests."""

import pytest
import requests

from utils import INVALID_STUDENT, OUT_OF_RANGE_STUDENT, get_access_token, get_random_student


@pytest.mark.parametrize(
    "authorization_header",
    [
        None,
        "Bearer invalid-token",
    ],
)


def test_predict_returns_401_when_token_is_missing_or_invalid(
    api_config: dict[str, str | int],
    authorization_header: str | None,
) -> None:
    """Prediction requires a valid bearer token."""
    X, _ = get_random_student()
    headers = {}
    if authorization_header is not None:
        headers["Authorization"] = authorization_header

    response = requests.post(
        f"{api_config['base_url']}/predict",
        json={"request": X},
        headers=headers,
        timeout=10,
    )

    assert response.status_code == 401, (
        f"Unexpected response: [{response.status_code}] {response.text}"
    )


def test_predict_returns_valid_prediction_for_valid_input(
    api_config: dict[str, str | int],
) -> None:
    """A valid payload and token should return one prediction."""
    X, _ = get_random_student()
    token = get_access_token(api_config)

    response = requests.post(
        f"{api_config['base_url']}/predict",
        json={"request": X},
        headers={"Authorization": f"Bearer {token}"},
        timeout=10,
    )

    assert response.status_code == 200, (
        f"Prediction failed: [{response.status_code}] {response.text}"
    )

    prediction = response.json().get("prediction")
    assert isinstance(prediction, float)


def test_predict_returns_error_for_invalid_input_data(
    api_config: dict[str, str | int],
) -> None:
    """Schema-invalid payloads must be rejected by the API."""
    token = get_access_token(api_config)

    response = requests.post(
        f"{api_config['base_url']}/predict",
        json={"request": INVALID_STUDENT},
        headers={"Authorization": f"Bearer {token}"},
        timeout=10,
    )

    assert response.status_code in {400, 422}, (
        f"Unexpected response: [{response.status_code}] {response.text}"
    )


def test_predict_returns_400_for_out_of_range_input(
    api_config: dict[str, str | int],
) -> None:
    """Out-of-range raw values must be rejected before normalization."""
    token = get_access_token(api_config)

    response = requests.post(
        f"{api_config['base_url']}/predict",
        json={"request": OUT_OF_RANGE_STUDENT},
        headers={"Authorization": f"Bearer {token}"},
        timeout=10,
    )

    assert response.status_code == 400, (
        f"Unexpected response: [{response.status_code}] {response.text}"
    )
