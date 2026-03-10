import json
from pathlib import Path

# internal imports
from src.adapters.constants import USER_DB_PATH
from src.api.users import APIUser
from src.ports.users import UserRepository


class UsersDB(UserRepository):
    """Basic file-backed user store."""

    def __init__(self, db_path: Path = USER_DB_PATH) -> None:
        print("Using Users database at:", db_path)
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.db_path.exists():
            self.db_path.write_text("[]", encoding="utf-8")

    def _load_users(self) -> list[dict[str, str]]:
        return json.loads(self.db_path.read_text(encoding="utf-8"))

    def save(self, users: list[dict[str, str]]) -> None:
        self.db_path.write_text(json.dumps(users, indent=2), encoding="utf-8")

    def create_user(self, user: APIUser) -> dict[str, str]:
        users = self._load_users()
        if user.username in [stored_user["username"] for stored_user in users]:
            raise ValueError(f"User '{user.username}' already exists.")

        stored_user = {
            "username": user.username,
            "encrypted_password": user.encoded_password,
        }
        users.append(stored_user)
        self.save(users)
        return stored_user

    def get_user(self, username: str) -> APIUser | None:
        users = self._load_users()
        for stored_user in users:
            if stored_user["username"] == username:
                # type: ignore
                return APIUser.from_existing(username=stored_user["username"], encoded_password=stored_user["encrypted_password"])
        return None


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="Utility to create an API User")
    parser.add_argument("-u", "--user", type=str,
                        help="Username for the API user")
    parser.add_argument("--password", type=str,
                        help="Password for the API user")
    args = parser.parse_args()
    # Create the APIUser
    user = APIUser(username=args.user, raw_password=args.password)
    try:
        # Store the created user
        users_db = UsersDB()
        users_db.create_user(user)
        print(
            f"Created user: {user.username} with encoded password: {user.encoded_password}")
    except ValueError as e:
        print(str(e))
