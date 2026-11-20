"""设置页面。"""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class SettingsPage(QWidget):
    """设置页面。"""

    def __init__(self, service=None) -> None:
        super().__init__()
        lay = QVBoxLayout(self)
        lay.addWidget(QLabel("设置"))
        lay.addWidget(QLabel("模型、数据源、推送、执行器、日志"))
        lay.addStretch(1)
