"""知识库模型。"""

from __future__ import annotations

from typing import Any

from sqlalchemy import JSON, Integer, String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, CreatedAt, Id, UpdatedAt


class KnowledgeBase(Base):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    """知识库。"""

    __tablename__ = "knowledge_base"

    name: Mapped[str] = mapped_column(String(200), index=True, comment="库名")
    domain: Mapped[str] = mapped_column(String(64), index=True, comment="领域，如‘半导体’、‘宏观’")
    description: Mapped[str] = mapped_column(Text, default="", comment="描述")
    status: Mapped[str] = mapped_column(
        String(16), default="active", comment="active/archived"
    )

    docs: Mapped[list["KnowledgeDoc"]] = relationship(
        back_populates="kb", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # noqa: D401
        return f"<KnowledgeBase(name={self.name!r}, domain={self.domain!r})>"


class KnowledgeDoc(Base):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    """知识库文档。"""

    __tablename__ = "knowledge_doc"

    kb_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("knowledge_base.id", ondelete="CASCADE"), index=True
    )
    source_type: Mapped[str] = mapped_column(
        String(32), comment="来源类型：pdf/web/rss/api/manual"
    )
    source_uri: Mapped[str | None] = mapped_column(
        String(512), default=None, comment="来源 URI"
    )
    title: Mapped[str] = mapped_column(String(200), comment="标题")
    raw_text: Mapped[str] = mapped_column(Text, default="", comment="原始文本")
    cleaned_text: Mapped[str] = mapped_column(
        Text, default="", comment="清洗后文本"
    )
    tags_json: Mapped[str] = mapped_column(
        JSON, default="[]", comment="标签数组 JSON"
    )
    credibility: Mapped[float] = mapped_column(
        default=1.0, comment="可信度 0~1"
    )

    kb: Mapped["KnowledgeBase"] = relationship(back_populates="docs")
    chunks: Mapped[list["KnowledgeChunk"]] = relationship(
        back_populates="doc", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # noqa: D401
        return f"<KnowledgeDoc(title={self.title!r}, kb_id={self.kb_id})>"


class KnowledgeChunk(Base):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    """知识库分块。"""

    __tablename__ = "knowledge_chunk"

    doc_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("knowledge_doc.id", ondelete="CASCADE"), index=True
    )
    chunk_index: Mapped[int] = mapped_column(Integer, comment="分块索引")
    text: Mapped[str] = mapped_column(Text, comment="分块文本")
    tokens: Mapped[int] = mapped_column(Integer, default=0, comment="Token 数")
    meta_json: Mapped[str] = mapped_column(JSON, default="{}", comment="元数据")

    doc: Mapped["KnowledgeDoc"] = relationship(back_populates="chunks")

    def __repr__(self) -> str:  # noqa: D401
        return f"<KnowledgeChunk(doc_id={self.doc_id}, index={self.chunk_index})>"


class VectorIndexConfig(Base):
    """向量索引配置。"""

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    __tablename__ = "vector_index_config"

    kb_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("knowledge_base.id", ondelete="CASCADE"), unique=True
    )
    field_mapping_json: Mapped[str] = mapped_column(
        JSON, default="{}", comment="字段映射配置"
    )
    recall_policy_json: Mapped[str] = mapped_column(
        JSON, default="{}", comment="召回策略配置"
    )
    dedup_rule_json: Mapped[str] = mapped_column(
        JSON, default="{}", comment="去重规则配置"
    )

    def __repr__(self) -> str:  # noqa: D401
        return f"<VectorIndexConfig(kb_id={self.kb_id})>"
