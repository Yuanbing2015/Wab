"""InterestTag 模型：单独表存储孩子兴趣标签

虽然 User.interest_tags 已用 JSONB 存了一份（便于读取），
但这里再建独立表是为了：
- 跨用户聚合分析（哪类兴趣最常用）
- 未来标签管理 UI 的查询/筛选
"""
from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field


class InterestTag(SQLModel, table=True):
    __tablename__ = "interest_tags"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    tag: str = Field(max_length=64)
    weight: int = Field(default=5, ge=1, le=10)
    created_at: datetime = Field(default_factory=datetime.utcnow)
