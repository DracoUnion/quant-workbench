"""运行中心页面。"""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class RunsPage(QWidget):
    """运行中心页面。"""

    def __init__(self, service=None) -> None:
        super().__init__()
        lay = QVBoxLayout(self)
        lay.addWidget(QLabel("运行中心"))
        lay.addWidget(QLabel("run 列表、节点时间线、日志、artifact、重跑、终止"))
        lay.addStretch(1)
