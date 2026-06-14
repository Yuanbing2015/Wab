"""健康检查端点"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": "wab-api", "version": "0.1.0"}
