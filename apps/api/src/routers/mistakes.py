"""错题录入与管理路由（Sprint 2）

流程：
1. POST /mistakes/recognize      上传图片 → AI 识别 → 返回草稿（不入库）
2. POST /mistakes                确认/编辑后入库
3. GET  /mistakes                列表（多维筛选）
4. GET  /mistakes/{id}           详情
5. PUT  /mistakes/{id}           编辑
6. DELETE /mistakes/{id}         删除
7. POST /mistakes/{id}/solution-hint   生成/补充解题思路
"""
import uuid
from datetime import datetime, date, timezone

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from pydantic import BaseModel
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.database import get_session
from src.core.config import settings
from src.core.security import get_current_user_id
from src.models.user import User
from src.models.mistake import (
    Mistake,
    MistakeImage,
    ErrorTag,
    MistakeTag,
    SolutionHint,
)
from src.services import llm_vision, llm_text, tts, storage

router = APIRouter()


# ============================================================
# DTO
# ============================================================
class RecognizeResult(BaseModel):
    subject: str = "数学"
    grade_guess: str | None = None
    question_type: str | None = None
    stem: str = ""
    options: list = []
    correct_answer: str | None = None
    child_answer: str | None = None
    auto_tags: list[str] = []
    error_hypothesis: str | None = None
    solution_hint_draft: str | None = None
    # 已上传的图片 object key（确认入库时带回）
    image_object_key: str | None = None


class CreateMistakeRequest(BaseModel):
    subject: str
    question_type: str | None = None
    stem_text: str
    options: list = []
    correct_answer: str | None = None
    child_answer: str | None = None
    grade: int | None = None
    occurred_at: date | None = None
    error_tags: list[str] = []
    custom_tags: list[str] = []
    solution_hint: str | None = None
    solution_url: str | None = None
    image_object_keys: list[str] = []
    is_golden: bool = False


class MistakeDTO(BaseModel):
    id: int
    subject: str
    question_type: str | None
    stem_text: str
    options: list
    correct_answer: str | None
    child_answer: str | None
    grade: int | None
    error_hypothesis: str | None
    mastery_score: float
    is_golden: bool
    status: str
    error_tags: list[str] = []
    custom_tags: list[str] = []
    image_urls: list[str] = []
    created_at: datetime


# ============================================================
# 1. 上传图片 + 识别（不入库）
# ============================================================
@router.post("/recognize", response_model=RecognizeResult)
async def recognize(
    file: UploadFile = File(...),
    grade_hint: str | None = Form(default=None),
    user_id: int = Depends(get_current_user_id),
):
    image_bytes = await file.read()
    if len(image_bytes) > 30 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="图片不能超过 30MB")

    # 先把原图存进 MinIO（双轨存储原则 D-13）
    ext = (file.filename or "img.jpg").rsplit(".", 1)[-1].lower()
    today = datetime.now(timezone.utc)
    object_key = f"uploads/{user_id}/{today:%Y/%m}/{uuid.uuid4().hex}.{ext}"
    storage.upload_bytes(
        settings.minio_bucket_uploads,
        object_key,
        image_bytes,
        content_type=file.content_type or "image/jpeg",
    )

    # AI 识别（DeepSeek 失败自动切 Qwen 兜底）
    try:
        data = await llm_vision.extract_mistake_from_image(image_bytes, grade_hint)
    except Exception:
        if settings.qwen_api_key:
            data = await llm_vision.extract_mistake_from_image(
                image_bytes, grade_hint, use_fallback=True
            )
        else:
            raise HTTPException(status_code=502, detail="AI 识别失败，请重试或检查 API 配置")

    return RecognizeResult(image_object_key=object_key, **{
        k: data.get(k) for k in RecognizeResult.model_fields if k != "image_object_key"
    })


# ============================================================
# 2. 确认入库
# ============================================================
@router.post("", response_model=MistakeDTO, status_code=201)
async def create_mistake(
    data: CreateMistakeRequest,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
):
    mistake = Mistake(
        user_id=user_id,
        subject=data.subject,
        question_type=data.question_type,
        stem_text=data.stem_text,
        stem_normalized=tts.normalize_for_speech(data.stem_text),
        options=data.options,
        correct_answer=data.correct_answer,
        child_answer=data.child_answer,
        grade=data.grade,
        occurred_at=data.occurred_at,
        is_golden=data.is_golden,
        status="confirmed",
    )
    session.add(mistake)
    await session.flush()  # 拿到 mistake.id

    for tag in data.error_tags:
        session.add(ErrorTag(mistake_id=mistake.id, tag=tag, source="parent"))
    for tag in data.custom_tags:
        session.add(MistakeTag(mistake_id=mistake.id, tag=tag))
    if data.solution_hint or data.solution_url:
        session.add(SolutionHint(
            mistake_id=mistake.id,
            content_md=data.solution_hint or "",
            url=data.solution_url,
            source="url" if data.solution_url else "parent",
        ))
    for i, key in enumerate(data.image_object_keys):
        session.add(MistakeImage(mistake_id=mistake.id, object_key=key, order=i))

    await session.commit()
    await session.refresh(mistake)
    return await _to_dto(mistake, session)


# ============================================================
# 3. 列表
# ============================================================
@router.get("", response_model=list[MistakeDTO])
async def list_mistakes(
    subject: str | None = Query(default=None),
    grade: int | None = Query(default=None),
    keyword: str | None = Query(default=None),
    is_golden: bool | None = Query(default=None),
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0),
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
):
    stmt = select(Mistake).where(Mistake.user_id == user_id)
    if subject:
        stmt = stmt.where(Mistake.subject == subject)
    if grade is not None:
        stmt = stmt.where(Mistake.grade == grade)
    if is_golden is not None:
        stmt = stmt.where(Mistake.is_golden == is_golden)
    if keyword:
        stmt = stmt.where(Mistake.stem_text.ilike(f"%{keyword}%"))
    stmt = stmt.order_by(Mistake.created_at.desc()).limit(limit).offset(offset)

    result = await session.execute(stmt)
    mistakes = result.scalars().all()
    return [await _to_dto(m, session) for m in mistakes]


# ============================================================
# 4. 详情
# ============================================================
@router.get("/{mistake_id}", response_model=MistakeDTO)
async def get_mistake(
    mistake_id: int,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
):
    mistake = await _owned_or_404(mistake_id, user_id, session)
    return await _to_dto(mistake, session)


# ============================================================
# 5. 编辑
# ============================================================
class UpdateMistakeRequest(BaseModel):
    subject: str | None = None
    question_type: str | None = None
    stem_text: str | None = None
    correct_answer: str | None = None
    child_answer: str | None = None
    grade: int | None = None
    is_golden: bool | None = None
    error_tags: list[str] | None = None
    custom_tags: list[str] | None = None


@router.put("/{mistake_id}", response_model=MistakeDTO)
async def update_mistake(
    mistake_id: int,
    data: UpdateMistakeRequest,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
):
    mistake = await _owned_or_404(mistake_id, user_id, session)

    for field in ("subject", "question_type", "correct_answer", "child_answer", "grade", "is_golden"):
        val = getattr(data, field)
        if val is not None:
            setattr(mistake, field, val)
    if data.stem_text is not None:
        mistake.stem_text = data.stem_text
        mistake.stem_normalized = tts.normalize_for_speech(data.stem_text)
    mistake.updated_at = datetime.utcnow()

    # 替换标签（全删全建，简单可靠）
    if data.error_tags is not None:
        await _replace_tags(session, ErrorTag, mistake_id, data.error_tags, source="parent")
    if data.custom_tags is not None:
        await _replace_tags(session, MistakeTag, mistake_id, data.custom_tags)

    await session.commit()
    await session.refresh(mistake)
    return await _to_dto(mistake, session)


# ============================================================
# 6. 删除
# ============================================================
@router.delete("/{mistake_id}", status_code=204)
async def delete_mistake(
    mistake_id: int,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
):
    mistake = await _owned_or_404(mistake_id, user_id, session)
    await session.delete(mistake)
    await session.commit()


# ============================================================
# 7. AI 生成解题思路
# ============================================================
@router.post("/{mistake_id}/solution-hint", response_model=dict)
async def gen_solution_hint(
    mistake_id: int,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
):
    mistake = await _owned_or_404(mistake_id, user_id, session)
    content = await llm_text.generate_solution_hint(
        mistake.stem_text, mistake.correct_answer or "", mistake.grade or 1
    )
    hint = SolutionHint(mistake_id=mistake_id, content_md=content, source="ai")
    session.add(hint)
    await session.commit()
    return {"content_md": content}


# ============================================================
# 内部工具
# ============================================================
async def _owned_or_404(mistake_id: int, user_id: int, session: AsyncSession) -> Mistake:
    mistake = await session.get(Mistake, mistake_id)
    if not mistake or mistake.user_id != user_id:
        raise HTTPException(status_code=404, detail="错题不存在")
    return mistake


async def _replace_tags(session, model, mistake_id: int, tags: list[str], source: str | None = None):
    existing = await session.execute(select(model).where(model.mistake_id == mistake_id))
    for row in existing.scalars().all():
        await session.delete(row)
    for tag in tags:
        kwargs = {"mistake_id": mistake_id, "tag": tag}
        if source and hasattr(model, "source"):
            kwargs["source"] = source
        session.add(model(**kwargs))


async def _to_dto(mistake: Mistake, session: AsyncSession) -> MistakeDTO:
    err = await session.execute(select(ErrorTag).where(ErrorTag.mistake_id == mistake.id))
    cus = await session.execute(select(MistakeTag).where(MistakeTag.mistake_id == mistake.id))
    imgs = await session.execute(select(MistakeImage).where(MistakeImage.mistake_id == mistake.id))
    return MistakeDTO(
        id=mistake.id,
        subject=mistake.subject,
        question_type=mistake.question_type,
        stem_text=mistake.stem_text,
        options=mistake.options or [],
        correct_answer=mistake.correct_answer,
        child_answer=mistake.child_answer,
        grade=mistake.grade,
        error_hypothesis=mistake.error_hypothesis,
        mastery_score=mistake.mastery_score,
        is_golden=mistake.is_golden,
        status=mistake.status,
        error_tags=[t.tag for t in err.scalars().all()],
        custom_tags=[t.tag for t in cus.scalars().all()],
        image_urls=[
            storage.public_url(settings.minio_bucket_uploads, img.object_key)
            for img in imgs.scalars().all()
        ],
        created_at=mistake.created_at,
    )
