"""日志模块。

按 run_id 分文件，便于排查单次运行。
"""

from __future__ import annotations

import logging
import logging.handlers
import os
from pathlib import Path

from .config import settings

LOG_DIR = Path("src/data/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)


def get_logger(name: str) -> logging.Logger:
    """获取（或创建）带文件处理器的 logger。"""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))

    # 控制台输出
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    )
    logger.addHandler(ch)

    # 按 run_id 分文件（运行时由 run_service 注入 run_id 后再添加 file handler）
    return logger


def get_run_logger(run_id: str, name: str = "run") -> logging.Logger:
    """获取（或创建）按 run_id 分文件的 logger。"""
    logger_name = f"{name}.{run_id}"
    logger = logging.getLogger(logger_name)
    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))

    # 文件处理器：src/data/logs/<run_id>.log
    fh = logging.handlers.RotatingFileHandler(
        LOG_DIR / f"{run_id}.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    )
    logger.addHandler(fh)

    # 同时输出到控制台
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    )
    logger.addHandler(ch)

    return logger
