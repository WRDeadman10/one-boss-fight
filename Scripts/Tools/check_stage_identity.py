#!/usr/bin/env python3
"""Read-only preflight for distinct Shipping and Development UAT stage roots."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re


REQUIRED = (
    "OneBossFight.exe",
    "Manifest_UFSFiles_Win64.txt",
    "Manifest_NonUFSFiles_Win64.txt",
    "OneBossFight/Saved/BuildStamp.txt",
)


def inspect_stage(root: Path, configuration: str) -> dict:
    root = root.resolve()
    missing = [name for name in REQUIRED if not (root / name).is_file()]
    empty = [name for name in REQUIRED if (root / name).is_file() and (root / name).stat().st_size == 0]
    stamp_path = root / "OneBossFight/Saved/BuildStamp.txt"
    stamp = stamp_path.read_text(encoding="ascii", errors="replace").strip() if stamp_path.is_file() else None
    valid_stamp = bool(stamp and re.fullmatch(r"OBF-" + configuration.upper() + r"-\d{8}T\d{6}Z-[0-9a-fA-F]{8}", stamp))
    issues = []
    if missing:
        issues.append("missing stage files: " + ", ".join(missing))
    if empty:
        issues.append("empty stage files: " + ", ".join(empty))
    if stamp is not None and not valid_stamp:
        issues.append("BuildStamp configuration or format mismatch: " + stamp)
    return {"root": str(root), "configuration": configuration, "build_id": stamp,
            "missing": missing, "empty": empty, "issues": issues}


def validate(shipping: Path, development: Path) -> dict:
    ship = inspect_stage(shipping, "Shipping")
    dev = inspect_stage(development, "Development")
    issues = ship["issues"] + dev["issues"]
    if ship["root"].casefold() == dev["root"].casefold():
        issues.append("Shipping and Development stage roots resolve to the same directory")
    if ship["build_id"] and ship["build_id"] == dev["build_id"]:
        issues.append("Shipping and Development share one build ID")
    return {"schema": "onebossfight.stage-identity/v1", "shipping": ship,
            "development": dev, "issues": issues, "verdict": "PASS" if not issues else "FAIL"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--shipping-stage", required=True, type=Path)
    parser.add_argument("--development-stage", required=True, type=Path)
    args = parser.parse_args()
    result = validate(args.shipping_stage, args.development_stage)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
