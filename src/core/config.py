"""核心配置层（pydantic-settings 风格，零 Qt）。

仅从环境变量读取配置，不依赖 Qt / 数据库 / QSettings。
可被 ui 层通过 AppContext 统一访问。
"""

from __future__ import annotations

from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置，全部从环境变量读取。"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ---- 数据库 ----
    database_url: str = Field(
        default="sqlite:///src/data/fin_workbench.db",
        description="SQLAlchemy 数据库连接 URL",
    )
    run_executor: str = Field(
        default="inline",
        description="运行执行器：inline / celery",
    )

    # ---- LLM ----
    llm_provider: str = Field(default="openai", description="LLM 提供商")
    llm_api_key: Optional[str] = Field(default=None, description="LLM API Key")
    llm_base_url: str = Field(default="https://api.openai.com/v1", description="LLM 基础 URL")
    llm_model: str = Field(default="gpt-4o-mini", description="LLM 模型名")

    # ---- 外部适配器 ----
    search_provider: str = Field(default="mock", description="搜索数据源提供商")
    market_data_provider: str = Field(default="mock", description="行情数据源提供商")
    push_channel: str = Field(default="mock", description="推送通道")

    # ---- Redis / Celery（可选） ----
    redis_url: Optional[str] = Field(default=None, description="Redis 连接 URL")
    celery_broker_url: Optional[str] = Field(default=None, description="Celery Broker URL")
    celery_result_backend: Optional[str] = Field(
        default=None, description="Celery 结果后端 URL"
    )

    # ---- UI / 数据源 ----
    prompts_data_path: str = Field(default="data/prompts.json", description="提示词种子数据文件路径")
    window_title: str = Field(default="金融智能体工作台 — QuantWorkbench", description="窗口标题")
    window_width: int = Field(default=1200, description="窗口宽度")
    window_height: int = Field(default=800, description="窗口高度")
    theme: str = Field(default="dark", description="界面主题：dark / light")

    # ---- 日志 ----
    log_level: str = Field(default="INFO", description="日志级别")


@lru_cache
def get_settings() -> Settings:
    """带缓存的 Settings 单例获取。"""
    return Settings()


# 向后兼容：供 bootstrap 等旧代码直接 import settings
settings = get_settings()
