"""TTS 朗读服务（edge-tts + MinIO 缓存）

接口：
- normalize_for_speech  数学符号 → 中文读法
- synthesize  合成 + 缓存 + 返回 URL
"""
import hashlib
import io
import re

import edge_tts

from src.core.config import settings
from src.services.storage import (
    upload_bytes,
    public_url,
    stat_exists,
)


# ---------- 朗读规范化（基础规则版，S3-2 完整版会扩） ----------
_BASIC_RULES: list[tuple[str, str]] = [
    ("²", " 的平方 "),
    ("³", " 的立方 "),
    ("√", " 根号 "),
    ("∠", " 角 "),
    ("π", " 派 "),
    ("×", " 乘以 "),
    ("÷", " 除以 "),
    ("≠", " 不等于 "),
    ("≥", " 大于等于 "),
    ("≤", " 小于等于 "),
    ("=", " 等于 "),
    ("+", " 加 "),
    ("-", " 减 "),
]

# 分数 a/b → "b 分之 a"（仅纯数字）
_FRACTION_RE = re.compile(r"(\d+)\s*/\s*(\d+)")


def normalize_for_speech(text: str) -> str:
    """把题干文本转成 TTS 友好的纯中文。"""
    if not text:
        return text
    # 分数（先处理，避免被 "+" "-" 干扰）
    text = _FRACTION_RE.sub(lambda m: f" {m.group(2)} 分之 {m.group(1)} ", text)
    # 符号替换
    for src, dst in _BASIC_RULES:
        text = text.replace(src, dst)
    # 连续空白合并
    text = re.sub(r"\s+", " ", text).strip()
    return text


# ---------- 合成 ----------
def _cache_key(text: str, voice: str, rate: str) -> str:
    raw = f"{text}|{voice}|{rate}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


async def synthesize(
    text: str,
    voice: str | None = None,
    rate: str | None = None,
) -> str:
    """合成 MP3 → 缓存到 MinIO → 返回公开访问 URL。

    缓存命中：直接返回 URL，无网络合成。
    """
    voice = voice or settings.tts_default_voice
    rate = rate or settings.tts_default_rate

    spoken = normalize_for_speech(text)
    key = _cache_key(spoken, voice, rate)
    object_key = f"{key}.mp3"
    bucket = settings.minio_bucket_tts

    # 缓存命中
    if stat_exists(bucket, object_key):
        return public_url(bucket, object_key)

    # 调用 edge-tts
    communicate = edge_tts.Communicate(spoken, voice, rate=rate)
    buf = io.BytesIO()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            buf.write(chunk["data"])

    data = buf.getvalue()
    if not data:
        raise RuntimeError("edge-tts 返回空音频")

    return upload_bytes(bucket, object_key, data, content_type="audio/mpeg")
