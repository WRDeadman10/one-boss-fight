#!/usr/bin/env python3
"""Emit a read-only JSON digest of Claude decision messages in a C-id range."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HEADER = re.compile(r"^### \[(?P<id>[A-Z]+-\d+)\] (?P<header>[^\r\n]*)$", re.MULTILINE)


def parse_id(value: str) -> int:
    match = re.fullmatch(r"C-(\d+)", value)
    if not match:
        raise ValueError(f"expected C-<number>, got {value!r}")
    return int(match.group(1))


def digest(text: str, start: str, end: str) -> dict[str, object]:
    first, last = parse_id(start), parse_id(end)
    if first > last:
        raise ValueError("start C-id must be less than or equal to end C-id")
    matches = list(HEADER.finditer(text))
    items = []
    for index, match in enumerate(matches):
        message_id = match.group("id")
        if not message_id.startswith("C-"):
            continue
        number = int(message_id[2:])
        if not first <= number <= last:
            continue
        stop = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        section = text[match.end():stop].strip()
        items.append({"id": message_id, "header": match.group("header"), "body": section})
    return {"schema": "onebossfight.mailbox-decision-digest/v1",
            "range": {"start_inclusive": start, "end_inclusive": end},
            "count": len(items), "messages": items}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("start", help="inclusive lower C-id, e.g. C-900")
    parser.add_argument("end", help="inclusive upper C-id, e.g. C-920")
    parser.add_argument("--mailbox", type=Path, default=ROOT / "Documentation/TEAM_MAILBOX.md")
    parser.add_argument("--output", type=Path, help="write JSON here; stdout by default")
    args = parser.parse_args()
    try:
        result = digest(args.mailbox.read_text(encoding="utf-8"), args.start, args.end)
        payload = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    except (OSError, UnicodeError, ValueError) as exc:
        parser.error(str(exc))
    if args.output:
        args.output.write_text(payload, encoding="utf-8", newline="\n")
    else:
        print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
