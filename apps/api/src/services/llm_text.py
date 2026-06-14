"""LLM 文本接入（DeepSeek-V3）

封装对话与业务函数：
- analyze_error  错因分析
- generate_solution_hint  解题思路生成
- generate_variants  变式题生成（六维度）
- render_with_interest  兴趣化剧情包装
"""
import json

from openai import AsyncOpenAI

from src.core.config import settings


_client: AsyncOpenAI | None = None


def get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(
            api_key=settings.deepseek_api_key,
            base_url=settings.deepseek_base_url,
        )
    return _client


async def chat(
    messages: list[dict],
    model: str | None = None,
    temperature: float = 0.7,
    response_format: dict | None = None,
) -> str:
    """通用对话接口（非流式）。"""
    kwargs: dict = {
        "model": model or settings.deepseek_model_text,
        "messages": messages,
        "temperature": temperature,
    }
    if response_format:
        kwargs["response_format"] = response_format
    resp = await get_client().chat.completions.create(**kwargs)
    return resp.choices[0].message.content or ""


def _safe_json(content: str):
    content = content.strip()
    if content.startswith("```"):
        content = content.split("```", 2)[1]
        if content.startswith("json"):
            content = content[4:]
        content = content.strip()
    return json.loads(content)


# ============================================================
# 业务函数
# ============================================================
async def analyze_error(
    stem: str, child_answer: str, correct_answer: str, grade: int
) -> dict:
    """S2-2: 分析错因 → {error_tags: [...], analysis: "..."}"""
    system = (
        "你是资深中小学老师。根据题目、孩子的错误答案、正确答案，分析孩子的错因。"
        "输出 JSON：{\"error_tags\": [\"简短错因标签\"], \"analysis\": \"一段通俗的错因分析\"}。"
        "error_tags 要精炼（如'进位忘加''审题漏条件''公式记错'），1-3 个。只返回 JSON。"
    )
    user = (
        f"年级：{grade}\n题目：{stem}\n孩子的答案：{child_answer}\n正确答案：{correct_answer}"
    )
    content = await chat(
        [{"role": "system", "content": system}, {"role": "user", "content": user}],
        temperature=0.3,
        response_format={"type": "json_object"},
    )
    return _safe_json(content)


async def generate_solution_hint(stem: str, correct_answer: str, grade: int) -> str:
    """S2-2: 生成解题思路 Markdown"""
    system = (
        "你是擅长启发式教学的老师。为题目写一份分步骤的解题思路，"
        "用 Markdown，语言通俗，适合家长讲给孩子。不要直接只给答案，要讲清每一步为什么。"
    )
    user = f"年级：{grade}\n题目：{stem}\n正确答案：{correct_answer}"
    return await chat(
        [{"role": "system", "content": system}, {"role": "user", "content": user}],
        temperature=0.5,
    )


async def generate_variants(
    stem: str,
    correct_answer: str,
    error_tags: list[str],
    interest_tags: list[str],
    grade: int,
    dimensions: list[str],
    n: int = 5,
) -> list[dict]:
    """S5-1: 六维度变式题生成

    dimensions: ['D1' 难度梯度, 'D2' 题型变化, 'D3' 错因针对, 'D4' 情境迁移, 'D5' 逆向, 'D6' 关联拓展]
    """
    dim_desc = {
        "D1": "难度梯度（简单/等难度/进阶/综合）",
        "D2": "题型变化（选择↔填空↔解答↔判断）",
        "D3": f"错因针对性，专门针对错因{error_tags}反复设陷阱",
        "D4": f"情境迁移，把题套入孩子的兴趣场景{interest_tags}",
        "D5": "逆向生成（给答案让孩子出题，或给条件让孩子设问）",
        "D6": "关联拓展（上下年级版本或跨学科情境）",
    }
    chosen = "；".join(dim_desc.get(d, d) for d in dimensions)
    system = (
        "你是命题专家。基于原错题，生成多道变式题用于巩固训练。"
        f"覆盖这些维度：{chosen}。"
        "输出 JSON 数组，每个元素："
        "{\"stem\":\"题干\",\"correct_answer\":\"答案\",\"dimension\":\"D1~D6\",\"generation_reason\":\"为什么生成这道题/考查点\"}。"
        "只返回 JSON 数组。"
    )
    user = (
        f"年级：{grade}\n原题：{stem}\n答案：{correct_answer}\n"
        f"错因：{error_tags}\n孩子兴趣：{interest_tags}\n生成数量：{n}"
    )
    content = await chat(
        [{"role": "system", "content": system}, {"role": "user", "content": user}],
        temperature=0.8,
    )
    data = _safe_json(content)
    return data if isinstance(data, list) else data.get("variants", [])


async def render_with_interest(
    stem: str, interest_tags: list[str], grade: int
) -> str:
    """S4-4: 兴趣化剧情包装（玩法 8）— 实时把抽象题套孩子兴趣场景。

    只改变情境包装，绝不改变数学/逻辑本质与答案。
    """
    system = (
        "你是会把枯燥题目变得有趣的老师。把题目的情境改写成孩子喜欢的主题，"
        "但【绝对不能改变】题目的数学关系、数字、考查点和正确答案，只换'外衣'。"
        "直接返回改写后的题干文本，不要解释。"
    )
    user = f"年级：{grade}\n孩子喜欢：{interest_tags}\n原题：{stem}"
    return await chat(
        [{"role": "system", "content": system}, {"role": "user", "content": user}],
        temperature=0.9,
    )
