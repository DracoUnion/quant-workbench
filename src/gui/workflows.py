"""工作流编排页面。"""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class WorkflowsPage(QWidget):
    """工作流编排页面。"""

    def __init__(self, service=None) -> None:
        super().__init__()
        lay = QVBoxLayout(self)
        lay.addWidget(QLabel("工作流编排"))
        lay.addWidget(QLabel("DAG 画布、节点配置、校验、发布"))
        lay.addStretch(1)
