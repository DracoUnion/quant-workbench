"""多模态适配器（Mock 实现）。"""

from __future__ import annotations

from typing import Any


class MultimodalAdapter:
    """多模态适配器（Mock）。"""

    def __init__(self) -> None:
        pass

    def describe(self, image_path: str, **kwargs: Any) -> dict:
        return {
            "image": image_path,
            "description": f"（Mock）图片描述：{image_path}",
        }
