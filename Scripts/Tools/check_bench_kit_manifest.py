#!/usr/bin/env python3
"""Validate the literal copy manifest in Scripts/MakeBenchKit.ps1."""
from __future__ import annotations

import argparse
import re
from pathlib import Path


LOOP = re.compile(r"foreach\s*\(\s*\$f\s+in\s*([^)]*)\)", re.IGNORECASE | re.DOTALL)
QUOTED = re.compile(r"'([^']+)'|\"([^\"]+)\"")


def manifest_names(text: str) -> list[str]:
    match = LOOP.search(text)
    if not match:
        raise ValueError("literal foreach ($f in ...) copy manifest not found")
    return [single or double for single, double in QUOTED.findall(match.group(1))]


def validate(names: list[str], scripts: Path) -> list[str]:
    issues = []
    seen: set[str] = set()
    for name in names:
        key = name.casefold()
        if key in seen:
            issues.append(f"DUPLICATE destination Scripts/{name}")
        seen.add(key)
        if not (scripts / name).is_file():
            issues.append(f"MISSING source Scripts/{name}")
    if not names:
        issues.append("EMPTY copy manifest")
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    names = manifest_names((args.root / "Scripts/MakeBenchKit.ps1").read_text(encoding="utf-8"))
    issues = validate(names, args.root / "Scripts")
    print(f"[BENCH_KIT_MANIFEST] entries={len(names)} unique_destinations={len({name.casefold() for name in names})} issues={len(issues)}")
    for issue in issues:
        print("ISSUE " + issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
