#!/usr/bin/env python3
"""Check baked card exports for increasing in-window sample times and finite 3D points."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cards_json", type=Path)
    args = parser.parse_args()
    cards = json.loads(args.cards_json.read_text(encoding="utf-8")).get("cards", [])
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
