"""Timer dataclasses."""

from dataclasses import dataclass


@dataclass
class TimerPreset:
    key: str
    label: str
    duration_seconds: int
    note: str = ""


@dataclass
class TimerState:
    elapsed_seconds: int
    remaining_seconds: int
    done: bool

