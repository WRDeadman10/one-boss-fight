#!/usr/bin/env python3
"""Extract error/fatal lines and build failure summaries from Unreal logs."""
from __future__ import annotations

import argparse
import re
from pathlib import Path

FAIL = re.compile(r"\b(?:error|fatal error|failed|failure|assertion failed)\b", re.I)


def find_failures(text: str) -> list[tuple[int, str]]:
    """BP-33: (1-based line number, right-stripped line) for every line matching FAIL; the logic main() used inline."""
    return [(n, line.rstrip()) for n, line in enumerate(text.splitlines(), 1) if FAIL.search(line)]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("log", type=Path)
    parser.add_argument("--limit", type=int, default=100)
    args = parser.parse_args()
    if not args.log.is_file():  # BP-11: a missing input is a named usage error (exit 2), not a traceback
        parser.error(f"input file not found: {args.log}")
    matches = find_failures(args.log.read_text(encoding="utf-8", errors="replace"))
    for number, line in matches[:max(args.limit, 0)]:
        print(f"{number}: {line}")
    print(f"matches={len(matches)} shown={min(len(matches), max(args.limit, 0))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
