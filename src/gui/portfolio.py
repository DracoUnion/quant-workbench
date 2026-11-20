"""组合风控页面。"""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class PortfolioPage(QWidget):
    """组合风控页面。"""

    def __init__(self, service=None) -> None:
        super().__init__()
        lay = QVBoxLayout(self)
        lay.addWidget(QLabel("组合风控"))
        lay.addWidget(QLabel("持仓、风险快照、预警、再平衡建议"))
        lay.addStretch(1)
