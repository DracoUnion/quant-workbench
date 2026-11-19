"""通用 UI 组件。唯一 PySide6 依赖层。"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QClipboard
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class PromptCard(QFrame):
    """单条提示词卡片：标题、描述、分类、收藏星标、复制按钮。"""

    clicked = Signal(str)  # 发出 prompt_id

    def __init__(self, prompt) -> None:
        super().__init__()
        self.setObjectName("PromptCard")
        self.setCursor(Qt.PointingHandCursor)
        self.prompt = prompt

        lay = QVBoxLayout(self)
        lay.setContentsMargins(14, 14, 14, 14)
        lay.setSpacing(8)

        # 顶行：标题 + 收藏
        top = QHBoxLayout()
        top.setSpacing(8)
        self.title_lbl = QLabel(prompt.title)
        self.title_lbl.setObjectName("PromptTitle")
        self.title_lbl.setWordWrap(True)
        self.star_btn = QPushButton("★" if prompt.favorite else "☆")
        self.star_btn.setObjectName("FavoriteStar")
        self.star_btn.setCheckable(True)
        self.star_btn.setChecked(prompt.favorite)
        self.star_btn.clicked.connect(self._on_star)
        top.addWidget(self.title_lbl, 1)
        top.addWidget(self.star_btn)
        lay.addLayout(top)

        # 分类元信息
        meta = QLabel(f"{prompt.category}  ›  {prompt.sub_category}")
        meta.setObjectName("PromptMeta")
        lay.addWidget(meta)

        # 描述
        desc = QLabel(prompt.description)
        desc.setObjectName("PromptDesc")
        desc.setWordWrap(True)
        lay.addWidget(desc)

        # 底行：复制按钮
        bottom = QHBoxLayout()
        self.copy_btn = QPushButton("复制全文")
        self.copy_btn.setObjectName("SecondaryButton")
        self.copy_btn.clicked.connect(self._on_copy)
        bottom.addStretch(1)
        bottom.addWidget(self.copy_btn)
        lay.addLayout(bottom)

    def mousePressEvent(self, event) -> None:  # noqa: D401
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.prompt.id)
        super().mousePressEvent(event)

    def _on_star(self, checked: bool) -> None:
        self.prompt.favorite = checked
        self.star_btn.setText("★" if checked else "☆")

    def _on_copy(self) -> None:
        clipboard: QClipboard = QApplication.clipboard()
        clipboard.setText(self.prompt.full_text)
        self.copy_btn.setText("已复制")
        self.copy_btn.setEnabled(False)


class CopyButton(QPushButton):
    """点击将指定文本复制到剪贴板。"""

    def __init__(self, text: str, label: str = "复制") -> None:
        super().__init__(label)
        self._text = text
        self.clicked.connect(self._copy)

    def _copy(self) -> None:
        QApplication.clipboard().setText(self._text)
        self.setText("已复制")
        self.setEnabled(False)
