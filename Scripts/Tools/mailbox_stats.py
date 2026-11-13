#!/usr/bin/env python3
"""Count TEAM_MAILBOX messages by sender party and date."""
from __future__ import annotations

import argparse
import collections
import re
from pathlib import Path

HEADER = re.compile(r"^###\s+\[([A-Z]+)-\d+\]\s+(.+?)\s*->\s*(.+?),\s*(\d{4}-\d{2}-\d{2})", re.M)


def party_day_counts(text: str) -> collections.Counter:
    """BP-33: messages per (party, date) from mailbox headers; the logic main() used inline."""
    return collections.Counter((party, date) for party, _, _, date in HEADER.findall(text))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mailbox", nargs="?", type=Path, default=Path(__file__).resolve().parents[2] / "Documentation" / "TEAM_MAILBOX.md")  # BP-03: repo-root default
    args = parser.parse_args()
    if not args.mailbox.is_file():  # BP-11: a missing input is a named usage error (exit 2), not a traceback
        parser.error(f"input file not found: {args.mailbox}")
    text = args.mailbox.read_text(encoding="utf-8", errors="replace")
    counts = party_day_counts(text)
    for (party, date), count in sorted(counts.items(), key=lambda item: (item[0][1], item[0][0])):
        print(f"{date}\t{party}\t{count}")
    print(f"messages={sum(counts.values())} party_days={len(counts)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
