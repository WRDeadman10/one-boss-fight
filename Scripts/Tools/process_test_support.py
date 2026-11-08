"""Bound subprocess helpers shared by offline test modules."""
from __future__ import annotations

import subprocess
from typing import Any


def run_test_subprocess(test_case: Any, command: list[str], *, timeout: float, **kwargs: Any) -> subprocess.CompletedProcess[str]:
    """Run a child with a mandatory wall-time bound and fail with captured context."""
    try:
        return subprocess.run(command, timeout=timeout, **kwargs)
    except subprocess.TimeoutExpired as exc:
        def display(value: str | bytes | None) -> str:
            if value is None:
                return ""
            return value.decode("utf-8", errors="replace") if isinstance(value, bytes) else value

        test_case.fail(
            f"subprocess exceeded {timeout:g}s timeout; command={exc.cmd!r}; "
            f"stdout={display(exc.stdout)!r}; stderr={display(exc.stderr)!r}"
        )
