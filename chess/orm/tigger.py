from .constant import When, Event
from .signal import Signal


class Tigger:
    def __init__(self, when: When, event: Event, model: type) -> None:
        self.when = when
        self.event = event
        self.model = model

    def __call__(self, func):
        signal_name = f"{self.model._table}_{self.when.name}_{self.event.name}"
        Signal.register(signal_name, func)
        return func
