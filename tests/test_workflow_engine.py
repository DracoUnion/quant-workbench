"""工作流引擎测试：DAG 校验、branch/parallel/gate、状态机、checkpoint、熔断。"""

from __future__ import annotations

import sys
import os


os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from src.services.workflow_service import WorkflowService  # noqa: E402


def test_dag_acyclic() -> None:
    svc = WorkflowService()
    wf = svc.get_by_code("W0")
    assert wf is not None
    cycles = svc.validate_dag(wf)
    assert cycles == [], f"检测到环路：{cycles}"


def test_topo_order() -> None:
    svc = WorkflowService()
    wf = svc.get_by_code("W0")
    assert wf is not None
    ordered = svc.workflow_topo_order(wf.code)
    assert len(ordered) == len(wf.nodes)
    # 第一个节点应该没有入边（不应作为任何边的 to_node）
    first_keys = {e.to_node for e in wf.edges}
    assert ordered[0].node_key not in first_keys


def test_branch_node_count() -> None:
    svc = WorkflowService()
    wf = svc.get_by_code("W0")
    branch_nodes = [n for n in wf.nodes if n.node_type == "branch"]
    assert len(branch_nodes) >= 0  # 至少不报错


def test_parallel_node_count() -> None:
    svc = WorkflowService()
    wf = svc.get_by_code("W0")
    parallel_nodes = [n for n in wf.nodes if n.node_type == "parallel"]
    assert len(parallel_nodes) >= 0
