"""投研页面。"""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class ResearchPage(QWidget):
    """投研页面。"""

    def __init__(self, service=None) -> None:
        super().__init__()
        lay = QVBoxLayout(self)
        lay.addWidget(QLabel("投研"))
        lay.addWidget(QLabel("财报提取结果、质疑清单、价值清单、现金流诊断"))
        lay.addStretch(1)
