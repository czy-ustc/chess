from typing import Any

from .task import Task

task_pool = []


class PoolMeta(type):
    def __init__(cls, name: str, bases: tuple, attrs: dict):
        cls._processor = None

    @property
    def processor(cls) -> Any:
        return cls._processor

    @processor.setter
    def processor(cls, value: Any) -> None:
        cls._processor = value
        for task in task_pool:
            value(task)


class Pool(metaclass=PoolMeta):
    @classmethod
    def add(cls, task: Task) -> Any:
        if cls.processor is None:
            task_pool.append(task)
            return None
        return cls.processor(task)
