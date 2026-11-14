"""
Centralized application configuration.

Technify VisionAI + Supabase ES256

All values are loaded from environment variables (.env locally,
real environment variables in production/CI).
"""

from functools import lru_cache
from typing import List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ------------------------------------------------------------------
    # Application
    # ------------------------------------------------------------------

    PROJECT_NAME: str = "Technify VisionAI"

    API_V1_PREFIX: str = "/api/v1"

    ENVIRONMENT: str = Field(
        default="development",
        description="development | staging | production",
    )

    LOG_LEVEL: str = Field(
        default="INFO",
        description="DEBUG | INFO | WARNING | ERROR | CRITICAL",
    )

    # ------------------------------------------------------------------
    # Supabase
    # ------------------------------------------------------------------

    SUPABASE_URL: str = Field(
        default="https://ziojazjvsjtzcqdckajq.supabase.co",
        description="Supabase project URL",
    )

    SUPABASE_ANON_KEY: str = Field(
        default="sb_publishable_0vVWKefsKdyZaHvLdrqZUA_YyxOaNwa",
        description="Supabase publishable/anon key",
    )

    SUPABASE_SERVICE_ROLE_KEY: str = Field(
        default="mock_service_role_key_for_local_development_mode",
        description="Supabase secret/service_role key for backend operations",
    )

    # ------------------------------------------------------------------
    # Supabase JWT
    # ------------------------------------------------------------------

    SUPABASE_JWT_ALGORITHM: str = Field(
        default="ES256",
        description="Supabase JWT signing algorithm",
    )

    SUPABASE_JWT_SECRET: Optional[str] = None

    # ------------------------------------------------------------------
    # Database
    # ------------------------------------------------------------------

    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./technify_visionai.db",
        description=(
            "Async connection string for SQLAlchemy. "
            "Supports postgresql+asyncpg:// or sqlite+aiosqlite:///"
        ),
    )

    # ------------------------------------------------------------------
    # Application Security
    # ------------------------------------------------------------------

    SECRET_KEY: str = Field(
        default="technify-visionai-super-secret-key-development-local-32chars",
        min_length=32,
        description=(
            "Secret used by the Technify VisionAI application "
            "for its own security operations"
        ),
    )

    ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # ------------------------------------------------------------------
    # CORS
    # ------------------------------------------------------------------

    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173,http://127.0.0.1:5173,http://127.0.0.1:3000"

    # ------------------------------------------------------------------
    # Redis
    # ------------------------------------------------------------------

    REDIS_URL: Optional[str] = None

    # ------------------------------------------------------------------
    # Notifications
    # ------------------------------------------------------------------

    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None

    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None

    WHATSAPP_API_KEY: Optional[str] = None

    # ------------------------------------------------------------------
    # Edge AI Gateway
    # ------------------------------------------------------------------

    EDGE_AI_GATEWAY_URL: Optional[str] = None

    # ------------------------------------------------------------------
    # Validators
    # ------------------------------------------------------------------

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, value: str) -> str:
        """
        Ensure the database URL uses an async driver.
        Auto-corrects postgresql:// to postgresql+asyncpg://.
        """
        if value.startswith("postgresql://"):
            value = value.replace("postgresql://", "postgresql+asyncpg://", 1)

        valid_prefixes = ("postgresql+asyncpg://", "sqlite+aiosqlite://")
        if not any(value.startswith(prefix) for prefix in valid_prefixes):
            # Fallback to local SQLite if invalid or empty
            value = "sqlite+aiosqlite:///./technify_visionai.db"

        return value

    @field_validator("SUPABASE_URL")
    @classmethod
    def validate_supabase_url(cls, value: str) -> str:
        """
        Validate the Supabase project URL.
        """
        if not value or not (value.startswith("http://") or value.startswith("https://")):
            return "https://ziojazjvsjtzcqdckajq.supabase.co"

        return value.rstrip("/")

    @field_validator("SUPABASE_JWT_ALGORITHM")
    @classmethod
    def validate_jwt_algorithm(cls, value: str) -> str:
        value = value.upper()
        allowed_algorithms = {"ES256", "RS256", "HS256"}
        if value not in allowed_algorithms:
            return "ES256"
        return value

    @field_validator("ENVIRONMENT")
    @classmethod
    def validate_environment(cls, value: str) -> str:
        allowed_environments = {"development", "staging", "production"}
        value = value.lower()
        if value not in allowed_environments:
            return "development"
        return value

    # ------------------------------------------------------------------
    # Derived properties
    # ------------------------------------------------------------------

    @property
    def cors_origins_list(self) -> List[str]:
        return [
            origin.strip()
            for origin in self.CORS_ORIGINS.split(",")
            if origin.strip()
        ]

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"

    @property
    def supabase_jwks_url(self) -> str:
        return f"{self.SUPABASE_URL}/auth/v1/.well-known/jwks.json"

    @property
    def supabase_jwt_issuer(self) -> str:
        return f"{self.SUPABASE_URL}/auth/v1"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
