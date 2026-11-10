"""Small deterministic sampling helpers for the Sevarog frame-capture driver."""

import math


def sample_times(duration_seconds, frames_per_second=15.0):
    """Return 0..duration at a fixed rate, including the exact final time once."""
    duration = float(duration_seconds)
    rate = float(frames_per_second)
    if not math.isfinite(duration) or duration < 0.0:
        raise ValueError("duration_seconds must be finite and non-negative")
    if not math.isfinite(rate) or rate <= 0.0:
        raise ValueError("frames_per_second must be finite and positive")

    last_regular_index = int(math.floor(duration * rate + 1.0e-9))
    times = [index / rate for index in range(last_regular_index + 1)]
    if duration - times[-1] > 1.0e-6:
        times.append(duration)
    return times
