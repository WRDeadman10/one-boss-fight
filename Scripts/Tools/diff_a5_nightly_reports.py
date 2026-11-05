#!/usr/bin/env python3
"""Compare two complete RunA5ParityNightly.ps1 Markdown summaries."""
from __future__ import annotations

import argparse
import re
from pathlib import Path


ROW = re.compile(r"^\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*(PASS|FAIL)\s*\|\s*(.*?)\s*\|$")
COUNT = re.compile(r"^(\d+)/(\d+)$")


def parse_report(path: Path) -> dict[str, dict]:
    rows = {}
    saw_header = False
    for line_number, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        if line.strip().startswith("| Driver | Legacy checks | Data checks | Result | Detail |"):
            saw_header = True
            continue
        match = ROW.match(line.strip())
        if not match:
            continue
        driver, legacy, data, result, detail = match.groups()
        if driver in {"Driver", "---"}:
            continue
        if driver in rows:
            raise ValueError(f"{path}:{line_number}: duplicate driver {driver}")
        if result not in {"PASS", "FAIL"}:
            raise ValueError(f"{path}:{line_number}: invalid result {result}")
        parsed_counts = []
        for label, value in (("legacy", legacy.strip()), ("data", data.strip())):
            if value == "-":
                parsed_counts.append(None)
                continue
            count = COUNT.fullmatch(value)
            if not count:
                raise ValueError(f"{path}:{line_number}: malformed {label} count {value!r}")
            parsed_counts.append((int(count.group(1)), int(count.group(2))))
        rows[driver] = {"legacy": parsed_counts[0], "data": parsed_counts[1],
                        "result": result, "detail": detail.strip()}
    if not saw_header:
        raise ValueError(f"{path}: A5 nightly summary header missing")
    if len(rows) != 31:
        raise ValueError(f"{path}: expected 31 complete driver rows, found {len(rows)}")
    if any(row["result"] == "PASS" and (row["legacy"] is None or row["data"] is None)
           for row in rows.values()):
        raise ValueError(f"{path}: PASS row lacks a completed arm count")
    return rows


def compare(left: dict[str, dict], right: dict[str, dict]) -> list[str]:
    if set(left) != set(right):
        missing = sorted(set(left) - set(right))
        added = sorted(set(right) - set(left))
        return [f"driver set mismatch: missing={missing}; added={added}"]
    changes = []
    for driver in sorted(left):
        before, after = left[driver], right[driver]
        if before["result"] != after["result"]:
            label = "NEW_FAIL" if after["result"] == "FAIL" else "FIXED"
            changes.append(f"{label} {driver}: {before['result']} -> {after['result']} ({after['detail']})")
        if before["legacy"] != after["legacy"] or before["data"] != after["data"]:
            changes.append(f"CHECK_COUNT_CHANGED {driver}: legacy {before['legacy']} -> {after['legacy']}; data {before['data']} -> {after['data']}")
    return changes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baseline", type=Path, help="previous complete summary.md")
    parser.add_argument("current", type=Path, help="new complete summary.md")
    args = parser.parse_args()
    try:
        changes = compare(parse_report(args.baseline), parse_report(args.current))
    except (OSError, UnicodeError, ValueError) as exc:
        parser.error(str(exc))
    if changes:
        print("CHANGES")
        for change in changes:
            print("- " + change)
    else:
        print("NO_CHANGES: all 31 driver verdicts and per-arm check counts match")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
