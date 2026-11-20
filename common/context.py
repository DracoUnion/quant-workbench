"""零 Qt 应用上下文（兼容旧导入路径）。

旧版字段 task_manager / service_facade 保留；services 为惰性属性，
首次访问时构建轻量级服务命名空间，供 headless 脚本与 tests 使用。
"""


from __future__ import annotations

from types import SimpleNamespace

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
        self.task_manager = None
        self._services: SimpleNamespace | None = None

    @property
    def service_facade(self) -> SimpleNamespace:
        return self.services

    @property
    def services(self) -> SimpleNamespace:
        if self._services is None:
            from services.compliance_service import ComplianceService  # noqa: W0611
            from services.prompt_service import PromptService
            from services.run_service import RunService
            from services.workflow_service import WorkflowService

            self._services = SimpleNamespace(
                prompt_service=PromptService(),
                workflow_service=WorkflowService(),
                run_service=RunService(),
                compliance_service=ComplianceService(),
            )
        return self._services

    def ready(self) -> None:
        """标记上下文就绪并发布事件。"""
        self.event_hub.publish("app.ready")
