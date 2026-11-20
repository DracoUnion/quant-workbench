"""零 Qt 任务层。

Task / TaskState / TaskManager + TaskCancelled，供后台非流式调用使用，
与 Qt 解耦，可被 headless 测试。
"""

from __future__ import annotations

import threading
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional


class TaskState(Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"


class TaskCancelled(Exception):
    """任务被取消。"""


@dataclass
class Task:
    id: str
    name: str
    func: Callable[..., Any]
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    state: TaskState = TaskState.pending
    result: Any = None
    error: Optional[BaseException] = None


class TaskManager:
    """极简任务池（零 Qt）。"""

    def __init__(self) -> None:
        self._tasks: dict[str, Task] = {}
        self._lock = threading.Lock()

    def submit(self, name: str, func: Callable[..., Any], *args, **kwargs) -> str:
        task_id = uuid.uuid4().hex
        task = Task(id=task_id, name=name, func=func, args=args, kwargs=kwargs)
        with self._lock:
            self._tasks[task_id] = task
        threading.Thread(target=self._run, args=(task,), daemon=True).start()
        return task_id

    def _run(self, task: Task) -> None:
        task.state = TaskState.RUNNING
        try:
            task.result = task.func(*task.args, **task.kwargs)
            task.state = TaskState.completed
        except TaskCancelled:
            task.state = TaskState.cancelled
        except BaseException as exc:  # noqa: BLE001
            task.error = exc
            task.state = TaskState.failed

    def get(self, task_id: str) -> Optional[Task]:
        with self._lock:
            return self._tasks.get(task_id)

    def cancel(self, task_id: str) -> bool:
        task = self.get(task_id)
        if task is None or task.state in (
            TaskState.completed,
            TaskState.failed,
            TaskState.cancelled,
        ):
            return False
        # 标记取消；func 自身需检查是否应中断
        task.state = TaskState.cancelled
        return True

    def all(self) -> list[Task]:
        with self._lock:
            return list(self._tasks.values())
