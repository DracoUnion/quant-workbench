"""零 Qt 应用上下文。

在 bootstrap 中构建一次，持有 Settings + EventHub + TaskManager + ServiceFacade，
由 ui 层通过 MainWindow(ctx=ctx) 统一访问，保持零 Qt 层对 ui 无感知。
"""

from __future__ import annotations

from .config import AppSettings, get_settings
from .events import EventHub


class AppContext:
    """应用上下文容器。"""

    def __init__(
        self,
        settings: AppSettings | None = None,
        event_hub: EventHub | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.event_hub = event_hub or EventHub()
        self.task_manager = None  # type: ignore[assignment]
        self.service_facade = None  # type: ignore[assignment]

    def ready(self) -> None:
        """标记上下文就绪并发布事件。"""
        self.event_hub.publish("app.ready")
