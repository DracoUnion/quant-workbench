"""工作流定义服务：CRUD、DAG 校验、发布版本。"""

from __future__ import annotations

from typing import Any

from ..models.workflow import WorkflowDefinition, WorkflowNode, WorkflowEdge


class WorkflowService:
    """工作流定义服务。"""

    def __init__(self) -> None:
        self._definitions: dict[int, WorkflowDefinition] = {}
        self._order: list[int] = []

    # ------------------------------------------------------------------ CRUD
    def all(self) -> list[WorkflowDefinition]:
        return [self._definitions[i] for i in self._order]

    def get(self, wf_id: int) -> WorkflowDefinition | None:
        return self._definitions.get(wf_id)

    def get_by_code(self, code: str) -> WorkflowDefinition | None:
        for wf in self.all():
            if wf.code == code:
                return wf
        return None

    def add(self, wf: WorkflowDefinition) -> None:
        self._definitions[wf.id] = wf
        self._order.append(wf.id)

    def delete(self, wf_id: int) -> bool:
        if wf_id not in self._definitions:
            return False
        self._definitions.pop(wf_id)
        self._order = [i for i in self._order if i != wf_id]
        return True

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

        queue: list[str] = [n for n, d in indeg.items() if d == 0]
        visited = 0
        while queue:
            n = queue.pop(0)
            visited += 1
            for m in adj[n]:
                indeg[m] -= 1
                if indeg[m] == 0:
                    queue.append(m)

        if visited != len(nodes):
            # 找出环路成员
            remaining = [n for n, d in indeg.items() if d > 0]
            return [f"环路节点: {n}" for n in remaining]
        return []

    def topological_order(self, wf: WorkflowDefinition) -> list[WorkflowNode]:
        """返回拓扑排序后的节点列表。"""
        adj: dict[str, list[str]] = {n.node_key: [] for n in wf.nodes}
        indeg: dict[str, int] = {n.node_key: 0 for n in wf.nodes}
        node_map: dict[str, WorkflowNode] = {n.node_key: n for n in wf.nodes}
        for e in wf.edges:
            if e.from_node in adj and e.to_node in adj:
                adj[e.from_node].append(e.to_node)
                indeg[e.to_node] += 1

        queue: list[str] = [n for n, d in indeg.items() if d == 0]
        result: list[WorkflowNode] = []
        while queue:
            nkey = queue.pop(0)
            result.append(node_map[nkey])
            for m in adj[nkey]:
                indeg[m] -= 1
                if indeg[m] == 0:
                    queue.append(m)
        return result
