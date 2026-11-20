"""零 Qt WebSocket 事件桥。

订阅 core.events.EventBus，可由 gui 层将事件桥接为 Qt 信号推送到页面。
此模块本身不导入 PySide6。
"""


from __future__ import annotations

from typing import Callable

from .core.events import EventBus


class WsClient:
    """订阅 EventBus，将业务事件分发给订阅者（由 gui 层绑定 Qt 信号）。"""

    def __init__(self, event_bus: EventBus | None = None) -> None:
        self.event_bus = event_bus
        self._subscribers: dict[str, list[Callable[[dict], None]]] = {}

    def subscribe(self, event_type: str, handler: Callable[[dict], None]) -> None:
        self._subscribers.setdefault(event_type, []).append(handler)

    def unsubscribe(self, event_type: str, handler: Callable[[dict], None]) -> None:
        handlers = self._subscribers.get(event_type, [])
        if handler in handlers:
            handlers.remove(handler)

    def publish(self, event_type: str, payload: dict) -> None:
        for handler in list(self._subscribers.get(event_type, [])):
            handler(payload)

    def subscribe_to_event_bus(self, event_bus: EventBus) -> None:
        """将 EventBus 的事件桥接到订阅者。"""

        def handler(event) -> None:
            self.publish(
                event.event_type,
                event.payload if hasattr(event, "payload") else {},
            )

        self.event_bus = event_bus
        event_bus.subscribe("*", handler)  # type: ignore[arg-type]
