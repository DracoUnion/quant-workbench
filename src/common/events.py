"""零 Qt 事件总线（EventHub）。

进程内发布 - 订阅，供业务模块与 ui 层解耦通信。
与 core.events.EventBus（业务领域事件）分离：EventHub 面向 UI 任务事件（进度、日志、提示）。
"""


from __future__ import annotations

from collections import defaultdict
from typing import Any, Callable

EventHandler = Callable[..., None]

# 约定的事件类型名
EV_APP_READY = "app.ready"


class EventHub:
    """轻量级进程内事件总线。"""

    def __init__(self) -> None:
        self._subscribers: dict[str, list[EventHandler]] = defaultdict(list)

    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        self._subscribers[event_type].append(handler)

    def unsubscribe(self, event_type: str, handler: EventHandler) -> None:
        handlers = self._subscribers.get(event_type, [])
        if handler in handlers:
            handlers.remove(handler)

    def publish(self, event_type: str, *args: Any, **kwargs: Any) -> None:
        for handler in list(self._subscribers.get(event_type, [])):
            handler(*args, **kwargs)
