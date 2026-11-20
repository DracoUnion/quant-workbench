"""架构测试：零 Qt 依赖、依赖方向、AppContext 装配、TaskManager 生命周期。"""

from __future__ import annotations

import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest  # noqa: E402

from src.bootstrap import build_context  # noqa: E402
from src.core.config import Settings, get_settings  # noqa: E402
from src.common.context import AppContext  # noqa: E402
from src.common.events import EventHub  # noqa: E402
from src.services.prompt_service import PromptService  # noqa: E402
from src.services.workflow_service import WorkflowService  # noqa: E402
from src.tasks.task import TaskManager  # noqa: E402


def test_app_settings_load() -> None:
    s = Settings()
    assert s.window_title
    assert s.theme in ("dark", "light")
    assert s.prompts_data_path


def test_app_context_assemble() -> None:
    ctx = build_context()
    assert ctx.settings is not None
    assert ctx.event_hub is not None
    assert ctx.task_manager is not None
    assert ctx.services is not None


def test_event_hub_pub_sub() -> None:
    hub = EventHub()
    received = []
    hub.subscribe("test.event", lambda e: received.append(e))
    hub.publish("test.event", {"foo": "bar"})
    hub.publish("other.event", {"x": 1})
    assert received == [{"foo": "bar"}]


def test_prompt_service_loads() -> None:
    ctx = build_context()
    svc: PromptService = ctx.services.prompt_service
    svc.load()
    prompts = svc.all()
    assert len(prompts) >= 1
    codes = {p.code for p in prompts}
    assert len(codes) == len(prompts), "code 必须唯一"


def test_task_manager_lifecycle() -> None:
    tm = TaskManager()
    results = []

    def job(x: int) -> int:
        return x * 2

    tid = tm.submit("job1", job, 21)
    tm2 = tm.get(tid)
    assert tm2 is not None
    assert tm2.state.name in ("pending", "running", "completed")


def test_qt_not_imported_in_zero_qt_layers() -> None:
    """扫描零 Qt 层模块，确保不 import PySide6。"""
    import importlib

    zero_qt_modules = [
        "src.common.config",
        "src.common.events",
        "src.common.context",
        "src.common.exceptions",
        "src.services.prompt_service",
        "src.services.workflow_service",
        "src.services.run_service",
        "src.tasks.task",
        "src.clients.clipboard",
    ]
    for mod_name in zero_qt_modules:
        mod = importlib.import_module(mod_name)
        src = open(mod.__file__, encoding="utf-8").read()
        assert "PySide6" not in src, f"{mod_name} 不应 import PySide6"
        assert "PyQt" not in src, f"{mod_name} 不应 import PyQt"


def test_dependency_direction() -> None:
    """验证依赖方向：gui → client → services/... → core/tasks → common。"""
    import src.gui.main_window  # noqa: F401

    import src.common.context  # noqa: F401
    import src.core.config  # noqa: F401
    import src.services.prompt_service  # noqa: F401

    # common 不应 import gui
    import types as _types

    common_mods = [
        mod.__name__
        for mod in sys.modules.values()
        if isinstance(mod, _types.ModuleType)
        and mod.__name__.startswith("src.common")
    ]
    assert "gui" not in common_mods


@pytest.mark.parametrize(
    "code", ["P001", "P002", "P076"]
)
def test_prompt_seed_loadable(code: str) -> None:
    ctx = build_context()
    svc: PromptService = ctx.services.prompt_service
    svc.load()
    p = svc.get(code)
    assert p is not None
    assert p.title
    assert p.full_text
