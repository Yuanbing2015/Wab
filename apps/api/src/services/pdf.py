"""PDF 导出（WeasyPrint）

S5-2: 三种 HTML 模版 → PDF
- 每日小测
- 专项突破卷
- 学期成长档案
"""


async def render_daily_quiz_pdf(mistakes: list[dict], variants: list[dict]) -> bytes:
    """S5-2: 每日小测 PDF（A4 单页 5-10 题）"""
    raise NotImplementedError("Story S5-2: 每日小测 PDF（待实现）")


async def render_focused_pack_pdf(
    error_tag: str, mistakes: list[dict], variants: list[dict]
) -> bytes:
    """S5-2: 专项突破卷 PDF"""
    raise NotImplementedError("Story S5-2: 专项突破卷 PDF（待实现）")


async def render_term_archive_pdf(user_id: int, term_data: dict) -> bytes:
    """S5-2: 学期成长档案 PDF"""
    raise NotImplementedError("Story S5-2: 学期成长档案 PDF（待实现）")
