import os
from typing import List

from pydantic import BaseModel, Field


def _split_csv(value: str | None) -> List[str]:
    if not value:
        return []
    return [part.strip() for part in value.split(",") if part.strip()]


class Settings(BaseModel):
    app_name: str = "Fin Scenario Map API"
    environment: str = Field(default="dev", description="Environment name (dev/test/prod)")

    # Database
    database_url: str = Field(
        default="postgresql://localhost/fin_scenario_map",
        description="PostgreSQL connection URL",
    )

    # CORS
    cors_allow_origins: List[str] = Field(
        default_factory=lambda: ["http://localhost:5173", "http://127.0.0.1:5173"]
    )
    cors_allow_origin_regex: str = r"^http://(localhost|127\.0\.0\.1)(:\d+)?$"

    # Upload validation
    max_upload_size_bytes: int = 5 * 1024 * 1024
    allowed_upload_content_types: List[str] = Field(
        default_factory=lambda: ["text/csv", "application/pdf", "application/json"]
    )


def get_settings() -> Settings:
    """
    Minimal env-based settings (no extra dependency like pydantic-settings).

    Supported env vars:
    - APP_NAME
    - ENVIRONMENT
    - DATABASE_URL
    - CORS_ALLOW_ORIGINS (comma-separated)
    - MAX_UPLOAD_SIZE_BYTES
    - ALLOWED_UPLOAD_CONTENT_TYPES (comma-separated)
    """
    database_url = os.getenv("DATABASE_URL") or Settings().database_url
    cors = _split_csv(os.getenv("CORS_ALLOW_ORIGINS"))
    allowed_types = _split_csv(os.getenv("ALLOWED_UPLOAD_CONTENT_TYPES"))

    max_upload_raw = os.getenv("MAX_UPLOAD_SIZE_BYTES")
    max_upload_size = int(max_upload_raw) if max_upload_raw and max_upload_raw.isdigit() else None

    return Settings(
        app_name=os.getenv("APP_NAME") or Settings().app_name,
        environment=os.getenv("ENVIRONMENT") or Settings().environment,
        database_url=database_url,
        cors_allow_origins=cors or Settings().cors_allow_origins,
        max_upload_size_bytes=max_upload_size or Settings().max_upload_size_bytes,
        allowed_upload_content_types=allowed_types or Settings().allowed_upload_content_types,
    )

