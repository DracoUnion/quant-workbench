"""回测服务：回测复盘、驳回审查、归因报告。"""

from __future__ import annotations

from typing import Any


class BacktestService:
    """回测服务。"""

    def __init__(self) -> None:
        self._results: dict[int, dict] = {}
        self._next_id = 1

    def create_run(self, strategy: str, params: dict | None = None) -> int:
        rid = self._next_id
        self._next_id += 1
        self._results[rid] = {
            "id": rid, "strategy": strategy, "params": params or {},
            "status": "pending",
        }
        return rid

    def get(self, run_id: int) -> dict | None:
        return self._results.get(run_id)
