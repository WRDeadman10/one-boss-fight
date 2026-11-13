#!/usr/bin/env python3
"""Strict offline intake gate for the owner-approved Round 6 Phase 2 receipt."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import sys as _sys
_sys.path.insert(0, str(Path(__file__).resolve().parent))  # BP-01/02: sibling imports work as a script or as `python -m Scripts.Tools.*`
from round6_benchmark_report import MODE_WITNESSES, SCHEMA, render, summarize, validate


EXPECTED_MODE = "Performance"
EXPECTED_PRIMARY_PERCENT = 50.0
EXPECTED_BUILD_ID = "OBF-DEVELOPMENT-20261106T071240Z-ed06b4d6"
BUILD_ID_PATTERN = re.compile(r"^OBF-DEVELOPMENT-\d{8}T\d{6}Z-[0-9a-f]{8}$")


def validate_phase2(receipt: Any) -> list[str]:
    if not isinstance(receipt, dict):
        return ["receipt must be an object"]
    issues = validate(receipt)
    if receipt.get("schema") != SCHEMA:
        return issues
    if receipt.get("phase") != "phase2":
        issues.append("phase must be phase2")

    build_id = receipt.get("build_id")
    if not isinstance(build_id, str) or not BUILD_ID_PATTERN.fullmatch(build_id):
        issues.append("build_id must match OBF-DEVELOPMENT-<UTC timestamp>-<8 lowercase hex>")
    elif build_id != EXPECTED_BUILD_ID:
        issues.append(f"build_id must match the Phase 2 R6b Development kit {EXPECTED_BUILD_ID}")

    selected_mode = receipt.get("selected_mode")
    if selected_mode != EXPECTED_MODE:
        issues.append(f"selected_mode must match C-951 owner choice {EXPECTED_MODE}")
    primary_percent = receipt.get("selected_primary_screen_percentage")
    if (not isinstance(primary_percent, (int, float)) or isinstance(primary_percent, bool)
            or abs(float(primary_percent) - EXPECTED_PRIMARY_PERCENT) > 0.01):
        issues.append("selected_primary_screen_percentage must be 50 for the C-951 Performance base")

    mode_witness = MODE_WITNESSES[EXPECTED_MODE]
    runs = receipt.get("runs")
    if isinstance(runs, list):
        for index, row in enumerate(runs):
            if not isinstance(row, dict) or row.get("kind") != "treatment":
                continue
            line = row.get("active_mode_log_line")
            if not isinstance(line, str) or mode_witness not in line:
                issues.append(f"runs[{index}].active_mode_log_line must witness {EXPECTED_MODE}")
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("receipt", type=Path)
    args = parser.parse_args()
    try:
        receipt = json.loads(args.receipt.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"INVALID: cannot read receipt: {exc}")
        return 2
    issues = validate_phase2(receipt)
    if issues:
        print("INVALID: " + "; ".join(issues))
        return 2
    print(f"VALID Phase 2 receipt: build={receipt['build_id']} mode={EXPECTED_MODE} runs={len(receipt['runs'])}")
    summary = summarize(receipt)
    summary["modes"][0]["mode"] = f"{EXPECTED_MODE} base"
    print(render(summary), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
