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

    # Groq (recommendation engine)
    groq_api_key: str = Field(default="", description="Groq API key for AI-generated recommendations")

    # JWT authentication
    jwt_secret_key: str = Field(default="change-me-in-production", description="Secret for signing JWTs")
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")
    jwt_access_token_expire_minutes: int = Field(default=60 * 24, description="Access token expiry in minutes")

    # Encryption at rest (PRD FR9 – AES-256). Base64-encoded 32-byte key; empty = no encryption.
    data_encryption_key: str = Field(default="", description="Base64-encoded 32-byte key for AES-256-GCM at rest")

    # S3-compatible storage for uploads (Tech). Use ACCESS_KEY/SECRET_ACCESS_KEY or S3_ACCESS_KEY/S3_SECRET_KEY.
    s3_endpoint_url: str = Field(default="", description="S3 endpoint; empty for AWS")
    s3_bucket: str = Field(default="fin-scenario-uploads", description="S3 bucket name")
    s3_access_key: str = Field(default="", description="S3 access key")
    s3_secret_key: str = Field(default="", description="S3 secret key")
    s3_region: str = Field(default="us-east-1", description="S3 region")
    s3_use_path_style: bool = Field(default=False, description="True for MinIO")


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
    - GROQ_API_KEY (for AI-generated recommendations)
    - JWT_SECRET_KEY, JWT_ALGORITHM, JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    - DATA_ENCRYPTION_KEY (base64 32-byte key for encryption at rest; PRD FR9)
    - S3: S3_BUCKET, S3_REGION, ACCESS_KEY, SECRET_ACCESS_KEY (or S3_ACCESS_KEY, S3_SECRET_KEY); optional S3_ENDPOINT_URL, S3_USE_PATH_STYLE
    - In transit: use HTTPS/TLS in production (deployment concern).
    """
    database_url = os.getenv("DATABASE_URL") or Settings().database_url
    cors = _split_csv(os.getenv("CORS_ALLOW_ORIGINS"))
    allowed_types = _split_csv(os.getenv("ALLOWED_UPLOAD_CONTENT_TYPES"))

    max_upload_raw = os.getenv("MAX_UPLOAD_SIZE_BYTES")
    max_upload_size = int(max_upload_raw) if max_upload_raw and max_upload_raw.isdigit() else None

    groq_api_key = (os.getenv("GROQ_API_KEY") or "").strip()
    jwt_secret_key = (os.getenv("JWT_SECRET_KEY") or "").strip() or Settings().jwt_secret_key
    jwt_algorithm = (os.getenv("JWT_ALGORITHM") or "").strip() or Settings().jwt_algorithm
    jwt_expire = os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
    jwt_access_token_expire_minutes = int(jwt_expire) if jwt_expire and jwt_expire.isdigit() else Settings().jwt_access_token_expire_minutes
    data_encryption_key = (os.getenv("DATA_ENCRYPTION_KEY") or "").strip()
    s3_endpoint_url = (os.getenv("S3_ENDPOINT_URL") or "").strip()
    s3_bucket = (os.getenv("S3_BUCKET") or "").strip() or "fin-scenario-uploads"
    s3_access_key = (os.getenv("S3_ACCESS_KEY") or os.getenv("ACCESS_KEY") or "").strip()
    s3_secret_key = (os.getenv("S3_SECRET_KEY") or os.getenv("SECRET_ACCESS_KEY") or "").strip()
    s3_region = (os.getenv("S3_REGION") or "").strip() or "us-east-1"
    s3_use_path_style = (os.getenv("S3_USE_PATH_STYLE") or "").lower() in ("1", "true", "yes")

    return Settings(
        app_name=os.getenv("APP_NAME") or Settings().app_name,
        environment=os.getenv("ENVIRONMENT") or Settings().environment,
        database_url=database_url,
        cors_allow_origins=cors or Settings().cors_allow_origins,
        max_upload_size_bytes=max_upload_size or Settings().max_upload_size_bytes,
        allowed_upload_content_types=allowed_types or Settings().allowed_upload_content_types,
        groq_api_key=groq_api_key,
        jwt_secret_key=jwt_secret_key,
        jwt_algorithm=jwt_algorithm,
        jwt_access_token_expire_minutes=jwt_access_token_expire_minutes,
        data_encryption_key=data_encryption_key or Settings().data_encryption_key,
        s3_endpoint_url=s3_endpoint_url or Settings().s3_endpoint_url,
        s3_bucket=s3_bucket,
        s3_access_key=s3_access_key or Settings().s3_access_key,
        s3_secret_key=s3_secret_key or Settings().s3_secret_key,
        s3_region=s3_region or Settings().s3_region,
        s3_use_path_style=s3_use_path_style,
    )

