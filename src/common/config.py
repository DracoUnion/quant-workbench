"""零 Qt 配置层兼容入口：委托 src.core.config。"""

from src.core.config import Settings, get_settings  # noqa: F401

AppSettings = Settings

# 向后兼容：供 bootstrap 等旧代码直接 import settings
settings = get_settings()

__all__ = ["AppSettings", "Settings", "get_settings", "settings"]
