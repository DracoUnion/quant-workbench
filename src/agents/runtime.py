"""智能体运行时：AgentRuntime（Store/Provider/Sink）。

零 Qt，可 headless 测试。
"""

from __future__ import annotations

from typing import Any


class AgentRuntime:
    """Agent 运行时：Store/Provider/Sink 三层。"""

    def __init__(self) -> None:
        self._store: dict[str, Any] = {}
        self._providers: dict[str, Any] = {}
        self._sinks: dict[str, Any] = {}

    def register_provider(self, name: str, provider: Any) -> None:
        self._providers[name] = provider

    def register_sink(self, name: str, sink: Any) -> None:
        self._sinks[name] = sink

    def run(self, agent_id: str, input_data: dict) -> dict:
        """运行智能体，返回结果。"""
        return {
            "agent_id": agent_id,
            "status": "done",
            "output": {},
        }
