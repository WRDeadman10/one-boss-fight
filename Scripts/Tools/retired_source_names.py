#!/usr/bin/env python3
"""List legacy boss implementation/pack names still mentioned by C++ source."""
from __future__ import annotations

import argparse
import re
from pathlib import Path

TERMS = ("RPGSevarogDirector", "GreystonePack", "SevarogPack")
PATTERN = re.compile("|".join(re.escape(x) for x in TERMS))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    count = 0
    for path in sorted((args.root / "Source").rglob("*")):
        if path.suffix.lower() not in {".h", ".cpp"}:
            continue
        for number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            match = PATTERN.search(line)
            if match:
                count += 1
                print(f"{path.relative_to(args.root)}:{number}: {match.group()}")
    print(f"terms={','.join(TERMS)} source_occurrences={count}; occurrence list only, not a verdict")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
