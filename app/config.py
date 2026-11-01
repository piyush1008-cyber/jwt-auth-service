import os


class Settings:
    """Application security & database settings."""
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "JWT Authentication & RBAC Service")
    VERSION: str = "1.0.0"

    # Cryptographic settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./auth.db")


settings = Settings()
