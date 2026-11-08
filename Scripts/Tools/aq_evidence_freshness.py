"""Classify evidence identity metadata without opening or changing raw artifacts."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def classify_record(
    record: dict[str, Any], *, expected_build: str, expected_route: str, cutoff_utc: datetime
) -> str:
    """Return CURRENT, STALE, MISSING_IDENTITY, or MISMATCH for a manifest row.

    Required identity is explicit build, route, and timezone-aware ISO timestamp.
    Missing fields are never inferred from a folder name or neighboring file.
    """
    build = record.get("build")
    route = record.get("route")
    timestamp = record.get("timestamp_utc")
    if not isinstance(build, str) or not build or not isinstance(route, str) or not route or not isinstance(timestamp, str) or not timestamp:
        return "MISSING_IDENTITY"
    if build != expected_build or route != expected_route:
        return "MISMATCH"
    try:
        observed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    except ValueError:
        return "MISSING_IDENTITY"
    if observed.tzinfo is None or observed.utcoffset() is None:
        return "MISSING_IDENTITY"
    if cutoff_utc.tzinfo is None or cutoff_utc.utcoffset() is None:
        raise ValueError("cutoff_utc must include a timezone")
    if observed.astimezone(timezone.utc) < cutoff_utc.astimezone(timezone.utc):
        return "STALE"
    return "CURRENT"
