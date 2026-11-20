"""零 Qt 应用上下文。

在 bootstrap 中构建一次，持有 Settings + EventHub + TaskManager + ServiceRegistry +
RunExecutor，由 ui 层通过 MainWindow(ctx=ctx) 统一访问，保持零 Qt 层对 ui 无感知。
"""


from __future__ import annotations

from typing import Any


class AppContext:
    """应用上下文容器。"""

    def __init__(
        self,
        settings: Any = None,
        event_hub: Any = None,
        task_manager: Any = None,
        services: Any = None,
        run_executor: Any = None,
    ) -> None:
        self.settings = settings
        self.event_hub = event_hub
        self.task_manager = task_manager   # 兼容测试断言 ctx.task_manager
        self.tasks = task_manager          # 任务书字段名
        self.services = services
        self.run_executor = run_executor

    def ready(self) -> None:
        """标记上下文就绪并发布就绪事件。"""
        if self.event_hub is not None:
            self.event_hub.publish("app.ready")
