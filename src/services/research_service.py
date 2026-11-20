"""投研服务：财报提取、摘要、质疑、价值筛选、现金流诊断。"""

from __future__ import annotations

from typing import Any


class ResearchService:
    """投研服务。"""

    def __init__(self) -> None:
        self._tasks: dict[int, dict] = {}
        self._next_id = 1

    def create_task(self, task_type: str, target: str) -> int:
        tid = self._next_id
        self._next_id += 1
        self._tasks[tid] = {
            "id": tid, "type": task_type, "target": target,
            "status": "pending",
        }
        return tid

    def get(self, task_id: int) -> dict | None:
        return self._tasks.get(task_id)

    def list(self) -> list[dict]:
        return list(self._tasks.values())
