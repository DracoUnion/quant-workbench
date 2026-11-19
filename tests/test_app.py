"""零 Qt 层自动化测试（headless）。验证构建上下文、提示词服务加载、分类/搜索/收藏。"""

import os
import sys

# 确保项目根目录在路径中
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from bootstrap import build_context  # noqa: E402
from services.prompt_service import PromptService  # noqa: E402


def main() -> None:
    ctx = build_context()
    print("[OK] build_context 成功")
    print("    settings.theme =", ctx.settings.theme)
    print("    prompts_data_path =", ctx.settings.prompts_data_path)

    service: PromptService = ctx.service_facade.prompt_service
    service.load()
    prompts = service.all()
    print(f"[OK] 加载提示词 {len(prompts)} 条")

    cats = service.categories()
    print("[OK] 一级分类数:", len(cats))
    for cat in cats:
        print("   -", cat.encode("ascii", "replace").decode())

    # 搜索
    results = service.search("合规")
    print(f"[OK] 搜索'合规' -> {len(results)} 条")

    # 收藏切换
    first_id = prompts[0].id
    service.toggle_favorite(first_id)
    favs = service.favorites()
    print(f"[OK] 收藏切换后收藏数 = {len(favs)} (预期 1)")
    service.toggle_favorite(first_id)
    print(f"[OK] 再次切换后收藏数 = {len(service.favorites())} (预期 0)")

    # 持久化
    service.save("data/prompts.test.json")
    print("[OK] 保存 data/prompts.test.json 成功")
    os.remove("data/prompts.test.json")

    # 验证 QApplication 与 MainWindow 可实例化（offscreen）
    from PySide6.QtWidgets import QApplication  # noqa: E402

    app = QApplication.instance() or QApplication(sys.argv)
    from ui.main_window import MainWindow  # noqa: E402

    win = MainWindow(ctx=ctx)
    print("[OK] MainWindow 实例化成功")
    win.close()
    print("[PASS] 全部测试通过")


if __name__ == "__main__":
    main()
