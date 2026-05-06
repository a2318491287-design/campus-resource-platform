"""
Configuration loader for MUST Campus Academic Resource Sharing Platform backend.
"""
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database — DEFAULT: MariaDB on VPS via Docker network
    # Override via DATABASE_URL env var. SQLite fallback supported for local dev:
    #   sqlite:///./local.db
    DATABASE_URL: str = "mysql+pymysql://campus:campus_pwd@db:3306/campus_resource_platform?charset=utf8mb4"

    # JWT
    SECRET_KEY: str = "change-me-in-production-please"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # File storage (resources/ folder relative to backend root)
    STORAGE_DIR: str = "/app/storage"

    # Points engine constants — same as SDD §4.2
    UPLOAD_REWARD: int = 10
    DOWNLOAD_RECEIVED_REWARD: int = 2
    RATING_RECEIVED_REWARD: int = 1
    DOWNLOAD_COST: int = 1
    DAILY_FREE_DOWNLOADS: int = 3

    # Search ranking — same as SDD §3.2
    WEIGHT_MATCH: float = 0.40
    WEIGHT_DOWNLOADS: float = 0.30
    WEIGHT_RATING: float = 0.30

    # Redemption costs
    REDEEM_DOWNLOAD_CREDIT_10_COST: int = 50
    REDEEM_PIN_7DAYS_COST: int = 100

    # CORS
    CORS_ORIGINS: list[str] = ["*"]

    class Config:
        env_file = ".env"


settings = Settings()
