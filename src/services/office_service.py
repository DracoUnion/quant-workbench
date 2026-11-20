"""办公服务：周报、月报、会议纪要、行动项。"""

from __future__ import annotations

from typing import Any


class OfficeService:
    """办公自动化服务。"""

    def __init__(self) -> None:
        self._reports: dict[int, dict] = {}
        self._next_id = 1

    def create_weekly(self, owner: str, period: str,
                      content_md: str) -> int:
        rid = self._next_id
        self._next_id += 1
        self._reports[rid] = {
            "id": rid, "owner": owner, "period": period,
            "content_md": content_md, "status": "draft",
        }
        return rid

    def list(self) -> list[dict]:
        return list(self._reports.values())
