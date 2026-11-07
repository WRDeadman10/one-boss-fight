#!/usr/bin/env python3
"""Discover focused offline player-contract tests without importing the suite."""
from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path


CONTRACT_FILES = (
    ("air_attack", "Scripts/Tools/test_air_attack_wiring_contract.py"),
    ("default_route", "Scripts/Tools/test_default_route_contract.py"),
    ("dlss_player_settings", "Scripts/Tools/test_dlss_player_settings_contract.py"),
    ("guard_counter", "Scripts/Tools/test_guard_counter_wiring_contract.py"),
    ("optional_presentation", "Scripts/Tools/test_optional_presentation_wiring_contract.py"),
)


def discover(root: Path) -> tuple[list[dict[str, object]], list[str]]:
    rows: list[dict[str, object]] = []
    issues: list[str] = []
    for group, relative in CONTRACT_FILES:
        path = root / relative
        if not path.is_file():
            issues.append(f"missing contract file: {relative}")
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=relative)
        except (OSError, UnicodeError, SyntaxError) as error:
            issues.append(f"cannot parse {relative}: {error}")
            continue
        tests = []
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                for member in node.body:
                    if isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef)) and member.name.startswith("test_"):
                        tests.append((f"{node.name}.{member.name}", member.lineno))
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_"):
                tests.append((node.name, node.lineno))
        tests.sort()
        if not tests:
            issues.append(f"no test methods discovered: {relative}")
        rows.extend({"group": group, "test": name, "path": relative, "line": line} for name, line in tests)
    rows.sort(key=lambda row: (str(row["group"]), str(row["test"]), str(row["path"]), int(row["line"])))
    return rows, issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--json", action="store_true", help="emit stable JSON instead of tab-separated rows")
    args = parser.parse_args()
    rows, issues = discover(args.root.resolve())
    if args.json:
        print(json.dumps({"schema": 1, "rows": rows, "issues": issues,
                          "test_count": len(rows), "group_count": len({row['group'] for row in rows})},
                         indent=2, sort_keys=True))
    else:
        for row in rows:
            print(f"{row['group']}\t{row['test']}\t{row['path']}:{row['line']}")
        print(f"focused_tests={len(rows)} groups={len({row['group'] for row in rows})}")
        for issue in issues:
            print(f"ERROR\t{issue}")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
