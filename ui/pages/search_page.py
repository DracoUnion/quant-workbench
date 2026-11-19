"""全文搜索页。唯一 PySide6 依赖。"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from services.prompt_service import PromptService
from ui.widgets import PromptCard


class SearchPage(QWidget):
    """关键词全文搜索，结果以卡片列表展示。"""

    prompt_selected = Signal(str)
    back_requested = Signal()

    def __init__(self, service: PromptService) -> None:
        super().__init__()
        self.service = service

        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(12)

        top = QHBoxLayout()
        self.back_btn = QPushButton("← 返回")
        self.back_btn.setObjectName("SecondaryButton")
        self.back_btn.clicked.connect(self.back_requested.emit)
        self.search_input = QLineEdit()
        self.search_input.setObjectName("SearchInput")
        self.search_input.setPlaceholderText("输入关键词搜索提示词……")
        self.search_input.returnPressed.connect(self._search)
        top.addWidget(self.back_btn)
        top.addWidget(self.search_input, 1)
        lay.addLayout(top)

        self.hint_lbl = QLabel()
        self.hint_lbl.setObjectName("PromptMeta")
        lay.addWidget(self.hint_lbl)

        self.list_widget = QListWidget()
        self.list_widget.setObjectName("NavList")
        self.list_widget.setSpacing(6)
        self.list_widget.setStyleSheet(
            "QListWidget { border: none; outline: none; background: transparent; }"
        )
        lay.addWidget(self.list_widget, 1)

    def _search(self) -> None:
        q = self.search_input.text().strip()
        results = self.service.search(q)
        self.list_widget.clear()
        self.hint_lbl.setText(f"共找到 {len(results)} 条结果" if q else "请输入关键词")
        if not results:
            empty = QLabel("无匹配结果")
            empty.setObjectName("EmptyState")
            self.list_widget.addItem(QListWidgetItem())
            self.list_widget.setItemWidget(self.list_widget.item(0), empty)
            return
        for p in results:
            item = QListWidgetItem()
            card = PromptCard(p)
            card.clicked.connect(self.prompt_selected.emit)
            card.star_btn.clicked.connect(
                lambda checked, pid=p.id: None  # 收藏变更在详情页处理；此处仅展示
            )
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, card)
