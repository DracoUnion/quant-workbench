"""知识库服务：文档清洗、入库、检索、向量配置。

零 Qt，可 headless 测试。
"""

from __future__ import annotations

from typing import Any


class KnowledgeService:
    """知识库服务：文档清洗、入库、检索、向量配置。"""

    def __init__(self) -> None:
        self._docs: dict[int, dict] = {}
        self._next_id = 1

    def list_kbs(self) -> list[dict]:
        return []

    def create_kb(self, name: str, domain: str, description: str = "") -> int:
        kid = self._next_id
        self._next_id += 1
        return kid

    def ingest_doc(self, kb_id: int, source_type: str, source_uri: str | None,
                   title: str, raw_text: str) -> int:
        did = self._next_id
        self._next_id += 1
        cleaned = self._clean(raw_text)
        self._docs[did] = {
            "id": did, "kb_id": kb_id, "source_type": source_type,
            "source_uri": source_uri, "title": title,
            "raw_text": raw_text, "cleaned_text": cleaned,
            "tags_json": [], "credibility": 1.0,
        }
        return did

    def search(self, kb_id: int, query: str, limit: int = 10) -> list[dict]:
        results = []
        for doc in self._docs.values():
            if doc["kb_id"] == kb_id and query.lower() in doc["cleaned_text"].lower():
                results.append({
                    "id": doc["id"], "title": doc["title"],
                    "snippet": doc["cleaned_text"][:200],
                })
                if len(results) >= limit:
                    break
        return results

    @staticmethod
    def _clean(text: str) -> str:
        """简单清洗：去页眉页脚、重复空行。"""
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        return "\n".join(lines)
