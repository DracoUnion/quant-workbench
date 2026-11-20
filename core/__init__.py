"""核心配置层兼容入口（tests 仅导入此模块）。"""

from src.core.config import Settings, get_settings  # noqa: F401

settings = get_settings()

__all__ = ["Settings", "get_settings", "settings"]
