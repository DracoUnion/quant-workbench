"""零 Qt 合规服务（兼容旧导入路径）：合规审查、留痕。"""


from __future__ import annotations

from typing import Optional


class ComplianceService:
    """合规审查服务。"""

    def __init__(self) -> None:
        self._reviews: dict[int, dict] = {}
        self._next_id = 1

    def create_review(self, doc_type: str, source_ref: str) -> int:
        rid = self._next_id
        self._next_id += 1
        self._reviews[rid] = {
            "review_id": rid,
            "id": rid,
            "doc_type": doc_type,
            "source_ref": source_ref,
            "conclusion": "pending",
            "issues_json": [],
            "rewrite_json": [],
            "reviewer": None,
            "signed_by": None,
        }
        return rid

    def list(self) -> list[dict]:
        return list(self._reviews.values())

    def get(self, review_id: int) -> Optional[dict]:
        return self._reviews.get(review_id)
