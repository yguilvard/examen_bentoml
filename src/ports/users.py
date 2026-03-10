# Python imports
from typing import Protocol

# Third-party imports

# Internal imports
from src.api.users import APIUser

# =============================== #
#   Ports interfaces definitions  #
# =============================== #


class UserRepository(Protocol):
    """Protocol for user repository implementations."""

    def create_user(self, user: APIUser) -> dict[str, str]: ...
    def get_user(self, username: str) -> APIUser | None: ...
    def save(self, users: list[dict[str, str]]) -> None: ...
