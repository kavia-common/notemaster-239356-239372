from __future__ import annotations

from functools import lru_cache
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # CORS / frontend integration
    frontend_origins: str = Field(
        default="http://localhost:3000",
        validation_alias="FRONTEND_ORIGINS",
        description="Comma-separated list of allowed origins for CORS.",
    )

    # Database
    database_url: Optional[str] = Field(
        default=None,
        validation_alias="DATABASE_URL",
        description="Full SQLAlchemy database URL. If unset, built from POSTGRES_* vars.",
    )

    postgres_url: str = Field(default="localhost", validation_alias="POSTGRES_URL")
    postgres_user: str = Field(default="appuser", validation_alias="POSTGRES_USER")
    postgres_password: str = Field(default="dbuser123", validation_alias="POSTGRES_PASSWORD")
    postgres_db: str = Field(default="myapp", validation_alias="POSTGRES_DB")
    postgres_port: int = Field(default=5000, validation_alias="POSTGRES_PORT")

    # Pagination
    default_page_size: int = Field(default=50, validation_alias="DEFAULT_PAGE_SIZE")
    max_page_size: int = Field(default=200, validation_alias="MAX_PAGE_SIZE")

    def allowed_origins(self) -> List[str]:
        """Return parsed CORS origins list."""
        return [o.strip() for o in self.frontend_origins.split(",") if o.strip()]

    def sqlalchemy_database_uri(self) -> str:
        """Return a SQLAlchemy-compatible database URI."""
        if self.database_url:
            return self.database_url

        # Build a URL compatible with SQLAlchemy.
        # Using psycopg2 driver per requirements (psycopg2-binary).
        return (
            f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_url}:{self.postgres_port}/{self.postgres_db}"
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached Settings instance."""
    return Settings()
