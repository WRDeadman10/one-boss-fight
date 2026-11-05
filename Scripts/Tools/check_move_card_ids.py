#!/usr/bin/env python3
"""Find duplicate MoveId values across one or more card JSON exports."""
from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("exports", nargs="+", type=Path)
    args = parser.parse_args()
    found = collections.defaultdict(list)
    paths = list(dict.fromkeys(path.resolve() for path in args.exports))
    for path in paths:
        data = json.loads(path.read_text(encoding="utf-8"))
        for card in data if isinstance(data, list) else data.get("cards", []):
            ident = card.get("MoveId") or card.get("moveId")
            if ident:
                found[ident].append(str(path))
    duplicates = {key: paths for key, paths in found.items() if len(paths) > 1}
    for ident, paths in sorted(duplicates.items()):
        print(f"DUPLICATE {ident}: {'; '.join(paths)}")
    print(f"move_ids={len(found)} duplicate_ids={len(duplicates)}")
    return int(bool(duplicates))


if __name__ == "__main__":
    raise SystemExit(main())
