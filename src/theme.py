"""主题与 QSS：dark / light 两套配色。"""


from __future__ import annotations

from PySide6.QtWidgets import QApplication


def load_qss(name: str = "styles.qss") -> str:
    """加载 qss 文件内容（供 ui 层调用）。"""
    from pathlib import Path

    path = Path(__file__).resolve().parent / name
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


def apply_theme(app: QApplication, theme: str = "dark") -> None:
    """为应用套用基础主题配色（零业务逻辑，纯视觉）。"""
    palette = app.palette()
    if theme == "light":
        palette.setColor(palette.ColorRole.Window, palette.color(palette.ColorRole.Window).lighter(110))
        app.setPalette(palette)
        app.setStyleSheet(load_qss("styles.qss") + "\n/* light overrides */")
    else:
        dark = """
        QMainWindow { background: #1e1e1e; }
        QWidget { background: #1e1e1e; color: #d4d4d4; }
        QListWidget { background: #252526; border: none; }
        QListWidget::item:selected { background: #37373d; color: #ffffff; }
        QTextEdit { background: #252526; color: #d4d4d4; border: 1px solid #3c3c3c; }
        QPushButton { background: #3c3c3c; color: #d4d4d4; border: 1px solid #555555; padding: 4px 12px; }
        QPushButton:hover { background: #505050; }
        QLineEdit { background: #252526; color: #d4d4d4; border: 1px solid #3c3c3c; padding: 4px; }
        QFrame#navLine { background: #3c3c3c; }
        """
        app.setStyleSheet(load_qss("styles.qss") + dark)
