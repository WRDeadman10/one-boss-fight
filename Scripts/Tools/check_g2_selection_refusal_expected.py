#!/usr/bin/env python3
"""Check that the G2 expected-sheet cases and tokens remain in its PIE driver."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import sys as _sys
_sys.path.insert(0, str(Path(__file__).resolve().parent))  # BP-06: sibling json_input as a script or via -m
from json_input import JsonInputError, fail, load_json, require_objects


def audit(sheet: dict, driver: str) -> list[str]:
    issues = []
    cases = sheet.get("cases")
    if not isinstance(cases, list) or not cases or len(cases) != len(set(cases)):
        issues.append("expected cases must be a nonempty unique list")
        cases = []
    for case in cases:
        if f'"{case}"' not in driver and f"'{case}'" not in driver:
            issues.append(f"case missing from driver: {case}")
    tokens = sheet.get("required_log_tokens")
    if not isinstance(tokens, list) or not tokens or len(tokens) != len(set(tokens)):
        issues.append("required_log_tokens must be a nonempty unique list")
        tokens = []
    for token in tokens:
        if token not in driver:
            issues.append(f"expected log token missing from driver: {token}")
    return issues


def load_sheet(path: Path) -> dict:
    """BP-06 (+ X-2298): the expected sheet must be a JSON object whose "cases" and "required_log_tokens" are nonempty
    lists of unique strings. Element types are validated BEFORE any set() use, so a malformed but valid-JSON sheet (for
    example {"cases": [{}]}) is a named JsonInputError (exit 2), never an uncaught TypeError."""
    sheet = load_json(path, dict)
    for key in ("cases", "required_log_tokens"):
        values = sheet.get(key)
        if not isinstance(values, list) or not values:
            raise JsonInputError(f"{path}: {key} must be a nonempty list")
        bad = [index for index, item in enumerate(values) if not isinstance(item, str)]
        if bad:
            raise JsonInputError(f"{path}: {key}[{bad[0]}] must be a string, found {type(values[bad[0]]).__name__}")
        if len(values) != len(set(values)):
            raise JsonInputError(f"{path}: {key} contains duplicate values")
    return sheet


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sheet", type=Path, default=Path(__file__).with_name("g2_selection_refusal_expected.json"))
    parser.add_argument("--driver", type=Path, default=Path(__file__).parents[1] / "Editor" / "pie_selection_refusal.py")
    args = parser.parse_args()
    try:
        sheet = load_sheet(args.sheet)
    except JsonInputError as error:
        return fail(error)
    driver = args.driver.read_text(encoding="utf-8")
    issues = audit(sheet, driver)
    if issues:
        print(f"[G2_EXPECTED] FAIL issues={len(issues)}")
        for issue in issues:
            print(f"ISSUE {issue}")
        return 1
    print(f"[G2_EXPECTED] PASS cases={len(sheet['cases'])} tokens={len(sheet['required_log_tokens'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
