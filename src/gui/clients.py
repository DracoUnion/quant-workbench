"""客户经营页面。"""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class ClientsPage(QWidget):
    """客户经营页面。"""

    def __init__(self, service=None) -> None:
        super().__init__()
        lay = QVBoxLayout(self)
        lay.addWidget(QLabel("客户经营"))
        lay.addWidget(QLabel("画像、Client-360、KYC、话术"))
        lay.addStretch(1)
