"""合规页面。"""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class CompliancePage(QWidget):
    """合规页面。"""

    def __init__(self, service=None) -> None:
        super().__init__()
        lay = QVBoxLayout(self)
        lay.addWidget(QLabel("合规"))
        lay.addWidget(QLabel("审查单、脱敏工具、交易安全熔断状态"))
        lay.addStretch(1)
