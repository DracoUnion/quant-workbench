"""收藏页。唯一 PySide6 依赖。"""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from services.prompt_service import PromptService
from ui.widgets import PromptCard


class FavoritesPage(QWidget):
    """展示已收藏的提示词，支持取消收藏并跳转详情。"""

    prompt_selected = Signal(str)
    back_requested = Signal()
    favorite_toggled = Signal(str, bool)

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
        self.title_lbl = QLabel("我的收藏")
        self.title_lbl.setObjectName("CategoryHeader")
        top.addWidget(self.back_btn)
        top.addWidget(self.title_lbl, 1)
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

    def refresh(self) -> None:
        favs = self.service.favorites()
        self.list_widget.clear()
        self.hint_lbl.setText(f"共 {len(favs)} 条已收藏")
        if not favs:
            empty = QLabel("暂无收藏，在提示词卡片上点击 ☆ 收藏")
            empty.setObjectName("EmptyState")
            self.list_widget.addItem(QListWidgetItem())
            self.list_widget.setItemWidget(self.list_widget.item(0), empty)
            return
        for p in favs:
            item = QListWidgetItem()
            card = PromptCard(p)
            card.clicked.connect(self.prompt_selected.emit)
            card.star_btn.clicked.connect(
                lambda checked, pid=p.id: self.favorite_toggled.emit(pid, checked)
            )
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, card)
