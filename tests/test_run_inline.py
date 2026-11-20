"""inline 执行、独立 Session、事件 sink 测试。"""

from __future__ import annotations

import os
import sys


os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from src.bootstrap import build_context  # noqa: E402


def test_inline_run() -> None:
    ctx = build_context()
    assert ctx is not None
    assert ctx.settings is not None
    assert ctx.event_hub is not None
    assert ctx.task_manager is not None
    assert ctx.services is not None
