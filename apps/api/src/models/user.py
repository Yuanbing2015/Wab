"""User 模型：孩子/家长账号"""
from datetime import datetime, date
from typing import Optional, Any

from sqlmodel import SQLModel, Field, Column
from sqlalchemy.dialects.postgresql import JSONB


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=64, unique=True, index=True)
    display_avatar: Optional[str] = Field(default=None, max_length=255)
    birth_date: Optional[date] = None
    current_grade: Optional[str] = Field(default=None, max_length=32)
    # 兴趣标签 + 权重，结构示例：{"我的世界": 9, "汪汪队": 7, "鹦鹉": 5}
    interest_tags: dict[str, Any] = Field(
        default_factory=dict, sa_column=Column(JSONB, server_default="{}")
    )
    theme: Optional[str] = Field(default="default", max_length=64)
    password_hash: str = Field(max_length=128)
    # kid（孩子）/ parent（家长）
    role: str = Field(default="kid", max_length=16)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
