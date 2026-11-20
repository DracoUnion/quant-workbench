"""业务事件总线（EventBus）。

Pydantic DomainEvent 总线，供业务模块之间解耦通信。
与 ui/ 的 common.events.EventHub（UI 任务事件）分离。
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Callable, Optional

from pydantic import BaseModel, Field


class DomainEvent(BaseModel):
    """业务领域事件基类。"""

    event_type: str
    payload: dict = Field(default_factory=dict)
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    run_id: Optional[str] = None
    node_key: Optional[str] = None


class EventBus:
    """进程内业务事件总线。"""

    def __init__(self) -> None:
        self._subscribers: dict[str, list[Callable[[DomainEvent], None]]] = (
            defaultdict(list)
        )

    def subscribe(self, event_type: str, handler: Callable[[DomainEvent], None]) -> None:
        self._subscribers[event_type].append(handler)

    def unsubscribe(
        self, event_type: str, handler: Callable[[DomainEvent], None]
    ) -> None:
        handlers = self._subscribers.get(event_type, [])
        if handler in handlers:
            handlers.remove(handler)

    def publish(self, event: DomainEvent) -> None:
        for handler in list(self._subscribers.get(event.event_type, [])):
            handler(event)
        # 同时发布到通配符 "*" 订阅者（若有）
        for handler in list(self._subscribers.get("*")):
            handler(event)


# 全局 EventBus 单例
event_bus = EventBus()


# 约定的业务事件类型名
EV_RUN_STATE_CHANGED = "run.state_changed"
EV_NODE_FINISHED = "node.finished"
EV_NODE_FAILED = "node.failed"
EV_ALERT_RAISED = "alert.raised"
EV_GATE_BLOCKED = "gate.blocked"
EV_GATE_RELEASED = "gate.released"
EV_CIRCUIT_BREAKER = "circuit.breaker"
