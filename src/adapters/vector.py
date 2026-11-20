"""向量检索适配器（Mock 实现）。"""

from __future__ import annotations

from typing import Any


class VectorAdapter:
    """向量检索适配器（Mock）。"""

    def __init__(self) -> None:
        pass

    def search(self, q: str, **kwargs: Any) -> dict:
        return {
            "results": [
                {"id": 1, "text": f"向量检索结果：{q}", "score": 0.95},
            ],
        }
