"""搜索适配器（Mock 实现）。"""

from __future__ import annotations

from typing import Any


class SearchAdapter:
    """搜索适配器（Mock）。"""

    def __init__(self, provider: str = "mock") -> None:
        self.provider = provider

    def search(self, q: str, **kwargs: Any) -> dict:
        return {
            "provider": self.provider,
            "query": q,
            "results": [
                {"title": f"结果 {i}：{q}", "url": "https://example.com", "snippet": "模拟结果"}
                for i in range(1, 4)
            ],
        }
