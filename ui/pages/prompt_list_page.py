"""提示词分类列表页。唯一 PySide6 依赖。"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from services.prompt_service import Prompt, PromptService
from ui.widgets import PromptCard


class PromptListPage(QWidget):
    """显示某一分类下的全部提示词卡片。"""

    prompt_selected = Signal(str)        # prompt_id
    back_requested = Signal()            # 返回分类首页
    favorite_toggled = Signal(str, bool) # prompt_id, 是否收藏

    def __init__(self, service: PromptService) -> None:
        super().__init__()
        self.service = service
        self.category: str | None = None

        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(12)

        # 顶行：返回 + 分类标题
        top = QHBoxLayout()
        self.back_btn = QPushButton("← 返回分类")
        self.back_btn.setObjectName("SecondaryButton")
        self.back_btn.clicked.connect(self.back_requested.emit)
        self.category_lbl = QLabel()
        self.category_lbl.setObjectName("CategoryHeader")
        top.addWidget(self.back_btn)
        top.addWidget(self.category_lbl, 1)
        lay.addLayout(top)

        # 卡片列表（垂直滚动）
        self.list_widget = QListWidget()
        self.list_widget.setObjectName("NavList")
        self.list_widget.setSpacing(6)
        self.list_widget.setStyleSheet("QListWidget { border: none; outline: none; background: transparent; }")
        lay.addWidget(self.list_widget, 1)

    # ------------------------------------------------------------------ public
    def set_category(self, category: str) -> None:
        self.category = category
        self.category_lbl.setText(category)
        self._reload()

    def _reload(self) -> None:
        self.list_widget.clear()
        prompts = self.service.by_category(self.category) if self.category else []
        if not prompts:
            empty = QLabel("暂无提示词模板")
            empty.setObjectName("EmptyState")
            self.list_widget.addItem(QListWidgetItem())
            self.list_widget.setItemWidget(self.list_widget.item(0), empty)
            return
        for p in prompts:
            item = QListWidgetItem()
            item.setSizeHint(p.sizeHint() if hasattr(p, "sizeHint") else None)  # type: ignore[attr-defined]
            card = PromptCard(p)
            card.clicked.connect(self.prompt_selected.emit)
            # 将收藏变更向上冒泡
            card.star_btn.clicked.connect(
                lambda checked, pid=p.id: self.favorite_toggled.emit(pid, checked)
            )
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, card)

    def refresh(self) -> None:
        self._reload()
