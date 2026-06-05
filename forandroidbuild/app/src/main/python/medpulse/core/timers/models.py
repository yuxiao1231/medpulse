"""Timer dataclasses."""

class TimerPreset:
    def __init__(self, key, label, duration_seconds, note=""):
        self.key = key
        self.label = label
        self.duration_seconds = duration_seconds
        self.note = note


class TimerState:
    def __init__(self, elapsed_seconds, remaining_seconds, done):
        self.elapsed_seconds = elapsed_seconds
        self.remaining_seconds = remaining_seconds
        self.done = done

