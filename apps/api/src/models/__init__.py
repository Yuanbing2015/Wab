"""统一导出所有 SQLModel 模型，供 Alembic autogenerate / 应用代码引用"""
from src.models.user import User
from src.models.interest_tag import InterestTag
from src.models.mistake import (
    Mistake,
    MistakeImage,
    ErrorTag,
    MistakeTag,
    SolutionHint,
)

__all__ = [
    "User",
    "InterestTag",
    "Mistake",
    "MistakeImage",
    "ErrorTag",
    "MistakeTag",
    "SolutionHint",
]
