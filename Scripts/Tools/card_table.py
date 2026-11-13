#!/usr/bin/env python3
"""Print move-card timing and baked sample counts from a JSON export."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import sys as _sys
_sys.path.insert(0, str(Path(__file__).resolve().parent))  # BO: helper import works as a script or as Scripts.Tools.*
from json_input import JsonInputError, fail, load_json, require_objects


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("card_json", type=Path)
    args = parser.parse_args()
    try:  # BO-04 / KI-166: validate the whole shape before printing anything (no partial table on bad input).
        data = load_json(args.card_json, (dict, list))
        cards = require_objects(args.card_json, data if isinstance(data, list) else data.get("cards", [data]), "cards")
        for index, card in enumerate(cards):
            windows = card.get("Windows", card.get("windows", [])) or []
            require_objects(args.card_json, windows, f"cards[{index}].Windows")
            for w, window in enumerate(windows):
                baked = window.get("BakedSamples", window.get("bakedSamples", [])) or []
                if not isinstance(baked, list):
                    raise JsonInputError(f"{args.card_json}: cards[{index}].Windows[{w}].BakedSamples must be a list")
    except JsonInputError as error:
        return fail(error)
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
