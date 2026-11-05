#!/usr/bin/env python3
"""Check that the G2 expected-sheet cases and tokens remain in its PIE driver."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sheet", type=Path, default=Path(__file__).with_name("g2_selection_refusal_expected.json"))
    parser.add_argument("--driver", type=Path, default=Path(__file__).parents[1] / "Editor" / "pie_selection_refusal.py")
    args = parser.parse_args()
    sheet = json.loads(args.sheet.read_text(encoding="utf-8"))
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
