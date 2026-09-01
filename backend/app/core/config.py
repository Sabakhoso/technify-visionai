
"""
Centralized application configuration.

Technify VisionAI + Supabase ES256

All values are loaded from environment variables (.env locally,
real environment variables in production/CI).

Supabase uses ES256 asymmetric JWT signing in this project.
Therefore, this configuration does NOT require SUPABASE_JWT_SECRET.

JWT verification will use Supabase's public JWKS endpoint.
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
        ...,
        description="Supabase project URL",
    )

    SUPABASE_ANON_KEY: str = Field(
        ...,
        description="Supabase publishable/anon key",
    )

    SUPABASE_SERVICE_ROLE_KEY: str = Field(
        ...,
        description="Supabase secret/service_role key for backend operations",
    )

    # ------------------------------------------------------------------
    # Supabase JWT
    # ------------------------------------------------------------------
    #
    # Your Supabase project uses ES256.
    #
    # ES256 is asymmetric JWT signing, so the backend does NOT need
    # the legacy SUPABASE_JWT_SECRET.
    #
    # JWT verification will use the public JWKS endpoint.
    # ------------------------------------------------------------------

    SUPABASE_JWT_ALGORITHM: str = Field(
        default="ES256",
        description="Supabase JWT signing algorithm",
    )

    # ------------------------------------------------------------------
    # Database
    # ------------------------------------------------------------------

    DATABASE_URL: str = Field(
        ...,
        description=(
            "Async PostgreSQL connection string for SQLAlchemy. "
            "Expected format: postgresql+asyncpg://..."
        ),
    )

    # ------------------------------------------------------------------
    # Application Security
    # ------------------------------------------------------------------

    SECRET_KEY: str = Field(
        ...,
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

    # Example:
    #
    # CORS_ORIGINS=http://localhost:3000,http://localhost:5173
    #

    CORS_ORIGINS: str = "http://localhost:3000"

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
        Ensure the database URL uses the async PostgreSQL driver.
        """

        if not value.startswith("postgresql+asyncpg://"):
            raise ValueError(
                "DATABASE_URL must use the "
                "'postgresql+asyncpg://' scheme for the async "
                "SQLAlchemy engine."
            )

        return value

    @field_validator("SUPABASE_URL")
    @classmethod
    def validate_supabase_url(cls, value: str) -> str:
        """
        Validate the Supabase project URL.
        """

        if not value.startswith("https://") or ".supabase.co" not in value:
            raise ValueError(
                "SUPABASE_URL looks malformed. Expected format: "
                "https://<project-ref>.supabase.co"
            )

        return value.rstrip("/")

    @field_validator("SUPABASE_JWT_ALGORITHM")
    @classmethod
    def validate_jwt_algorithm(cls, value: str) -> str:
        """
        Validate the Supabase JWT signing algorithm.
        """

        value = value.upper()

        allowed_algorithms = {
            "ES256",
            "RS256",
            "HS256",
        }

        if value not in allowed_algorithms:
            raise ValueError(
                "SUPABASE_JWT_ALGORITHM must be one of "
                f"{allowed_algorithms}, got '{value}'"
            )

        return value

    @field_validator("ENVIRONMENT")
    @classmethod
    def validate_environment(cls, value: str) -> str:
        """
        Validate the application environment.
        """

        allowed_environments = {
            "development",
            "staging",
            "production",
        }

        value = value.lower()

        if value not in allowed_environments:
            raise ValueError(
                "ENVIRONMENT must be one of "
                f"{allowed_environments}, got '{value}'"
            )

        return value

    # ------------------------------------------------------------------
    # Derived properties
    # ------------------------------------------------------------------

    @property
    def cors_origins_list(self) -> List[str]:
        """
        Convert comma-separated CORS origins into a list.
        """

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
        """
        Public Supabase JWKS endpoint used for asymmetric JWT
        signature verification.
        """

        return (
            f"{self.SUPABASE_URL}"
            "/auth/v1/.well-known/jwks.json"
        )

    @property
    def supabase_jwt_issuer(self) -> str:
        """
        Expected issuer for Supabase Auth JWTs.
        """

        return f"{self.SUPABASE_URL}/auth/v1"

    # ------------------------------------------------------------------
    # Pydantic Settings Configuration
    # ------------------------------------------------------------------

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


# ----------------------------------------------------------------------
# Cached settings loader
# ----------------------------------------------------------------------

@lru_cache
def get_settings() -> Settings:
    """
    Load and validate settings once per process.
    """

    return Settings()

@property
def supabase_jwks_url(self) -> str:
    """Supabase JWKS endpoint used to verify ES256 JWTs."""
    return f"{self.SUPABASE_URL}/auth/v1/.well-known/jwks.json"


# ----------------------------------------------------------------------
# Module-level settings instance
# ----------------------------------------------------------------------

settings = get_settings()
