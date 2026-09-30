from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    APP_NAME: str = "Real-Time Cloud Event RSVP Tracker"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    PORT: int = 8000
    FRONTEND_URL: str = "http://localhost:5173"

    DATABASE_URL: str = "sqlite+aiosqlite:///./event_tracker.db"

    JWT_SECRET: str = "dev-secret-key-not-for-production-change-this"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440

    # Firebase / Google Cloud (optional)
    FIREBASE_PROJECT_ID: Optional[str] = None
    FIREBASE_STORAGE_BUCKET: Optional[str] = None
    FIREBASE_CLIENT_EMAIL: Optional[str] = None
    FIREBASE_PRIVATE_KEY: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


settings = Settings()
