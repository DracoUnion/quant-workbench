"""提示词详情页：完整正文、复制、收藏、返回。唯一 PySide6 依赖。"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from services.prompt_service import Prompt, PromptService
from ui.widgets import CopyButton


class PromptDetailPage(QWidget):
    """单条提示词详情：标题、元信息、完整 Markdown 正文、操作按钮。"""

    back_requested = Signal()
    favorite_toggled = Signal(str, bool)
    copy_requested = Signal(str)

    def __init__(self, service: PromptService) -> None:
        super().__init__()
        self.service = service
        self._prompt: Prompt | None = None

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        # 顶部操作栏
        top = QHBoxLayout()
        top.setContentsMargins(16, 12, 16, 12)
        top.setSpacing(10)
        self.back_btn = QPushButton("← 返回")
        self.back_btn.setObjectName("SecondaryButton")
        self.back_btn.clicked.connect(self.back_requested.emit)
        self.title_lbl = QLabel()
        self.title_lbl.setObjectName("DetailTitle")
        self.star_btn = QPushButton("☆")
        self.star_btn.setObjectName("FavoriteStar")
        self.star_btn.setCheckable(True)
        self.star_btn.clicked.connect(self._on_star)
        self.copy_btn = QPushButton("复制全文")
        self.copy_btn.setObjectName("PrimaryButton")
        self.copy_btn.clicked.connect(self._on_copy)
        top.addWidget(self.back_btn)
        top.addWidget(self.title_lbl, 1)
        top.addWidget(self.star_btn)
        top.addWidget(self.copy_btn)
        lay.addLayout(top)

        # 元信息
        self.meta_lbl = QLabel()
        self.meta_lbl.setObjectName("DetailMeta")
        self.meta_lbl.setWordWrap(True)
        lay.addWidget(self.meta_lbl)

        # 正文滚动区
        scroll = QScrollArea()
        scroll.setObjectName("DetailView")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        self.body = QTextEdit()
        self.body.setReadOnly(True)
        self.body.setAcceptRichText(False)
        self.body.setPlainText("")
        scroll.setWidget(self.body)
        lay.addWidget(scroll, 1)

    # ------------------------------------------------------------------ public
    def set_prompt(self, prompt: Prompt) -> None:
        self._prompt = prompt
        self.title_lbl.setText(prompt.title)
        self.meta_lbl.setText(
            f"{prompt.category}  ›  {prompt.sub_category}   |   ID: {prompt.id}"
        )
        self.body.setPlainText(prompt.full_text)
        self.star_btn.setChecked(prompt.favorite)
        self.star_btn.setText("★" if prompt.favorite else "☆")
        self.copy_btn.setText("复制全文")
        self.copy_btn.setEnabled(True)

    # ------------------------------------------------------------------ slots
    def _on_star(self, checked: bool) -> None:
        if self._prompt:
            self.service.toggle_favorite(self._prompt.id)
            self.favorite_toggled.emit(self._prompt.id, checked)

    def _on_copy(self) -> None:
        if self._prompt:
            self.copy_requested.emit(self._prompt.id)
            from PySide6.QtWidgets import QApplication

            QApplication.clipboard().setText(self._prompt.full_text)
            self.copy_btn.setText("已复制")
            self.copy_btn.setEnabled(False)
