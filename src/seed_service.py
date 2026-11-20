"""种子服务：将 P001-P076 提示词与 W0-W9 工作流定义幂等地写入数据库。

供 src/main.py 首次启动时调用；可重复执行。
"""


from __future__ import annotations

from typing import Any

from .seed.prompts import PROMPTS  # noqa: import-not-found  (src 根在 sys.path 中)
from .seed.workflows import WORKFLOWS  # noqa: import-not-found


def _upsert_prompts(session: Any) -> int:
    from src.models.prompt import PromptTemplate, PromptVersion
    from sqlalchemy import select

    count = 0
    for item in PROMPTS:
        code = item.get("code") or item.get("id")
        if not code:
            continue
        row = session.execute(select(PromptTemplate).where(PromptTemplate.code == code)).scalar_one_or_none()
        defaults = dict(
            title=item.get("title", ""),
            category=item.get("category", ""),
            sub_category=item.get("sub_category", ""),
            body=item.get("body") or item.get("full_text", ""),
            params_json=item.get("params_json") or {},
            version=item.get("version", 1),
        )
        if row is None:
            session.add(PromptTemplate(code=code, **defaults))
            count += 1
        else:
            changed = False
            for key, value in defaults.items():
                if getattr(row, key) != value:
                    setattr(row, key, value)
                    changed = True
            if changed:
                session.add(
                    PromptVersion(
                        prompt_id=row.id,
                        version=row.version,
                        body=row.body,
                    )
                )
                row.version += 1
                count += 1
    return count


def _upsert_workflows(session: Any) -> int:
    from src.models.workflow import WorkflowDefinition, WorkflowEdge, WorkflowNode
    from sqlalchemy import select

    count = 0
    for wf_item in WORKFLOWS:
        code = wf_item["code"]
        row = session.execute(
            select(WorkflowDefinition).where(WorkflowDefinition.code == code)
        ).scalar_one_or_none()
        defaults = dict(
            name=wf_item["name"],
            description=wf_item.get("description", ""),
            version=wf_item.get("version", 1),
            status=wf_item.get("status", "published"),
            config_json={},
        )
        if row is None:
            row = WorkflowDefinition(code=code, **defaults)
            session.add(row)
            session.flush()
            count += 1
        else:
            for key, value in defaults.items():
                setattr(row, key, value)
        # 节点与边按 code 重建（幂等：先删再建）
        session.execute(
            WorkflowNode.__table__.delete().where(WorkflowNode.workflow_id == row.id)  # type: ignore[attr-defined]
        )
        session.execute(
            WorkflowEdge.__table__.delete().where(WorkflowEdge.workflow_id == row.id)  # type: ignore[attr-defined]
        )
        session.flush()
        for node in wf_item["nodes"]:
            session.add(
                WorkflowNode(
                    workflow_id=row.id,
                    node_key=node["node_key"],
                    node_type=node["node_type"],
                    prompt_code=node.get("prompt_code"),
                    tool_key=node.get("tool_key"),
                    config_json=node.get("config_json") or {},
                    order=node.get("order", 0),
                )
            )
        for edge in wf_item["edges"]:
            session.add(
                WorkflowEdge(
                    workflow_id=row.id,
                    from_node=edge["from_node"],
                    to_node=edge["to_node"],
                    condition_json=edge.get("condition_json") or {},
                )
            )
        count += 1
    return count


def seed_all(ctx: Any) -> None:
    """幂等播种：提示词种子 + 工作流定义。"""
    from .core.database import session_scope

    with session_scope() as session:
        n_prompt = _upsert_prompts(session)
        n_wf = _upsert_workflows(session)
    print(f"[seed] 提示词 {n_prompt} 条，工作流 {n_wf} 条")
