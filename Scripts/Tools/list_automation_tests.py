#!/usr/bin/env python3
"""Inventory Unreal automation test registrations and source locations."""
from __future__ import annotations

import argparse
import re
from pathlib import Path

TEST = re.compile(r"\bIMPLEMENT_(?:SIMPLE_)?AUTOMATION_TEST\s*\(\s*([^,]+)")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    rows = []
    for path in sorted((args.root / "Source/OneBossFight/Tests").rglob("*.cpp")):
        for number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            match = TEST.search(line)
            if match:
                rows.append((match.group(1).strip(), path.relative_to(args.root).as_posix(), number))
    for name, path, number in rows:
        print(f"{name}\t{path}:{number}")
    print(f"registrations={len(rows)} unique_names={len({x[0] for x in rows})}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
