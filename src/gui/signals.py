"""短线信号页面。"""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class SignalsPage(QWidget):
    """短线信号页面。"""

    def __init__(self, service=None) -> None:
        super().__init__()
        lay = QVBoxLayout(self)
        lay.addWidget(QLabel("短线信号"))
        lay.addWidget(QLabel("题材简报、龙虎榜、早盘/盘中决策板、阿尔法警报"))
        lay.addStretch(1)
