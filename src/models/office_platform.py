"""办公与平台模型。"""

from __future__ import annotations

from typing import Any

from sqlalchemy import JSON, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, CreatedAt, Id, UpdatedAt


class WeeklyReport(Base):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    """周报。"""

    __tablename__ = "weekly_report"

    owner: Mapped[str] = mapped_column(String(100), index=True, comment="负责人")
    period: Mapped[str] = mapped_column(
        String(32), index=True, comment="周期，如 2026-W47"
    )
    content_md: Mapped[str] = mapped_column(Text, default="", comment="Markdown 内容")
    status: Mapped[str] = mapped_column(
        String(16), default="draft", comment="draft/published/archived"
    )

    def __repr__(self) -> str:  # noqa: D401
        return f"<WeeklyReport(owner={self.owner!r}, period={self.period!r})>"


class MeetingNote(Base):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    """会议纪要。"""

    __tablename__ = "meeting_note"

    title: Mapped[str] = mapped_column(String(200), index=True, comment="会议标题")
    time: Mapped[str] = mapped_column(String(32), index=True, comment="会议时间")
    attendees: Mapped[str] = mapped_column(Text, default="", comment="参会人员 JSON")
    decisions_json: Mapped[str] = mapped_column(
        JSON, default="[]", comment="决议列表 JSON"
    )
    actions_json: Mapped[str] = mapped_column(
        JSON, default="[]", comment="行动项列表 JSON"
    )

    def __repr__(self) -> str:  # noqa: D401
        return f"<MeetingNote(title={self.title!r}, time={self.time!r})>"


class AuditLog(Base):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    """审计日志。"""

    __tablename__ = "audit_log"

    actor: Mapped[str] = mapped_column(String(100), index=True, comment="操作者")
    action: Mapped[str] = mapped_column(String(64), index=True, comment="操作类型")
    target: Mapped[str | None] = mapped_column(
        String(255), default=None, index=True, comment="操作目标"
    )
    payload_json: Mapped[str] = mapped_column(JSON, default="{}", comment="操作载荷")
    created_at: Mapped[CreatedAt]

    def __repr__(self) -> str:  # noqa: D401
        return f"<AuditLog(actor={self.actor!r}, action={self.action!r})>"


class PlatformSetting(Base):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    """平台配置。"""

    __tablename__ = "platform_setting"

    key: Mapped[str] = mapped_column(String(64), unique=True, index=True, comment="配置键")
    value: Mapped[str] = mapped_column(Text, default="", comment="配置值")
    description: Mapped[str] = mapped_column(String(255), default="", comment="说明")

    def __repr__(self) -> str:  # noqa: D401
        return f"<PlatformSetting(key={self.key!r})>"
