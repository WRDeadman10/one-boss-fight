"""Small runtime-independent helpers shared by Unreal PIE drivers."""


class FinalResult:
    """Emit one stable terminal RESULT line for a PIE driver."""

    def __init__(self, logger, driver):
        self._logger = logger
        self._driver = str(driver)
        self._emitted = False

    @property
    def emitted(self):
        return self._emitted

    def emit(self, passed, reason, **fields):
        if self._emitted:
            return False
        self._emitted = True
        clean = lambda value: str(value).replace("\r", " ").replace("\n", " ")
        suffix = " ".join("%s=%s" % (clean(key), clean(value)) for key, value in sorted(fields.items()))
        line = "RESULT=%s driver=%s reason=%s" % (
            "PASS" if passed else "FAIL", clean(self._driver), clean(reason))
        self._logger(line + ((" " + suffix) if suffix else ""))
        return True


class MappingReadinessGate:
    """Bounded polling gate. poll returns ready, waiting, or a terminal error."""

    def __init__(self, timeout_seconds):
        self.timeout_seconds = float(timeout_seconds)
        self.elapsed = 0.0
        self.finished = False

    def poll(self, delta_seconds, readiness):
        if self.finished:
            return "already_finished"
        try:
            delta = float(delta_seconds)
            if delta < 0.0 or delta != delta or delta == float("inf"):
                self.finished = True
                return "invalid_delta"
            ready = bool(readiness())
        except Exception:
            self.finished = True
            return "readiness_error"
        if ready:
            self.finished = True
            return "ready"
        self.elapsed += delta
        if self.elapsed >= self.timeout_seconds:
            self.finished = True
            return "timeout"
        return "waiting"
