"""入口：build_context() → QApplication → MainWindow(ctx) → app.exec()。

参照 tiange 架构：唯一 PySide6 依赖在 ui/，此处仅负责组装。
"""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from bootstrap import build_context
from ui.main_window import MainWindow


def main() -> int:
    # 1. 构建零 Qt 上下文（Settings + EventHub + TaskManager + ServiceFacade）
    ctx = build_context()

    # 2. QApplication + QSS（ui.theme）
    app = QApplication(sys.argv)
    app.setApplicationName(ctx.settings.window_title)

    # 3. 主窗口，页面经 ctx.services 访问服务
    window = MainWindow(ctx=ctx)
    window.resize(ctx.settings.window_width, ctx.settings.window_height)
    window.show()

    # 4. app.exec()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
