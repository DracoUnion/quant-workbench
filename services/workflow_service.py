"""零 Qt 工作流定义服务（兼容旧导入路径）。

W0-W9 定义来自 src.seed.workflows，全部为无环 DAG，可直接调度执行。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from src.seed.workflows import WORKFLOWS  # noqa: import-not-found (根目录在 sys.path 中)


@dataclass
class WorkflowNode:
    node_key: str
    node_type: str
    prompt_code: Optional[str] = None
    tool_key: Optional[str] = None
    config_json: dict = field(default_factory=dict)
    order: int = 0


@dataclass
class WorkflowEdge:
    from_node: str
    to_node: str
    condition_json: dict = field(default_factory=dict)


@dataclass
class WorkflowDefinition:
    id: int
    code: str
    name: str
    description: str = ""
    version: int = 1
    status: str = "published"
    nodes: list[WorkflowNode] = field(default_factory=list)
    edges: list[WorkflowEdge] = field(default_factory=list)


class WorkflowService:
    """工作流定义服务：CRUD、DAG 校验、拓扑排序。"""

    def __init__(self) -> None:
        self._definitions: dict[str, WorkflowDefinition] = {}
        self._order: list[str] = []
        for index, item in enumerate(WORKFLOWS, start=1):
            nodes = [
                WorkflowNode(
                    node_key=n["node_key"],
                    node_type=n["node_type"],
                    prompt_code=n.get("prompt_code"),
                    tool_key=n.get("tool_key"),
                    config_json=n.get("config_json") or {},
                    order=n.get("order", 0),
                )
                for n in item["nodes"]
            ]
            edges = [
                WorkflowEdge(
                    from_node=e["from_node"],
                    to_node=e["to_node"],
                    condition_json=e.get("condition_json") or {},
                )
                for e in item["edges"]
            ]
            wf = WorkflowDefinition(
                id=index,
                code=item["code"],
                name=item["name"],
                description=item.get("description", ""),
                version=item.get("version", 1),
                status=item.get("status", "published"),
                nodes=nodes,
                edges=edges,
            )
            self._definitions[item["code"]] = wf
            self._order.append(item["code"])

    def all(self) -> list[WorkflowDefinition]:
        return [self._definitions[c] for c in self._order]

    def get(self, wf_id: int) -> Optional[WorkflowDefinition]:
        for wf in self.all():
            if wf.id == wf_id:
                return wf
        return None

    def get_by_code(self, code: str) -> Optional[WorkflowDefinition]:
        return self._definitions.get(code)

    # ------------------------------------------------------------------ DAG
    def validate_dag(self, wf: WorkflowDefinition) -> list[str]:
        """校验 DAG 无环，返回环路节点（空则有效）。"""
        nodes = {n.node_key for n in wf.nodes}
        adj: dict[str, list[str]] = {n.node_key: [] for n in wf.nodes}
        indeg: dict[str, int] = {n.node_key: 0 for n in wf.nodes}
        for e in wf.edges:
            if e.from_node in adj and e.to_node in adj:
                adj[e.from_node].append(e.to_node)
                indeg[e.to_node] += 1

        queue = [n for n, d in indeg.items() if d == 0]
        visited = 0
        while queue:
            n = queue.pop(0)
            visited += 1
            for m in adj[n]:
                indeg[m] -= 1
                if indeg[m] == 0:
                    queue.append(m)

        if visited != len(nodes):
            remaining = [n for n, d in indeg.items() if d > 0]
            return [f"环路节点: {n}" for n in remaining]
        return []

    def topological_order(self, wf: WorkflowDefinition) -> list[WorkflowNode]:
        adj: dict[str, list[str]] = {n.node_key: [] for n in wf.nodes}
        indeg: dict[str, int] = {n.node_key: 0 for n in wf.nodes}
        node_map: dict[str, WorkflowNode] = {n.node_key: n for n in wf.nodes}
        for e in wf.edges:
            if e.from_node in adj and e.to_node in adj:
                adj[e.from_node].append(e.to_node)
                indeg[e.to_node] += 1

        queue = [n for n, d in indeg.items() if d == 0]
        result: list[WorkflowNode] = []
        while queue:
            nkey = queue.pop(0)
            result.append(node_map[nkey])
            for m in adj[nkey]:
                indeg[m] -= 1
                if indeg[m] == 0:
                    queue.append(m)
        return result

    def workflow_topo_order(self, code: str) -> list[WorkflowNode]:
        """按工作流编号返回拓扑排序后的节点列表。"""
        wf = self.get_by_code(code)
        if wf is None:
            return []
        return self.topological_order(wf)
