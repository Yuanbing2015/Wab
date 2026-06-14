"""MinIO 对象存储 — 上传下载 + presigned URL

约定：
- bucket = settings.minio_bucket_xxx
- object_key = 业务路径，如 'uploads/2026/05/abc.jpg' / 'tts/{hash}.mp3'
- 前端直传：服务端签 PUT URL，前端用 fetch(url, {method:'PUT', body:file})
- 公开访问：通过 nginx 反代 /files/{bucket}/{key} 静态展示
"""
from datetime import timedelta
from typing import BinaryIO

from minio import Minio

from src.core.config import settings


_client: Minio | None = None


def get_client() -> Minio:
    global _client
    if _client is None:
        _client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_root_user,
            secret_key=settings.minio_root_password,
            secure=settings.minio_use_ssl,
        )
    return _client


def presigned_put(bucket: str, object_key: str, expires_minutes: int = 30) -> str:
    """前端直传 URL（PUT method）。"""
    return get_client().presigned_put_object(
        bucket, object_key, expires=timedelta(minutes=expires_minutes)
    )


def presigned_get(bucket: str, object_key: str, expires_minutes: int = 60) -> str:
    """临时下载 URL（GET method）。"""
    return get_client().presigned_get_object(
        bucket, object_key, expires=timedelta(minutes=expires_minutes)
    )


def public_url(bucket: str, object_key: str) -> str:
    """通过 nginx /files/ 反代访问的公开 URL（仅静态资源使用）。"""
    return f"{settings.minio_public_endpoint}/{bucket}/{object_key}"


def upload_bytes(
    bucket: str,
    object_key: str,
    data: bytes,
    content_type: str = "application/octet-stream",
) -> str:
    """服务端直接上传字节流（如 TTS 合成结果），返回 public URL。"""
    import io

    get_client().put_object(
        bucket,
        object_key,
        io.BytesIO(data),
        length=len(data),
        content_type=content_type,
    )
    return public_url(bucket, object_key)


def stat_exists(bucket: str, object_key: str) -> bool:
    """对象是否已存在（用于缓存命中检查）。"""
    try:
        get_client().stat_object(bucket, object_key)
        return True
    except Exception:
        return False
