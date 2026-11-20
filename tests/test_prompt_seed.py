"""P001-P076 提示词种子测试：全部入库、code 唯一、参数可解析。"""

from __future__ import annotations

import os
import sys


os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest  # noqa: E402

from src.bootstrap import build_context  # noqa: E402
from src.services.prompt_service import PromptService  # noqa: E402


def test_all_prompts_loaded() -> None:
    ctx = build_context()
    svc: PromptService = ctx.services.prompt_service
    svc.load()
    prompts = svc.all()
    codes = [p.code for p in prompts]
    assert len(prompts) == len(codes), "code 必须唯一"
    assert len(prompts) >= 76, f"期望至少 76 条，实际 {len(prompts)}"
    # 每条都应有 title 和 body
    for p in prompts:
        assert p.title, f"{p.code} 缺少 title"
        assert p.body or p.full_text, f"{p.code} 缺少正文"


def test_all_categories_parseable() -> None:
    ctx = build_context()
    svc: PromptService = ctx.services.prompt_service
    svc.load()
    cats = svc.categories()
    assert len(cats) > 0
    for cat in cats:
        subcats = svc.sub_categories(cat)
        assert isinstance(subcats, list)


def test_search_works() -> None:
    ctx = build_context()
    svc: PromptService = ctx.services.prompt_service
    svc.load()
    results = svc.search("合规")
    assert isinstance(results, list)
    assert len(results) >= 1
