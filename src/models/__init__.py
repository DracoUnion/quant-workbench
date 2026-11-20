"""数据模型包：导入全部模型，注册到 Base.metadata。"""

from . import (  # noqa: F401
    base,
    knowledge,
    office_platform,
    portfolio,
    prompt,
    research,
    run,
    signal_event_client_compliance,
    workflow,
)

__all__ = [
    "base",
    "knowledge",
    "office_platform",
    "portfolio",
    "prompt",
    "research",
    "run",
    "signal_event_client_compliance",
    "workflow",
]
