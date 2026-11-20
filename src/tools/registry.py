"""工具注册表 + 实现。

零 Qt，可 headless 测试。
"""

from __future__ import annotations

from typing import Any


class ToolRegistry:
    """工具注册表。"""

    def __init__(self) -> None:
        self._tools: dict[str, Any] = {}
        self._register_builtins()

    def _register_builtins(self) -> None:
        from tools.finance_tools import (
            web_search_tool,
            iwencai_tool,
            code_interpreter_tool,
            doc_reader_tool,
            multimodal_tool,
            push_tool,
            vector_search_tool,
        )
        for t in [
            web_search_tool, iwencai_tool, code_interpreter_tool,
            doc_reader_tool, multimodal_tool, push_tool, vector_search_tool,
        ]:
            self.register(t)

    def register(self, tool: Any) -> None:
        self._tools[tool.key] = tool

    def get(self, key: str) -> Any | None:
        return self._tools.get(key)

    def list(self) -> list[str]:
        return list(self._tools.keys())

    def execute(self, key: str, **kwargs) -> Any:
        tool = self._tools.get(key)
        if not tool:
            raise ValueError(f"Tool {key!r} not found")
        return tool.execute(**kwargs)


# 单例
registry = ToolRegistry()
