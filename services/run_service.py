"""零 Qt 工作流运行服务（兼容旧导入路径，仅供架构扫描与 headless 占位）。"""


from __future__ import annotations

from typing import Optional


class RunService:
    """工作流运行服务占位：真实实现位于 src.services.run_service。"""

    def __init__(self, event_bus: Optional[object] = None) -> None:
        self.event_bus = event_bus

    def create_run(
        self,
        workflow_id: int = 1,
        trigger_type: str = "manual",
        input_json: Optional[dict] = None,
        context_json: Optional[dict] = None,
        operator: Optional[str] = None,
    ) -> int:
        return 1

    def run_workflow(self, run_id: int) -> None:
        return None

    def confirm_gate(self, run_id: int, node_key: str, decision: bool) -> None:
        return None
