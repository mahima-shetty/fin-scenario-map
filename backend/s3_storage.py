"""S3-compatible storage for uploaded files. No-op if S3 not configured."""
import uuid
from datetime import datetime


def _get_client():
    """Return boto3 S3 client or None if config missing."""
    try:
        from .settings import get_settings
        s = get_settings()
        if not s.s3_bucket or not s.s3_access_key or not s.s3_secret_key:
            return None
        import boto3
        from botocore.config import Config
        config = Config(signature_version="s3v4")
        kwargs = {
            "service_name": "s3",
            "aws_access_key_id": s.s3_access_key,
            "aws_secret_access_key": s.s3_secret_key,
            "region_name": s.s3_region or "us-east-1",
            "config": config,
        }
        if s.s3_endpoint_url:
            kwargs["endpoint_url"] = s.s3_endpoint_url
        if getattr(s, "s3_use_path_style", False):
            config = Config(signature_version="s3v4", s3={"addressing_style": "path"})
            kwargs["config"] = config
        return boto3.client(**kwargs)
    except Exception:
        return None


def upload_file(body: bytes, filename: str, content_type: str | None) -> str | None:
    """Upload bytes to S3. Key: uploads/YYYY/MM/dd/uuid_filename. Returns object key or None."""
    client = _get_client()
    if not client:
        return None
    try:
        from .settings import get_settings
        bucket = get_settings().s3_bucket
        now = datetime.utcnow()
        safe_name = (filename or "upload").replace(" ", "_")
        key = f"uploads/{now.year}/{now.month:02d}/{now.day:02d}/{uuid.uuid4().hex}_{safe_name}"
        extra = {}
        if content_type:
            extra["ContentType"] = content_type
        client.put_object(Bucket=bucket, Key=key, Body=body, **extra)
        return key
    except Exception:
        return None


def get_presigned_download_url(object_key: str, expires_in: int = 3600) -> str | None:
    """Return presigned URL for GET, or None."""
    client = _get_client()
    if not client:
        return None
    try:
        from .settings import get_settings
        bucket = get_settings().s3_bucket
        return client.generate_presigned_url(
            "get_object", Params={"Bucket": bucket, "Key": object_key}, ExpiresIn=expires_in
        )
    except Exception:
        return None
