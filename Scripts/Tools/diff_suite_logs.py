#!/usr/bin/env python3
"""Compare completed automation tests: exit 0 same, 1 changed, 2 invalid input."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

COMPLETED = re.compile(r"Test Completed\. Result=\{([^}]+)\} Name=\{([^}]*)\}(?: Path=\{([^}]*)\})?")
COMPLETE_MARKER = "TEST COMPLETE. EXIT CODE: 0"


def has_completion_marker(path: Path) -> bool:
    return COMPLETE_MARKER in path.read_text(encoding="utf-8", errors="replace")


def load(path: Path) -> dict[str, str]:
    rows: dict[str, str] = {}
    for number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        match = COMPLETED.search(line)
        if not match:
            continue
        result, name, test_path = match.groups()
        key = test_path or name
        if key in rows:
            raise ValueError(f"{path}:{number}: duplicate completed test identity {key!r}")
        rows[key] = result
    if not rows:
        raise ValueError(f"{path}: no Test Completed records found")
    return rows


def compare(before: dict[str, str], after: dict[str, str]) -> tuple[list[str], list[str], list[str]]:
    added = sorted(after.keys() - before.keys())
    removed = sorted(before.keys() - after.keys())
    changed = sorted(key for key in before.keys() & after.keys() if before[key] != after[key])
    return added, removed, changed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("before", type=Path)
    parser.add_argument("after", type=Path)
    args = parser.parse_args()
    if not args.before.is_file() or not args.after.is_file():
        parser.error("both suite logs must exist")
    incomplete = [label for label, path in (("before", args.before), ("after", args.after)) if not has_completion_marker(path)]
    try:
        before, after = load(args.before), load(args.after)
    except (OSError, ValueError) as error:
        print(f"INVALID: {error}", file=sys.stderr)
        if incomplete:
            print("PARTIAL: missing terminal " + COMPLETE_MARKER + " in " + ", ".join(incomplete))
            return 3
        return 2
    if incomplete:
        print("PARTIAL: missing terminal " + COMPLETE_MARKER + " in " + ", ".join(incomplete))
    added, removed, changed = compare(before, after)
    for label, names in (("ADDED", added), ("REMOVED", removed), ("CHANGED", changed)):
        for name in names:
            print(f"{label} {name}" + (f" {before[name]} -> {after[name]}" if label == "CHANGED" else ""))
    print(f"before={len(before)} after={len(after)} added={len(added)} removed={len(removed)} changed={len(changed)}")
    if incomplete:
        return 3
    return 1 if added or removed or changed else 0


if __name__ == "__main__":
    raise SystemExit(main())
