"""零 Qt 提示词服务层（兼容旧导入路径）。

纯数据/纯函数层，不导入任何 Qt 模块，可被 headless 测试。
数据优先从 data/prompts.json 加载；文件缺失时回退内置少量种子。
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Prompt:
    """单条提示词模板。"""

    code: str
    title: str
    category: str
    sub_category: str = ""
    description: str = ""
    body: str = ""
    full_text: str = ""
    params_json: dict = field(default_factory=dict)
    version: int = 1
    favorite: bool = False


class PromptService:
    """提示词服务：加载、检索、收藏、渲染。"""

    def __init__(self, data_path: str = "data/prompts.json") -> None:
        self.data_path = data_path
        self._prompts: dict[str, Prompt] = {}
        self._order: list[str] = []

    def load(self) -> list[Prompt]:
        if os.path.exists(self.data_path):
            self._load_from_json(self.data_path)
        else:
            self._load_builtins()
        return list(self.all())

    def _load_from_json(self, path: str) -> None:
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        self._prompts.clear()
        self._order.clear()
        for item in raw:
            p = Prompt(
                code=item.get("code") or item.get("id", ""),
                title=item.get("title", ""),
                category=item.get("category", ""),
                sub_category=item.get("sub_category", ""),
                description=item.get("description", ""),
                body=item.get("body") or item.get("full_text", ""),
                full_text=item.get("full_text") or item.get("body", ""),
                params_json=item.get("params_json") or {},
                version=item.get("version", 1),
            )
            if p.code:
                self._prompts[p.code] = p
                self._order.append(p.code)

    def _load_builtins(self) -> None:
        seeds = [
            Prompt(
                code="P001",
                title="第二代提示词参数化引导模板",
                category="核心框架",
                sub_category="通用骨架",
                description="金融场景提示词的配置文件结构：Role/Profile/Context/Workflow/Constraints/Output Format。",
                body="# 第二代提示词参数化引导模板\n\n## Role\n【身份、从业年限、核心圈层】\n\n## Output Format\n【结构化样板】",
                full_text="# 第二代提示词参数化引导模板\n\n## Role\n【身份、从业年限、核心圈层】\n\n## Output Format\n【结构化样板】",
            ),
        ]
        for p in seeds:
            self._prompts[p.code] = p
            self._order.append(p.code)

    def all(self) -> list[Prompt]:
        return [self._prompts[c] for c in self._order]

    def get(self, code: str) -> Optional[Prompt]:
        return self._prompts.get(code)

    def by_category(self, category: str) -> list[Prompt]:
        return [p for p in self.all() if p.category == category]

    def categories(self) -> list[str]:
        seen: list[str] = []
        for p in self.all():
            if p.category not in seen:
                seen.append(p.category)
        return seen

    def sub_categories(self, category: str) -> list[str]:
        seen: list[str] = []
        for p in self.by_category(category):
            if p.sub_category not in seen:
                seen.append(p.sub_category)
        return seen

    def search(self, query: str) -> list[Prompt]:
        q = query.lower()
        if not q:
            return self.all()
        result = []
        for p in self.all():
            haystack = " ".join(
                [p.title, p.category, p.sub_category, p.description, p.body, p.full_text]
            ).lower()
            if q in haystack:
                result.append(p)
        return result

    def favorites(self) -> list[Prompt]:
        return [p for p in self.all() if p.favorite]

    def toggle_favorite(self, code: str) -> bool:
        p = self._prompts.get(code)
        if not p:
            return False
        p.favorite = not p.favorite
        return p.favorite

    def save(self, path: Optional[str] = None) -> None:
        target = path or self.data_path
        target_dir = os.path.dirname(target)
        if target_dir:
            os.makedirs(target_dir, exist_ok=True)
        data = [
            {
                "code": p.code,
                "id": p.code,
                "title": p.title,
                "category": p.category,
                "sub_category": p.sub_category,
                "description": p.description,
                "body": p.body,
                "full_text": p.full_text,
                "params_json": p.params_json,
                "version": p.version,
                "favorite": p.favorite,
            }
            for p in self.all()
        ]
        with open(target, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def render(self, code: str, context: dict | None = None) -> str:
        p = self.get(code)
        if not p:
            raise KeyError(f"Prompt {code!r} not found")
        ctx = context or {}
        text = p.full_text or p.body
        for k, v in ctx.items():
            text = text.replace("{" + k + "}", str(v))
        return text
