import boto3
import os
import uuid
import requests
from typing import Optional
from ..config import settings

def _s3():
    if not (settings.CLOUDFLARE_ACCOUNT_ID and settings.CLOUDFLARE_R2_ACCESS_KEY_ID and settings.CLOUDFLARE_R2_SECRET_ACCESS_KEY):
        raise RuntimeError("Cloudflare R2 credentials are not fully configured")
    endpoint = f"https://{settings.CLOUDFLARE_ACCOUNT_ID}.r2.cloudflarestorage.com"
    return boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=settings.CLOUDFLARE_R2_ACCESS_KEY_ID,
        aws_secret_access_key=settings.CLOUDFLARE_R2_SECRET_ACCESS_KEY,
        region_name="auto"
    )

def _public_url(key: str) -> str:
    if settings.CLOUDFLARE_R2_PUBLIC_BASE_URL:
        base = settings.CLOUDFLARE_R2_PUBLIC_BASE_URL.rstrip("/")
        return f"{base}/{key}"
    # Fallback basic public URL (requires public bucket or signed URLs)
    return f"https://{settings.CLOUDFLARE_R2_BUCKET_NAME}.{settings.CLOUDFLARE_ACCOUNT_ID}.r2.cloudflarestorage.com/{key}"

def upload_bytes(data: bytes, content_type: str, prefix: str = "generated/") -> str:
    key = f"{prefix}{uuid.uuid4().hex}"
    s3 = _s3()
    s3.put_object(Bucket=settings.CLOUDFLARE_R2_BUCKET_NAME, Key=key, Body=data, ContentType=content_type, ACL="public-read")
    return _public_url(key)

def upload_from_url(url: str, content_type: Optional[str] = None, prefix: str = "generated/") -> str:
    resp = requests.get(url, stream=True, timeout=120)
    resp.raise_for_status()
    ct = content_type or resp.headers.get("Content-Type", "application/octet-stream")
    return upload_bytes(resp.content, ct, prefix=prefix)