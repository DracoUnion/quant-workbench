"""研究/投研模型。"""

from __future__ import annotations

from typing import Any

from sqlalchemy import JSON, Integer, String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, CreatedAt, Id, UpdatedAt


class ResearchTask(Base):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    """投研任务。"""

    __tablename__ = "research_task"

    type: Mapped[str] = mapped_column(
        String(32),
        index=True,
        comment="report/financial/value/cashflow 等",
    )
    target: Mapped[str] = mapped_column(String(255), comment="分析标的（代码/行业/宏观指标）")
    status: Mapped[str] = mapped_column(
        String(16), default="pending", index=True, comment="pending/running/done/failed"
    )
    run_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("workflow_run.id", ondelete="SET NULL"), index=True, default=None,
        comment="关联的工作流运行 ID",
    )

    def __repr__(self) -> str:  # noqa: D401
        return f"<ResearchTask(type={self.type!r}, target={self.target!r}, status={self.status!r})>"


class FinancialStatement(Base):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    """财务报表指标。"""

    __tablename__ = "financial_statement"

    company: Mapped[str] = mapped_column(String(100), index=True, comment="公司名称/代码")
    period: Mapped[str] = mapped_column(String(32), index=True, comment="报告期，如 2024Q3")
    metrics_json: Mapped[str] = mapped_column(JSON, default="{}", comment="财务指标 JSON")
    source_page: Mapped[str | None] = mapped_column(
        String(64), default=None, comment="来源页码"
    )
    anomaly_flag: Mapped[bool] = mapped_column(default=False, index=True, comment="是否标记异常")

    def __repr__(self) -> str:  # noqa: D401
        return f"<FinancialStatement(company={self.company!r}, period={self.period!r})>"
