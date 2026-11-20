"""入口：bootstrap env → init_db → seed → QApplication → MainWindow → app.exec()。

参照任务书与 tiange 架构：唯一 PySide6 依赖在 gui/、main_window.py、widgets.py、theme.py，
此处仅负责组装，零 Qt 业务逻辑不 import PySide6。
"""


from __future__ import annotations

import os
import sys

from dotenv import load_dotenv

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def main() -> int:
    # 1. 加载 .env（桌面端强制 SQLite + inline 执行器）
    load_dotenv(os.path.join(ROOT, ".env"), override=False)

    # 2. 构建零 Qt 上下文
    from src.bootstrap import build_context

    ctx = build_context()

    # 3. 初始化数据库表并播种种子数据（幂等）
    from src.core.database import init_db

    init_db()
    from src.seed_service import seed_all

    seed_all(ctx)

    # 4. QApplication + 主窗口（唯一 PySide6 依赖层）
    from PySide6.QtWidgets import QApplication

    from src.main_window import MainWindow

    app = QApplication(sys.argv)
    app.setApplicationName(ctx.settings.window_title)

    from src.theme import apply_theme

    apply_theme(app, ctx.settings.theme)

    window = MainWindow(ctx=ctx)
    window.resize(ctx.settings.window_width, ctx.settings.window_height)
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
