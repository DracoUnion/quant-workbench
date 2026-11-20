"""提示词模型。"""

from __future__ import annotations

from typing import Any

from sqlalchemy import JSON, Integer, String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, CreatedAt, Id, UpdatedAt


class PromptTemplate(Base):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    """提示词模板种子数据。"""

    __tablename__ = "prompt_template"

    code: Mapped[str] = mapped_column(String(64), unique=True, index=True, comment="模板编号 P001…P076")
    title: Mapped[str] = mapped_column(String(200), comment="模板标题")
    category: Mapped[str] = mapped_column(String(64), comment="一级分类，如‘核心框架’、‘合规审查’")
    sub_category: Mapped[str] = mapped_column(
        String(64), default="", comment="二级分类，如‘通用骨架’、‘红线词扫描’"
    )
    body: Mapped[str] = mapped_column(Text, comment="提示词正文 Markdown")
    params_json: Mapped[str] = mapped_column(
        JSON, default="{}", comment="结构化参数：权重、约束、输出格式等"
    )
    version: Mapped[int] = mapped_column(Integer, default=1, comment="模板版本号")

    versions: Mapped[list["PromptVersion"]] = relationship(
        back_populates="template", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # noqa: D401
        return f"<PromptTemplate(code={self.code!r}, title={self.title!r})>"


class PromptVersion(Base):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    """提示词模板版本历史。"""

    __tablename__ = "prompt_version"

    prompt_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("prompt_template.id", ondelete="CASCADE"), index=True
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, comment="版本号")
    body: Mapped[str] = mapped_column(Text, comment="该版本的正文")
    diff: Mapped[str | None] = mapped_column(Text, default=None, comment="与上一版本的差异")
    created_at: Mapped[CreatedAt]

    template: Mapped["PromptTemplate"] = relationship(back_populates="versions")

    def __repr__(self) -> str:  # noqa: D401
        return f"<PromptVersion(prompt_id={self.prompt_id}, version={self.version})>"
