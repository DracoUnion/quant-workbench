"""组合服务：组合、持仓、风险快照、再平衡。"""

from __future__ import annotations

from typing import Any


class PortfolioService:
    """组合服务。"""

    def __init__(self) -> None:
        self._portfolios: dict[int, dict] = {}
        self._positions: dict[int, list[dict]] = {}
        self._next_id = 1

    def create(self, name: str, owner: str, base_currency: str = "CNY",
               risk_level: str = "medium") -> int:
        pid = self._next_id
        self._next_id += 1
        self._portfolios[pid] = {
            "id": pid, "name": name, "owner": owner,
            "base_currency": base_currency, "risk_level": risk_level,
        }
        return pid

    def list(self) -> list[dict]:
        return list(self._portfolios.values())
