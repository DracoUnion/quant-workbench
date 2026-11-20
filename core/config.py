"""核心配置层兼容入口：委托 src.core.config。"""

from src.core.config import Settings, get_settings  # noqa: F401

settings = get_settings()

__all__ = ["Settings", "get_settings", "settings"]
