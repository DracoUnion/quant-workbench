"""零 Qt 配置层。

仅从环境变量与默认值读取配置，不依赖 Qt / 数据库 / QSettings。
可被 ui 层通过 AppContext 统一访问。
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass
class AppSettings:
    """应用配置。"""

    # 文档 / 数据源
    prompts_doc_path: str = os.getenv("PROMPTS_DOC_PATH", "doc/提示词与工作流.md")
    prompts_data_path: str = os.getenv("PROMPTS_DATA_PATH", "data/prompts.json")

    # 窗口
    window_title: str = os.getenv("APP_WINDOW_TITLE", "提示词与工作流 — 零代码 AI 金融智能体")
    window_width: int = int(os.getenv("APP_WINDOW_WIDTH", "1200"))
    window_height: int = int(os.getenv("APP_WINDOW_HEIGHT", "800"))

    # 主题
    theme: str = os.getenv("APP_THEME", "dark")  # dark / light

    # 剪贴板
    clipboard_enabled: bool = os.getenv("APP_CLIPBOARD_ENABLED", "true").lower() == "true"

    @classmethod
    def from_env(cls) -> "AppSettings":
        return cls()


# 全局单例，供 bootstrap 注入
settings: AppSettings | None = None


def get_settings() -> AppSettings:
    global settings
    if settings is None:
        settings = AppSettings.from_env()
    return settings
