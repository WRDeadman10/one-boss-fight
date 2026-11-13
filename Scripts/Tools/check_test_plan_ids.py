#!/usr/bin/env python3
"""Check BUILD IDs in TEST_PLAN.md are unique and numerically sorted."""
from __future__ import annotations

import argparse
import re
from pathlib import Path

ROW = re.compile(r"^\|\s*BUILD-(\d+)\s*\|", re.M)


def build_ids(text: str):
    """BP-34: (BUILD ids in table order, sorted duplicate ids) from TEST_PLAN text; moved from main()."""
    ids = [int(value) for value in ROW.findall(text)]
    return ids, sorted({value for value in ids if ids.count(value) > 1})


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])  # BP-03: repo root, not the current folder
    args = parser.parse_args()
    path = args.root / "Documentation/TEST_PLAN.md"
    ids, duplicates = build_ids(path.read_text(encoding="utf-8"))
    if duplicates:
        print("duplicate BUILD IDs: " + ", ".join(f"BUILD-{value:03d}" for value in duplicates))
    if ids != sorted(ids):
        print("BUILD IDs are not in numeric order")
    print(f"build_rows={len(ids)} unique={len(set(ids))}")
    return int(bool(duplicates or ids != sorted(ids)))


if __name__ == "__main__":
    raise SystemExit(main())
