#!/usr/bin/env python3
"""Compare [FrameworkProof] event token counts between two logs."""
from __future__ import annotations

import argparse
import collections
import re
from pathlib import Path

TOKEN = re.compile(r"\[FrameworkProof\]\s+(\S+)")


def count(path: Path):
    return collections.Counter(TOKEN.findall(path.read_text(encoding="utf-8", errors="replace")))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("before", type=Path)
    parser.add_argument("after", type=Path)
    args = parser.parse_args()
    a, b = count(args.before), count(args.after)
    print("TOKEN\tBEFORE\tAFTER\tDELTA")
    for token in sorted(a.keys() | b.keys()):
        print(f"{token}\t{a[token]}\t{b[token]}\t{b[token]-a[token]:+d}")
    print(f"tokens={len(a.keys() | b.keys())} before_events={sum(a.values())} after_events={sum(b.values())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
