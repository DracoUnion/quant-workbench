"""推送适配器（Mock 实现）。"""

from __future__ import annotations

from typing import Any


class PushAdapter:
    """推送适配器（Mock）。"""

    def __init__(self, channel: str = "mock") -> None:
        self.channel = channel

    def push(self, title: str, content: str, **kwargs: Any) -> dict:
        return {
            "channel": self.channel,
            "title": title,
            "content": content,
            "sent": True,
        }
