"""零 Qt 公共层。"""

from .config import AppSettings, get_settings, settings
from .context import AppContext
from .events import (
    EV_APP_READY,
    EV_PROMPT_COPIED,
    EV_PROMPT_FAVORITE_TOGGLED,
    EV_PROMPT_SELECTED,
    EV_SEARCH_QUERY_CHANGED,
    EventHub,
)
from .exceptions import AppError, ConfigError, PromptError, ServiceError

__all__ = [
    "AppSettings",
    "AppContext",
    "EventHub",
    "AppError",
    "ConfigError",
    "PromptError",
    "ServiceError",
    "get_settings",
    "settings",
    "EV_APP_READY",
    "EV_PROMPT_SELECTED",
    "EV_PROMPT_COPIED",
    "EV_PROMPT_FAVORITE_TOGGLED",
    "EV_SEARCH_QUERY_CHANGED",
]
