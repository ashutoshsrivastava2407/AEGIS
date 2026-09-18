"""AEGIS Platform Centralized Settings Configuration."""

from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Core Environment
    AEGIS_ENV: str = Field(default="development")
    AEGIS_LOG_LEVEL: str = Field(default="INFO")
    AEGIS_SECRET_KEY: str = Field(default="dev_secret_key_change_in_production")

    # API Configuration
    API_HOST: str = Field(default="0.0.0.0")
    API_PORT: int = Field(default=8000)
    API_CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"]
    )

    # PostgreSQL Database
    POSTGRES_HOST: str = Field(default="localhost")
    POSTGRES_PORT: int = Field(default=5432)
    POSTGRES_DB: str = Field(default="aegis_db")
    POSTGRES_USER: str = Field(default="aegis_user")
    POSTGRES_PASSWORD: str = Field(default="aegis_secure_password")
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://aegis_user:aegis_secure_password@localhost:5432/aegis_db"
    )

    # Redis Cache & Events
    REDIS_HOST: str = Field(default="localhost")
    REDIS_PORT: int = Field(default=6379)
    REDIS_PASSWORD: str = Field(default="")
    REDIS_URL: str = Field(default="redis://localhost:6379/0")

    # Multi-Tenancy & Security
    DEFAULT_TENANT_ID: str = Field(default="00000000-0000-0000-0000-000000000001")
    JWT_ALGORITHM: str = Field(default="HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60)


settings = Settings()
