import os

JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY",
    "change-me-dev-secret-key-min-32-bytes",
)
