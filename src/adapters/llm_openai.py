"""适配器：llm/openai（OpenAI 兼容 Provider，Mock 实现）。"""

from __future__ import annotations

from typing import Any


class OpenAIProvider:
    """OpenAI 兼容大模型 Provider（Mock 实现，真实源后接）。"""

    def __init__(self, api_key: str | None = None,
                 base_url: str = "https://api.openai.com/v1",
                 model: str = "gpt-4o-mini") -> None:
        self.api_key = api_key
        self.base_url = base_url
        self.model = model

    def chat(self, messages: list[dict], **kwargs: Any) -> dict:
        """Mock 聊天完成。"""
        last_msg = messages[-1] if messages else {}
        user_text = last_msg.get("content", "")
        return {
            "model": self.model,
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": f"（Mock 回复）收到：{user_text[:200]}",
                }
            }],
        }


def get_openai_provider() -> OpenAIProvider:
    """获取 OpenAI Provider 单例。"""
    from common.config import get_settings
    s = get_settings()
    return OpenAIProvider(
        api_key=s.llm_api_key,
        base_url=s.llm_base_url,
        model=s.llm_model,
    )
