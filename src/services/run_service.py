"""工作流运行服务：状态机、checkpoint、闸门、event sink、日志留痕。

零 Qt，可 headless 测试。每次数据库操作独立开启 Session，禁止跨线程共享。
"""

from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any

from ..core.database import session_scope
from ..core.events import EventBus
from ..models.run import (
    Artifact,
    NodeRun,
    RunEvent,
    WorkflowRun,
)

# 节点状态机
NODE_STATES = ("pending", "running", "blocked", "done", "failed", "killed")
# 流程状态机
RUN_STATES = ("pending", "running", "blocked", "done", "failed", "killed")


class RunService:
    """工作流运行服务：创建 run、调度、状态机、checkpoint、闸门。"""

    def __init__(self, event_bus: EventBus | None = None) -> None:
        self.event_bus = event_bus

    # ------------------------------------------------------------------ create run
    def create_run(
        self,
        workflow_id: int,
        trigger_type: str = "manual",
        input_json: dict | None = None,
        context_json: dict | None = None,
        operator: str | None = None,
    ) -> int:
        with session_scope() as session:
            wf = session.get(WorkflowDefinition, workflow_id)
            if not wf:
                raise ValueError(f"WorkflowDefinition {workflow_id} not found")
            # 在会话内读取节点，避免会话关闭后访问 DetachedInstance 错误
            nodes = [
                {
                    "node_key": n.node_key,
                    "node_type": n.node_type,
                    "prompt_code": n.prompt_code,
                    "tool_key": n.tool_key,
                    "config_json": n.config_json or {},
                    "order": n.order,
                }
                for n in wf.nodes
            ]
            edges = [
                {"from_node": e.from_node, "to_node": e.to_node, "condition_json": e.condition_json or {}}
                for e in wf.edges
            ]
            run = WorkflowRun(
                workflow_id=workflow_id,
                status="pending",
                trigger_type=trigger_type,
                input_json=input_json or {},
                context_json=context_json or {},
                operator=operator,
            )
            session.add(run)
            session.flush()
            run_id = run.id
            session.commit()
            # 把 DAG 静态信息写入 context_json，供后续会话使用
            context = dict(run.context_json or {})
            context["_nodes"] = nodes
            context["_edges"] = edges
            self._update_run_json(run_id, context_json=context)
            return run_id

    # ------------------------------------------------------------------ run execution
    def run_workflow(self, run_id: int) -> None:
        """执行一个 run：拓扑排序 + 依次执行节点。"""
        with session_scope() as session:
            run = session.get(WorkflowRun, run_id)
            if not run:
                raise ValueError(f"WorkflowRun {run_id} not found")
            context = dict(run.context_json or {})
            nodes = context.get("_nodes") or []
            edges = context.get("_edges") or []

        # 状态机：pending -> running
        self._set_run_status(run_id, "running")
        self._emit(run_id, "run.state_changed", {"status": "running"})

        try:
            ordered_nodes = self._topological_order(nodes, edges)
            for node in ordered_nodes:
                self._execute_node(run_id, node)
            # 全部完成
            self._set_run_status(run_id, "done")
            self._emit(run_id, "run.state_changed", {"status": "done"})
        except Exception as exc:  # noqa: BLE001
            self._set_run_status(run_id, "failed")
            self._emit(run_id, "run.state_changed", {"status": "failed", "error": str(exc)})
            raise

    def confirm_gate(self, run_id: int, node_key: str, decision: bool) -> None:
        """人工闸门确认：decision 为 True 时释放闸门，恢复 running；否则置 failed。"""
        with session_scope() as session:
            run = session.get(WorkflowRun, run_id)
            if not run:
                raise ValueError(f"WorkflowRun {run_id} not found")
            if run.status != "blocked":
                raise ValueError(f"WorkflowRun {run_id} is not blocked")
            if decision:
                run.status = "running"
                session.add(run)
                session.commit()
        self._emit(run_id, "gate.released", {"node_key": node_key, "decision": decision})
        if decision:
            self._emit(run_id, "run.state_changed", {"status": "running"})
        else:
            self._set_run_status(run_id, "failed")
            self._emit(run_id, "run.state_changed", {"status": "failed", "error": "gate rejected"})

    def _topological_order(
        self, nodes: list[dict], edges: list[dict]
    ) -> list[dict]:
        """拓扑排序：依赖前置节点先执行。"""
        from collections import deque

        node_map = {n["node_key"]: n for n in nodes}
        adj: dict[str, list[str]] = {n["node_key"]: [] for n in nodes}
        indeg: dict[str, int] = {n["node_key"]: 0 for n in nodes}
        for e in edges:
            if e["from_node"] in adj and e["to_node"] in adj:
                adj[e["from_node"]].append(e["to_node"])
                indeg[e["to_node"]] += 1

        queue = deque([nk for nk, d in indeg.items() if d == 0])
        result: list[dict] = []
        while queue:
            nk = queue.popleft()
            result.append(node_map[nk])
            for m in adj[nk]:
                indeg[m] -= 1
                if indeg[m] == 0:
                    queue.append(m)

        if len(result) != len(nodes):
            raise ValueError("Workflow DAG 存在环路，无法执行")
        return result

    def _execute_node(self, run_id: int, node: dict) -> None:
        with session_scope() as session:
            nr = NodeRun(
                run_id=run_id,
                node_key=node["node_key"],
                node_type=node["node_type"],
                status="running",
                input_json={},
            )
            session.add(nr)
            session.flush()
            nr_id = nr.id
            session.commit()

        self._emit(run_id, "node.started", {"node_key": node["node_key"], "node_type": node["node_type"]})

        try:
            node_type = node["node_type"]
            if node_type == "llm":
                output = self._exec_llm_node(run_id, node)
            elif node_type == "tool":
                output = self._exec_tool_node(run_id, node)
            elif node_type == "branch":
                output = self._exec_branch_node(run_id, node)
            elif node_type == "parallel":
                output = self._exec_parallel_node(run_id, node)
            elif node_type == "gate":
                output = self._exec_gate_node(run_id, node)
            elif node_type == "transform":
                output = self._exec_transform_node(run_id, node)
            elif node_type == "notify":
                output = self._exec_notify_node(run_id, node)
            elif node_type == "artifact":
                output = self._exec_artifact_node(run_id, node)
            else:
                raise ValueError(f"未知节点类型: {node_type}")

            with session_scope() as session:
                nr = session.get(NodeRun, nr_id)
                nr.status = "done"
                nr.output_json = output if isinstance(output, dict) else {"result": output}
                nr.ended_at = datetime.now(timezone.utc)
                session.add(nr)
                session.commit()

            self._emit(run_id, "node.finished", {"node_key": node["node_key"], "output": nr.output_json})

        except Exception as exc:  # noqa: BLE001
            with session_scope() as session:
                nr = session.get(NodeRun, nr_id)
                nr.status = "failed"
                nr.error = str(exc)
                nr.ended_at = datetime.now(timezone.utc)
                session.add(nr)
                session.commit()

            self._emit(run_id, "node.failed", {"node_key": node["node_key"], "error": str(exc)})
            # 熔断：整个 run 失败
            self._set_run_status(run_id, "failed")
            self._emit(run_id, "run.state_changed", {"status": "failed", "error": str(exc)})
            raise

    # ---------------- 节点执行器（占位实现） ----------------
    def _exec_llm_node(self, run_id: int, node: dict) -> dict:
        return {"status": "llm_executed", "node": node["node_key"]}

    def _exec_tool_node(self, run_id: int, node: dict) -> dict:
        return {"status": "tool_executed", "node": node["node_key"]}

    def _exec_branch_node(self, run_id: int, node: dict) -> dict:
        return {"status": "branch_evaluated", "node": node["node_key"]}

    def _exec_parallel_node(self, run_id: int, node: dict) -> dict:
        return {"status": "parallel_executed", "node": node["node_key"]}

    def _exec_gate_node(self, run_id: int, node: dict) -> dict:
        """人工闸门：将 run 置 blocked，等待 UI 确认。"""
        self._set_run_status(run_id, "blocked")
        self._emit(run_id, "gate.blocked", {"node_key": node["node_key"]})
        return {"status": "blocked", "node": node["node_key"]}

    def _exec_transform_node(self, run_id: int, node: dict) -> dict:
        return {"status": "transformed", "node": node["node_key"]}

    def _exec_notify_node(self, run_id: int, node: dict) -> dict:
        return {"status": "notified", "node": node["node_key"]}

    def _exec_artifact_node(self, run_id: int, node: dict) -> dict:
        return {"status": "artifact_created", "node": node["node_key"]}

    # ------------------------------------------------------------------ helpers
    def _set_run_status(self, run_id: int, status: str) -> None:
        with session_scope() as session:
            run = session.get(WorkflowRun, run_id)
            if run:
                run.status = status
                if status in ("done", "failed", "killed"):
                    run.ended_at = datetime.now(timezone.utc)
                session.add(run)
                session.commit()

    def _update_run_json(
        self, run_id: int, context_json: dict | None = None
    ) -> None:
        with session_scope() as session:
            run = session.get(WorkflowRun, run_id)
            if run:
                run.context_json = context_json or {}
                session.add(run)
                session.commit()

    def _emit(self, run_id: int, event_type: str, payload: dict) -> None:
        if self.event_bus is not None:
            from ..core.events import DomainEvent

            self.event_bus.publish(
                DomainEvent(
                    event_type=event_type,
                    run_id=str(run_id),
                    payload=payload,
                )
            )
