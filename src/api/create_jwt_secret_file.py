import secrets
import argparse
from pathlib import Path


def create_jwt_secret_file(secret_path: str | Path, force:bool=False) -> Path:
    """Create a local JWT secret file if it does not already exist."""
    path = Path(secret_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(secrets.token_urlsafe(48), encoding="utf-8")
    return path


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output', type=Path, default=Path('.')/".jwt_secret")
    parser.add_argument('-f', '--force', action='store_true', default=False)
    args = parser.parse_args()
    create_jwt_secret_file(args.output, force=args.force)
