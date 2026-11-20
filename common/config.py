"""零 Qt 配置层（兼容旧导入路径）。

AppSettings 与 get_settings 委托 src.core.config，保持与 tests 的
导入路径 `from common.config import AppSettings, get_settings` 可用。
"""

from src.core.config import Settings, get_settings  # noqa: F401

AppSettings = Settings

# 向后兼容：供 bootstrap 等旧代码直接 import settings
settings = get_settings()

__all__ = ["AppSettings", "get_settings", "settings"]
