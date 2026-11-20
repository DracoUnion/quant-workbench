"""SQLAlchemy 模型基类。

所有 ORM 模型从此派生，自动提供 id（主键）、created_at、updated_at。
"""

from __future__ import annotations

from datetime import datetime
from typing import Annotated

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, declared_attr, mapped_column

#: 通用主键列
Id = Annotated[int, mapped_column(primary_key=True, autoincrement=True)]
#: 通用创建时间列
CreatedAt = Annotated[
    datetime,
    mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False),
]
#: 通用更新时间列
UpdatedAt = Annotated[
    datetime,
    mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    ),
]


class Base(DeclarativeBase):
    """所有 ORM 模型的基类。"""

    id: Id
    created_at: CreatedAt
    updated_at: UpdatedAt

    @declared_attr.directive
    def __tablename__(cls) -> str:  # noqa: D401
        return cls.__name__.lower()

    def __repr__(self) -> str:  # noqa: D401
        return f"<{self.__class__.__name__}(id={self.id})>"
