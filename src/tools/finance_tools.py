"""金融工具实现（Mock 优先，真实源后接）。

每个工具：key + execute(**kwargs) -> dict。
"""

from __future__ import annotations

from .registry import registry


class Tool:
    """工具基类。"""

    def __init__(self, key: str) -> None:
        self.key = key

    def execute(self, **kwargs: Any) -> dict:
        raise NotImplementedError


# ---------- web_search ----------
class WebSearchTool(Tool):
    def __init__(self) -> None:
        super().__init__("web_search")

    def execute(self, **kwargs: Any) -> dict:
        q = kwargs.get("q", "")
        return {
            "tool": "web_search",
            "query": q,
            "results": [
                {"title": f"结果 {i}：{q}", "url": "https://example.com", "snippet": "模拟结果"}
                for i in range(1, 4)
            ],
        }


# ---------- iwencai ----------
class IwencaiTool(Tool):
    def __init__(self) -> None:
        super().__init__("iwencai")

    def execute(self, **kwargs: Any) -> dict:
        return {
            "tool": "iwencai",
            "query": kwargs.get("q", ""),
            "data": [{"code": "600000", "name": "浦发银行", "price": 10.5}],
        }


# ---------- code_interpreter ----------
class CodeInterpreterTool(Tool):
    def __init__(self) -> None:
        super().__init__("code_interpreter")

    def execute(self, **kwargs: Any) -> dict:
        code = kwargs.get("code", "")
        return {
            "tool": "code_interpreter",
            "code": code,
            "result": {"mock": True, "value": 42},
        }


# ---------- doc_reader ----------
class DocReaderTool(Tool):
    def __init__(self) -> None:
        super().__init__("doc_reader")

    def execute(self, **kwargs: Any) -> dict:
        return {"tool": "doc_reader", "text": kwargs.get("text", "")[:200]}


# ---------- multimodal ----------
class MultimodalTool(Tool):
    def __init__(self) -> None:
        super().__init__("multimodal")

    def execute(self, **kwargs: Any) -> dict:
        return {"tool": "multimodal", "result": "mock_image_description"}


# ---------- push ----------
class PushTool(Tool):
    def __init__(self) -> None:
        super().__init__("push")

    def execute(self, **kwargs: Any) -> dict:
        return {"tool": "push", "sent": True}


# ---------- vector_search ----------
class VectorSearchTool(Tool):
    def __init__(self) -> None:
        super().__init__("vector_search")

    def execute(self, **kwargs: Any) -> dict:
        q = kwargs.get("q", "")
        return {
            "tool": "vector_search",
            "query": q,
            "results": [
                {"id": 1, "text": f"向量检索结果：{q}", "score": 0.95},
            ],
        }


# 注册到全局注册表
from .registry import registry

registry.register(WebSearchTool())
registry.register(IwencaiTool())
registry.register(CodeInterpreterTool())
registry.register(DocReaderTool())
registry.register(MultimodalTool())
registry.register(PushTool())
registry.register(VectorSearchTool())
