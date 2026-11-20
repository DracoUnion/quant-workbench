"""工作流运行模型。"""

from __future__ import annotations

from typing import Any

from sqlalchemy import Boolean, Integer, JSON, String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, CreatedAt, Id, UpdatedAt


class WorkflowRun(Base):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    """工作流运行实例。"""

    __tablename__ = "workflow_run"

    workflow_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("workflow_definition.id", ondelete="CASCADE"), index=True
    )
    status: Mapped[str] = mapped_column(
        String(16),
        default="pending",
        index=True,
        comment="pending/running/blocked/done/failed/killed",
    )
    trigger_type: Mapped[str] = mapped_column(
        String(32), default="manual", comment="手动/定时/事件/外部API"
    )
    input_json: Mapped[str] = mapped_column(JSON, default="{}", comment="运行输入参数")
    context_json: Mapped[str] = mapped_column(
        JSON, default="{}", comment="运行上下文（用户画像、持仓等）"
    )
    started_at: Mapped[CreatedAt | None] = mapped_column(default=None, comment="开始时间")
    ended_at: Mapped[CreatedAt | None] = mapped_column(default=None, comment="结束时间")
    operator: Mapped[str | None] = mapped_column(
        String(64), default=None, comment="操作人"
    )

    nodes: Mapped[list["NodeRun"]] = relationship(
        back_populates="run", cascade="all, delete-orphan", order_by="NodeRun.started_at"
    )
    events: Mapped[list["RunEvent"]] = relationship(
        back_populates="run", cascade="all, delete-orphan", order_by="RunEvent.created_at"
    )
    artifacts: Mapped[list["Artifact"]] = relationship(
        back_populates="run", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # noqa: D401
        return f"<WorkflowRun(id={self.id}, status={self.status!r})>"


class NodeRun(Base):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    """工作流节点运行记录。"""

    __tablename__ = "node_run"

    run_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("workflow_run.id", ondelete="CASCADE"), index=True
    )
    node_key: Mapped[str] = mapped_column(String(64), index=True, comment="节点 key")
    node_type: Mapped[str | None] = mapped_column(
        String(32), default=None, comment="节点类型 llm/tool/branch/parallel/gate/…"
    )
    status: Mapped[str] = mapped_column(
        String(16),
        default="pending",
        index=True,
        comment="pending/running/blocked/done/failed/killed",
    )
    input_json: Mapped[str] = mapped_column(JSON, default="{}", comment="节点输入")
    output_json: Mapped[str] = mapped_column(
        JSON, default="{}", comment="节点输出"
    )
    error: Mapped[str | None] = mapped_column(Text, default=None, comment="错误信息")
    started_at: Mapped[CreatedAt | None] = mapped_column(default=None, comment="开始时间")
    ended_at: Mapped[CreatedAt | None] = mapped_column(default=None, comment="结束时间")

    run: Mapped["WorkflowRun"] = relationship(back_populates="nodes")
    events: Mapped[list["RunEvent"]] = relationship(
        back_populates="node_run", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # noqa: D401
        return f"<NodeRun(node_key={self.node_key!r}, status={self.status!r})>"


class RunEvent(Base):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    """运行事件留痕。"""

    __tablename__ = "run_event"

    run_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("workflow_run.id", ondelete="CASCADE"), index=True
    )
    node_run_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("node_run.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="所属节点运行",
    )
    node_key: Mapped[str | None] = mapped_column(
        String(64), default=None, index=True, comment="触发事件的节点 key"
    )
    event_type: Mapped[str] = mapped_column(
        String(64), index=True, comment="事件类型：run.state_changed / node.finished / alert.raised / gate.blocked"
    )
    payload_json: Mapped[str] = mapped_column(JSON, default="{}", comment="事件载荷")
    created_at: Mapped[CreatedAt]

    run: Mapped["WorkflowRun"] = relationship(back_populates="events")
    node_run: Mapped["NodeRun | None"] = relationship(back_populates="events")

    def __repr__(self) -> str:  # noqa: D401
        return f"<RunEvent(event_type={self.event_type!r}, run_id={self.run_id})>"


class Artifact(Base):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    """工作流产出物。"""

    __tablename__ = "artifact"

    run_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("workflow_run.id", ondelete="CASCADE"), index=True
    )
    node_key: Mapped[str] = mapped_column(String(64), index=True, comment="产出所属节点 key")
    artifact_type: Mapped[str] = mapped_column(
        String(32), index=True, comment="产出物类型：report/chart/table/text/file"
    )
    title: Mapped[str] = mapped_column(String(200), comment="标题")
    content: Mapped[str] = mapped_column(Text, default="", comment="文本内容")
    file_path: Mapped[str | None] = mapped_column(
        String(512), default=None, comment="附件文件路径"
    )
    meta_json: Mapped[str] = mapped_column(JSON, default="{}", comment="元数据")

    run: Mapped["WorkflowRun"] = relationship(back_populates="artifacts")

    def __repr__(self) -> str:  # noqa: D401
        return f"<Artifact(title={self.title!r}, type={self.artifact_type!r})>"
