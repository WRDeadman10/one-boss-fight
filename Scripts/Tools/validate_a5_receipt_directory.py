#!/usr/bin/env python3
"""Check expected A5 receipt-pair IDs and exactly one legacy/data arm per pair."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


ARM_FILES = {"legacy": "receipt_legacy.json", "data": "receipt_data.json"}


def validate(root: Path, expected_ids: list[str]) -> list[str]:
    issues = []
    if not root.is_dir():
        return [f"receipt root is not a directory: {root}"]
    seen: dict[str, Path] = {}
    found: set[str] = set()
    for legacy_path in sorted(root.rglob(ARM_FILES["legacy"])):
        pair_dir = legacy_path.parent
        data_path = pair_dir / ARM_FILES["data"]
        legacy_path = pair_dir / ARM_FILES["legacy"]
        if not data_path.is_file():
            issues.append(f"MISSING data arm for {pair_dir.relative_to(root).as_posix()}")
            continue
        try:
            legacy = json.loads(legacy_path.read_text(encoding="utf-8-sig"))
            data = json.loads(data_path.read_text(encoding="utf-8-sig"))
        except (OSError, UnicodeError, json.JSONDecodeError) as error:
            issues.append(f"INVALID receipt in {pair_dir.relative_to(root).as_posix()}: {error}")
            continue
        if not isinstance(legacy, dict) or not isinstance(data, dict):
            issues.append(f"INVALID receipt object in {pair_dir.relative_to(root).as_posix()}: expected JSON objects")
            continue
        left_identity = legacy.get("identity")
        right_identity = data.get("identity")
        left = left_identity.get("driver") if isinstance(left_identity, dict) else None
        right = right_identity.get("driver") if isinstance(right_identity, dict) else None
        if not isinstance(left, str) or not left or not isinstance(right, str) or not right:
            issues.append(f"MISSING pair ID (identity.driver) in {pair_dir.relative_to(root).as_posix()}")
            continue
        if left != right:
            issues.append(f"CONTRADICTORY pair IDs in {pair_dir.relative_to(root).as_posix()}: {left} vs {right}")
        pair_id = left
        if pair_id in seen:
            issues.append(f"DUPLICATE pair ID {pair_id}: {seen[pair_id].relative_to(root).as_posix()} and {pair_dir.relative_to(root).as_posix()}")
        else:
            seen[pair_id] = pair_dir
        found.update((left, right))
        for route, receipt in (("legacy", legacy), ("data", data)):
            if receipt.get("route") != route:
                issues.append(f"CONTRADICTORY {route} arm route for {pair_id}: {receipt.get('route')!r}")
    for data_path in sorted(root.rglob(ARM_FILES["data"])):
        legacy_path = data_path.parent / ARM_FILES["legacy"]
        if not legacy_path.is_file():
            issues.append(f"MISSING legacy arm for {data_path.parent.relative_to(root).as_posix()}")
    for pair_id in sorted(set(expected_ids) - found):
        issues.append(f"MISSING pair ID {pair_id}")
    for pair_id in sorted(found - set(expected_ids)):
        issues.append(f"UNEXPECTED pair ID {pair_id}")
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("receipt_root", type=Path)
    parser.add_argument("--expected", type=Path, required=True, help="JSON array of expected identity.driver IDs")
    args = parser.parse_args()
    try:
        expected = json.loads(args.expected.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        print(f"[A5_RECEIPT_DIRECTORY] FAIL invalid expected IDs: {error}")
        return 2
    if not isinstance(expected, list) or any(not isinstance(item, str) or not item for item in expected) or len(expected) != len(set(expected)):
        print("[A5_RECEIPT_DIRECTORY] FAIL expected IDs must be a unique array of nonempty strings")
        return 2
    issues = validate(args.receipt_root, expected)
    if issues:
        print(f"[A5_RECEIPT_DIRECTORY] FAIL issues={len(issues)}")
        for issue in issues:
            print("ISSUE " + issue)
        return 1
    print(f"[A5_RECEIPT_DIRECTORY] PASS pairs={len(expected)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
