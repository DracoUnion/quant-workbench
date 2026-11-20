"""零 Qt 架构层：ApiClient。

进程内直连 ServiceRegistry，保留 HTTP 接口形状（方法名、入参、返回 dict）。
模块级 get_client() 单例。
"""


from __future__ import annotations

from typing import Any

from .core.config import get_settings
from .core.database import session_scope
from .models.run import WorkflowRun
from .services.prompt_service import PromptService
from .services.run_service import RunService
from .services.workflow_service import WorkflowService


class ApiClient:
    """进程内直连 services 的客户端，保留 HTTP 接口形状。"""

    _instance: "ApiClient | None" = None

    def __new__(cls) -> "ApiClient":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if getattr(self, "_initialized", False):
            return
        self._initialized = True
        get_settings()
        self.prompt = PromptService()
        self.workflow = WorkflowService()
        self.run = RunService()

    # ---------- prompt 域 ----------
    def prompt_list(self) -> list[dict]:
        return [self._to_dict(p) for p in self.prompt.all()]

    def prompt_get(self, code: str) -> dict | None:
        p = self.prompt.get(code)
        return self._to_dict(p) if p else None

    def prompt_render(self, code: str, context: dict | None = None) -> str:
        return self.prompt.render(code, context)

    # ---------- workflow 域 ----------
    def workflow_list(self) -> list[dict]:
        return [self._to_dict(w) for w in self.workflow.all()]

    def workflow_get_by_code(self, code: str) -> dict | None:
        w = self.workflow.get_by_code(code)
        return self._to_dict(w) if w else None

    def workflow_validate_dag(self, code: str) -> list[str]:
        w = self.workflow.get_by_code(code)
        if not w:
            return [f"Workflow {code} not found"]
        return self.workflow.validate_dag(w)

    def workflow_topo_order(self, code: str) -> list[dict]:
        w = self.workflow.get_by_code(code)
        if not w:
            return []
        ordered = self.workflow.topological_order(w)
        return [self._to_dict(n) for n in ordered]

    # ---------- run 域 ----------
    def run_create(
        self,
        workflow_id: int,
        trigger_type: str = "manual",
        input_json: dict | None = None,
        context_json: dict | None = None,
        operator: str | None = None,
    ) -> int:
        return self.run.create_run(
            workflow_id=workflow_id,
            trigger_type=trigger_type,
            input_json=input_json,
            context_json=context_json,
            operator=operator,
        )

    def run_execute(self, run_id: int) -> None:
        self.run.run_workflow(run_id)

    def run_get(self, run_id: int) -> dict | None:
        with session_scope() as session:
            run = session.get(WorkflowRun, run_id)
            if not run:
                return None
            return {
                "id": run.id,
                "workflow_id": run.workflow_id,
                "status": run.status,
                "trigger_type": run.trigger_type,
                "input_json": run.input_json,
                "context_json": run.context_json,
                "started_at": run.started_at.isoformat() if run.started_at else None,
                "ended_at": run.ended_at.isoformat() if run.ended_at else None,
                "operator": run.operator,
            }

    # ---------------- internal ----------------
    @staticmethod
    def _to_dict(obj: Any) -> dict:
        if obj is None:
            return None
        if hasattr(obj, "__dict__"):
            d = dict(obj.__dict__)
            d.pop("_sa_instance_state", None)
            return d
        return obj
