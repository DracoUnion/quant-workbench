"""办公自动化页面。"""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class OfficePage(QWidget):
    """办公自动化页面。"""

    def __init__(self, service=None) -> None:
        super().__init__()
        lay = QVBoxLayout(self)
        lay.addWidget(QLabel("办公自动化"))
        lay.addWidget(QLabel("周报、月报、会议纪要、行动项"))
        lay.addStretch(1)
