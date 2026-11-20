"""信号/预警/事件/客户/合规/办公/平台模型。"""

from __future__ import annotations

from typing import Any

from sqlalchemy import JSON, Integer, String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, CreatedAt, Id, UpdatedAt


class Signal(Base):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    """交易信号。"""

    __tablename__ = "signal"

    source: Mapped[str] = mapped_column(
        String(32), index=True, comment="W5/W6 等信号源"
    )
    symbol: Mapped[str] = mapped_column(String(20), index=True, comment="证券代码")
    signal_type: Mapped[str] = mapped_column(
        String(32), index=True, comment="多/空/中性"
    )
    score: Mapped[float] = mapped_column(default=0, comment="信号得分")
    confidence: Mapped[float] = mapped_column(default=0, comment="置信度 0~1")
    payload_json: Mapped[str] = mapped_column(JSON, default="{}", comment="信号载荷")
    status: Mapped[str] = mapped_column(
        String(16), default="active", index=True, comment="active/expired/cancelled"
    )

    def __repr__(self) -> str:  # noqa: D401
        return f"<Signal(symbol={self.symbol!r}, type={self.signal_type!r}, score={self.score})>"


class Alert(Base):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    """风险预警。"""

    __tablename__ = "alert"

    signal_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("signal.id", ondelete="CASCADE"), index=True
    )
    level: Mapped[str] = mapped_column(
        String(16), index=True, comment="red/orange/yellow/green"
    )
    title: Mapped[str] = mapped_column(String(200), comment="预警标题")
    body: Mapped[str] = mapped_column(Text, default="", comment="预警正文")
    pushed_at: Mapped[CreatedAt | None] = mapped_column(default=None, comment="推送时间")
    ack_by: Mapped[str | None] = mapped_column(
        String(100), default=None, comment="确认人"
    )

    def __repr__(self) -> str:  # noqa: D401
        return f"<Alert(signal_id={self.signal_id}, level={self.level!r})>"


class EventCard(Base):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    """事件卡：特殊事件（供应链/内部人/研报情绪/套利）。"""

    __tablename__ = "event_card"

    event_type: Mapped[str] = mapped_column(
        String(64), index=True, comment="事件类型：supply_chain/insider/sentiment/arbitrage"
    )
    target: Mapped[str] = mapped_column(
        String(255), index=True, comment="事件目标（标的/行业/地区）"
    )
    decoded_json: Mapped[str] = mapped_column(
        JSON, default="{}", comment="解码后的事件数据"
    )
    history_winrate: Mapped[float] = mapped_column(default=0, comment="历史胜率")
    risk_json: Mapped[str] = mapped_column(JSON, default="{}", comment="风险 JSON")

    def __repr__(self) -> str:  # noqa: D401
        return f"<EventCard(event_type={self.event_type!r}, target={self.target!r})>"


class Client(Base):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    """客户。"""

    __tablename__ = "client"

    name: Mapped[str] = mapped_column(String(100), index=True, comment="客户名称")
    risk_level: Mapped[str] = mapped_column(
        String(16), default="medium", comment="风险等级：conservative/medium/aggressive"
    )
    stage: Mapped[str] = mapped_column(
        String(32), default="prospect", comment="客户阶段：prospect/active/inactive"
    )
    tags_json: Mapped[str] = mapped_column(JSON, default="[]", comment="标签数组")

    profile: Mapped["ClientProfile | None"] = relationship(
        back_populates="client", cascade="all, delete-orphan", uselist=False
    )
    kyc_reviews: Mapped[list["KycReview"]] = relationship(
        back_populates="client", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # noqa: D401
        return f"<Client(name={self.name!r}, risk_level={self.risk_level!r})>"


class ClientProfile(Base):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    """客户画像。"""

    __tablename__ = "client_profile"

    client_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("client.id", ondelete="CASCADE"), unique=True, index=True
    )
    profile_json: Mapped[str] = mapped_column(JSON, default="{}", comment="画像 JSON")
    updated_at: Mapped[CreatedAt]

    client: Mapped["Client"] = relationship(back_populates="profile")

    def __repr__(self) -> str:  # noqa: D401
        return f"<ClientProfile(client_id={self.client_id})>"


class KycReview(Base):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    """KYC 审核。"""

    __tablename__ = "kyc_review"

    client_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("client.id", ondelete="CASCADE"), index=True
    )
    result: Mapped[str] = mapped_column(
        String(32), comment="approved/rejected/needs_review"
    )
    issues_json: Mapped[str] = mapped_column(JSON, default="{}", comment="问题清单 JSON")
    aml_level: Mapped[str] = mapped_column(
        String(16), default="low", comment="AML 风险等级：low/medium/high"
    )
    reviewer: Mapped[str | None] = mapped_column(
        String(100), default=None, comment="审核人"
    )
    client: Mapped["Client"] = relationship(back_populates="kyc_reviews")

    def __repr__(self) -> str:  # noqa: D401
        return f"<KycReview(client_id={self.client_id}, result={self.result!r})>"
