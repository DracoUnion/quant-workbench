"""事件服务：事件卡、供应链、内部人、研报情绪、套利。"""

from __future__ import annotations

from typing import Any


class EventService:
    """事件服务。"""

    def __init__(self) -> None:
        self._events: dict[int, dict] = {}
        self._next_id = 1

    def create(self, event_type: str, target: str,
               decoded: dict | None = None) -> int:
        eid = self._next_id
        self._next_id += 1
        self._events[eid] = {
            "id": eid, "event_type": event_type, "target": target,
            "decoded": decoded or {},
            "history_winrate": 0.0,
            "risk_json": {},
        }
        return eid

    def list(self) -> list[dict]:
        return list(self._events.values())
