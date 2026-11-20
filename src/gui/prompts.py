"""提示词工坊页面：P001-P076 列表、参数表单、版本 diff、试运行。"""


from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class PromptsPage(QWidget):
    """提示词工坊页面。"""

    def __init__(self, service=None) -> None:
        super().__init__()
        self.service = service
        self._prompts = []

        lay = QVBoxLayout(self)

        top = QHBoxLayout()
        top.addWidget(QLabel("提示词工坊（P001-P076）"))
        self.search = QLineEdit()
        self.search.setPlaceholderText("按编号/标题/分类搜索……")
        self.search.textChanged.connect(self._filter)
        top.addWidget(self.search)
        lay.addLayout(top)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        self.list = QListWidget()
        self.list.currentRowChanged.connect(self._on_select)
        splitter.addWidget(self.list)

        self.detail = QTextEdit()
        self.detail.setReadOnly(True)
        splitter.addWidget(self.detail)
        splitter.setStretchFactor(1, 1)

        lay.addWidget(splitter)

        btns = QHBoxLayout()
        self.btn_render = QPushButton("试运行（渲染）")
        self.btn_render.clicked.connect(self._render)
        self.btn_copy = QPushButton("复制正文")
        self.btn_copy.clicked.connect(self._copy)
        btns.addWidget(self.btn_render)
        btns.addWidget(self.btn_copy)
        btns.addStretch(1)
        lay.addLayout(btns)

        self._reload()

    # ------------------------------------------------------------------ data
    def _reload(self) -> None:
        self._prompts = []
        if self.service is not None:
            try:
                self.service.load()
                self._prompts = self.service.all()
            except Exception:  # noqa: BLE001
                self._prompts = []
        self._filter()

    def _filter(self) -> None:
        q = self.search.text().lower()
        self.list.clear()
        for p in self._prompts:
            haystack = f"{p.code} {p.title} {p.category} {p.sub_category}".lower()
            if q in haystack:
                item = QListWidgetItem(f"{p.code}  {p.title}")
                item.setData(Qt.ItemDataRole.UserRole, p.code)
                self.list.addItem(item)
        if self.list.count() > 0:
            self.list.setCurrentRow(0)

    def _on_select(self, row: int) -> None:
        if row < 0:
            return
        item = self.list.item(row)
        code = item.data(Qt.ItemDataRole.UserRole)
        p = next((p for p in self._prompts if p.code == code), None)
        if p is None:
            return
        lines = [
            f"# {p.title}",
            f"编号：{p.code}",
            f"分类：{p.category} / {p.sub_category}",
            f"版本：{p.version}",
            "",
            p.full_text or p.body or "",
        ]
        self.detail.setPlainText("\n".join(lines))

    def _render(self) -> None:
        item = self.list.currentItem()
        if not item or self.service is None:
            return
        code = item.data(Qt.ItemDataRole.UserRole)
        try:
            text = self.service.render(code, {})
            QMessageBox.information(self, f"渲染：{code}", text[:4000])
        except Exception as exc:  # noqa: BLE001
            QMessageBox.warning(self, "渲染失败", str(exc))

    def _copy(self) -> None:
        item = self.list.currentItem()
        if not item:
            return
        code = item.data(Qt.ItemDataRole.UserRole)
        p = next((p for p in self._prompts if p.code == code), None)
        if p is None:
            return
        clipboard = QApplication.clipboard()
        clipboard.setText(p.full_text or p.body or "")

    def refresh_from_event(self, event_type: str, payload: dict) -> None:
        self._reload()


# 迟导入，避免模块级拿不到 QApplication
from PySide6.QtWidgets import QApplication  # noqa: E402
