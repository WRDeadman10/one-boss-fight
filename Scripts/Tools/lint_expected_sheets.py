#!/usr/bin/env python3
"""Lint FrameworkProof EXPECTED sheets for registered tokens and required sections."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

TOKEN_LINE = re.compile(r"\[FrameworkProof\]\s*([A-Za-z_][A-Za-z0-9_]*)")
HEADINGS = {"setup", "control", "pass", "fail"}


def load_schemas(root: Path) -> set[str]:
    reviews = root / "Docs/BossCombatReview/Execution/Antigravity/Reviews"
    sys.path.insert(0, str(reviews))
    import validate_framework_proof_logs
    return set(validate_framework_proof_logs.SCHEMAS)


def lint(path: Path, schema_tokens: set[str]) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    headings = {match.group(1).strip().casefold() for match in re.finditer(r"^##\s+(.+?)\s*$", text, re.MULTILINE)}
    issues = [f"missing required section: {name}" for name in sorted(HEADINGS - headings)]
    for number, line in enumerate(text.splitlines(), 1):
        for match in TOKEN_LINE.finditer(line):
            token = match.group(1)
            if token not in schema_tokens:
                issues.append(f"line {number}: unregistered FrameworkProof token {token!r}")
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path, help="one or more *_EXPECTED.md sheets")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    try:
        schemas = load_schemas(args.root.resolve())
    except (ImportError, OSError, SyntaxError) as error:
        parser.error(f"could not load FrameworkProof schemas: {error}")
    failed = False
    for path in args.paths:
        if not path.is_file():
            print(f"FAIL {path}: file missing")
            failed = True
            continue
        issues = lint(path, schemas)
        if issues:
            failed = True
            for issue in issues:
                print(f"FAIL {path}: {issue}")
        else:
            print(f"PASS {path}: registered tokens; Setup/Control/PASS/FAIL sections present")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
