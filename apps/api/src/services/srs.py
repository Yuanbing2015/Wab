"""SRS（间隔重复算法）— 基于 py-fsrs

约定：
- mistake.srs_state 存 fsrs.Card 的序列化字典
- 每次复习后调用 review() 更新状态
"""
from datetime import datetime
from typing import Any

# 占位实现，S4-1 时引入 fsrs 真实算法
# from fsrs import FSRS, Card, Rating


def init_card_state() -> dict[str, Any]:
    """新错题入库时初始化 SRS 状态。"""
    return {
        "due": datetime.utcnow().isoformat(),
        "stability": 0.0,
        "difficulty": 0.0,
        "elapsed_days": 0,
        "scheduled_days": 0,
        "reps": 0,
        "lapses": 0,
        "state": "new",  # new | learning | review | relearning
        "last_review": None,
    }


def review(state: dict[str, Any], rating: str) -> dict[str, Any]:
    """rating: 'again' | 'hard' | 'good' | 'easy'

    S4-1 接入真实 fsrs；当前为占位，让上层流程能跑通。
    """
    raise NotImplementedError("Story S4-1: FSRS 算法接入（待实现）")
