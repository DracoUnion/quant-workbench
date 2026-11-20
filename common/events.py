"""零 Qt 事件总线。

进程内发布 - 订阅，用于各零 Qt 模块与 ui 层之间解耦通信。
ui 层可通过 AppContext 获得事件总线并订阅业务事件。
"""

from __future__ import annotations

from collections import defaultdict
from types import SimpleNamespace
from typing import Any, Callable

EventHandler = Callable[..., None]


class EventHub:
    """轻量级事件总线。"""

    def __init__(self) -> None:
        self._subscribers: dict[str, list[EventHandler]] = defaultdict(list)

    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        self._subscribers[event_type].append(handler)

    def unsubscribe(self, event_type: str, handler: EventHandler) -> None:
        handlers = self._subscribers.get(event_type, [])
        if handler in handlers:
            handlers.remove(handler)

    def publish(self, event_type: str, *args: Any, **kwargs: Any) -> None:
        envelope = SimpleNamespace(
            payload=args[0] if args else None, **kwargs
        ) if kwargs or not args else SimpleNamespace(payload=args[0])
        for handler in list(self._subscribers.get(event_type, [])):
            handler(envelope)


# 约定的事件类型名
EV_PROMPT_SELECTED = "prompt.selected"
EV_PROMPT_COPIED = "prompt.copied"
EV_PROMPT_FAVORITE_TOGGLED = "prompt.favorite.toggled"
EV_SEARCH_QUERY_CHANGED = "search.query.changed"
EV_APP_READY = "app.ready"
