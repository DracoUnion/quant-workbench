"""工作台总览页面。"""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class DashboardPage(QWidget):
    """工作台总览页面。"""

    def __init__(self, service=None) -> None:
        super().__init__()
        lay = QVBoxLayout(self)
        lay.addWidget(QLabel("工作台总览"))
        lay.addWidget(QLabel("运行中 run、待确认闸门、预警卡片、快捷入口"))
        lay.addStretch(1)
