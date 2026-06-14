"""认证路由：注册 + 登录"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from src.core.database import get_session
from src.core.security import (
    create_access_token,
    hash_password,
    verify_password,
    get_current_user_id,
)
from src.models.user import User

router = APIRouter()


# ---------- DTO ----------
class LoginRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=64)
    password: str = Field(..., min_length=1, max_length=128)


class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=64)
    password: str = Field(..., min_length=4, max_length=128)
    role: str = Field(default="kid", pattern="^(kid|parent)$")
    current_grade: str | None = Field(default=None, max_length=32)
    theme: str | None = Field(default="default", max_length=64)


class UserDTO(BaseModel):
    id: int
    name: str
    role: str
    theme: str | None
    current_grade: str | None


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserDTO


# ---------- 端点 ----------
@router.post("/register", response_model=LoginResponse, status_code=201)
async def register(
    data: RegisterRequest, session: AsyncSession = Depends(get_session)
):
    existing = await session.execute(select(User).where(User.name == data.name))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="用户名已存在")

    user = User(
        name=data.name,
        password_hash=hash_password(data.password),
        role=data.role,
        current_grade=data.current_grade,
        theme=data.theme or "default",
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)

    token = create_access_token(user.id, extra={"name": user.name, "role": user.role})
    return LoginResponse(
        access_token=token,
        user=UserDTO(
            id=user.id,
            name=user.name,
            role=user.role,
            theme=user.theme,
            current_grade=user.current_grade,
        ),
    )


@router.post("/login", response_model=LoginResponse)
async def login(data: LoginRequest, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(User).where(User.name == data.name))
    user = result.scalar_one_or_none()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="账号或密码错误"
        )
    token = create_access_token(user.id, extra={"name": user.name, "role": user.role})
    return LoginResponse(
        access_token=token,
        user=UserDTO(
            id=user.id,
            name=user.name,
            role=user.role,
            theme=user.theme,
            current_grade=user.current_grade,
        ),
    )


@router.get("/me", response_model=UserDTO)
async def me(
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
):
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return UserDTO(
        id=user.id,
        name=user.name,
        role=user.role,
        theme=user.theme,
        current_grade=user.current_grade,
    )
