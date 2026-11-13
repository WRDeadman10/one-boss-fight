#!/usr/bin/env python3
"""Find duplicate MoveId values across one or more card JSON exports."""
from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path

import sys as _sys
_sys.path.insert(0, str(Path(__file__).resolve().parent))  # BP-06: sibling json_input as a script or via -m
from json_input import JsonInputError, fail, load_json, require_objects


def load_cards(path: Path) -> list:
    """BP-07: a card export is a list of card objects or an object with a "cards" list; raises JsonInputError otherwise."""
    data = load_json(path, (dict, list))
    if isinstance(data, dict):  # X-2298: an object export must carry an explicit "cards" list ({} is not an empty export)
        if "cards" not in data:
            raise JsonInputError(f"{path}: object export has no \"cards\" key")
        data = data["cards"]
    return require_objects(path, data, "cards")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("exports", nargs="+", type=Path)
    args = parser.parse_args()
    found = collections.defaultdict(list)
    paths = list(dict.fromkeys(path.resolve() for path in args.exports))
    try:  # BP-07: validate every export before reporting anything
        loaded = [(path, load_cards(path)) for path in paths]
    except JsonInputError as error:
        return fail(error)
    for path, cards in loaded:
        for card in cards:
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
