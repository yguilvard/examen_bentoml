from dataclasses import dataclass, InitVar
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from jwt import encode as jwt_encode, decode as jwt_decode

from src.admission.errors import InvalidTokenError
from src.api.constants import JWT_ALGORITHM, JWT_EXPIRE_MINUTES, JWT_SECRET_KEY


@dataclass(frozen=False)
class APIToken:
    username: str
    token: str = "change-me"
    lifetime_mn: InitVar[int] = JWT_EXPIRE_MINUTES
    expires_at: datetime | None = None

    def __post_init__(self, lifetime_mn) -> None:
        if self.token != "change-me":
            return

        self.expires_at = datetime.now(
            timezone.utc) + timedelta(minutes=lifetime_mn)
        self.token = jwt_encode(
            {
                "sub": self.username,
                "exp": self.expires_at,
                "jti": str(uuid4()),
            },
            JWT_SECRET_KEY,
            algorithm=JWT_ALGORITHM,
        )

    @classmethod
    def from_token(cls, token: str) -> APIToken:
        try:
            payload = jwt_decode(token, JWT_SECRET_KEY,
                                 algorithms=[JWT_ALGORITHM])
            api_token = cls(username=payload["sub"], token=token)
            api_token.expires_at = datetime.fromtimestamp(
                payload["exp"],
                tz=timezone.utc,
            )
            return api_token
        except Exception as e:
            raise InvalidTokenError(f"Invalid token: {e}")

    @classmethod
    def extract_bearer_token(cls, authorization_header: str) -> str | None:
        """Extract the JWT token from a standard Bearer Authorization header."""
        scheme, _, token = authorization_header.partition(" ")
        if scheme.lower() != "bearer" or not token:
            raise InvalidTokenError(
                "Invalid Authorization header format. Expected")
        return token

    @classmethod
    def decode_access_token(cls, token: str) -> dict:
        """Decode the JWT token and return its payload."""
        try:
            payload = jwt_decode(token, JWT_SECRET_KEY,
                                 algorithms=[JWT_ALGORITHM])
            return payload
        except Exception as e:
            raise InvalidTokenError(f"Invalid token: {e}")
