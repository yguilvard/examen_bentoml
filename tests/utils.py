"""Shared HTTP test helpers."""

import random
from typing import Any, Hashable

import pandas as pd
import requests

from src.data.constants import PROCESSED_DATA_DIRECTORY

X_TEST_PATH = PROCESSED_DATA_DIRECTORY / "X_test.csv"
Y_TEST_PATH = PROCESSED_DATA_DIRECTORY / "y_test.csv"
TARGET_COLUMN = "chances"


def get_random_student() -> tuple[dict[Hashable, Any], float]:
    """Return one random student from the processed test split."""
    x_test = pd.read_csv(X_TEST_PATH)
    y_test = pd.read_csv(Y_TEST_PATH)

    random_index = random.randint(0, len(x_test) - 1)
    student_features = x_test.iloc[random_index].to_dict()
    true_admission_chance = float(y_test.iloc[random_index][TARGET_COLUMN])
    return student_features, true_admission_chance


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
