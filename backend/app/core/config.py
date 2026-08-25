"""
Centralized application configuration.

All values are loaded from environment variables (.env file locally,
real environment variables in production/Docker/CI). Nothing here is
hardcoded — this file only defines *shape*, *types*, *defaults for
non-secret values*, and *validation rules*.

Secrets (API keys, DB passwords, JWT secret) must always come from
the environment and are never given fallback values here — if they're
missing, the app should fail fast at startup rather than run silently
with broken or empty credentials.
"""

from functools import lru_cache
from typing import List, Optional

from pydantic import Field, PostgresDsn, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --------------------------------------------------------------------
    # App metadata
    # --------------------------------------------------------------------
    PROJECT_NAME: str = "Technify VisionAI"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = Field(default="development")  # development | staging | production
    LOG_LEVEL: str = Field(default="INFO")  # DEBUG | INFO | WARNING | ERROR | CRITICAL

    # --------------------------------------------------------------------
    # Supabase
    # --------------------------------------------------------------------
    SUPABASE_URL: str = Field(..., description="Supabase project URL")
    SUPABASE_ANON_KEY: str = Field(..., description="Supabase publishable/anon key")
    SUPABASE_SERVICE_ROLE_KEY: str = Field(..., description="Supabase secret/service_role key")
    SUPABASE_JWT_SECRET: Optional[str] = Field(
        default=None,
        description="Supabase project JWT secret (Project Settings -> API -> JWT Secret). "
        "Required when SUPABASE_JWT_ALGORITHM is HS256; unused for asymmetric (JWKS) projects.",
    )
    SUPABASE_JWT_ALGORITHM: str = Field(
        default="HS256",
        description="HS256 for the legacy symmetric secret; RS256/ES256 for projects migrated "
        "to asymmetric signing keys (verified via the JWKS endpoint).",
    )

    # --------------------------------------------------------------------
    # Database
    # --------------------------------------------------------------------
    DATABASE_URL: str = Field(..., description="Async Postgres connection string (asyncpg driver)")

    # --------------------------------------------------------------------
    # Security / JWT
    # --------------------------------------------------------------------
    SECRET_KEY: str = Field(..., min_length=32, description="Secret used to sign JWTs")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # --------------------------------------------------------------------
    # CORS
    # --------------------------------------------------------------------
    # Comma-separated list in .env, e.g.:
    # CORS_ORIGINS=http://localhost:3000,https://app.technify-visionai.com
    CORS_ORIGINS: str = "http://localhost:3000"

    # --------------------------------------------------------------------
    # Redis (optional for now — used later for event caching/rate limiting)
    # --------------------------------------------------------------------
    REDIS_URL: Optional[str] = None

    # --------------------------------------------------------------------
    # Notifications (optional — filled in when we build alerting)
    # --------------------------------------------------------------------
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    WHATSAPP_API_KEY: Optional[str] = None

    # --------------------------------------------------------------------
    # Edge AI Gateway (optional — filled in once the edge server exists)
    # --------------------------------------------------------------------
    EDGE_AI_GATEWAY_URL: Optional[str] = None

    # --------------------------------------------------------------------
    # Validators
    # --------------------------------------------------------------------

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        if not v.startswith("postgresql+asyncpg://"):
            raise ValueError(
                "DATABASE_URL must use the 'postgresql+asyncpg://' scheme for the async "
                "SQLAlchemy engine. Supabase gives you 'postgresql://' by default — "
                "change the prefix in your .env."
            )
        return v

    @field_validator("SUPABASE_URL")
    @classmethod
    def validate_supabase_url(cls, v: str) -> str:
        if not v.startswith("https://") or ".supabase.co" not in v:
            raise ValueError(
                "SUPABASE_URL looks malformed. Expected format: "
                "https://<project-ref>.supabase.co"
            )
        return v.rstrip("/")

    @field_validator("ENVIRONMENT")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        allowed = {"development", "staging", "production"}
        v_lower = v.lower()
        if v_lower not in allowed:
            raise ValueError(f"ENVIRONMENT must be one of {allowed}, got '{v}'")
        return v_lower

    @model_validator(mode="after")
    def warn_on_weak_secret_in_production(self) -> "Settings":
        if self.ENVIRONMENT == "production" and self.SECRET_KEY.startswith("change-this"):
            raise ValueError(
                "SECRET_KEY appears to be a placeholder value. "
                "Generate a real one with: python -c \"import secrets; print(secrets.token_urlsafe(64))\""
            )
        return self

    @model_validator(mode="after")
    def require_jwt_secret_for_hs256(self) -> "Settings":
        if self.SUPABASE_JWT_ALGORITHM == "HS256" and not self.SUPABASE_JWT_SECRET:
            raise ValueError(
                "SUPABASE_JWT_SECRET is required when SUPABASE_JWT_ALGORITHM is 'HS256'. "
                "Copy it from Supabase → Project Settings → API → JWT Secret, or switch "
                "SUPABASE_JWT_ALGORITHM to RS256/ES256 if your project uses asymmetric keys."
            )
        return self

    # --------------------------------------------------------------------
    # Derived / computed properties
    # --------------------------------------------------------------------

    @property
    def cors_origins_list(self) -> List[str]:
        """Parses the comma-separated CORS_ORIGINS string into a clean list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"

    # --------------------------------------------------------------------
    # Pydantic settings config
    # --------------------------------------------------------------------
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """
    Cached settings loader.

    Using lru_cache means the .env file is only read and validated once
    per process, not on every import — this matters for performance since
    config.settings gets imported across many modules (main.py, database.py,
    every endpoint, every service).
    """
    return Settings()


# Module-level singleton — import this everywhere as `from app.core.config import settings`
settings = get_settings()