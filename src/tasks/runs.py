"""工作流运行执行器。

RunExecutor：运行执行器接口。
InlineExecutor：桌面默认执行器，每个 run 启动一个 daemon Thread 执行，
每次数据库操作独立开启 SQLAlchemy Session，禁止跨线程共享 Session。
"""

from __future__ import annotations

import threading
from abc import ABC, abstractmethod
from typing import Any


class RunExecutor(ABC):
    """运行执行器接口。"""

    @abstractmethod
    def submit(self, run_id: int) -> str:
        """提交一个 run 执行，返回任务标识。"""

    def stop(self, run_id: int) -> bool:
        """请求终止一个 run（默认不可终止）。"""
        return False


class InlineExecutor(RunExecutor):
    """进程内 inline 执行器：每个 run 独享 daemon Thread 与数据库 Session。"""

    def __init__(self, run_service: Any) -> None:
        self.run_service = run_service
        self._threads: dict[int, threading.Thread] = {}
        self._lock = threading.Lock()

    def submit(self, run_id: int) -> str:
        with self._lock:
            if run_id in self._threads:
                return str(run_id)
            thread = threading.Thread(target=self._run, args=(run_id,), daemon=True)
            self._threads[run_id] = thread
            thread.start()
        return str(run_id)

    def _run(self, run_id: int) -> None:
        try:
            self.run_service.run_workflow(run_id)
        finally:
            with self._lock:
                self._threads.pop(run_id, None)

    def stop(self, run_id: int) -> bool:
        with self._lock:
            thread = self._threads.get(run_id)
        if thread is None or not thread.is_alive():
            return False
        # daemon 线程无法安全中断；由 run_service 层面的熔断/终止标记控制
        return False
