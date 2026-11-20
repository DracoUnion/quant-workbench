"""组合/持仓/风险模型。"""

from __future__ import annotations

from typing import Any

from sqlalchemy import JSON, Integer, Numeric, String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, CreatedAt, Id, UpdatedAt


class Portfolio(Base):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    """投资组合。"""

    __tablename__ = "portfolio"

    name: Mapped[str] = mapped_column(String(100), index=True, comment="组合名称")
    owner: Mapped[str] = mapped_column(String(100), index=True, comment="所属用户/客户")
    base_currency: Mapped[str] = mapped_column(String(16), default="CNY", comment="基础货币")
    risk_level: Mapped[str] = mapped_column(
        String(16), default="medium", comment="风险等级：conservative/medium/aggressive"
    )

    positions: Mapped[list["Position"]] = relationship(
        back_populates="portfolio", cascade="all, delete-orphan"
    )
    snapshots: Mapped[list["RiskSnapshot"]] = relationship(
        back_populates="portfolio", cascade="all, delete-orphan", order_by="RiskSnapshot.created_at.desc()"
    )

    def __repr__(self) -> str:  # noqa: D401
        return f"<Portfolio(name={self.name!r}, owner={self.owner!r})>"


class Position(Base):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    """持仓。"""

    __tablename__ = "position"

    portfolio_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("portfolio.id", ondelete="CASCADE"), index=True
    )
    symbol: Mapped[str] = mapped_column(String(20), index=True, comment="证券代码")
    qty: Mapped[float] = mapped_column(Numeric(18, 6), default=0, comment="持仓数量")
    cost: Mapped[float] = mapped_column(Numeric(18, 4), default=0, comment="成本价")
    market_value: Mapped[float] = mapped_column(
        Numeric(18, 4), default=0, comment="当前市值"
    )
    portfolio: Mapped["Portfolio"] = relationship(back_populates="positions")

    def __repr__(self) -> str:  # noqa: D401
        return f"<Position(symbol={self.symbol!r}, qty={self.qty})>"


class RiskSnapshot(Base):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    """风险快照。"""

    __tablename__ = "risk_snapshot"

    portfolio_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("portfolio.id", ondelete="CASCADE"), index=True
    )
    var: Mapped[float] = mapped_column(
        Numeric(18, 4), default=0, comment="VaR 风险价值"
    )
    exposure_json: Mapped[str] = mapped_column(
        JSON, default="{}", comment="各因子敞口 JSON"
    )
    drawdown: Mapped[float] = mapped_column(
        Numeric(9, 4), default=0, comment="当前回撤"
    )
    level: Mapped[str] = mapped_column(
        String(16), default="normal", comment="绿色/黄色/橙色/红色"
    )
    created_at: Mapped[CreatedAt]

    portfolio: Mapped["Portfolio"] = relationship(back_populates="snapshots")

    def __repr__(self) -> str:  # noqa: D401
        return f"<RiskSnapshot(portfolio_id={self.portfolio_id}, var={self.var}, level={self.level!r})>"
