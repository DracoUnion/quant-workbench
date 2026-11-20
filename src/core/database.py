"""数据库层：SQLAlchemy 2 引擎 + Session 管理。

零 Qt 层，可被 headless 测试。
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from .config import settings
from ..models.base import Base

# ---------------------------------------------------------------------------
# Engine（单例，全局复用）
# ---------------------------------------------------------------------------

_engine = None
_session_factory = None


def get_engine():
    """获取（单例）SQLAlchemy Engine。"""
    global _engine
    if _engine is None:
        import os

        database_url = settings.database_url
        connect_args = {}
        if database_url.startswith("sqlite"):
            # 确保 SQLite 文件所在目录存在
            db_path = database_url[len("sqlite:///"):]
            parent = os.path.dirname(os.path.abspath(db_path))
            if parent:
                os.makedirs(parent, exist_ok=True)
            connect_args = {"check_same_thread": False}
        _engine = create_engine(
            database_url,
            echo=False,
            pool_pre_ping=True,
            connect_args=connect_args,
        )
    return _engine


def get_sessionmaker() -> sessionmaker:
    """获取 Session 工厂（单例）。"""
    global _session_factory
    if _session_factory is None:
        _session_factory = sessionmaker(
            bind=get_engine(), autoflush=False, expire_on_commit=False
        )
    return _session_factory


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    """提供一个事务性作用域的 Session。

    用法：
        with session_scope() as session:
            session.add(obj)
    # 自动 commit / rollback / close
    """
    session = get_sessionmaker()()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()




def init_db() -> None:
    """初始化数据库：创建所有表（首次启动调用）。"""
    from sqlalchemy import inspect

    engine = get_engine()
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())

    # 导入所有模型以注册到 Base.metadata
    import src.models  # noqa: F401  # noqa: E501

    Base.metadata.create_all(bind=engine, tables=None)

    # 打印新建表（调试用）
    all_tables = set(inspector.get_table_names())
    new_tables = all_tables - existing_tables
    if new_tables:
        print(f"[init_db] 新建表: {sorted(new_tables)}")
