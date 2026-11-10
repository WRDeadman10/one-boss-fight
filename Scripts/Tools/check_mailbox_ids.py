#!/usr/bin/env python3
"""Audit sequential C-, X- and A- message header IDs in TEAM_MAILBOX.md."""
from __future__ import annotations

import argparse
import collections
import re
from pathlib import Path

HEADER = re.compile(r"^###\s+\[([CXA])-(\d+)\]")


def audit(path: Path) -> list[str]:
    found: dict[str, list[tuple[int, int]]] = collections.defaultdict(list)
    for line_number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        match = HEADER.match(line)
        if match:
            found[match.group(1)].append((int(match.group(2)), line_number))
    issues: list[str] = []
    for party in "CXA":
        seen: dict[int, list[int]] = collections.defaultdict(list)
        for value, line in found.get(party, []):
            seen[value].append(line)
        for value, lines in sorted(seen.items()):
            if len(lines) > 1:
                issues.append(f"{party}-{value}: duplicate headers at lines {','.join(map(str, lines))}")
        values = sorted(seen)
        if values and values[0] > 1:
            issues.append(f"{party}: skipped IDs 1..{values[0] - 1}")
        for previous, current in zip(values, values[1:]):
            if current > previous + 1:
                issues.append(f"{party}: skipped IDs {previous + 1}..{current - 1}")
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mailbox", nargs="?", type=Path, default=Path("Documentation/TEAM_MAILBOX.md"))
    args = parser.parse_args()
    if not args.mailbox.is_file():
        parser.error(f"mailbox not found: {args.mailbox}")
    issues = audit(args.mailbox)
    for issue in issues:
        print(issue)
    print(f"message_headers={sum(len(v) for v in _headers(args.mailbox).values())} issues={len(issues)}")
    return 1 if issues else 0


def _headers(path: Path) -> dict[str, list[int]]:
    result: dict[str, list[int]] = collections.defaultdict(list)
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        match = HEADER.match(line)
        if match:
            result[match.group(1)].append(int(match.group(2)))
    return result


if __name__ == "__main__":
    raise SystemExit(main())
