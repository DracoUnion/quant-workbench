"""文档解析适配器（Mock 实现）。"""

from __future__ import annotations

from typing import Any


class DocParserAdapter:
    """文档解析适配器（Mock）。"""

    def __init__(self) -> None:
        pass

    def parse(self, file_path: str, **kwargs: Any) -> dict:
        return {
            "file": file_path,
            "text": f"（Mock 解析）{file_path} 的文本内容...",
            "pages": 1,
        }
