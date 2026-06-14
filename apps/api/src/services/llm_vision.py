"""LLM 视觉接入 — DeepSeek-VL2 主力 + Qwen-VL-Max 兜底

负责：
- 单题拍照 → 结构化 JSON（S2-1 / S2-3）
- 整张试卷 → 多题切分（S2-4）
"""
import base64
import json
from typing import Any

from openai import AsyncOpenAI

from src.core.config import settings


_deepseek: AsyncOpenAI | None = None
_qwen: AsyncOpenAI | None = None


def _get_deepseek() -> AsyncOpenAI:
    global _deepseek
    if _deepseek is None:
        _deepseek = AsyncOpenAI(
            api_key=settings.deepseek_api_key,
            base_url=settings.deepseek_base_url,
        )
    return _deepseek


def _get_qwen() -> AsyncOpenAI:
    global _qwen
    if _qwen is None:
        if not settings.qwen_api_key:
            raise RuntimeError("QWEN_API_KEY 未配置，无法启用兜底视觉")
        _qwen = AsyncOpenAI(
            api_key=settings.qwen_api_key,
            base_url=settings.qwen_base_url,
        )
    return _qwen


def encode_image_b64(image_bytes: bytes, mime: str = "image/jpeg") -> str:
    return f"data:{mime};base64,{base64.b64encode(image_bytes).decode('utf-8')}"


# ============================================================
# Prompt
# ============================================================
_EXTRACT_SYSTEM = """你是一位资深的中国中小学老师，精通各学科。
你的任务是看一张「错题」照片，把它整理成结构化数据，方便家长录入错题本。
请严格输出 JSON，不要任何额外解释。字段说明：
- subject: 学科（数学/语文/英语/物理/化学/生物/历史/地理/政治/科学，二选一最贴切的）
- grade_guess: 估计年级（如"一年级""初二"）
- question_type: 题型（选择题/填空题/应用题/判断题/解答题/看图题/计算题）
- stem: 题干完整文本（数学符号用通用写法，如 3+5、1/2、x²）
- options: 选项数组（选择题才有，如 ["A. ...","B. ..."]；否则空数组）
- correct_answer: 正确答案（若图中能判断；否则给出你的解答）
- child_answer: 孩子写的错误答案（若图中可识别；否则 null）
- auto_tags: 知识点标签数组（如 ["20以内进位加法","单位换算"]）
- error_hypothesis: 一句话推测孩子的错因（如"进位时忘记加1"）
- solution_hint_draft: 简明解题思路（分步骤，适合家长讲给孩子听）
请只返回一个 JSON 对象。"""

_SPLIT_SYSTEM = """你是一位资深老师。这是一张包含多道题的试卷/作业照片。
请把其中【做错的题】逐一拆分，输出 JSON 数组，每个元素结构同单题抽取：
{subject, grade_guess, question_type, stem, options, correct_answer, child_answer, auto_tags, error_hypothesis, solution_hint_draft}
只返回 JSON 数组，不要额外解释。"""


def _safe_json(content: str) -> Any:
    """容错解析 LLM 返回的 JSON（去除可能的 ```json 包裹）。"""
    content = content.strip()
    if content.startswith("```"):
        content = content.split("```", 2)[1]
        if content.startswith("json"):
            content = content[4:]
        content = content.strip()
    return json.loads(content)


async def _vision_chat(client: AsyncOpenAI, model: str, system: str, image_b64: str, user_text: str) -> str:
    resp = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_text},
                    {"type": "image_url", "image_url": {"url": image_b64}},
                ],
            },
        ],
        temperature=0.2,
    )
    return resp.choices[0].message.content or ""


# ============================================================
# 业务函数
# ============================================================
async def extract_mistake_from_image(
    image_bytes: bytes,
    grade_hint: str | None = None,
    use_fallback: bool = False,
) -> dict:
    """S2-1: 从错题照片抽取结构化错题。

    use_fallback=True 时直接用 Qwen-VL（DeepSeek 视觉失败时由上层重试）。
    """
    image_b64 = encode_image_b64(image_bytes)
    user_text = "请整理这道错题。"
    if grade_hint:
        user_text += f"参考年级：{grade_hint}。"

    if use_fallback:
        content = await _vision_chat(
            _get_qwen(), settings.qwen_model_vision, _EXTRACT_SYSTEM, image_b64, user_text
        )
    else:
        content = await _vision_chat(
            _get_deepseek(), settings.deepseek_model_vision, _EXTRACT_SYSTEM, image_b64, user_text
        )
    return _safe_json(content)


async def split_paper_into_questions(image_bytes: bytes) -> list[dict]:
    """S2-4: 整张试卷扫描 → 切分多道题"""
    image_b64 = encode_image_b64(image_bytes)
    content = await _vision_chat(
        _get_deepseek(),
        settings.deepseek_model_vision,
        _SPLIT_SYSTEM,
        image_b64,
        "请拆分这张试卷上做错的题。",
    )
    data = _safe_json(content)
    return data if isinstance(data, list) else data.get("questions", [])
