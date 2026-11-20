"""UI 主窗口兼容入口：重导出 src.main_window.MainWindow（旧 tiange 残留，不再作为主入口）。"""

from src.main_window import MainWindow  # noqa: F401

__all__ = ["MainWindow"]
