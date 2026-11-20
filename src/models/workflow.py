"""工作流定义模型。"""

from __future__ import annotations

from typing import Any

from sqlalchemy import Boolean, Integer, JSON, String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, CreatedAt, Id, UpdatedAt


class WorkflowDefinition(Base):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    """工作流定义（W0-W9）。"""

    __tablename__ = "workflow_definition"

    code: Mapped[str] = mapped_column(String(16), unique=True, index=True, comment="工作流编号 W0…W9")
    name: Mapped[str] = mapped_column(String(128), comment="工作流名称")
    description: Mapped[str] = mapped_column(Text, default="", comment="描述")
    version: Mapped[int] = mapped_column(Integer, default=1, comment="版本号")
    status: Mapped[str] = mapped_column(String(16), default="draft", comment="draft/published/archived")
    config_json: Mapped[str] = mapped_column(
        JSON, default="{}", comment="全局参数：阈值、模板、输出格式等"
    )

    nodes: Mapped[list["WorkflowNode"]] = relationship(
        back_populates="workflow", cascade="all, delete-orphan", order_by="WorkflowNode.order"
    )
    edges: Mapped[list["WorkflowEdge"]] = relationship(
        back_populates="workflow", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # noqa: D401
        return f"<WorkflowDefinition(code={self.code!r}, name={self.name!r})>"


class WorkflowNode(Base):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    """工作流节点。"""

    __tablename__ = "workflow_node"

    workflow_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("workflow_definition.id", ondelete="CASCADE"), index=True
    )
    node_key: Mapped[str] = mapped_column(String(64), index=True, comment="节点唯一标识")
    node_type: Mapped[str] = mapped_column(
        String(32),
        comment="节点类型：llm/tool/branch/parallel/gate/tool/transform/notify/artifact",
    )
    prompt_code: Mapped[str | None] = mapped_column(
        String(64), default=None, comment="绑定的提示词编号 P001…"
    )
    tool_key: Mapped[str | None] = mapped_column(
        String(64), default=None, comment="工具 key，如 web_search/iwencai/code_interpreter"
    )
    config_json: Mapped[str] = mapped_column(
        JSON, default="{}", comment="节点参数：阈值、模板、输出格式等"
    )
    order: Mapped[int] = mapped_column(Integer, default=0, comment="执行顺序")

    workflow: Mapped["WorkflowDefinition"] = relationship(back_populates="nodes")

    def __repr__(self) -> str:  # noqa: D401
        return f"<WorkflowNode(node_key={self.node_key!r}, type={self.node_type!r})>"


class WorkflowEdge(Base):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    """工作流边（DAG 边）。"""

    __tablename__ = "workflow_edge"

    workflow_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("workflow_definition.id", ondelete="CASCADE"), index=True
    )
    from_node: Mapped[str] = mapped_column(String(64), index=True, comment="源节点 key")
    to_node: Mapped[str] = mapped_column(String(64), index=True, comment="目标节点 key")
    condition_json: Mapped[str] = mapped_column(
        JSON, default="{}", comment="分支条件（JSON Logic），为空表示无条件"
    )
    workflow: Mapped["WorkflowDefinition"] = relationship(back_populates="edges")

    def __repr__(self) -> str:  # noqa: D401
        return f"<WorkflowEdge({self.from_node!r} -> {self.to_node!r})>"
