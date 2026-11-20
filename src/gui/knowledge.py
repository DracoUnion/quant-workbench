"""知识库页面。"""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class KnowledgePage(QWidget):
    """知识库页面。"""

    def __init__(self, service=None) -> None:
        super().__init__()
        lay = QVBoxLayout(self)
        lay.addWidget(QLabel("知识库"))
        lay.addWidget(QLabel("文档导入、清洗预览、chunk、检索测试、向量配置"))
        lay.addStretch(1)
