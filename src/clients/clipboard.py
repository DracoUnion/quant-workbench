"""零 Qt 外部依赖层。

本层不导入任何 Qt 模块，仅定义与外部系统交互的抽象协议。
具体的 Qt 实现由 ui 层提供并注入。
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class ClipboardClient(ABC):
    """剪贴板抽象协议。"""

    @abstractmethod
    def copy_text(self, text: str) -> bool:
        """将文本写入剪贴板，成功返回 True。"""
        raise NotImplementedError

    @abstractmethod
    def is_available(self) -> bool:
        """剪贴板是否可用。"""
        raise NotImplementedError
