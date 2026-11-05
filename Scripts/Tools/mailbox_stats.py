#!/usr/bin/env python3
"""Count TEAM_MAILBOX messages by sender party and date."""
from __future__ import annotations

import argparse
import collections
import re
from pathlib import Path

HEADER = re.compile(r"^###\s+\[([A-Z]+)-\d+\]\s+(.+?)\s*->\s*(.+?),\s*(\d{4}-\d{2}-\d{2})", re.M)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mailbox", nargs="?", type=Path, default=Path("Documentation/TEAM_MAILBOX.md"))
    args = parser.parse_args()
    text = args.mailbox.read_text(encoding="utf-8", errors="replace")
    counts = collections.Counter((party, date) for party, _, _, date in HEADER.findall(text))
    for (party, date), count in sorted(counts.items(), key=lambda item: (item[0][1], item[0][0])):
        print(f"{date}\t{party}\t{count}")
    print(f"messages={sum(counts.values())} party_days={len(counts)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
