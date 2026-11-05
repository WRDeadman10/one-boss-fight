#!/usr/bin/env python3
"""Compact explicit open-state mentions in the last N team mailbox posts."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

HEADER = re.compile(r"^### \[(?P<id>[A-Z]+-\d+)\] (?P<header>[^\r\n]*)$", re.MULTILINE)
OPEN_SIGNAL = re.compile(r"\b(?:OPEN|WAITING|PENDING|BLOCKED|PARTIAL|REVIEW REQUESTED|DECISION NEEDED)\b", re.I)


def digest(text: str, limit: int = 200) -> dict[str, object]:
    matches = list(HEADER.finditer(text))[-limit:]
    messages = []
    for index, match in enumerate(matches):
        stop = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        body = text[match.end():stop].strip()
        signals = list(dict.fromkeys(signal.upper() for signal in OPEN_SIGNAL.findall(body)))
        if signals:
            compact = " ".join(body.split())
            messages.append({"id": match.group("id"), "header": match.group("header"),
                             "signals": signals, "excerpt": compact[:360]})
    return {"schema": "onebossfight.mailbox-open-mentions/v1", "window_messages": len(matches),
            "items": messages,
            "interpretation": "explicit status-word mentions only; items are not deduplicated or inferred closed"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mailbox", type=Path, default=Path(__file__).resolve().parents[2] / "Documentation/TEAM_MAILBOX.md")
    parser.add_argument("--limit", type=int, default=200)
    args = parser.parse_args()
    if args.limit < 1:
        parser.error("--limit must be positive")
    try:
        result = digest(args.mailbox.read_text(encoding="utf-8"), args.limit)
    except (OSError, UnicodeError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
