"""零 Qt 引导层。

build_context()：Settings + EventHub + TaskManager + ServiceRegistry + InlineExecutor。
与任务书保持一致：此处零 Qt，唯一 PySide6 依赖在 gui/ 与 main_window.py。
"""


from __future__ import annotations

from .common.context import AppContext
from .common.events import EventHub
from .core.config import get_settings
from .services.backtest_service import BacktestService
from .services.client_service import ClientService
from .services.compliance_service import ComplianceService
from .services.event_service import EventService
from .services.knowledge_service import KnowledgeService
from .services.office_service import OfficeService
from .services.portfolio_service import PortfolioService
from .services.prompt_service import PromptService
from .services.research_service import ResearchService
from .services.run_service import RunService
from .services.signal_service import SignalService
from .services.workflow_service import WorkflowService
from .tasks.runs import InlineExecutor
from .tasks.task import TaskManager


class ServiceRegistry:
    """按域聚合的业务门面。"""

    def __init__(self, ctx: AppContext) -> None:
        self.ctx = ctx
        self.prompt_service = PromptService(ctx.settings.prompts_data_path, ctx=ctx)
        self.workflow_service = WorkflowService()
        self.run_service = RunService(ctx.event_hub)
        self.knowledge_service = KnowledgeService()
        self.research_service = ResearchService()
        self.portfolio_service = PortfolioService()
        self.signal_service = SignalService()
        self.event_service = EventService()
        self.client_service = ClientService()
        self.compliance_service = ComplianceService()
        self.office_service = OfficeService()
        self.backtest_service = BacktestService()


def build_context() -> AppContext:
    settings = get_settings()
    event_hub = EventHub()
    task_manager = TaskManager()
    ctx = AppContext(
        settings=settings,
        event_hub=event_hub,
        task_manager=task_manager,
        services=None,
        run_executor=None,
    )
    ctx.services = ServiceRegistry(ctx)
    ctx.run_executor = InlineExecutor(ctx.services.run_service)
    ctx.ready()
    return ctx
