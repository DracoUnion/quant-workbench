"""零 Qt 引导层。

build_context()：Settings + EventHub + TaskManager + ServiceFacade。
与 tiange 保持一致：唯一 PySide6 依赖在 ui/，此处零 Qt。
"""

from __future__ import annotations

from common.config import AppSettings, get_settings
from common.context import AppContext
from common.events import EventHub
from services.prompt_service import PromptService
from tasks.task import TaskManager


class ServiceFacade:
    """零 Qt 业务门面。"""

    def __init__(self, context: AppContext) -> None:
        self.ctx = context
        self.prompt_service = PromptService(context.settings.prompts_data_path)

    def ai_stream(self, system: str, messages: list[str]):
        """占位：AI 流式由 ui/ai_worker.py（QThread）承载，此处零 Qt 不直接实现。"""
        raise NotImplementedError("AI 流式请走 ui/ai_worker.py（QThread Qt 桥）")


def build_context() -> AppContext:
    settings = get_settings()
    event_hub = EventHub()
    ctx = AppContext(settings=settings, event_hub=event_hub)
    ctx.task_manager = TaskManager()
    ctx.service_facade = ServiceFacade(ctx)
    ctx.ready()
    return ctx
