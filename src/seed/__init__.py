"""种子数据入口：python -m src.seed"""

from __future__ import annotations

import sys

from . import prompts as _prompts  # noqa: F401  # 触发提示词种子常量（若有）
from . import workflows as _workflows  # noqa: F401  # 触发工作流种子常量
from . import demo as _demo  # noqa: F401


def main() -> None:
    _demo.seed_demo()


if __name__ == "__main__":
    main()
