# Python imports
from pathlib import Path
from datetime import datetime, timedelta, timezone

# Third party imports
import json

# Local imports
from src.adapters.constants import TOKENS_DB_PATH
from src.api.tokens import APIToken
from src.api.constants import JWT_EXPIRE_MINUTES
from src.ports.tokens import TokenRepository


class TokensDB(TokenRepository):
    """Basic file-backed token store."""

    def __init__(self, localpath: Path = TOKENS_DB_PATH) -> None:
        self.db_path = localpath
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.db_path.exists():
            self.db_path.write_text("[]", encoding="utf-8")

    def _load_tokens(self) -> list[dict[str, str]]:
        return json.loads(self.db_path.read_text(encoding="utf-8"))

    def _write_tokens(self, stored_tokens: list[dict[str, str]]) -> None:
        self.db_path.write_text(json.dumps(
            stored_tokens, indent=2), encoding="utf-8")

    def create_token(self, username: str, duration_mn: int = JWT_EXPIRE_MINUTES) -> APIToken:
        stored_tokens = self._load_tokens()
        # Check if the user already has an active token
        now = datetime.now(timezone.utc)
        for token_record in stored_tokens:
            if token_record["username"] == username and datetime.fromisoformat(token_record["expires_at"]) > now:
                return APIToken.from_token(token_record["token"])

        # Create a new token
        api_token = APIToken(username=username)
        # Add the new token to the list of token
        stored_tokens.append({
            "username": username,
            "token": api_token.token,
            "expires_at": (now + timedelta(minutes=duration_mn)).isoformat(),
        })
        # Write the tokens in the db
        self._write_tokens(stored_tokens)
        # Returns the new token
        return api_token

    def get_token(self, token: str) -> APIToken:
        self.delete_expired_tokens()
        for stored_token in self._load_tokens():
            if stored_token["token"] == token:
                return APIToken.from_token(token=token)
        raise

    def list_active_tokens(self) -> list[dict[str, str]]:
        self.delete_expired_tokens()
        return self._load_tokens()

    def delete_expired_tokens(self) -> None:
        now = datetime.now(timezone.utc)
        active_tokens = [
            token_record
            for token_record in self._load_tokens()
            if datetime.fromisoformat(token_record["expires_at"]) > now
        ]
        self._write_tokens(active_tokens)
