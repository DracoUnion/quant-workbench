"""客户服务：画像、Client-360、KYC、话术。"""

from __future__ import annotations

from typing import Any


class ClientService:
    """客户服务。"""

    def __init__(self) -> None:
        self._clients: dict[int, dict] = {}
        self._next_id = 1

    def create(self, name: str, risk_level: str = "medium",
               stage: str = "prospect") -> int:
        cid = self._next_id
        self._next_id += 1
        self._clients[cid] = {
            "id": cid, "name": name, "risk_level": risk_level,
            "stage": stage, "tags_json": [],
        }
        return cid

    def list(self) -> list[dict]:
        return list(self._clients.values())
