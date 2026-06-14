"""Mistake 及其关联模型：错题核心数据

设计依据脑暴纪要 §3.2 数据骨架：
  错题 = 原题 + 知识点 + 错因Tag + 自定义Tag + 解题思路 + 变式题 + 复习记录 + 掌握度
本文件覆盖：Mistake / MistakeImage / ErrorTag / MistakeTag / SolutionHint
（KnowledgePoint / Variant / ReviewRecord 在后续 Sprint 建表）
"""
from datetime import datetime, date
from typing import Optional, Any

from sqlmodel import SQLModel, Field, Column
from sqlalchemy.dialects.postgresql import JSONB


class Mistake(SQLModel, table=True):
    __tablename__ = "mistakes"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)

    subject: str = Field(max_length=32, index=True)          # 学科
    question_type: Optional[str] = Field(default=None, max_length=32)  # 题型
    stem_text: str = Field(default="")                       # 题干文本
    stem_normalized: Optional[str] = Field(default=None)     # 朗读化文本（TTS 用）
    options: list[Any] = Field(default_factory=list, sa_column=Column(JSONB, server_default="[]"))
    correct_answer: Optional[str] = Field(default=None)
    child_answer: Optional[str] = Field(default=None)        # 孩子的错答

    knowledge_point_id: Optional[int] = Field(default=None, index=True)
    error_hypothesis: Optional[str] = Field(default=None)    # AI 错因猜测
    grade: Optional[int] = Field(default=None, index=True)   # 年级数字 1-12
    occurred_at: Optional[date] = None                       # 做错日期

    # FSRS 状态（S4-1 接入），结构见 services/srs.py::init_card_state
    srs_state: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSONB, server_default="{}"))
    mastery_score: float = Field(default=0.0)                # 掌握度 0-1
    is_golden: bool = Field(default=False)                   # 金牌题/高光题

    # 录入状态：draft（AI 识别待确认）/ confirmed（家长已确认）
    status: str = Field(default="draft", max_length=16, index=True)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class MistakeImage(SQLModel, table=True):
    __tablename__ = "mistake_images"

    id: Optional[int] = Field(default=None, primary_key=True)
    mistake_id: int = Field(foreign_key="mistakes.id", index=True)
    object_key: str = Field(max_length=512)                  # MinIO object key
    image_type: str = Field(default="original", max_length=32)  # original/geometry/annotation
    order: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ErrorTag(SQLModel, table=True):
    __tablename__ = "error_tags"

    id: Optional[int] = Field(default=None, primary_key=True)
    mistake_id: int = Field(foreign_key="mistakes.id", index=True)
    tag: str = Field(max_length=64)                          # 如"进位忘加"
    source: str = Field(default="ai", max_length=16)         # ai/parent


class MistakeTag(SQLModel, table=True):
    __tablename__ = "mistake_tags"

    id: Optional[int] = Field(default=None, primary_key=True)
    mistake_id: int = Field(foreign_key="mistakes.id", index=True)
    tag: str = Field(max_length=64)                          # 自定义 Tag：逻辑题/几何题


class SolutionHint(SQLModel, table=True):
    __tablename__ = "solution_hints"

    id: Optional[int] = Field(default=None, primary_key=True)
    mistake_id: int = Field(foreign_key="mistakes.id", index=True)
    content_md: str = Field(default="")                      # Markdown 解题思路
    source: str = Field(default="ai", max_length=16)         # ai/parent/url
    url: Optional[str] = Field(default=None, max_length=512)  # 外部视频/文档链接
    order: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
