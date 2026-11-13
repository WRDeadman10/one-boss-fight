#!/usr/bin/env python3
"""Check baked card exports for increasing in-window sample times and finite 3D points."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import sys as _sys
_sys.path.insert(0, str(Path(__file__).resolve().parent))  # BO: helper import works as a script or as Scripts.Tools.*
from json_input import JsonInputError, fail, load_json, require_objects


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cards_json", type=Path)
    args = parser.parse_args()
    try:  # BO-04 / KI-166: name the input and fail closed on malformed JSON or a wrong shape.
        cards = require_objects(args.cards_json, load_json(args.cards_json, dict).get("cards", []), "cards")
        for index, card in enumerate(cards):
            windows = require_objects(args.cards_json, card.get("Windows", []), f"cards[{index}].Windows")
            for w, window in enumerate(windows):
                require_objects(args.cards_json, window.get("BakedSamples", []), f"cards[{index}].Windows[{w}].BakedSamples")
    except JsonInputError as error:
        return fail(error)
    issues = samples = 0
    for card in cards:
        for window in card.get("Windows", []):
            previous = None
            for index, sample in enumerate(window.get("BakedSamples", [])):
                samples += 1
                time = sample.get("TimeSeconds")
                points = [sample.get(key) for key in ("BaseCS", "TipCS")]
                valid = isinstance(time, (int, float)) and math.isfinite(time)
                valid = valid and all(isinstance(p, list) and len(p) == 3 and all(isinstance(v, (int, float)) and math.isfinite(v) for v in p) for p in points)
                if valid:
                    valid = window.get("StartSeconds", time) - 1e-6 <= time <= window.get("EndSeconds", time) + 1e-6
                    valid = valid and (previous is None or time > previous)
                if not valid:
                    issues += 1
                    print(f"{card.get('MoveId','?')}:{window.get('WindowId','?')} sample[{index}] invalid or unordered")
                elif valid:
                    previous = time
    print(f"cards={len(cards)} samples={samples} issues={issues}")
    return int(issues > 0)


if __name__ == "__main__":
    raise SystemExit(main())
