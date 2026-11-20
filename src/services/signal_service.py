"""信号服务：题材、异动、阿尔法、早盘/盘中决策板。"""

from __future__ import annotations

from typing import Any


class SignalService:
    """信号服务。"""

    def __init__(self) -> None:
        self._signals: dict[int, dict] = {}
        self._next_id = 1

    def create(self, source: str, symbol: str, signal_type: str,
               score: float, confidence: float,
               payload: dict | None = None) -> int:
        sid = self._next_id
        self._next_id += 1
        self._signals[sid] = {
            "id": sid, "source": source, "symbol": symbol,
            "signal_type": signal_type, "score": score,
            "confidence": confidence,
            "payload": payload or {},
            "status": "active",
        }
        return sid

    def list(self) -> list[dict]:
        return list(self._signals.values())
