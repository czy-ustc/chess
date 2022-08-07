from typing import Any, Callable, Dict, List


class Signal:
    _listeners: Dict[str, List[Callable]] = {}

    @classmethod
    def register(cls, signal: str, listener: Callable) -> None:
        cls._listeners.setdefault(signal, [])
        cls._listeners[signal].append(listener)

    @classmethod
    def send(cls, signal: str, *args: Any, **kwargs: Any) -> None:
        for listener in cls._listeners.get(signal, []):
            listener(*args, **kwargs)
