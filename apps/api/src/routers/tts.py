"""TTS 朗读路由（S3-1）"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from src.core.security import get_current_user_id
from src.services import tts

router = APIRouter()


class TTSRequest(BaseModel):
    text: str
    voice: str | None = None
    rate: str | None = None


class TTSResponse(BaseModel):
    url: str


@router.post("/synthesize", response_model=TTSResponse)
async def synthesize(
    data: TTSRequest,
    _user_id: int = Depends(get_current_user_id),
):
    url = await tts.synthesize(data.text, voice=data.voice, rate=data.rate)
    return TTSResponse(url=url)
