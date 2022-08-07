from typing import Any

from .constant import TaskType


class Task:
    def __init__(self, tasktype: TaskType, value: Any) -> None:
        self._tasktype = tasktype
        self._value = value

    @property
    def tasktype(self) -> TaskType:
        return self._tasktype

    @property
    def value(self) -> Any:
        return self._value
