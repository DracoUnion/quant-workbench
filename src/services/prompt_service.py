"""提示词服务：模板 CRUD、版本、渲染、参数校验。

零 Qt，可 headless 测试。数据优先从 src/seed/prompts.py 种子入库；
若上下文中挂载了数据库服务，则优先从数据库加载。
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Prompt:
    """内存中的提示词模板。"""

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
    """提示词模板服务：CRUD、版本、渲染、参数校验。"""

    def __init__(self, data_path: str = "data/prompts.json", ctx: Any = None) -> None:
        self.data_path = data_path
        self.ctx = ctx
        self._prompts: dict[str, Prompt] = {}
        self._order: list[str] = []

    # ------------------------------------------------------------------ load
    def load(self) -> list[Prompt]:
        """加载提示词：数据库有数据则以数据库为准，否则从种子文件加载。"""
        if self.ctx is not None and getattr(self.ctx, "services", None) is not None:
            rows = self._load_from_db()
            if rows:
                return list(self.all())

        if self.data_path and os.path.exists(self.data_path):
            self._load_from_json(self.data_path)
        else:
            self._load_from_seed()
        return list(self.all())

    def _load_from_db(self) -> list[Prompt]:
        try:
            from sqlalchemy import select

            from ..core.database import session_scope
            from ..models.prompt import PromptTemplate

            with session_scope() as session:
                stmt = select(PromptTemplate)
                db_rows = session.execute(stmt).scalars().all()
        except Exception:  # noqa: BLE001
            return []
        if not db_rows:
            return []
        self._prompts.clear()
        self._order.clear()
        for row in db_rows:
            self._prompts[row.code] = Prompt(
                code=row.code,
                title=row.title,
                category=row.category,
                sub_category=row.sub_category,
                description=row.title,
                body=row.body,
                full_text=row.body,
                params_json=row.params_json or {},
                version=row.version,
            )
            self._order.append(row.code)
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

    def _load_from_seed(self) -> None:
        """内置种子兜底：确保无 data 目录时仍可运行演示。"""
        from .seed.prompts import PROMPTS  # noqa: import-not-found

        self._prompts.clear()
        self._order.clear()
        for item in PROMPTS:
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
            self._prompts[p.code] = p
            self._order.append(p.code)

    # ------------------------------------------------------------------ query
    def all(self) -> list[Prompt]:
        return [self._prompts[c] for c in self._order]

    def get(self, code: str) -> Prompt | None:
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

    def save(self, path: str | None = None) -> None:
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

    # ------------------------------------------------------------------ render
    def render(self, code: str, context: dict[str, Any] | None = None) -> str:
        """渲染提示词：将正文中的 {var} 替换为 context 值。"""
        p = self.get(code)
        if not p:
            raise KeyError(f"Prompt {code!r} not found")
        ctx = context or {}
        text = p.full_text or p.body
        for k, v in ctx.items():
            text = text.replace("{" + k + "}", str(v))
        return text
