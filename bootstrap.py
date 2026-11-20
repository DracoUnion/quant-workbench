"""入口兼容层：重导出 src.bootstrap.build_context。

tests 与旧脚本通过项目根路径导入 bootstrap，此处保持该入口可用，
底层统一走 src/ 的零 Qt 装配。
"""

from src.bootstrap import build_context  # noqa: F401

__all__ = ["build_context"]
