"""零 Qt 公共层：事件总线与应用上下文。"""

from .context import AppContext
from .events import (
    EV_APP_READY,
    EventHub,
)

__all__ = [
    "AppContext",
    "EventHub",
    "EV_APP_READY",
]
