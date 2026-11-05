#!/usr/bin/env python3
"""Print move-card timing and baked sample counts from a JSON export."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("card_json", type=Path)
    args = parser.parse_args()
    data = json.loads(args.card_json.read_text(encoding="utf-8"))
    cards = data if isinstance(data, list) else data.get("cards", [data])
    print("MOVE\tCLIP\tCOMMIT\tACTIVE START\tACTIVE END\tRECOVERY\tBAKED SAMPLES")
    for card in cards:
        windows = card.get("Windows", card.get("windows", [])) or []
        samples = sum(len(window.get("BakedSamples", window.get("bakedSamples", [])) or []) for window in windows)
        def field(*keys):
            return next((card[k] for k in keys if k in card), "")
        print("\t".join(str(x) for x in (field("MoveId", "moveId"), field("ClipLengthSeconds", "clipLengthSeconds"),
              field("CommitSeconds", "commitSeconds"), field("ActiveStartSeconds", "activeStartSeconds"),
              field("ActiveEndSeconds", "activeEndSeconds"), field("RecoveryEndSeconds", "recoveryEndSeconds"), samples)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
