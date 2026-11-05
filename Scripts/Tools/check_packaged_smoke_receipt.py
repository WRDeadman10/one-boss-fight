#!/usr/bin/env python3
"""Validate captured stdout from Scripts/PackagedSmoke.ps1."""
from __future__ import annotations

import argparse
import re
from pathlib import Path


PROCESS = re.compile(r"^\[Smoke\] (PASS|FAIL) process \d+ (remained alive for|exited before) (\d+) s$", re.MULTILINE)
SHIPPING_CHECK = re.compile(r"^\[Smoke\] (PASS|FAIL) Shipping binary check(?: exit \d+)?$", re.MULTILINE)
DEV_CHECK = re.compile(r"^\[Smoke\] (PASS|FAIL) packaged log checker(?: exit \d+)?$", re.MULTILINE)
VERDICT = re.compile(r"^\[Smoke\] VERDICT (PASS|FAIL)(?: \(Shipping: alive and no debug names\))?$", re.MULTILINE)


def validate(text: str, configuration: str, exit_code: int) -> list[str]:
    issues: list[str] = []
    process = PROCESS.findall(text)
    verdict = VERDICT.findall(text)
    shipping = SHIPPING_CHECK.findall(text)
    development = DEV_CHECK.findall(text)
    if len(process) != 1:
        issues.append(f"expected exactly one process result; found {len(process)}")
    if len(verdict) != 1:
        issues.append(f"expected exactly one verdict; found {len(verdict)}")
    expected = shipping if configuration == "Shipping" else development
    forbidden = development if configuration == "Shipping" else shipping
    if len(expected) != 1:
        issues.append(f"expected exactly one {configuration} validation result; found {len(expected)}")
    if forbidden:
        issues.append(f"unexpected validation result for other configuration; found {len(forbidden)}")
    if len(process) == 1:
        status, action, _seconds = process[0]
        if (status == "PASS") != (action == "remained alive for"):
            issues.append("process status contradicts process detail")
    if len(verdict) == 1 and len(process) == 1 and len(expected) == 1:
        status = verdict[0]
        check_status = expected[0]
        process_ok = process[0][0] == "PASS"
        expected_ok = check_status == "PASS"
        should_pass = process_ok and expected_ok
        if (status == "PASS") != should_pass:
            issues.append("verdict contradicts process and configuration check results")
    if len(verdict) == 1 and ((verdict[0] == "PASS") != (exit_code == 0)):
        issues.append("process exit code contradicts verdict")
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("receipt", type=Path, help="captured complete PackagedSmoke stdout")
    parser.add_argument("--configuration", choices=("Shipping", "Development"), required=True)
    parser.add_argument("--exit-code", type=int, required=True, help="PackagedSmoke.ps1 process exit code")
    args = parser.parse_args()
    try:
        text = args.receipt.read_text(encoding="utf-8-sig")
    except OSError as error:
        print(f"[SMOKE_RECEIPT] FAIL cannot read receipt: {error}")
        return 2
    issues = validate(text, args.configuration, args.exit_code)
    if issues:
        print(f"[SMOKE_RECEIPT] FAIL configuration={args.configuration} issues={len(issues)}")
        for issue in issues:
            print(f"ISSUE {issue}")
        return 1
    print(f"[SMOKE_RECEIPT] PASS configuration={args.configuration} exit_code={args.exit_code}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
