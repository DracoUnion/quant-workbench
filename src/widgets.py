"""通用小部件（零业务逻辑，纯 UI 素材）。"""


from __future__ import annotations

from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout


class Card(QFrame):
    """卡片容器。"""

    def __init__(self, title: str = "") -> None:
        super().__init__()
        self.setObjectName("card")
        lay = QVBoxLayout(self)
        if title:
            lab = QLabel(title)
            lab.setObjectName("cardTitle")
            lay.addWidget(lay) if False else None
            lay.addWidget(lab)
        self.content = QWidget()
        self.content_lay = QVBoxLayout(self.content)
        lay.addWidget(self.content)

    def add_widget(self, widget: QLabel) -> None:
        self.content_lay.addWidget(widget)
