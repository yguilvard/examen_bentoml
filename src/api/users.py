import bcrypt
from dataclasses import InitVar, dataclass
from typing import Optional


@dataclass(frozen=False)
class APIUser:
    username: str
    raw_password: InitVar[str]
    encoded_password: Optional[str|None] = None

    def __post_init__(self, raw_password: str) -> None:
        if raw_password  is not None:
            self.encoded_password = bcrypt.hashpw(
                raw_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        elif self.encoded_password is None or not len(self.encoded_password):
            raise ValueError("No password provided for user {self.username}")

    def check_password(self, raw_password: str) -> bool:
        return bcrypt.checkpw(raw_password.encode("utf-8"), self.encoded_password.encode("utf-8")) # type: ignore

    @classmethod
    def from_existing(cls, username: str, encoded_password: str) -> APIUser:
        user = cls(username=username, raw_password="")
        user.encoded_password = encoded_password
        return user
