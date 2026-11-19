"""主窗口：顶栏 + QSplitter（QListWidget 导航 + QStackedWidget）。

参照 tiange 架构：唯一 PySide6 页面层，页面经 ctx.services 访问服务。
"""

from __future__ import annotations

from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QSplitter,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from bootstrap import build_context
from common import (
    EV_PROMPT_COPIED,
    EV_PROMPT_FAVORITE_TOGGLED,
    EventHub,
)
from services.prompt_service import PromptService
from ui.pages import (
    FavoritesPage,
    PromptDetailPage,
    PromptListPage,
    SearchPage,
)
from ui.theme import load_qss


class MainWindow(QMainWindow):
    def __init__(self, ctx) -> None:
        super().__init__()
        self.ctx = ctx
        self.settings = ctx.settings
        self.event_hub: EventHub = ctx.event_hub
        self.service: PromptService = ctx.service_facade.prompt_service

        self._current_category: str | None = None
        self._source_stack_index = 0  # 记录 detail 页返回时应回到的页面索引

        self._build_ui()
        self._bind_events()
        self._load_categories()

        # 应用主题
        self.setStyleSheet(load_qss(self.settings.theme))

        # 打开首个分类（触发 currentItemChanged -> _on_nav_changed）
        cats = self.service.categories()
        if cats:
            self.nav_list.setCurrentRow(0)

    # ------------------------------------------------------------------ UI
    def _build_ui(self) -> None:
        self.setWindowTitle(self.settings.window_title)

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # 顶栏
        top = QFrame()
        top.setObjectName("TopBar")
        top_lay = QHBoxLayout(top)
        top_lay.setContentsMargins(20, 0, 20, 0)
        self.title_lbl = QLabel(self.settings.window_title)
        self.title_lbl.setObjectName("TitleLabel")
        self.sub_lbl = QLabel("零代码 AI 金融智能体 — 提示词模板与工作流检索工具")
        self.sub_lbl.setObjectName("SubtitleLabel")
        top_lay.addWidget(self.title_lbl)
        top_lay.addWidget(self.sub_lbl)
        top_lay.addStretch(1)
        root.addWidget(top)

        # 分割器：左侧导航 | 右侧页面
        splitter = QSplitter(Qt.Horizontal)

        # 左侧导航
        self.nav_list = QListWidget()
        self.nav_list.setObjectName("NavList")
        self.nav_list.setFixedWidth(220)
        self.nav_list.setSpacing(4)
        splitter.addWidget(self.nav_list)

        # 右侧页面栈
        self.stack = QStackedWidget()
        self.stack.setObjectName("PageContainer")

        self.list_page = PromptListPage(self.service)
        self.detail_page = PromptDetailPage(self.service)
        self.search_page = SearchPage(self.service)
        self.fav_page = FavoritesPage(self.service)

        self.stack.addWidget(self.list_page)   # index 0
        self.stack.addWidget(self.detail_page)  # index 1
        self.stack.addWidget(self.search_page)  # index 2
        self.stack.addWidget(self.fav_page)     # index 3
        splitter.addWidget(self.stack)

        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        root.addWidget(splitter, 1)

    # ------------------------------------------------------------------ 绑定
    def _bind_events(self) -> None:
        # 左侧导航切换
        self.nav_list.currentItemChanged.connect(self._on_nav_changed)

        # 列表页：选卡片 → 详情
        self.list_page.prompt_selected.connect(self._open_detail)
        self.list_page.back_requested.connect(self._go_list)
        self.list_page.favorite_toggled.connect(self._on_favorite_toggled)

        # 详情页：返回 / 收藏 / 复制
        self.detail_page.back_requested.connect(self._go_back_from_detail)
        self.detail_page.favorite_toggled.connect(self._on_favorite_toggled)
        self.detail_page.copy_requested.connect(self._on_copy)

        # 搜索页
        self.search_page.prompt_selected.connect(self._open_detail)
        self.search_page.back_requested.connect(self._go_list)

        # 收藏页
        self.fav_page.prompt_selected.connect(self._open_detail)
        self.fav_page.back_requested.connect(self._go_list)
        self.fav_page.favorite_toggled.connect(self._on_favorite_toggled)

        # 全局事件总线：复制 / 收藏变更
        self.event_hub.subscribe(EV_PROMPT_COPIED, self._on_event_copied)
        self.event_hub.subscribe(EV_PROMPT_FAVORITE_TOGGLED, self._on_event_favorite)

    # ------------------------------------------------------------------ 分类加载
    def _load_categories(self) -> None:
        self.nav_list.clear()
        # “全部”项
        all_item = QListWidgetItem("全部提示词")
        all_item.setData(Qt.UserRole, "__all__")
        self.nav_list.addItem(all_item)
        for cat in self.service.categories():
            item = QListWidgetItem(cat)
            item.setData(Qt.UserRole, cat)
            self.nav_list.addItem(item)
        # 功能项
        for label, data in [("🔍 全文搜索", "__search__"), ("⭐ 我的收藏", "__fav__")]:
            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, data)
            self.nav_list.addItem(item)

    def _on_nav_changed(self, cur: QListWidgetItem, prev: QListWidgetItem) -> None:
        if cur is None:
            return
        data = cur.data(Qt.UserRole)
        if data == "__search__":
            self.stack.setCurrentIndex(2)
            self.search_page._search()
            return
        if data == "__fav__":
            self.stack.setCurrentIndex(3)
            self.fav_page.refresh()
            return
        # 分类项
        cat = "全部提示词" if data == "__all__" else data
        if cat == "全部提示词":
            # 显示全部：用搜索空字符串等价于全部
            self.stack.setCurrentIndex(2)
            self.search_page.search_input.clear()
            self.search_page._search()
            self._current_category = None
        else:
            self.stack.setCurrentIndex(0)
            self._source_stack_index = 0
            self.list_page.set_category(cat)
            self._current_category = cat

    # ------------------------------------------------------------------ 页面跳转
    def _open_detail(self, prompt_id: str) -> None:
        prompt = self.service.get(prompt_id)
        if not prompt:
            return
        # 记录来源：若当前在列表/搜索/收藏，detail 页返回应回到对应页面
        cur_idx = self.stack.currentIndex()
        self._source_stack_index = cur_idx
        self.detail_page.set_prompt(prompt)
        self.stack.setCurrentIndex(1)

    def _go_list(self) -> None:
        self.stack.setCurrentIndex(0)
        if self._current_category:
            self.list_page.set_category(self._current_category)
        # 让左侧导航高亮对应分类
        self._highlight_nav(self._current_category)

    def _go_back_from_detail(self) -> None:
        self.stack.setCurrentIndex(self._source_stack_index)

    def _highlight_nav(self, category: str | None) -> None:
        if not category:
            return
        for i in range(self.nav_list.count()):
            item = self.nav_list.item(i)
            if item.data(Qt.UserRole) == category:
                self.nav_list.setCurrentItem(item)
                break

    # ------------------------------------------------------------------ 事件
    def _on_favorite_toggled(self, prompt_id: str, checked: bool) -> None:
        self.event_hub.publish(EV_PROMPT_FAVORITE_TOGGLED, prompt_id, checked)
        # 刷新收藏页与列表页星标
        self.fav_page.refresh()
        self.list_page.refresh()

    def _on_copy(self, prompt_id: str) -> None:
        self.event_hub.publish(EV_PROMPT_COPIED, prompt_id)

    def _on_event_copied(self, prompt_id: str) -> None:
        # 可在此显示状态提示（简化：仅日志）
        pass

    def _on_event_favorite(self, prompt_id: str, checked: bool) -> None:
        pass

    def sizeHint(self) -> QSize:  # noqa: D401
        return QSize(self.settings.window_width, self.settings.window_height)


def run() -> None:
    ctx = build_context()
    from PySide6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    app.setApplicationName(ctx.settings.window_title)
    win = MainWindow(ctx=ctx)
    win.resize(ctx.settings.window_width, ctx.settings.window_height)
    win.show()
    sys.exit(app.exec())
