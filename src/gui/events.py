"""事件套利页面。"""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class EventsPage(QWidget):
    """事件套利页面。"""

    def __init__(self, service=None) -> None:
        super().__init__()
        lay = QVBoxLayout(self)
        lay.addWidget(QLabel("事件套利"))
        lay.addWidget(QLabel("事件卡、供应链、内部人、研报情绪、套利信号"))
        lay.addStretch(1)
