"""主窗口：左侧导航 + 右侧页面堆栈。

唯一 PySide6 依赖窗口层，业务数据仅通过 ctx.services / ApiClient 访问。
"""


from __future__ import annotations

from PySide6.QtCore import QObject, QSize, Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from src.gui.clients import ClientsPage
from src.gui.compliance import CompliancePage
from src.gui.dashboard import DashboardPage
from src.gui.events import EventsPage
from src.gui.knowledge import KnowledgePage
from src.gui.office import OfficePage
from src.gui.prompts import PromptsPage
from src.gui.portfolio import PortfolioPage
from src.gui.research import ResearchPage
from src.gui.runs import RunsPage
from src.gui.settings import SettingsPage
from src.gui.signals import SignalsPage
from src.gui.workflows import WorkflowsPage

from src.ws_client import WsClient


# 页面注册：(标题, 模块页类, 服务属性名)
PAGES: list[tuple[str, type, str | None]] = [
    ("工作台总览", DashboardPage, None),
    ("提示词工坊", PromptsPage, "prompt_service"),
    ("工作流编排", WorkflowsPage, "workflow_service"),
    ("运行中心", RunsPage, "run_service"),
    ("知识库", KnowledgePage, None),
    ("投研", ResearchPage, None),
    ("组合风控", PortfolioPage, None),
    ("短线信号", SignalsPage, None),
    ("事件套利", EventsPage, None),
    ("客户经营", ClientsPage, None),
    ("合规", CompliancePage, None),
    ("办公自动化", OfficePage, None),
    ("设置", SettingsPage, None),
]


class EventBridge(QObject):
    """把 ws_manager/EventBus 的业务事件桥接为 Qt 信号，推送到页面。"""

    event_arrived = Signal(str, dict)

    def __init__(self, event_bus=None) -> None:
        super().__init__()
        self.ws_client = WsClient(event_bus)
        self.ws_client.subscribe_to_event_bus(event_bus) if event_bus else None
        self.ws_client.subscribe("*", self._on_event)

    def _on_event(self, payload: dict) -> None:
        self.event_arrived.emit(
            payload.get("event_type", "event"), payload if isinstance(payload, dict) else {}
        )


class MainWindow(QMainWindow):
    """主窗口：左侧 QListWidget 导航，右侧 QStackedWidget 页面。"""

    def __init__(self, ctx=None) -> None:
        super().__init__()
        self.ctx = ctx
        self.setWindowTitle(getattr(ctx.settings, "window_title", "QuantWorkbench") if ctx else "QuantWorkbench")

        # 事件桥：业务事件 → Qt 信号 → 页面刷新
        event_bus = getattr(ctx.services, "run_service", None).event_bus if ctx and getattr(ctx, "services", None) else None
        self.bridge = EventBridge(event_bus)
        self.bridge.event_arrived.connect(self._on_event_arrived)

        central = QWidget()
        self.setCentralWidget(central)
        lay = QHBoxLayout(central)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        # 左侧导航
        self.nav = QListWidget()
        self.nav.setFixedWidth(200)
        self.nav.setObjectName("nav")
        for title, _page_cls, _svc in PAGES:
            item = QListWidgetItem(title)
            item.setSizeHint(QSize(200, 40))
            self.nav.addItem(item)
        self.nav.currentRowChanged.connect(self._switch_page)
        lay.addWidget(self.nav)

        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.Shape.VLine)
        line.setObjectName("navLine")
        lay.addWidget(line)

        # 右侧页面堆栈
        self.stack = QStackedWidget()
        self.pages: list[QWidget] = []
        services = getattr(ctx, "services", None) if ctx else None
        for title, page_cls, svc_name in PAGES:
            service = getattr(services, svc_name) if services and svc_name else None
            page = page_cls(service=service)
            self.pages.append(page)
            self.stack.addWidget(page)
        lay.addWidget(self.stack, stretch=1)

        self.nav.setCurrentRow(0)

    # ------------------------------------------------------------------ slots
    def _switch_page(self, row: int) -> None:
        if 0 <= row < self.stack.count():
            self.stack.setCurrentIndex(row)

    def _on_event_arrived(self, event_type: str, payload: dict) -> None:
        """业务事件到达：刷新当前页面（子类可绑定具体刷新逻辑）。"""
        current = self.stack.currentWidget()
        refresh = getattr(current, "refresh_from_event", None)
        if callable(refresh):
            try:
                refresh(event_type, payload)
            except Exception:  # noqa: BLE001
                pass
