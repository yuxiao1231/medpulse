"""Deterministic timer calculations."""

import time

from medpulse.core.timers.models import TimerPreset, TimerState


DEFAULT_PRESETS = {
    "tpa_4_5h": TimerPreset("tpa_4_5h", "tPA 4.5h", 4 * 3600 + 30 * 60, "Time window countdown only"),
    "sepsis_1h": TimerPreset("sepsis_1h", "Sepsis 1h", 3600, "Bundle timer"),
    "sepsis_3h": TimerPreset("sepsis_3h", "Sepsis 3h", 3 * 3600, "Bundle timer"),
    "acls_cpr_cycle": TimerPreset("acls_cpr_cycle", "ACLS CPR 2min", 120, "CPR cycle reminder"),
}


def countdown_status(started_at_epoch, duration_seconds, now_epoch=None):
    now = int(now_epoch if now_epoch is not None else time.time())
    elapsed = max(0, now - int(started_at_epoch))
    remaining = max(0, int(duration_seconds) - elapsed)
    return TimerState(elapsed_seconds=elapsed, remaining_seconds=remaining, done=remaining == 0)


def elapsed_status(started_at_epoch, now_epoch=None):
    now = int(now_epoch if now_epoch is not None else time.time())
    elapsed = max(0, now - int(started_at_epoch))
    return TimerState(elapsed_seconds=elapsed, remaining_seconds=0, done=False)

