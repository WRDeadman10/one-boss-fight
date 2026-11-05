#!/usr/bin/env python3
"""Print a compact text timeline of [FrameworkProof] events from an Unreal log."""
from __future__ import annotations

import argparse
import datetime as dt
import re
from pathlib import Path

EVENT = re.compile(r"\[(\d{4}\.\d\d\.\d\d-\d\d\.\d\d\.\d\d:\d+)\]\[(\s*\d+)\].*?\[FrameworkProof\]\s+(\S+)(.*)")
FIELD = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)=([^\s]+)")


def events(path: Path) -> list[tuple[float, int, str, str, str, str]]:
    rows = []
    origin = None
    active_encounter = active_generation = None
    for line_number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        match = EVENT.search(line)
        if not match:
            continue
        stamp, frame, token, payload = match.groups()
        when = dt.datetime.strptime(stamp, "%Y.%m.%d-%H.%M.%S:%f")
        origin = when if origin is None else origin
        fields = dict(FIELD.findall(payload))
        if "encounter" in fields:
            active_encounter = fields["encounter"]
        if "generation" in fields:
            active_generation = fields["generation"]
        identity = []
        if fields.get("encounter", active_encounter) is not None:
            identity.append("e=" + fields.get("encounter", active_encounter))
        if fields.get("generation", active_generation) is not None:
            identity.append("g=" + fields.get("generation", active_generation))
        if "instance" in fields:
            identity.append("i=" + fields["instance"])
        detail = " ".join(f"{key}={fields[key]}" for key in ("instance", "card", "kind", "window", "outcome", "state", "reason") if key in fields)
        rows.append(((when-origin).total_seconds(), line_number, frame.strip(), "/".join(identity) or "-", token, detail or payload.strip()))
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("log", type=Path)
    parser.add_argument("--limit", type=int, default=300)
    args = parser.parse_args()
    if not args.log.is_file():
        parser.error(f"missing log: {args.log}")
    rows = events(args.log)
    if not rows:
        print("No [FrameworkProof] timeline events found.")
        return 0
    print(f"elapsed  log_line frame group          token              details ({args.log})")
    for seconds, line_number, frame, group, token, detail in rows[:max(0, args.limit)]:
        print(f"{seconds:7.3f}s {line_number:>8} {frame:>5} {group:<14} {token:<18} {detail}")
    if len(rows) > args.limit:
        print(f"... {len(rows)-args.limit} additional events omitted")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
